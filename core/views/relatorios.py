import csv
import datetime
import io
import logging
import sys
import os
from datetime import date
from collections import defaultdict
from functools import partial

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, Max
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

from ..models import (Aluno, AnoLetivo, ConteudoProgramatico, Disciplina,
                     Escola, GradeHoraria, Ocorrencia, Professor,
                     SugestaoConteudo, Turma, Configuracao, AulaExtraProgramada)
from ..utils import get_professor, get_feriados, get_client_ip
from .ocorrencias import TIPOS_OCORRENCIA

# Logger para auditoria de ações sensíveis
logger = logging.getLogger('core')



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
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify', 
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
        logger.debug('RECAPTCHA verify: token_prefix=%s result=%s', str(token)[:30], result)
        return result.get('success', False)
    except Exception as e:
        # Em caso de falha de rede, registra o erro e BLOQUEIA por segurança
        logger.warning('reCAPTCHA: falha na verificação (%s). Bloqueando requisição.', e)
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

    if prof.pode_ver_tudo:
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
        'tipos_ocorrencia': TIPOS_OCORRENCIA,
    }
    # Paginação para os conteúdos filtrados
    from django.core.paginator import Paginator
    paginator = Paginator(cont_filtrados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context['conteudos'] = page_obj
    
    # Merge content stats without overwriting ocorrência totals
    context.update(calcular_stats_conteudo(prof,
                                           data_ini=request.GET.get('data_ini', ''),
                                           data_fim=request.GET.get('data_fim', ''),
                                           ano_letivo=request.ano_letivo,
                                           escola=request.escola))
    
    # Se for uma requisição AJAX (parcial)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('is_ajax') == '1':
        return render(request, 'core/partials/conteudos_table_body.html', context)
        
    return render(request, 'core/dashboard.html', context)
def calcular_stats_conteudo(prof, data_ini=None, data_fim=None, feriados=None, ano_letivo=None, escola=None):
    """
    Retorna estatísticas de total/preenchidos/faltam.
    Otimizado para evitar o problema N+1 queries.
    """
    if feriados is None:
        feriados = get_feriados(ano_letivo=ano_letivo, escola=escola)

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
    
    ae_qs = AulaExtraProgramada.objects.select_related('turma', 'professor')
    if ano_letivo:
        ae_qs = ae_qs.filter(turma__ano_letivo=ano_letivo)
    if escola:
        ae_qs = ae_qs.filter(turma__escola=escola)
    if not global_view:
        ae_qs = ae_qs.filter(professor=prof)
    aulas_extras = list(ae_qs)

    if not grades and not aulas_extras:
        return {
            'total_conteudo': 0, 'preenchidos': 0, 'faltam': 0,
            'total_ate_hoje': 0, 'preenchidos_ate_hoje': 0, 'faltam_ate_hoje': 0
        }

    # Agrupa dias da semana por tríade (prof, turma, disc) em memória.
    # Usa set de weekdays (não contagem): garante que múltiplos horários no mesmo
    # dia da semana não inflam o total — igual à lógica do relatório de pendências.
    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    slots_map = defaultdict(set)  # key -> set of weekdays com aula
    extra_dates_map = defaultdict(set) # key -> set of specific dates com aula extra

    for g in grades:
        key = (g.professor_id, g.turma.codigo, g.disciplina_id)
        if g.dia_semana in DIA_TO_WEEKDAY:
            slots_map[key].add(DIA_TO_WEEKDAY[g.dia_semana])
            
    for ae in aulas_extras:
        key = (ae.professor_id, ae.turma.codigo, ae.disciplina_id)
        extra_dates_map[key].add(ae.data)

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
            if key in slots_map or key in extra_dates_map: # Só conta se estiver na grade ou extra
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

    all_keys = set(slots_map.keys()) | set(extra_dates_map.keys())

    for key in all_keys:
        weekdays = slots_map.get(key, set())
        extra_dates = extra_dates_map.get(key, set())
        
        # Cálculo de esperado (Total): 1 por data de aula no período
        cur = inicio
        while cur <= fim:
            is_expected = (cur.weekday() in weekdays or cur in extra_dates)
            if is_expected and cur not in feriados:
                total += 1
                if cur <= hoje:
                    total_ate_hoje += 1
            cur += datetime.timedelta(days=1)

        # Cálculo de realizado (Preenchidos): 1 por data efetivamente lançada
        dates_lancadas = lancados_map.get(key, set())
        for d in dates_lancadas:
            is_expected = (d.weekday() in weekdays or d in extra_dates)
            if is_expected and d not in feriados:
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
    aulas_extras = AulaExtraProgramada.objects.filter(professor=professor, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).select_related('turma', 'disciplina')
    
    # Group by turma+disciplina to find missing dates
    turma_disc_map = defaultdict(lambda: {'weekdays': set(), 'extra_dates': set(), 'turma': None, 'disc': None})
    for g in grades:
        key = (g.turma.codigo, g.disciplina.id)
        turma_disc_map[key]['weekdays'].add(DIA_TO_WEEKDAY[g.dia_semana])
        turma_disc_map[key]['turma'] = g.turma
        turma_disc_map[key]['disc'] = g.disciplina
        
    for ae in aulas_extras:
        key = (ae.turma.codigo, ae.disciplina.id)
        turma_disc_map[key]['extra_dates'].add(ae.data)
        turma_disc_map[key]['turma'] = ae.turma
        turma_disc_map[key]['disc'] = ae.disciplina

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
            is_expected = (cur.weekday() in info['weekdays'] or cur in info['extra_dates'])
            if is_expected and cur not in feriados:
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
def relatorio_alocacao(request):
    prof = get_professor(request.user)
    if prof and not prof.pode_ver_tudo:
        messages.error(request, 'Acesso restrito à gestão.')
        return redirect('dashboard')
    
    from django.db.models import Prefetch
    professores = Professor.objects.filter(cargo='PROFESSOR').prefetch_related(
        'disciplinas', 'turmas', 
        Prefetch('grade_horaria', queryset=GradeHoraria.objects.select_related('turma', 'disciplina'))
    ).order_by('nome')
    return render(request, 'core/relatorio_alocacao.html', {
        'professores': professores,
        'prof': prof,
    })

