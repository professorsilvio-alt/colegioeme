import csv
import datetime
import io
import sys
import os
from datetime import date
from collections import defaultdict

from django.conf import settings

# ─────────────────────────────────────────────────────────
# FERIADOS 2026 — Nacionais + RJ (estaduais) + Nova Iguaçu
# ─────────────────────────────────────────────────────────
FERIADOS_2026 = {
    # Nacionais fixos
    datetime.date(2026, 1, 1),   # Confraternização Universal
    datetime.date(2026, 4, 21),  # Tiradentes
    datetime.date(2026, 5, 1),   # Dia do Trabalho
    datetime.date(2026, 9, 7),   # Independência do Brasil
    datetime.date(2026, 10, 12), # Nossa Senhora Aparecida
    datetime.date(2026, 11, 2),  # Finados
    datetime.date(2026, 11, 15), # Proclamação da República
    datetime.date(2026, 11, 20), # Consciência Negra (nacional)
    datetime.date(2026, 12, 25), # Natal
    # Nacionais móveis (2026)
    datetime.date(2026, 2, 16),  # Carnaval (segunda)
    datetime.date(2026, 2, 17),  # Carnaval (terça)
    datetime.date(2026, 4, 2),   # Sexta-feira Santa
    datetime.date(2026, 4, 4),   # Páscoa
    datetime.date(2026, 6, 4),   # Corpus Christi
    # Estaduais — Rio de Janeiro
    datetime.date(2026, 4, 23),  # São Jorge (padroeiro do RJ)
    # Municipais — Nova Iguaçu
    datetime.date(2026, 1, 15),  # Aniversário de Nova Iguaçu
    datetime.date(2026, 4, 25),  # Dia de São Marcos (padroeiro)
}


def get_feriados(ano_letivo=None, escola=None):
    """Retorna o conjunto de datas de feriados a partir da Configuracao."""
    try:
        from .models import Configuracao
        config = Configuracao.objects.filter(ano_letivo=ano_letivo, escola=escola).first()
        if config:
            feriados = config.get_feriados()
            if feriados:
                return feriados
    except Exception:
        pass
    # Fallback apenas para 2026 se o ano for compatível ou não informado
    if not ano_letivo or ano_letivo.ano == 2026:
        return FERIADOS_2026
    return set()


from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.staticfiles import finders
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .models import (Aluno, ConteudoProgramatico, Disciplina, Ocorrencia,
                     Professor, SugestaoConteudo, Turma, Configuracao)


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

def _verificar_recaptcha(token):
    """Verifica o token reCAPTCHA v3 com os servidores do Google. Retorna True se válido."""
    if settings.DEBUG or getattr(settings, 'BYPASS_RECAPTCHA', False):
        return True
    import urllib.request
    import urllib.parse
    import json
    secret = settings.RECAPTCHA_SECRET_KEY
    if not secret or not token:
        # Se não configurado, permite a requisição (modo de desenvolvimento)
        return True
    data = urllib.parse.urlencode({
        'secret': secret,
        'response': token,
    }).encode()
    try:
        req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
        return result.get('success', False) and result.get('score', 0) >= settings.RECAPTCHA_MIN_SCORE
    except Exception:
        # Em caso de falha de rede, permite (não bloqueia usuários legítimos)
        return True


def login_view(request):
    from .models import Escola
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        senha = request.POST.get('senha', '')
        token = request.POST.get('g-recaptcha-response', '')
        escola_id = request.POST.get('escola')

        # Verifica reCAPTCHA antes de autenticar
        if not _verificar_recaptcha(token):
            messages.error(request, 'Verificação de segurança falhou. Tente novamente.')
            return render(request, 'core/login.html', {
                'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
                'escolas': Escola.objects.all()
            })

        user = authenticate(request, username=usuario, password=senha)
        if user:
            login(request, user)
            # Salva a escola selecionada na sessão
            if escola_id:
                request.session['escola_id'] = escola_id
            # Limpa tentativas em caso de sucesso
            ip = request.META.get('REMOTE_ADDR')
            cache.delete(f'login_attempts_{ip}')
            return redirect('dashboard')
        else:
            # Incrementa tentativas em caso de falha
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            cache.set(cache_key, attempts + 1, 300) # Expira em 5 min
            messages.error(request, 'Usuário ou senha incorretos!')
    return render(request, 'core/login.html', {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
        'escolas': Escola.objects.all()
    })


def logout_view(request):
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def get_professor(user):
    """Retorna o Professor ligado ao user, ou None (admin sem perfil)."""
    try:
        return user.professor
    except Professor.DoesNotExist:
        return None


def ocorrencias_do_usuario(request):
    user = request.user
    prof = get_professor(user)
    ano_letivo = request.ano_letivo
    escola = request.escola
    qs = Ocorrencia.objects.select_related('turma', 'professor', 'disciplina').prefetch_related('alunos')
    
    if escola:
        qs = qs.filter(turma__escola=escola)
    if ano_letivo:
        qs = qs.filter(turma__ano_letivo=ano_letivo)
    
    if not prof:
        return qs  # superuser/admin sem perfil: vê tudo
    
    # Secretária não deve visualizar as ocorrências
    if not prof.pode_ver_ocorrencias:
        return Ocorrencia.objects.none()

    if prof.cargo == 'INSPETOR' or prof.cargo in ['DIRETOR', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR', 'ADMIN']:
        # Cargos de gestão e inspetores veem tudo (respeitando a restrição de secretária acima)
        pass
    else:
        # Professor comum vê apenas suas próprias ocorrências
        qs = qs.filter(professor=prof)
    return qs


def conteudos_do_usuario(request):
    user = request.user
    prof = get_professor(user)
    ano_letivo = request.ano_letivo
    escola = request.escola
    qs = ConteudoProgramatico.objects.select_related('professor', 'disciplina').prefetch_related('turmas')
    
    if escola:
        qs = qs.filter(turmas__escola=escola)
    if ano_letivo:
        qs = qs.filter(turmas__ano_letivo=ano_letivo).distinct()
        
    if prof and not prof.pode_ver_tudo:
        qs = qs.filter(professor=prof)
    return qs


def filtrar_ocorrencias(request, qs):
    filtro_turma = request.GET.get('filtro_turma', '')
    filtro_status = request.GET.get('filtro_status', '')
    filtro_professor = request.GET.get('filtro_professor', '')
    filtro_data_ini = request.GET.get('data_ini', '')
    filtro_data_fim = request.GET.get('data_fim', '')

    resumo = []
    if filtro_turma:
        qs = qs.filter(turma__codigo=filtro_turma)
        resumo.append(f"Turma: {filtro_turma}")
    if filtro_status:
        qs = qs.filter(status=filtro_status)
        resumo.append(f"Status: {filtro_status}")
    if filtro_professor:
        p = get_object_or_404(Professor, pk=filtro_professor)
        qs = qs.filter(professor=p)
        resumo.append(f"Professor: {p.nome}")
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
        resumo.append(f"Início: {filtro_data_ini}")
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
        resumo.append(f"Fim: {filtro_data_fim}")

    return qs, " | ".join(resumo)


def filtrar_conteudos(request, qs, override_prof=None):
    filtro_turma_c = request.GET.get('filtro_turma_c', '')
    filtro_disc_c = request.GET.get('filtro_disc_c', '')
    filtro_prof_c = override_prof or request.GET.get('filtro_prof_c', '')
    filtro_data_ini = request.GET.get('data_ini', '')
    filtro_data_fim = request.GET.get('data_fim', '')

    resumo = []
    if filtro_turma_c:
        qs = qs.filter(turmas__codigo=filtro_turma_c)
        resumo.append(f"Turma: {filtro_turma_c}")
    if filtro_disc_c:
        d = get_object_or_404(Disciplina, pk=filtro_disc_c)
        qs = qs.filter(disciplina=d)
        resumo.append(f"Disc: {d.nome}")
    if filtro_prof_c:
        p = get_object_or_404(Professor, pk=filtro_prof_c)
        qs = qs.filter(professor=p)
        resumo.append(f"Prof: {p.nome}")
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
        resumo.append(f"Início: {filtro_data_ini}")
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
        resumo.append(f"Fim: {filtro_data_fim}")

    return qs, " | ".join(resumo)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    prof = get_professor(request.user)
    turmas_qs = prof.get_turmas(ano_letivo=request.ano_letivo, escola=request.escola) if prof else Turma.objects.filter(ano_letivo=request.ano_letivo, escola=request.escola)
    disciplinas_qs = prof.get_disciplinas() if prof else Disciplina.objects.all()

    ocorrencias = ocorrencias_do_usuario(request)
    total = ocorrencias.count()
    abertas = ocorrencias.filter(status='Aberta').count()
    resolvidas = ocorrencias.filter(status='Resolvida').count()

    oc_filtradas, _ = filtrar_ocorrencias(request, ocorrencias)
    cont_qs = conteudos_do_usuario(request)
    
    filtro_turma_c = request.GET.get('filtro_turma_c', '')
    filtro_disc_c = request.GET.get('filtro_disc_c', '')
    filtro_prof_c = request.GET.get('filtro_prof_c', '')
    
    override_prof = None
    if filtro_turma_c and filtro_disc_c and not filtro_prof_c:
        from .models import GradeHoraria
        grade = GradeHoraria.objects.filter(turma__codigo=filtro_turma_c, disciplina_id=filtro_disc_c)
        if grade.exists():
            prof_auto = grade.first().professor
            if prof_auto:
                override_prof = str(prof_auto.pk)
                filtro_prof_c = override_prof

    cont_filtrados, _ = filtrar_conteudos(request, cont_qs, override_prof=override_prof)

    # Lógica de Filtros Cascata para Conteúdo
    disciplinas_tab_c = disciplinas_qs
    professores_tab_c = Professor.objects.all()

    if filtro_turma_c:
        from .models import GradeHoraria
        # Filtra disciplinas baseadas na grade horária daquela turma
        disc_ids = GradeHoraria.objects.filter(
            turma__codigo=filtro_turma_c
        ).values_list('disciplina_id', flat=True).distinct()
        
        # Filtra professores baseados na grade horária daquela turma
        prof_ids = GradeHoraria.objects.filter(
            turma__codigo=filtro_turma_c
        ).values_list('professor_id', flat=True).distinct()

        if prof and not prof.pode_ver_tudo:
            # Professor comum: vê apenas suas disciplinas naquela turma
            disc_ids_prof = GradeHoraria.objects.filter(
                turma__codigo=filtro_turma_c,
                professor=prof
            ).values_list('disciplina_id', flat=True).distinct()
            disciplinas_tab_c = Disciplina.objects.filter(pk__in=disc_ids_prof)
            professores_tab_c = Professor.objects.filter(pk=prof.pk)
        else:
            # Admin/Gestão: vê todas as disciplinas e professores daquela turma
            disciplinas_tab_c = Disciplina.objects.filter(pk__in=disc_ids)
            professores_tab_c = Professor.objects.filter(pk__in=prof_ids)
    else:
        # Se nenhuma turma selecionada, mas for professor, limita aos dele
        if prof and not prof.pode_ver_tudo:
            disciplinas_tab_c = prof.get_disciplinas()
            professores_tab_c = Professor.objects.filter(pk=prof.pk)

    # Garante que as disciplinas referentes a eventuais Aulas Extras que o usuário lançou apareçam no filtro
    if cont_qs.exists():
        lancadas_ids = cont_qs.values_list('disciplina_id', flat=True).distinct()
        disciplinas_tab_c = (disciplinas_tab_c | Disciplina.objects.filter(pk__in=lancadas_ids)).distinct()

    context = {
        'prof': prof,
        'turmas': turmas_qs,
        'disciplinas': disciplinas_qs,  # usado em modais/outros forms
        'disciplinas_tab_c': disciplinas_tab_c,  # usado no filtro da aba conteúdos
        'todos_professores': Professor.objects.all(), # usado em filtros de ocorrencias
        'professores_tab_c': professores_tab_c, # usado no filtro da aba conteúdos
        'total': total,
        'abertas': abertas,
        'resolvidas': resolvidas,
        'ocorrencias': oc_filtradas,
        'conteudos': cont_filtrados,
        'filtro_turma': request.GET.get('filtro_turma', ''),
        'filtro_status': request.GET.get('filtro_status', ''),
        'filtro_professor': request.GET.get('filtro_professor', ''),
        'filtro_data_ini': request.GET.get('data_ini', ''),
        'filtro_data_fim': request.GET.get('data_fim', ''),
        'filtro_turma_c': filtro_turma_c,
        'filtro_disc_c': filtro_disc_c,
        'filtro_prof_c': filtro_prof_c,
        'filtro_data_ini_c': request.GET.get('data_ini', ''),
        'filtro_data_fim_c': request.GET.get('data_fim', ''),
        'today': date.today().isoformat(),
        'config_pk': Configuracao.objects.filter(ano_letivo=request.ano_letivo, escola=request.escola).values_list('pk', flat=True).first(),
    }
    # Merge content stats without overwriting ocorrência totals
    context.update(calcular_stats_conteudo(prof,
                                           data_ini=request.GET.get('data_ini', ''),
                                           data_fim=request.GET.get('data_fim', ''),
                                           ano_letivo=request.ano_letivo,
                                           escola=request.escola))
    return render(request, 'core/dashboard.html', context)


# ──────────────────────────────────────────────
# API: alunos por turma (AJAX)
# ──────────────────────────────────────────────

@login_required
def api_alunos_turma(request, codigo):
    alunos = Aluno.objects.filter(turma__codigo=codigo, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).order_by('nome')
    data = []
    for a in alunos:
        foto_url = a.foto.url if a.foto else None
        data.append({'id': a.id, 'nome': a.nome, 'foto_url': foto_url})
    return JsonResponse(data, safe=False)


@login_required
def api_professores_disciplina(request, disc_id):
    prof = get_professor(request.user)
    profs = Professor.objects.filter(disciplinas__pk=disc_id)
    if prof and not prof.todas_disciplinas:
        profs = profs.filter(pk=prof.pk)
    return JsonResponse(list(profs.values('id', 'nome')), safe=False)


@login_required
def api_disciplinas_turma(request, codigo):
    """Return disciplines taught in a given turma (from GradeHoraria), filtered by logged-in professor."""
    from .models import GradeHoraria
    prof_logado = get_professor(request.user)
    is_extra = request.GET.get('extra') == '1'

    if is_extra:
        # Modo Aula Extra: ignora a grade horária.
        # Mostra as disciplinas que o professor pode lecionar (se não for admin)
        turmas_1_ano = ['11', '12', '13']
        turmas_2_ano = ['21', '22', '23']
        turmas_3_ano = ['31', '32']
        
        if prof_logado and not prof_logado.pode_ver_tudo and not prof_logado.todas_disciplinas:
            discs = prof_logado.disciplinas.all()
        else:
            discs = Disciplina.objects.all()

        if codigo in turmas_1_ano:
            areas = ['Sociedade e Cidadania', 'Sustentabilidade e Meio Ambiente']
            for area in areas:
                Disciplina.objects.get_or_create(nome=area)
            extras = Disciplina.objects.filter(nome__in=areas)
            discs = (discs | extras).distinct()
            
        elif codigo in turmas_2_ano:
            areas = ['Educação Financeira', 'Múltiplas Linguagens']
            for area in areas:
                Disciplina.objects.get_or_create(nome=area)
            extras = Disciplina.objects.filter(nome__in=areas)
            discs = (discs | extras).distinct()
            
        elif codigo in turmas_3_ano:
            areas = [
                'Ciências da Natureza',
                'Ciências Humanas',
                'Matemática e suas tecnologias',
                'Linguagens e códigos'
            ]
            for area in areas:
                Disciplina.objects.get_or_create(nome=area)
            extras = Disciplina.objects.filter(nome__in=areas)
            discs = (discs | extras).distinct()
            
        # Remover duplicatas devido a JOINs no UNION e ordenar
        ids_vistos = set()
        lista_discs = []
        for d in discs.order_by('nome').values('id', 'nome'):
            if d['id'] not in ids_vistos:
                ids_vistos.add(d['id'])
                lista_discs.append(d)
                
        return JsonResponse(lista_discs, safe=False)
    else:
        qs = GradeHoraria.objects.filter(turma__codigo=codigo, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola)
        if prof_logado and not prof_logado.pode_ver_tudo:
            qs = qs.filter(professor=prof_logado)
        disc_ids = qs.values_list('disciplina_id', flat=True).distinct()
        discs = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
        
    return JsonResponse(list(discs.values('id', 'nome')), safe=False)


@login_required
def api_professores_turma_disc(request, codigo, disc_id):
    """Return professors who teach a given discipline in a given turma."""
    from .models import GradeHoraria
    prof_logado = get_professor(request.user)
    is_extra = request.GET.get('extra') == '1'

    if is_extra:
        # Modo Aula extra: ignora a grade. Todos os professores aptos (ou si mesmo).
        profs = Professor.objects.all().order_by('nome')
    else:
        prof_ids = GradeHoraria.objects.filter(
            turma__codigo=codigo,
            turma__ano_letivo=request.ano_letivo,
            turma__escola=request.escola,
            disciplina__pk=disc_id
        ).values_list('professor_id', flat=True).distinct()
        profs = Professor.objects.filter(pk__in=prof_ids).order_by('nome')
        
    # If the logged-in user is a professor (not admin/coord), limit to themselves
    if prof_logado and not prof_logado.pode_ver_tudo:
        profs = profs.filter(pk=prof_logado.pk)
        
    return JsonResponse(list(profs.values('id', 'nome')), safe=False)


@login_required
def api_datas_validas(request, codigo, prof_id):
    """Return all school-year dates where prof teaches turma, with 'lancado' flag."""
    from .models import GradeHoraria, ConteudoProgramatico
    import datetime

    disc_id = request.GET.get('disciplina')

    # Weekday numbers in GradeHoraria: '1'=Segunda=Monday(0), ..., '5'=Sexta=Friday(4)
    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}

    # Find which days of week this professor teaches this turma
    query = GradeHoraria.objects.filter(
        turma__codigo=codigo,
        turma__ano_letivo=request.ano_letivo,
        turma__escola=request.escola,
        professor__pk=prof_id
    )
    if disc_id:
        query = query.filter(disciplina__pk=disc_id)
        
    dias = query.values_list('dia_semana', flat=True).distinct()

    if not dias:
        return JsonResponse([], safe=False)

    weekdays = {DIA_TO_WEEKDAY[d] for d in dias if d in DIA_TO_WEEKDAY}

    # School year boundaries from configuration or defaults
    config = Configuracao.objects.filter(ano_letivo=request.ano_letivo, escola=request.escola).first()
    if config:
        inicio = config.inicio_periodo_letivo
        fim = config.fim_periodo_letivo
    else:
        ano = datetime.date.today().year
        inicio = datetime.date(ano, 1, 1)
        fim = datetime.date(ano, 12, 20)

    # Generate all valid school dates (excluding holidays)
    feriados = get_feriados(ano_letivo=request.ano_letivo, escola=request.escola)
    datas_validas = []
    cur = inicio
    while cur <= fim:
        if cur.weekday() in weekdays and cur not in feriados:
            datas_validas.append(cur)
        cur += datetime.timedelta(days=1)

    # Find which dates already have a content entry for this professor+turma
    query_lancados = ConteudoProgramatico.objects.filter(
        professor__pk=prof_id,
        turmas__codigo=codigo,
        turmas__ano_letivo=request.ano_letivo,
        turmas__escola=request.escola
    )
    if disc_id:
        query_lancados = query_lancados.filter(disciplina__pk=disc_id)
        
    lancados = set(
        query_lancados.values_list('data', flat=True)
    )

    result = [
        {
            'data': d.isoformat(),
            'label': d.strftime('%d/%m/%Y (%a)').replace(
                'Mon', 'Seg').replace('Tue', 'Ter').replace('Wed', 'Qua'
                ).replace('Thu', 'Qui').replace('Fri', 'Sex'),
            'lancado': d in lancados
        }
        for d in datas_validas
    ]
    return JsonResponse(result, safe=False)


@login_required
def api_professor_grades(request, prof_id):
    """Return all turmas and their weekdays for a given professor."""
    from .models import GradeHoraria
    
    disc_id = request.GET.get('disciplina')
    query = GradeHoraria.objects.filter(professor_id=prof_id, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola)
    if disc_id:
        query = query.filter(disciplina_id=disc_id)
        
    grades = query.values('turma__codigo', 'dia_semana').distinct()
    
    mapping = defaultdict(list)
    for g in grades:
        mapping[g['turma__codigo']].append(g['dia_semana'])
    
    return JsonResponse(dict(mapping), safe=False)
    

@login_required
def api_verificar_duplicidade(request):
    """
    Verifica se já existem registros de conteúdo para as turmas na data e disciplina informadas.
    Retorna uma lista de códigos de turmas que já possuem lançamento.
    """
    data_str = request.GET.get('data')
    prof_id = request.GET.get('professor')
    disc_id = request.GET.get('disciplina')
    turma_cods = request.GET.getlist('turmas[]')

    if not all([data_str, prof_id, disc_id, turma_cods]):
        return JsonResponse({'conflicts': []})

    from .models import ConteudoProgramatico
    conflicts = []
    
    for t_cod in turma_cods:
        # Verifica se já existe um registro para este professor, nesta data, nesta disciplina contendo esta turma
        exists = ConteudoProgramatico.objects.filter(
            data=data_str,
            professor_id=prof_id,
            disciplina_id=disc_id,
            turmas__codigo=t_cod,
            turmas__ano_letivo=request.ano_letivo,
            turmas__escola=request.escola
        ).exists()
        if exists:
            conflicts.append(t_cod)
            
    return JsonResponse({'conflicts': conflicts})


@login_required
def api_precheck_coletivo(request):
    """
    Pre-check para lançamento coletivo: identifica conflitos para múltiplos professores/turmas.
    Suporta busca por data única ou período.
    """
    data_ini_str = request.GET.get('data')
    data_fim_str = request.GET.get('data_fim')
    turma_ids = request.GET.getlist('turmas[]')

    if not data_ini_str or not turma_ids:
        return JsonResponse({'conflicts': []})

    try:
        data_ini = datetime.datetime.strptime(data_ini_str, '%Y-%m-%d').date()
        if data_fim_str:
            data_fim = datetime.datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            if data_fim < data_ini:
                data_ini, data_fim = data_fim, data_ini
        else:
            data_fim = data_ini
    except ValueError:
        return JsonResponse({'conflicts': []})

    from .models import GradeHoraria, ConteudoProgramatico
    
    # Busca todas as grades para as turmas selecionadas
    grades = GradeHoraria.objects.filter(
        turma_id__in=turma_ids
    ).select_related('professor', 'disciplina', 'turma')

    conflicts = []
    seen = set() # Evita duplicatas na lista de conflitos

    for g in grades:
        key = (g.professor_id, g.disciplina_id, g.turma_id)
        if key in seen: continue

        # Verifica se já existe QUALQUER registro para este professor/disciplina/turma no período informado
        exists = ConteudoProgramatico.objects.filter(
            data__gte=data_ini,
            data__lte=data_fim,
            professor_id=g.professor_id,
            disciplina_id=g.disciplina_id,
            turmas__id=g.turma_id
        ).exists()

        if exists:
            conflicts.append({
                'turma_id': g.turma_id,
                'turma_cod': g.turma.codigo,
                'prof_nome': g.professor.nome,
                'disc_nome': g.disciplina.nome
            })
            seen.add(key)

    return JsonResponse({'conflicts': conflicts})


def calcular_stats_conteudo(prof, data_ini=None, data_fim=None, feriados=None, ano_letivo=None, escola=None):
    """
    Retorna estatísticas de total/preenchidos/faltam.
    Otimizado para evitar o problema N+1 queries.
    """
    if feriados is None:
        feriados = get_feriados(ano_letivo=ano_letivo, escola=escola)
    from .models import GradeHoraria, ConteudoProgramatico, Turma
    from django.db.models import Q
    import datetime

    CARGOS_GLOBAIS = ['ADMIN', 'DIRETOR', 'SECRETARIA', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR']
    hoje = datetime.date.today()
    
    # Datas do período letivo
    config = Configuracao.objects.filter(ano_letivo=ano_letivo, escola=escola).first()
    if config:
        config_ini = config.inicio_periodo_letivo
        config_fim = config.fim_periodo_letivo
    else:
        ano = ano_letivo.ano if ano_letivo else hoje.year
        config_ini = datetime.date(ano, 1, 1)
        config_fim = datetime.date(ano, 12, 20)

    # Filtros de data
    inicio = config_ini
    if data_ini:
        try:
            inicio_prov = datetime.datetime.strptime(data_ini, '%Y-%m-%d').date() if isinstance(data_ini, str) else data_ini
            inicio = max(inicio, inicio_prov)
        except (ValueError, TypeError): pass

    fim = config_fim
    if data_fim:
        try:
            fim_prov = datetime.datetime.strptime(data_fim, '%Y-%m-%d').date() if isinstance(data_fim, str) else data_fim
            fim = min(fim, fim_prov)
        except (ValueError, TypeError): pass

    # Escopo: global ou por professor
    global_view = (not prof) or (prof.cargo in CARGOS_GLOBAIS)
    
    # 1. Busca todas as grades relevantes de uma vez
    gh_qs = GradeHoraria.objects.select_related('turma', 'professor')
    if ano_letivo:
        gh_qs = gh_qs.filter(turma__ano_letivo=ano_letivo)
    if escola:
        gh_qs = gh_qs.filter(turma__escola=escola)
    if not global_view:
        gh_qs = gh_qs.filter(professor=prof)
    
    grades = list(gh_qs)
    if not grades:
        return {
            'total_conteudo': 0, 'preenchidos': 0, 'faltam': 0,
            'total_ate_hoje': 0, 'preenchidos_ate_hoje': 0, 'faltam_ate_hoje': 0
        }

    # Agrupa dias da semana por tríade (prof, turma, disc) em memória.
    # Usa set de weekdays (não contagem): garante que múltiplos horários no mesmo
    # dia da semana não inflam o total — igual à lógica do relatório de pendências.
    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    slots_map = defaultdict(set)  # key -> set of weekdays com aula

    for g in grades:
        key = (g.professor_id, g.turma.codigo, g.disciplina_id)
        if g.dia_semana in DIA_TO_WEEKDAY:
            slots_map[key].add(DIA_TO_WEEKDAY[g.dia_semana])

    # 2. Busca todos os conteúdos lançados no período de uma vez
    cp_qs = ConteudoProgramatico.objects.filter(data__gte=inicio, data__lte=fim).prefetch_related('turmas')
    if ano_letivo:
        cp_qs = cp_qs.filter(turmas__ano_letivo=ano_letivo)
    if escola:
        cp_qs = cp_qs.filter(turmas__escola=escola)
    if not global_view:
        cp_qs = cp_qs.filter(professor=prof)
    
    # Mapeia lançamentos existentes: (prof_id, turma_cod, disc_id) -> set of dates
    lancados_map = defaultdict(set)
    extras_adicionais = 0
    extras_adicionais_ate_hoje = 0
    
    disciplinas_peso_2 = [
        'Eletiva 1', 'Eletiva 2', # Nomes legados, caso existam registros
        'Sociedade e Cidadania', 'Sustentabilidade e Meio Ambiente',
        'Educação Financeira', 'Múltiplas Linguagens',
        'Ciências da Natureza', 'Ciências Humanas', 
        'Matemática e suas tecnologias', 'Linguagens e códigos'
    ]

    for cp in cp_qs:
        for t in cp.turmas.all():
            key = (cp.professor_id, t.codigo, cp.disciplina_id)
            if key in slots_map: # Só conta se estiver na grade
                lancados_map[key].add(cp.data)
            elif cp.disciplina and cp.disciplina.nome in disciplinas_peso_2:
                # Aula extra fora da grade com peso 2
                extras_adicionais += 2
                if cp.data <= hoje:
                    extras_adicionais_ate_hoje += 2

    # 3. Processa cálculos em Python
    total = extras_adicionais
    total_ate_hoje = extras_adicionais_ate_hoje
    preenchidos = extras_adicionais
    preenchidos_ate_hoje = extras_adicionais_ate_hoje

    for key, weekdays in slots_map.items():
        # Cálculo de esperado (Total): 1 por data de aula no período
        cur = inicio
        while cur <= fim:
            if cur.weekday() in weekdays and cur not in feriados:
                total += 1
                if cur <= hoje:
                    total_ate_hoje += 1
            cur += datetime.timedelta(days=1)

        # Cálculo de realizado (Preenchidos): 1 por data efetivamente lançada
        dates_lancadas = lancados_map.get(key, set())
        for d in dates_lancadas:
            if d.weekday() in weekdays and d not in feriados:
                preenchidos += 1
                if d <= hoje:
                    preenchidos_ate_hoje += 1

    return {
        'total_conteudo': total,
        'preenchidos': preenchidos,
        'faltam': max(0, total - preenchidos),
        'total_ate_hoje': total_ate_hoje,
        'preenchidos_ate_hoje': preenchidos_ate_hoje,
        'faltam_ate_hoje': max(0, total_ate_hoje - preenchidos_ate_hoje)
    }


@login_required
def relatorio_pendencias(request):
    """Summarizes missing content launches for all professors."""
    prof_user = get_professor(request.user)
    if prof_user and prof_user.cargo == 'PROFESSOR':
        return redirect('detalhe_pendencias_professor', prof_id=prof_user.pk)

    if prof_user and not prof_user.pode_ver_tudo:
        return redirect('dashboard')

    from .models import Professor, GradeHoraria, ConteudoProgramatico

    # Only include active professors (those with GradeHoraria entries)
    prof_ids_com_grade = GradeHoraria.objects.filter(turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).values_list('professor_id', flat=True).distinct()
    professores = Professor.objects.filter(pk__in=prof_ids_com_grade).order_by('nome')

    # Filtering
    nome_filtro = request.GET.get('nome', '')
    data_ini = request.GET.get('data_ini', '')
    data_fim = request.GET.get('data_fim', '')

    if nome_filtro:
        professores = professores.filter(nome__icontains=nome_filtro)

    # Pre-fetch feriados once to avoid N+1 queries inside the loop
    feriados_set = get_feriados(ano_letivo=request.ano_letivo, escola=request.escola)
    relatorio = []
    for p in professores:
        stats = calcular_stats_conteudo(p, data_ini=data_ini, data_fim=data_fim, feriados=feriados_set, ano_letivo=request.ano_letivo, escola=request.escola)
        if stats['total_conteudo'] > 0:
            p.stats = stats
            relatorio.append(p)

    # Tabela Extra - Controle de Aulas Extras
    disciplina_extra_filtro = request.GET.get('disciplina_extra', '')
    disciplinas_peso_2 = [
        'Eletiva 1', 'Eletiva 2', 'Sociedade e Cidadania', 'Sustentabilidade e Meio Ambiente',
        'Educação Financeira', 'Múltiplas Linguagens', 'Ciências da Natureza', 
        'Ciências Humanas', 'Matemática e suas tecnologias', 'Linguagens e códigos'
    ]
    
    extras_qs = ConteudoProgramatico.objects.filter(
        disciplina__nome__in=disciplinas_peso_2
    ).select_related('professor', 'disciplina').prefetch_related('turmas').order_by('-data')
    
    if nome_filtro:
        extras_qs = extras_qs.filter(professor__nome__icontains=nome_filtro)
    if data_ini:
        extras_qs = extras_qs.filter(data__gte=data_ini)
    if data_fim:
        extras_qs = extras_qs.filter(data__lte=data_fim)
    if disciplina_extra_filtro:
        extras_qs = extras_qs.filter(disciplina__nome=disciplina_extra_filtro)

    context = {
        'prof': prof_user,
        'relatorio': relatorio,
        'nome_filtro': nome_filtro,
        'data_ini': data_ini,
        'data_fim': data_fim,
        'disciplina_extra_filtro': disciplina_extra_filtro,
        'todas_turmas': Turma.objects.filter(ano_letivo=request.ano_letivo, escola=request.escola),
        'aulas_extras_lancadas': extras_qs,
        'opcoes_extras': disciplinas_peso_2,
    }
    return render(request, 'core/relatorio_pendencias.html', context)


@login_required
def detalhe_pendencias_professor(request, prof_id):
    """Lists every specific date/turma that is missing content for a professor."""
    prof_user = get_professor(request.user)
    
    # Allow if user is admin/director/etc OR if the professor is viewing their own page
    is_own_page = (prof_user and prof_user.pk == prof_id)
    if not is_own_page and (prof_user and not prof_user.pode_ver_tudo):
        return redirect('dashboard')

    professor = get_object_or_404(Professor, pk=prof_id)
    from .models import GradeHoraria, ConteudoProgramatico
    import datetime

    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    hoje = datetime.date.today()
    config = Configuracao.objects.filter(ano_letivo=request.ano_letivo, escola=request.escola).first()
    if config:
        inicio = config.inicio_periodo_letivo
        config_fim = config.fim_periodo_letivo
    else:
        ano = request.ano_letivo.ano if request.ano_letivo else hoje.year
        inicio = datetime.date(ano, 2, 3)
        config_fim = datetime.date(ano, 12, 18)
    # Pendencies only count up to today
    fim = min(hoje, config_fim)
    feriados = get_feriados(ano_letivo=request.ano_letivo, escola=request.escola)

    # All (turma, disciplina) pairings for this professor
    grades = GradeHoraria.objects.filter(professor=professor, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).select_related('turma', 'disciplina')
    
    # Group by turma+disciplina to find missing dates
    turma_disc_map = defaultdict(lambda: {'weekdays': set(), 'turma': None, 'disc': None})
    for g in grades:
        key = (g.turma.codigo, g.disciplina.id)
        turma_disc_map[key]['weekdays'].add(DIA_TO_WEEKDAY[g.dia_semana])
        turma_disc_map[key]['turma'] = g.turma
        turma_disc_map[key]['disc'] = g.disciplina

    pendencias = []
    for (t_cod, d_id), info in turma_disc_map.items():
        # Get existing launches for this specific combo
        lancados = set(
            ConteudoProgramatico.objects.filter(
                professor=professor,
                turmas__codigo=t_cod,
                disciplina_id=d_id
            ).values_list('data', flat=True)
        )

        missing_dates = []
        cur = inicio
        while cur <= fim:
            if cur.weekday() in info['weekdays'] and cur not in feriados:
                if cur not in lancados:
                    missing_dates.append(cur)
            cur += datetime.timedelta(days=1)
        
        if missing_dates:
            pendencias.append({
                'turma': info['turma'],
                'disciplina': info['disc'],
                'datas': missing_dates
            })

    context = {
        'prof': prof_user,
        'professor': professor,
        'pendencias': pendencias,
    }
    return render(request, 'core/detalhe_pendencias.html', context)


@login_required
def lancamento_coletivo(request):
    """Bulks create content for selected turmas over a date range (Admin/Diretor only)."""
    prof_user = get_professor(request.user)
    if not prof_user or prof_user.cargo not in ['ADMIN', 'DIRETOR']:
        messages.error(request, "Apenas administradores e diretores podem realizar lançamentos coletivos.")
        return redirect('dashboard')

    if request.method == 'POST':
        data_ini_str = request.POST.get('data')
        data_fim_str = request.POST.get('data_fim')
        descricao = request.POST.get('descricao')
        turma_ids = request.POST.getlist('turmas_coletivo')

        if not data_ini_str or not descricao or not turma_ids:
            messages.error(request, "Início, descrição e pelo menos uma turma são obrigatórios.")
            return redirect('relatorio_pendencias')

        try:
            data_ini = datetime.datetime.strptime(data_ini_str, '%Y-%m-%d').date()
            if data_fim_str:
                data_fim = datetime.datetime.strptime(data_fim_str, '%Y-%m-%d').date()
                if data_fim < data_ini:
                    data_ini, data_fim = data_fim, data_ini
            else:
                data_fim = data_ini
        except ValueError:
            messages.error(request, "Formato de data inválido.")
            return redirect('relatorio_pendencias')

        from .models import GradeHoraria, ConteudoProgramatico, Turma
        from django.db import transaction

        # Gera a lista de datas letivas no período (segunda a sexta)
        datas_letivas = []
        curr = data_ini
        while curr <= data_fim:
            if curr.weekday() <= 4: # 0..4 = Seg..Sex
                datas_letivas.append(curr)
            curr += datetime.timedelta(days=1)
        
        if not datas_letivas:
            messages.info(request, "Não há dias letivos (segunda a sexta) no período selecionado.")
            return redirect('relatorio_pendencias')

        criados = 0
        ja_existiam = 0

        with transaction.atomic():
            for data_obj in datas_letivas:
                dia_semana_str = str(data_obj.weekday() + 1)

                # Busca as grades vigentes para as turmas selecionadas no dia da semana atual
                grades = GradeHoraria.objects.filter(
                    dia_semana=dia_semana_str,
                    turma_id__in=turma_ids
                ).values('professor_id', 'turma_id', 'disciplina_id').distinct()

                for g in grades:
                    t_id = g['turma_id']
                    # Resolução global para conflitos daquela turma (enviada via modal de pre-check)
                    res = request.POST.get(f'resolucao_{t_id}')
                    
                    if res == 'pular':
                        ja_existiam += 1
                        continue

                    existing = ConteudoProgramatico.objects.filter(
                        data=data_obj,
                        professor_id=g['professor_id'],
                        disciplina_id=g['disciplina_id'],
                        turmas__id=t_id
                    ).first()

                    if res == 'mesclar' and existing:
                        # Evita duplicar exatamente o mesmo texto se já estiver lá
                        if descricao not in existing.descricao:
                            existing.descricao += f"\n\n[MESCLADO EM {datetime.date.today().strftime('%d/%m/%Y')}]: {descricao}"
                            existing.save()
                        criados += 1
                    elif not existing:
                        cp = ConteudoProgramatico.objects.create(
                            data=data_obj,
                            professor_id=g['professor_id'],
                            disciplina_id=g['disciplina_id'],
                            descricao=descricao
                        )
                        cp.turmas.add(t_id)
                        criados += 1
                    else:
                        ja_existiam += 1

        messages.success(request, f"Lançamento coletivo concluído: {criados} registros processados em {len(datas_letivas)} dias. ({ja_existiam} pulados ou já existiam)")
        return redirect('relatorio_pendencias')

    return redirect('relatorio_pendencias')


@login_required
def gerenciar_sugestoes(request):
    """Standalone page for administrators to manage content suggestions."""
    prof = get_professor(request.user)
    
    # Permission check: Admin, Diretor or superuser without profile
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
    
    filtro_disciplina = request.GET.get('disciplina', '')
    filtro_turma = request.GET.get('turma', '')
    filtro_aplicado = bool(filtro_disciplina or filtro_turma)

    # Só carrega os dados do banco quando pelo menos um filtro foi aplicado.
    # Isso evita carregar milhares de sugestões desnecessariamente na abertura da página.
    if filtro_aplicado:
        qs = SugestaoConteudo.objects.all().select_related('disciplina').prefetch_related('turmas').order_by('disciplina__nome', 'texto')
        if filtro_disciplina:
            qs = qs.filter(disciplina_id=filtro_disciplina)
        if filtro_turma:
            qs = qs.filter(turmas__id=filtro_turma)
            qs = qs.distinct()  # evita duplicatas por ManyToMany
    else:
        qs = SugestaoConteudo.objects.none()

    context = {
        'prof': prof,
        'sugestoes': qs,
        'filtro_aplicado': filtro_aplicado,
        'disciplinas': Disciplina.objects.all().order_by('nome'),
        'turmas': Turma.objects.all().order_by('ordem_exibicao', 'codigo'),
        'filtro_disciplina': filtro_disciplina,
        'filtro_turma': filtro_turma,
    }
    return render(request, 'core/gerenciar_sugestoes.html', context)


@login_required
def sugestao_editar(request, pk):
    sug = get_object_or_404(SugestaoConteudo, pk=pk)
    prof = get_professor(request.user)
    
    # Permission check
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
            
    if request.method == 'POST':
        texto = request.POST.get('texto')
        disc_id = request.POST.get('disciplina')
        turmas_ids = request.POST.getlist('turmas')
        
        if texto and disc_id:
            sug.texto = texto
            sug.disciplina = get_object_or_404(Disciplina, pk=disc_id)
            sug.save()
            
            if turmas_ids:
                sug.turmas.set(turmas_ids)
            else:
                sug.turmas.clear()
                
            messages.success(request, "Sugestão atualizada com sucesso.")
        else:
            messages.error(request, "Texto e disciplina são obrigatórios.")
            
    return redirect('gerenciar_sugestoes')


@login_required
@require_POST
def sugestao_excluir(request, pk):
    sug = get_object_or_404(SugestaoConteudo, pk=pk)
    prof = get_professor(request.user)
    
    # Permission check
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
            
    sug.delete()
    messages.success(request, "Sugestão excluída com sucesso.")
    return redirect('gerenciar_sugestoes')


@login_required
@require_POST
def sugestoes_acoes_massa(request):
    sugestoes_ids = request.POST.getlist('sugestao_id')
    acao = request.POST.get('acao')

    if not sugestoes_ids:
        messages.error(request, "Nenhuma sugestão selecionada.")
        return redirect('gerenciar_sugestoes')

    prof = get_professor(request.user)
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')

    sugestoes = SugestaoConteudo.objects.filter(pk__in=sugestoes_ids)

    if acao == 'excluir':
        count = sugestoes.count()
        sugestoes.delete()
        messages.success(request, f"{count} sugestões excluídas com sucesso.")
    
    elif acao == 'editar':
        disc_id = request.POST.get('disciplina')
        turmas_ids = request.POST.getlist('turmas')
        
        if not disc_id:
            messages.error(request, "Para edição em massa, é necessário informar a nova disciplina.")
            return redirect('gerenciar_sugestoes')
            
        disciplina = get_object_or_404(Disciplina, pk=disc_id)
        
        for sug in sugestoes:
            sug.disciplina = disciplina
            sug.save()
            if turmas_ids:
                sug.turmas.set(turmas_ids)
            else:
                sug.turmas.clear()
                
        messages.success(request, f"{sugestoes.count()} sugestões foram atualizadas com sucesso.")
        
    return redirect('gerenciar_sugestoes')


@login_required
@require_POST
def ocorrencia_criar(request):
    prof = get_professor(request.user)
    data = request.POST.get('data')
    turma_cod = request.POST.get('turma')
    alunos_ids = request.POST.getlist('alunos')
    prof_id = request.POST.get('professor')
    disc_id = request.POST.get('disciplina')
    descricao = request.POST.get('descricao', '')
    status = request.POST.get('status', 'Aberta')

    turma = get_object_or_404(Turma, codigo=turma_cod)
    disciplina = get_object_or_404(Disciplina, pk=disc_id) if disc_id else None
    
    # Security: Ensure only admins or professors can create occurrences.
    # Orientador and Coordenador only change status.
    if prof and prof.cargo in ['ORIENTADOR', 'COORDENADOR', 'SECRETARIA']:
        messages.error(request, 'Seu cargo não permite registrar novas ocorrências.')
        return redirect('dashboard')

    # Security: Ensure only admins can set a specific professor
    if prof_id and prof and prof.pode_editar_tudo:
        professor = get_object_or_404(Professor, pk=prof_id)
    else:
        professor = prof

    oc = Ocorrencia.objects.create(
        data=data, turma=turma, professor=professor,
        disciplina=disciplina, descricao=descricao, status=status
    )
    if alunos_ids:
        oc.alunos.set(Aluno.objects.filter(pk__in=alunos_ids))
    messages.success(request, f'Ocorrência OC-{oc.pk:04d} criada com sucesso!')
    return redirect('dashboard')


@login_required
def ocorrencia_ver(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions
    if prof:
        if prof.cargo == 'INSPETOR':
            # Inspetor vê todas as ocorrências sem bloqueio
            pass
        elif not prof.pode_ver_tudo:
            if oc.professor != prof:
                messages.error(request, 'Você não tem permissão para visualizar esta ocorrência.')
                return redirect('dashboard')

    return render(request, 'core/ocorrencia_ver.html', {'oc': oc})


@login_required
def ocorrencia_editar(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Gestão de permissões específicas:
    # Coordenador e Orientador visualizam tudo, mas não editam nada (apenas status).
    if prof and prof.cargo in ['COORDENADOR', 'ORIENTADOR', 'INSPETOR']:
        messages.error(request, 'Seu cargo permiti apenas a visualização e alteração de status desta ocorrência.')
        return redirect('dashboard')

    if prof and not prof.pode_editar_tudo and oc.professor != prof:
        messages.error(request, 'Você não tem permissão para editar esta ocorrência.')
        return redirect('dashboard')

    turmas_qs = prof.get_turmas() if prof else Turma.objects.all()
    disciplinas_qs = prof.get_disciplinas() if prof else Disciplina.objects.all()

    if request.method == 'POST':
        data = request.POST.get('data')
        turma_cod = request.POST.get('turma')
        alunos_ids = request.POST.getlist('alunos')
        prof_id = request.POST.get('professor')
        disc_id = request.POST.get('disciplina')
        descricao = request.POST.get('descricao', '')
        status = request.POST.get('status', 'Aberta')

        oc.data = data
        oc.turma = get_object_or_404(Turma, codigo=turma_cod)
        oc.disciplina = get_object_or_404(Disciplina, pk=disc_id) if disc_id else None
        oc.professor = get_object_or_404(Professor, pk=prof_id) if prof_id else prof
        oc.descricao = descricao
        oc.status = status
        oc.save()
        if alunos_ids:
            oc.alunos.set(Aluno.objects.filter(pk__in=alunos_ids))
        else:
            oc.alunos.clear()
        messages.success(request, 'Ocorrência atualizada!')
        return redirect('dashboard')

    alunos_turma = Aluno.objects.filter(turma=oc.turma) if oc.turma else []
    context = {
        'oc': oc,
        'turmas': turmas_qs,
        'disciplinas': disciplinas_qs,
        'todos_professores': Professor.objects.all(),
        'alunos_turma': alunos_turma,
    }
    return render(request, 'core/ocorrencia_editar.html', context)


@login_required
@require_POST
def ocorrencia_excluir(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions logic
    if prof and prof.cargo in ['COORDENADOR', 'ORIENTADOR', 'INSPETOR']:
        messages.error(request, 'Você não tem permissão para excluir ocorrências.')
        return redirect('dashboard')

    if prof and not prof.pode_editar_tudo and oc.professor != prof:
        messages.error(request, 'Você não tem permissão para excluir esta ocorrência.')
        return redirect('dashboard')
        
    oc.delete()
    messages.success(request, 'Ocorrência excluída.')
    return redirect('dashboard')


@login_required
@require_POST
def ocorrencia_excluir_varios(request):
    ids = request.POST.getlist('ids')
    prof = get_professor(request.user)

    # Apenas quem pode editar tudo (ADMIN, DIRETOR) realiza exclusão em massa
    if prof and not prof.pode_editar_tudo:
        messages.error(request, 'Você não tem permissão para realizar exclusão em massa.')
        return redirect('dashboard')

    Ocorrencia.objects.filter(pk__in=ids).delete()
    messages.success(request, f'{len(ids)} ocorrência(s) excluída(s).')
    return redirect('dashboard')


@login_required
@require_POST
def ocorrencia_mudar_status(request):
    ids = request.POST.getlist('ids')
    novo_status = request.POST.get('status', 'Resolvida')
    prof = get_professor(request.user)

    qs = Ocorrencia.objects.filter(pk__in=ids)

    # Professor comum só pode alterar status das próprias ocorrências
    if prof and not prof.pode_ver_tudo:
        qs = qs.filter(professor=prof)

    qs.update(status=novo_status)
    messages.success(request, f'Status alterado para "{novo_status}".')
    return redirect('dashboard')


@login_required
def ocorrencia_mudar_status_direto(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions
    if prof:
        if prof.cargo == 'INSPETOR':
            pass # Inspetores podem mudar
        elif not prof.pode_ver_tudo:
            if oc.professor != prof:
                messages.error(request, 'Sem permissão.')
                return redirect('dashboard')

    oc.status = 'Resolvida' if oc.status == 'Aberta' else 'Aberta'
    oc.save()
    messages.success(request, f'Status da OC-{oc.pk:04d} alterado para {oc.status}.')
    return redirect('dashboard')


@login_required
def api_sugestoes_conteudo(request):
    turma_cod = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    
    from django.db.models import Q
    qs = SugestaoConteudo.objects.filter(disciplina_id=disciplina_id).order_by('texto')
    if turma_cod:
        qs = qs.filter(Q(turmas__codigo=turma_cod) | Q(turmas__isnull=True))
    
    sugestoes = list(qs.values('id', 'texto'))
    return JsonResponse(sugestoes, safe=False)


# ──────────────────────────────────────────────
# CONTEÚDOS
# ──────────────────────────────────────────────

@login_required
@require_POST
def conteudo_criar(request):
    prof_logado = get_professor(request.user)
    data = request.POST.get('data')
    turmas_cods = request.POST.getlist('turmas')
    disc_id = request.POST.get('disciplina')
    prof_id = request.POST.get('professor')
    descricao = request.POST.get('descricao', '')

    disciplina = get_object_or_404(Disciplina, pk=disc_id) if disc_id else None
    
    # Security: Ensure only admins can set a specific professor
    if prof_id and prof_logado and prof_logado.pode_editar_tudo:
        professor = get_object_or_404(Professor, pk=prof_id)
    else:
        professor = prof_logado

    from django.db import transaction
    with transaction.atomic():
        for t_cod in turmas_cods:
            res = request.POST.get(f'resolucao_{t_cod}')
            
            if res == 'pular':
                continue
            
            # Busca registro existente para possível mesclagem
            existing = ConteudoProgramatico.objects.filter(
                data=data,
                professor=professor,
                disciplina=disciplina,
                turmas__codigo=t_cod
            ).first()

            if res == 'mesclar' and existing:
                existing.descricao += f"\n\n[MESCLADO EM {datetime.date.today().strftime('%d/%m/%Y')}]: {descricao}"
                existing.save()
            elif not existing or not res:
                # Se não existe ou não foi solicitada resolução (lançamento normal), cria novo.
                # Nota: se já existia e res não veio, o comportamento antigo era duplicar. 
                # Agora o JS deve sempre enviar res se houver conflito.
                cont = ConteudoProgramatico.objects.create(
                    data=data, professor=professor, disciplina=disciplina, descricao=descricao
                )
                cont.turmas.add(Turma.objects.get(codigo=t_cod))

    messages.success(request, 'Conteúdo(s) lançado(s) com sucesso!')
    return redirect('/?tab=conteudos')


@login_required
def conteudo_ver(request, pk):
    cont = get_object_or_404(ConteudoProgramatico, pk=pk)
    prof = get_professor(request.user)
    
    # Simple check: if not admin, can only see if related to them or has pode_ver_tudo
    if prof and not prof.pode_ver_tudo and cont.professor != prof:
        messages.error(request, 'Você não tem permissão para visualizar este conteúdo.')
        return redirect('dashboard')
        
    return render(request, 'core/conteudo_ver.html', {
        'cont': cont,
        'prof': prof,
    })


@login_required
def conteudo_editar(request, pk):
    cont = get_object_or_404(ConteudoProgramatico, pk=pk)
    prof = get_professor(request.user)

    # Permissões: Coordenador visualiza mas não edita diários.
    if prof and prof.cargo == 'COORDENADOR':
        messages.error(request, 'Coordenadores não podem editar lançamentos nos diários.')
        return redirect('dashboard')

    # Bloqueio: confirmado pela secretaria
    if cont.confirmado_secretaria and not (prof and prof.pode_editar_tudo):
        messages.error(request, '⛔ Este lançamento foi confirmado pela Secretaria e não pode ser editado.')
        return redirect('dashboard')

    # Check permissions
    if prof and not prof.pode_editar_tudo and cont.professor != prof:
        messages.error(request, 'Você não tem permissão para editar este conteúdo.')
        return redirect('dashboard')

    if request.method == 'POST':
        data = request.POST.get('data')
        turmas_cods = request.POST.getlist('turmas')
        disc_id = request.POST.get('disciplina')
        prof_id = request.POST.get('professor')
        descricao = request.POST.get('descricao', '')

        cont.data = data
        cont.disciplina = get_object_or_404(Disciplina, pk=disc_id) if disc_id else None
        
        # Security: Ensure only admins can change the professor
        if prof_id and prof and prof.pode_editar_tudo:
            cont.professor = get_object_or_404(Professor, pk=prof_id)
        elif not prof_id:
            cont.professor = prof

        cont.descricao = descricao
        cont.save()
        
        turmas = list(Turma.objects.filter(codigo__in=turmas_cods))
        if turmas:
            # A primeira turma fica no registro atual
            cont.turmas.set([turmas[0]])
            
            # Turmas adicionais criam/separam em novos registros
            for extra_turma in turmas[1:]:
                novo_cp = ConteudoProgramatico.objects.create(
                    data=cont.data,
                    professor=cont.professor,
                    disciplina=cont.disciplina,
                    descricao=cont.descricao
                )
                novo_cp.turmas.add(extra_turma)
        else:
            cont.turmas.clear()

        
        messages.success(request, 'Conteúdo atualizado com sucesso!')
        return redirect('/?tab=conteudos')

    # Filtra turmas da mesma série
    primeira_turma = cont.turmas.first()
    todas_do_prof = prof.get_turmas() if prof else Turma.objects.all()
    
    if primeira_turma:
        import re
        m = re.search(r'\d', primeira_turma.codigo)
        serie = m.group() if m else primeira_turma.codigo[0]
        
        turmas_comp = set()
        for t in todas_do_prof:
            t_m = re.search(r'\d', t.codigo)
            t_serie = t_m.group() if t_m else t.codigo[0]
            if t_serie == serie:
                turmas_comp.add(t)
        
        # Garante que as turmas atuais vinculadas ao conteúdo apareçam sempre
        for t in cont.turmas.all():
            turmas_comp.add(t)
            
        turmas_qs = sorted(list(turmas_comp), key=lambda x: str(x.codigo))
    else:
        turmas_qs = todas_do_prof

    disciplinas_qs = prof.get_disciplinas() if prof else Disciplina.objects.all()
    
    # Garantia de que a disciplina de origem (como aula extra) apareça no dropdown da edição
    if cont.disciplina:
        disciplinas_qs = (disciplinas_qs | Disciplina.objects.filter(pk=cont.disciplina.pk)).distinct()

    context = {
        'cont': cont,
        'turmas': turmas_qs,
        'disciplinas': disciplinas_qs,
        'todos_professores': Professor.objects.all(),
        'cont_turmas_pks': cont.turmas.values_list('pk', flat=True),
    }
    return render(request, 'core/conteudo_editar.html', context)


@login_required
@require_POST
def conteudo_excluir(request, pk):
    cont = get_object_or_404(ConteudoProgramatico, pk=pk)
    prof = get_professor(request.user)

    # Permissões: Coordenador não exclui diários.
    if prof and prof.cargo == 'COORDENADOR':
        messages.error(request, 'Coordenadores não podem excluir lançamentos nos diários.')
        return redirect('dashboard')

    # Bloqueio: confirmado pela secretaria
    if cont.confirmado_secretaria and not (prof and prof.pode_editar_tudo):
        messages.error(request, '⛔ Este lançamento foi confirmado pela Secretaria e não pode ser excluído.')
        return redirect('dashboard')

    # Check permissions
    if prof and not prof.pode_editar_tudo and cont.professor != prof:
        messages.error(request, 'Você não tem permissão para excluir este conteúdo.')
        return redirect('dashboard')

    cont.delete()
    messages.success(request, 'Conteúdo excluído.')
    return redirect('dashboard')


@login_required
@require_POST
def conteudo_excluir_varios(request):
    ids = request.POST.getlist('ids')
    prof = get_professor(request.user)

    # Restrict mass delete to those with global edit permissions
    if prof and not prof.pode_editar_tudo:
        messages.error(request, 'Você não tem permissão para realizar exclusão em massa.')
        return redirect('dashboard')

    # Nunca excluir confirmados (mesmo para ADMIN/DIRETOR, exige desconfirmar antes)
    confirmados = ConteudoProgramatico.objects.filter(pk__in=ids, confirmado_secretaria=True).count()
    if confirmados > 0:
        messages.warning(request, f'{confirmados} lançamento(s) estão confirmados e não foram excluídos. Desconfirme-os primeiro.')
        ids_excluir = list(ConteudoProgramatico.objects.filter(pk__in=ids, confirmado_secretaria=False).values_list('pk', flat=True))
    else:
        ids_excluir = ids

    if ids_excluir:
        ConteudoProgramatico.objects.filter(pk__in=ids_excluir).delete()
        messages.success(request, f'{len(ids_excluir)} conteúdo(s) excluído(s).')
    return redirect('dashboard')


# ──────────────────────────────────────────────
# LANÇAMENTOS COLETIVOS (agrupados por conteúdo)
# ──────────────────────────────────────────────

@login_required
def lancamentos_coletivos(request):
    """
    Exibe lançamentos agrupados por (professor, disciplina, data, descricao).
    Turmas que receberam o mesmo conteúdo no mesmo dia aparecem agrupadas.
    Permite à secretaria confirmar lançamentos.
    """
    prof = get_professor(request.user)

    # Apenas perfis com acesso gerencial
    if not prof or not prof.pode_ver_tudo:
        messages.error(request, 'Acesso restrito.')
        return redirect('dashboard')

    # Filtros opcionais
    filtro_prof      = request.GET.get('filtro_prof', '')
    filtro_turma     = request.GET.get('filtro_turma', '')
    filtro_disc      = request.GET.get('filtro_disc', '')
    filtro_data_ini  = request.GET.get('data_ini', '')
    filtro_data_fim  = request.GET.get('data_fim', '')
    filtro_confirmado = request.GET.get('confirmado', '0')  # '0'=pendentes '1'=confirmados 'todos'

    qs = ConteudoProgramatico.objects.select_related('professor', 'disciplina').prefetch_related('turmas')

    if filtro_prof:
        qs = qs.filter(professor_id=filtro_prof)
    if filtro_turma:
        qs = qs.filter(turmas__codigo=filtro_turma)
    if filtro_disc:
        qs = qs.filter(disciplina_id=filtro_disc)
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
    if filtro_confirmado == '0':
        qs = qs.filter(confirmado_secretaria=False)
    elif filtro_confirmado == '1':
        qs = qs.filter(confirmado_secretaria=True)

    qs = qs.order_by('-data', 'professor__nome', 'disciplina__nome')

    # Agrupar por (professor, disciplina, data, descricao)
    grupos = {}  # chave -> {'ids': [], 'turmas': set(), 'obj': primeiro_cont}
    for cont in qs:
        chave = (cont.professor_id, cont.disciplina_id, cont.data, cont.descricao)
        if chave not in grupos:
            grupos[chave] = {
                'ids': [],
                'turmas': [],
                'obj': cont,
                'confirmado': cont.confirmado_secretaria,
                'confirmado_em': cont.confirmado_em,
                'confirmado_por': cont.confirmado_por,
            }
        grupos[chave]['ids'].append(cont.pk)
        for t in cont.turmas.all():
            if t.codigo not in [x.codigo for x in grupos[chave]['turmas']]:
                grupos[chave]['turmas'].append(t)

    # Ordenar turmas dentro de cada grupo
    for g in grupos.values():
        g['turmas'].sort(key=lambda t: t.codigo)
        g['turmas_str'] = ', '.join(t.codigo for t in g['turmas'])
        g['ids_str'] = ','.join(str(i) for i in g['ids'])

    grupos_lista = list(grupos.values())

    professores = Professor.objects.filter(cargo='PROFESSOR').order_by('nome')
    turmas      = Turma.objects.all()
    disciplinas = Disciplina.objects.all()

    return render(request, 'core/lancamentos_coletivos.html', {
        'grupos': grupos_lista,
        'professores': professores,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'prof': prof,
        'filtro_prof': filtro_prof,
        'filtro_turma': filtro_turma,
        'filtro_disc': filtro_disc,
        'filtro_data_ini': filtro_data_ini,
        'filtro_data_fim': filtro_data_fim,
        'filtro_confirmado': filtro_confirmado,
        'is_secretaria': prof.cargo in ['SECRETARIA', 'ADMIN', 'DIRETOR'],
    })


@login_required
@require_POST
def conteudo_confirmar(request):
    """
    A secretaria confirma lançamentos selecionados.
    Após confirmado, professores não podem editar nem excluir.
    """
    prof = get_professor(request.user)

    if not prof or prof.cargo not in ['SECRETARIA', 'ADMIN', 'DIRETOR']:
        messages.error(request, 'Apenas a Secretaria pode confirmar lançamentos.')
        return redirect('lancamentos_coletivos')

    ids_raw = request.POST.get('ids_confirmacao', '')
    if not ids_raw:
        messages.warning(request, 'Nenhum lançamento selecionado.')
        return redirect('lancamentos_coletivos')

    try:
        ids = [int(i.strip()) for i in ids_raw.split(',') if i.strip().isdigit()]
    except ValueError:
        messages.error(request, 'Dados inválidos.')
        return redirect('lancamentos_coletivos')

    import django.utils.timezone as tz
    agora = tz.now()

    atualizados = ConteudoProgramatico.objects.filter(pk__in=ids, confirmado_secretaria=False)
    count = atualizados.update(
        confirmado_secretaria=True,
        confirmado_em=agora,
        confirmado_por=request.user,
    )

    messages.success(request, f'✅ {count} lançamento(s) confirmado(s) com sucesso! Os professores não poderão mais alterá-los.')
    return redirect('lancamentos_coletivos')


@login_required
@require_POST
def conteudo_desconfirmar(request, pk):
    """
    Administrador ou Diretor pode desconfirmar um lançamento (devolver para edição).
    """
    prof = get_professor(request.user)

    if not prof or not prof.pode_editar_tudo:
        messages.error(request, 'Apenas Admin ou Diretor podem desconfirmar lançamentos.')
        return redirect('lancamentos_coletivos')

    cont = get_object_or_404(ConteudoProgramatico, pk=pk)
    cont.confirmado_secretaria = False
    cont.confirmado_em = None
    cont.confirmado_por = None
    cont.save(update_fields=['confirmado_secretaria', 'confirmado_em', 'confirmado_por'])
    messages.success(request, f'Lançamento {pk} desconfirmado e aberto para edição novamente.')
    return redirect('lancamentos_coletivos')


@login_required
@require_POST
def conteudo_desconfirmar_varios(request):
    """
    Admin ou Diretor desconfirma vários lançamentos de uma vez (via checkboxes).
    """
    prof = get_professor(request.user)

    if not prof or not prof.pode_editar_tudo:
        messages.error(request, 'Apenas Admin ou Diretor podem desconfirmar lançamentos.')
        return redirect('lancamentos_coletivos')

    ids_raw = request.POST.get('ids_desconfirmacao', '')
    if not ids_raw:
        messages.warning(request, 'Nenhum lançamento selecionado.')
        return redirect('lancamentos_coletivos')

    ids = [int(i.strip()) for i in ids_raw.split(',') if i.strip().isdigit()]

    count = ConteudoProgramatico.objects.filter(
        pk__in=ids,
        confirmado_secretaria=True,
    ).update(
        confirmado_secretaria=False,
        confirmado_em=None,
        confirmado_por=None,
    )

    messages.success(request, f'↩ {count} lançamento(s) desconfirmado(s). Professores podem editar novamente.')
    return redirect('lancamentos_coletivos')


# ──────────────────────────────────────────────
# EXPORTAR CSV
# ──────────────────────────────────────────────

@login_required
def exportar_ocorrencias_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="ocorrencias.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Data', 'Turma', 'Alunos', 'Professor', 'Disciplina', 'Descrição', 'Status'])
    
    qs, _ = filtrar_ocorrencias(request, ocorrencias_do_usuario(request.user))
    for oc in qs:
        writer.writerow([
            f'OC-{oc.pk:04d}',
            oc.data.strftime('%d/%m/%Y') if oc.data else '',
            oc.turma.codigo if oc.turma else '',
            oc.alunos_str(),
            oc.professor.nome if oc.professor else '',
            oc.disciplina.nome if oc.disciplina else '',
            oc.descricao,
            oc.status,
        ])
    return response


@login_required
def exportar_conteudos_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="conteudos.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data', 'Turmas', 'Professor', 'Disciplina', 'Descrição'])
    
    qs, _ = filtrar_conteudos(request, conteudos_do_usuario(request.user))
    for c in qs:
        writer.writerow([
            c.data.strftime('%d/%m/%Y') if c.data else '',
            c.turmas_str(),
            c.professor.nome if c.professor else '',
            c.disciplina.nome if c.disciplina else '',
            c.descricao,
        ])
    return response


# ──────────────────────────────────────────────
# EXPORTAR PDF
# ──────────────────────────────────────────────

def _pdf_response(buf, filename):
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)


class EllipticalImage(Image):
    """Custom Image class to apply elliptical clipping and border (matches web logo)."""
    def draw(self):
        # Save state to apply clipping
        self.canv.saveState()
        w, h = self.drawWidth, self.drawHeight

        # Create elliptical clip path
        path = self.canv.beginPath()
        # center_x, center_y, width, height (actually it's x1, y1, x2, y2)
        # But reportlab's path.ellipse(x1, y1, width, height)
        path.ellipse(0, 0, w, h)
        self.canv.clipPath(path, stroke=0)

        # Draw background color (matching the web dashboard)
        self.canv.setFillColor(colors.HexColor('#003366'))
        self.canv.rect(0, 0, w, h, fill=1, stroke=0)

        # Draw the image (it will be clipped)
        super().draw()
        
        # Restore to remove clipping
        self.canv.restoreState()

        # Draw the white elliptical border
        self.canv.saveState()
        self.canv.setStrokeColor(colors.white)
        self.canv.setLineWidth(2)
        self.canv.ellipse(0, 0, w, h)
        self.canv.restoreState()


def _get_logo_path(mode='eme'):
    """Retorna o caminho absoluto para a logo usando finders do Django."""
    if mode == 'capelum':
        search_paths = [
            'core/capelum_logo_transparent.png',
            'core/capelum_logo.png',
        ]
    else:
        # EME / Escola
        search_paths = [
            'core/logo.jpg',
            'core/logo.png',
            'core/img/logo.png',
        ]
    
    for relative_path in search_paths:
        abs_path = finders.find(relative_path)
        if abs_path:
            return abs_path
            
    # Fallback search if mode fails
    if mode == 'capelum':
        return _get_logo_path(mode='eme')
    return None


def _get_logo_element():
    """Helper to return the standardized elliptical logo for PDFs (cabeçalho - EME)."""
    logo_path = _get_logo_path(mode='eme')
    if logo_path:
        # 4cm x 2cm maintains the 2:1 ratio used in the web dashboard (200x100px)
        logo = EllipticalImage(logo_path, width=4*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        return logo
    return None


@login_required
def exportar_ocorrencias_pdf(request):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', fontSize=7, leading=9)
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True)
    cell_normal = ParagraphStyle('cell_normal', fontSize=8, leading=10)
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Ocorrências - SCA - Sistema de Controle Acadêmico', styles['Title']))
    
    qs, resumo_filtros = filtrar_ocorrencias(request, ocorrencias_do_usuario(request.user))
    if resumo_filtros:
        elems.append(Paragraph(f"Filtros aplicados: {resumo_filtros}", filter_style))
    
    elems.append(Spacer(1, 0.3*cm))
    data = [['ID', 'Data', 'Turma', 'Alunos', 'Professor', 'Disciplina', 'Status']]
    for oc in qs:
        data.append([
            f'OC-{oc.pk:04d}',
            oc.data.strftime('%d/%m/%Y') if oc.data else '',
            oc.turma.codigo if oc.turma else '',
            Paragraph(oc.alunos_str(), small),
            oc.professor.nome if oc.professor else '',
            Paragraph(oc.disciplina.nome if oc.disciplina else '', cell_normal),
            oc.status,
        ])
    # Total width with 1.0cm margins on A4 (21cm) is 19cm.
    # 1.8+2.0+1.4+5.0+4.0+2.8+2.0 = 19.0cm (Perfect Fill)
    t = Table(data, colWidths=[1.8*cm, 2.0*cm, 1.4*cm, 5.0*cm, 4.0*cm, 2.8*cm, 2.0*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'ocorrencias.pdf')


def _add_signature_footer(canvas, doc, data_professor=None, data_secretaria=None):
    """Adds signature lines for Professor and Secretary at the bottom of the page,
    with different dates (Prof=last launch, Sec=last confirmation), and draws the Capelum logo centered."""
    canvas.saveState()

    # Configuration
    page_width, page_height = doc.pagesize
    margin = 1.5 * cm
    line_width = 7 * cm
    line_y  = 3.2 * cm
    text_y  = 2.8 * cm
    small_y = 2.4 * cm

    # ── Logo Capelum centralizado no rodapé ────────────────────
    logo_path = _get_logo_path(mode='capelum')
    if logo_path:
        logo_w, logo_h = 3.5 * cm, 1.75 * cm
        logo_x = (page_width - logo_w) / 2
        logo_y = 0.5 * cm
        try:
            canvas.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── Assinatura Professor (esquerda) ─────────────────
    canvas.setFont('Helvetica', 9)
    canvas.line(margin, line_y, margin + line_width, line_y)
    canvas.drawCentredString(margin + (line_width / 2), text_y, 'Assinatura do Professor')
    
    # Data do lançamento do Professor
    if data_professor:
        if hasattr(data_professor, 'astimezone'): data_professor = data_professor.astimezone()
        prof_str = f'Lançado em: {data_professor.strftime("%d/%m/%Y %H:%M")}'
    else:
        from datetime import datetime as dt
        prof_str = f'Assinado eletronicamente em: {dt.now().strftime("%d/%m/%Y %H:%M")}'
    
    canvas.setFont('Helvetica-Oblique', 7)
    canvas.drawCentredString(margin + (line_width / 2), small_y, prof_str)

    # ── Assinatura Secretaria (direita) ─────────────────
    canvas.setFont('Helvetica', 9)
    canvas.line(page_width - margin - line_width, line_y, page_width - margin, line_y)
    canvas.drawCentredString(page_width - margin - (line_width / 2), text_y, 'Assinatura da Secretaria')
    
    # Data da confirmação da Secretaria
    if data_secretaria:
        if hasattr(data_secretaria, 'astimezone'): data_secretaria = data_secretaria.astimezone()
        sec_str = f'Confirmado pela Secretaria em: {data_secretaria.strftime("%d/%m/%Y %H:%M")}'
    else:
        from datetime import datetime as dt
        sec_str = f'Assinado eletronicamente em: {dt.now().strftime("%d/%m/%Y %H:%M")}'

    canvas.setFont('Helvetica-Oblique', 7)
    canvas.drawCentredString(page_width - margin - (line_width / 2), small_y, sec_str)

    canvas.restoreState()


@login_required
def exportar_conteudos_pdf(request):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', fontSize=7, leading=9)
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True)
    cell_normal = ParagraphStyle('cell_normal', fontSize=8, leading=10)

    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Conteúdo Programático - SCA - Sistema de Controle Acadêmico', styles['Title']))
    
    qs, resumo_filtros = filtrar_conteudos(request, conteudos_do_usuario(request.user))
    if resumo_filtros:
        elems.append(Paragraph(f"Filtros aplicados: {resumo_filtros}", filter_style))
        
    elems.append(Spacer(1, 0.3*cm))
    data = [['Data', 'Turmas', 'Professor', 'Disciplina', 'Descrição']]
    for c in qs:
        data.append([
            c.data.strftime('%d/%m/%Y') if c.data else '',
            c.turmas_str(),
            c.professor.nome if c.professor else '',
            Paragraph(c.disciplina.nome if c.disciplina else '', cell_normal),
            Paragraph(c.descricao, small),
        ])
    # Total width with 1.0cm margins on A4 (21cm) is 19cm.
    # 1.8+1.6+2.8+3.4+9.4 = 19.0cm (Perfect Fill)
    t = Table(data, colWidths=[1.8*cm, 1.6*cm, 2.8*cm, 3.4*cm, 9.4*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elems.append(t)

    # Datas das assinaturas no queryset
    from functools import partial
    from django.db.models import Max
    resumo = qs.aggregate(max_criado=Max('criado_em'), max_confirmado=Max('confirmado_em'))
    
    footer_fn = partial(_add_signature_footer, 
                        data_professor=resumo['max_criado'], 
                        data_secretaria=resumo['max_confirmado'])

    doc.build(elems, onFirstPage=footer_fn, onLaterPages=footer_fn)
    return _pdf_response(buf, 'conteudos.pdf')


@login_required
def relatorio_alocacao(request):
    prof = get_professor(request.user)
    if prof and not prof.pode_ver_tudo:
        messages.error(request, 'Acesso restrito à gestão.')
        return redirect('dashboard')
    
    professores = Professor.objects.filter(cargo='PROFESSOR').prefetch_related('disciplinas', 'turmas', 'grade_horaria').order_by('nome')
    return render(request, 'core/relatorio_alocacao.html', {
        'professores': professores,
        'prof': prof,
    })


@login_required
def exportar_alocacao_pdf(request):
    prof = get_professor(request.user)
    if prof and not prof.pode_gerar_relatorios:
        return HttpResponse('Acesso negado', status=403)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=0.5*cm, rightMargin=0.5*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, leading=8)
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Relatório de Alocação de Professores', styles['Title']))
    elems.append(Spacer(1, 0.5*cm))
    
    professores = Professor.objects.filter(cargo='PROFESSOR').prefetch_related('disciplinas', 'turmas', 'grade_horaria').order_by('nome')
    
    data = [['Professor', 'Disciplinas', 'Turmas', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex']]
    for p in professores:
        discs = ", ".join([d.nome for d in p.disciplinas.all()])
        turmas_list = sorted([t.codigo for t in p.turmas.all()])
        turmas = ", ".join(turmas_list)
        
        seg = []
        ter = []
        qua = []
        qui = []
        sex = []
        for gh in p.grade_horaria.all():
            line = f"{gh.hora_inicio.strftime('%H:%M')}: {gh.turma.codigo} ({gh.disciplina.nome})"
            if gh.dia_semana == '1': seg.append(line)
            elif gh.dia_semana == '2': ter.append(line)
            elif gh.dia_semana == '3': qua.append(line)
            elif gh.dia_semana == '4': qui.append(line)
            elif gh.dia_semana == '5': sex.append(line)
        
        data.append([
            p.nome, 
            Paragraph(discs, small_style), 
            Paragraph(turmas, small_style),
            Paragraph("<br/>".join(seg), small_style),
            Paragraph("<br/>".join(ter), small_style),
            Paragraph("<br/>".join(qua), small_style),
            Paragraph("<br/>".join(qui), small_style),
            Paragraph("<br/>".join(sex), small_style)
        ])
    # Total width with 0.5cm margins on A4 (21cm) is 20cm.
    # 2.0 + 2.5 + 1.5 + 5 * 2.5 = 6.0 + 12.5 = 18.5cm (Safe)
    t = Table(data, colWidths=[2.0*cm, 2.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'alocacao_professores.pdf')


@login_required
def sugestao_criar_massa(request):
    prof = get_professor(request.user)
    if not prof or not prof.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    if request.method == 'POST':
        discs_ids = request.POST.getlist('disciplinas')
        turmas_ids = request.POST.getlist('turmas')
        file_obj = request.FILES.get('arquivo_excel')

        if not discs_ids or not turmas_ids or not file_obj:
            messages.error(request, 'Selecione pelo menos uma disciplina, turmas e o arquivo Excel.')
            return redirect('dashboard')

        try:
            import openpyxl
        except ImportError:
            # Check if it's a CSV file, which doesn't need openpyxl
            if file_obj.name.lower().endswith('.csv'):
                pass # Will handle below
            else:
                debug_info = f" (Python: {sys.version.split()[0]}, Path: {sys.path[:3]})"
                messages.error(request, f'O servidor não possui "openpyxl" para arquivos Excel. Use um arquivo .CSV ou peça suporte. {debug_info}')
                return redirect('dashboard')

        try:
            textos = []
            
            if file_obj.name.lower().endswith('.csv'):
                # Handle CSV
                content = file_obj.read().decode('utf-8-sig')
                io_string = io.StringIO(content)
                reader = csv.reader(io_string, delimiter=';') # Try semicolon first (common in Excel CSV)
                
                # Check if it looks like comma delimited instead
                first_row = next(reader, None)
                if first_row and len(first_row) == 1 and ',' in first_row[0]:
                    io_string.seek(0)
                    reader = csv.reader(io_string, delimiter=',')
                else:
                    # Reset if semicolon worked
                    io_string.seek(0)
                    reader = csv.reader(io_string, delimiter=';')

                for row in reader:
                    if row and str(row[0]).strip():
                        textos.append(str(row[0]).strip())
            else:
                # Handle Excel
                workbook = openpyxl.load_workbook(file_obj, data_only=True)
                sheet = workbook.active
                for row in sheet.iter_rows(min_row=1, max_col=1, values_only=True):
                    val = row[0]
                    if val and str(val).strip():
                        textos.append(str(val).strip())
            
            if not textos:
                messages.warning(request, 'Nenhum conteúdo encontrado na primeira coluna da planilha.')
                return redirect('dashboard')

            disciplinas = Disciplina.objects.filter(pk__in=discs_ids)
            turmas = Turma.objects.filter(pk__in=turmas_ids)
            
            from django.db import transaction
            with transaction.atomic():
                # Opcional: Evitar duplicidade exata na mesma disc/turma?
                # Por agora, cria direto seguindo o pedido anterior.
                for txt in textos:
                    for disciplina in disciplinas:
                        sug = SugestaoConteudo.objects.create(disciplina=disciplina, texto=txt)
                        sug.turmas.set(turmas)

            total_criado = len(textos) * disciplinas.count()
            messages.success(request, f'{total_criado} sugestões cadastradas com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao processar Excel: {str(e)}')
            
        return redirect('dashboard')

    return redirect('dashboard')


@login_required
def exportar_pendencias_pdf(request):
    """Exports the pendency report table to PDF."""
    prof_user = get_professor(request.user)
    if prof_user and not prof_user.pode_gerar_relatorios:
        return HttpResponse('Acesso negado', status=403)

    from .models import GradeHoraria
    prof_ids_com_grade = GradeHoraria.objects.filter(turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).values_list('professor_id', flat=True).distinct()
    professores = Professor.objects.filter(pk__in=prof_ids_com_grade).order_by('nome')
    nome_filtro = request.GET.get('nome', '')
    data_ini = request.GET.get('data_ini', '')
    data_fim = request.GET.get('data_fim', '')

    if nome_filtro:
        professores = professores.filter(nome__icontains=nome_filtro)

    feriados_set = get_feriados(ano_letivo=request.ano_letivo, escola=request.escola)
    relatorio = []
    for p in professores:
        stats = calcular_stats_conteudo(p, data_ini=data_ini, data_fim=data_fim, feriados=feriados_set, ano_letivo=request.ano_letivo, escola=request.escola)
        if stats['total_conteudo'] > 0:
            p.stats = stats
            relatorio.append(p)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    title = 'Pendências de Conteúdo'
    if data_ini and data_fim:
        title += f' ({data_ini} a {data_fim})'
    elif data_ini:
        title += f' (desde {data_ini})'
        
    elems.append(Paragraph(title, styles['Title']))
    elems.append(Spacer(1, 0.5*cm))

    data = [['Professor', 'Total Esperado', 'Preenchidos', 'Faltam (Hoje)', 'Faltam (Total)']]
    for p in relatorio:
        data.append([
            p.nome,
            str(p.stats['total_conteudo']),
            str(p.stats['preenchidos']),
            str(p.stats['faltam_ate_hoje']),
            str(p.stats['faltam']),
        ])
    
    t = Table(data, colWidths=[8*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'pendencias.pdf')


# ──────────────────────────────────────────────
# TROCA DE SENHA FORÇADA
# ──────────────────────────────────────────────

@login_required
def forcar_troca_senha(request):
    """Exibido quando deve_trocar_senha=True. Força o usuário a definir uma nova senha."""
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    # Busca o professor com segurança
    prof = getattr(request.user, 'professor', None)

    # Se não for professor ou não precisar trocar, manda pro dashboard
    if not prof or not prof.deve_trocar_senha:
        return redirect('dashboard')

    erros = []

    if request.method == 'POST':
        nova = request.POST.get('nova_senha', '').strip()
        confirma = request.POST.get('confirmar_senha', '').strip()

        # Não pode ser a senha padrão (primeiras 3 letras do username + @123)
        username = request.user.username
        prefixo = username[:3].lower() if len(username) >= 3 else username.lower()
        senha_padrao = f"{prefixo}@123"

        if not nova:
            erros.append('A senha não pode ser vazia.')
        elif nova != confirma:
            erros.append('As senhas não conferem.')
        elif nova.lower() == senha_padrao:
            erros.append('Por segurança, você não pode usar a senha padrão. Crie uma senha exclusiva.')
        else:
            try:
                validate_password(nova, request.user)
            except ValidationError as e:
                erros.extend(e.messages)

        if not erros:
            request.user.set_password(nova)
            request.user.save()
            prof.deve_trocar_senha = False
            prof.save()
            # Atualiza hash da sessão para não deslogar
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha atualizada! Agora cadastre seu e-mail de contato.')
            return redirect('cadastrar_email')

    return render(request, 'core/trocar_senha.html', {
        'erros': erros,
        'prof': prof,
    })


# ──────────────────────────────────────────────
# CADASTRO DE E-MAIL DE CONTATO (PRIMEIRO ACESSO)
# ──────────────────────────────────────────────

@login_required
def cadastrar_email(request):
    """
    Exibida após a troca de senha obrigatória.
    Solicita o e-mail pessoal do professor para contato e recuperação de senha.
    O professor pode pular (pular=1) e cadastrar depois via perfil.
    """
    prof = getattr(request.user, 'professor', None)

    # Já foi preenchido ou não é professor → vai ao dashboard
    if not prof:
        return redirect('dashboard')

    if request.method == 'POST':
        # Se clicou em "Pular por agora"
        if request.POST.get('pular'):
            messages.info(request, 'Você pode cadastrar seu e-mail a qualquer momento nas configurações do perfil.')
            return redirect('dashboard')

        email = request.POST.get('email', '').strip()

        if not email:
            return render(request, 'core/cadastrar_email.html', {
                'erro': 'Por favor, informe um endereço de e-mail válido.',
                'prof': prof,
            })

        # Valida formato básico
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as VE
        try:
            validate_email(email)
        except VE:
            return render(request, 'core/cadastrar_email.html', {
                'erro': 'O endereço de e-mail informado não é válido.',
                'prof': prof,
            })

        # Salva no modelo Professor e no User (para recuperação de senha)
        prof.email_contato = email
        prof.save(update_fields=['email_contato'])
        request.user.email = email
        request.user.save(update_fields=['email'])

        messages.success(request, f'E-mail {email} cadastrado com sucesso! Bem-vindo ao Capelum.')
        return redirect('dashboard')

    return render(request, 'core/cadastrar_email.html', {'prof': prof})


# ──────────────────────────────────────────────
# RECUPERAÇÃO DE SENHA (SENHA TEMPORÁRIA)
# ──────────────────────────────────────────────

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'core/recuperar_senha.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/recuperar-senha/enviado/'

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'core/recuperar_senha_enviada.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/login/'

    def form_valid(self, form):
        user = form.save()
        prof = getattr(user, 'professor', None)
        if prof:
            prof.deve_trocar_senha = False
            prof.save(update_fields=['deve_trocar_senha'])
        messages.success(self.request, 'Senha redefinida com sucesso! Você já pode entrar.')
        return super().form_valid(form)


@login_required
def migrar_alunos(request):
    """Ferramenta para migrar (copiar) alunos de um ano letivo para outro."""
    prof = get_professor(request.user)
    if not prof or not prof.pode_editar_tudo:
        messages.error(request, "Acesso restrito à administração e direção.")
        return redirect('dashboard')
    
    from .models import AnoLetivo, Turma, Aluno
    anos = AnoLetivo.objects.all()
    turmas_origem = []
    alunos = []
    turmas_destino = []
    
    ano_origem_id = request.GET.get('ano_origem')
    turma_origem_id = request.GET.get('turma_origem')
    ano_destino_id = request.GET.get('ano_destino')
    
    if ano_origem_id:
        turmas_origem = Turma.objects.filter(ano_letivo_id=ano_origem_id, escola=request.escola)
        
    if turma_origem_id:
        alunos = Aluno.objects.filter(turma_id=turma_origem_id)
        
    if ano_destino_id:
        turmas_destino = Turma.objects.filter(ano_letivo_id=ano_destino_id, escola=request.escola)

    if request.method == 'POST':
        aluno_ids = request.POST.getlist('alunos_migrar')
        turma_dest_id = request.POST.get('turma_destino')
        
        if not aluno_ids or not turma_dest_id:
            messages.error(request, "Selecione os alunos e a turma de destino.")
        else:
            t_dest = get_object_or_404(Turma, pk=turma_dest_id)
            sucesso = 0
            for a_id in aluno_ids:
                try:
                    a_origem = Aluno.objects.get(pk=a_id)
                    # Cria um NOVO registro de aluno vinculado à turma de destino
                    # Preserva os dados básicos e a foto
                    Aluno.objects.create(
                        nome=a_origem.nome,
                        turma=t_dest,
                        email_responsavel=a_origem.email_responsavel,
                        foto=a_origem.foto
                    )
                    sucesso += 1
                except Aluno.DoesNotExist:
                    continue
            
            messages.success(request, f"Migração concluída: {sucesso} alunos copiados para {t_dest}.")
            return redirect('migrar_alunos')

    context = {
        'anos': anos,
        'turmas_origem': turmas_origem,
        'turmas_destino': turmas_destino,
        'alunos': alunos,
        'ano_origem_id': int(ano_origem_id) if ano_origem_id else None,
        'turma_origem_id': int(turma_origem_id) if turma_origem_id else None,
        'ano_destino_id': int(ano_destino_id) if ano_destino_id else None,
    }
    return render(request, 'core/migrar_alunos.html', context)
@login_required
def escola_configurar(request):
    """Permite ao administrador da escola alterar as cores e logo."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')

    from .forms import EscolaForm
    escola = request.escola

    if request.method == 'POST':
        form = EscolaForm(request.POST, request.FILES, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações da escola atualizadas com sucesso!')
            return redirect('escola_configurar')
    else:
        form = EscolaForm(instance=escola)

    return render(request, 'core/escola_configurar.html', {
        'form': form,
        'escola': escola
    })


@login_required
def escola_professores_list(request):
    """Lista professores da escola atual."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    professores = Professor.objects.filter(escolas=request.escola).order_by('nome')
    return render(request, 'core/escola_professores_list.html', {
        'professores': professores
    })


@login_required
def escola_professor_edit(request, pk):
    """Edita um professor (vínculo com a escola atual)."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    professor = get_object_or_404(Professor, pk=pk, escolas=request.escola)
    from .forms import ProfessorForm
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST, instance=professor, escola=request.escola)
        if form.is_valid():
            # Precisamos manter as turmas de OUTRAS escolas
            # O CheckboxSelectMultiple filtrado remove as outras
            outras_turmas = list(professor.turmas.exclude(escola=request.escola))
            professor = form.save(commit=False)
            professor.save()
            form.save_m2m() # Salva as turmas da escola atual
            
            # Re-adiciona as outras
            for t in outras_turmas:
                professor.turmas.add(t)
                
            messages.success(request, f'Professor {professor.nome} atualizado!')
            return redirect('escola_professores_list')
    else:
        form = ProfessorForm(instance=professor, escola=request.escola)
        
    return render(request, 'core/escola_professor_form.html', {
        'form': form,
        'professor': professor,
        'titulo': f'Editar: {professor.nome}'
    })


@login_required
def escola_professor_novo(request):
    """Cria um novo professor e seu respectivo User."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    from .forms import ProfessorForm
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST, escola=request.escola)
        usuario_login = request.POST.get('username_login')
        
        if form.is_valid() and usuario_login:
            if User.objects.filter(username=usuario_login).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
            else:
                # 1. Cria o User
                # Senha padrão é o próprio username no primeiro acesso
                user = User.objects.create_user(username=usuario_login, password=usuario_login)
                
                # 2. Cria o Professor
                professor = form.save(commit=False)
                professor.user = user
                professor.deve_trocar_senha = True # Força troca no primeiro login
                professor.save()
                form.save_m2m()
                
                # 3. Vincula à escola atual
                professor.escolas.add(request.escola)
                
                messages.success(request, f'Professor {professor.nome} criado com sucesso! Login: {usuario_login}')
                return redirect('escola_professores_list')
    else:
        form = ProfessorForm(escola=request.escola)
        
    return render(request, 'core/escola_professor_form.html', {
        'form': form,
        'titulo': 'Cadastrar Novo Professor',
        'novo': True
    })
