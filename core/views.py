import csv
import datetime
import io
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

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .models import (Aluno, ConteudoProgramatico, Disciplina, Ocorrencia,
                     Professor, Turma)


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        senha = request.POST.get('senha', '')
        user = authenticate(request, username=usuario, password=senha)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Usuário ou senha incorretos!')
    return render(request, 'core/login.html')


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


def ocorrencias_do_usuario(user):
    prof = get_professor(user)
    qs = Ocorrencia.objects.select_related('turma', 'professor', 'disciplina').prefetch_related('alunos')
    if not prof:
        return qs  # superuser/admin sem perfil: vê tudo
    if prof.cargo == 'INSPETOR':
        # Inspetor vê apenas ocorrências das suas turmas
        turmas_ids = prof.turmas_inspetor.values_list('pk', flat=True)
        qs = qs.filter(turma__pk__in=turmas_ids)
    elif not prof.pode_ver_tudo:
        # Professor comum vê apenas suas próprias ocorrências
        qs = qs.filter(professor=prof)
    return qs


def conteudos_do_usuario(user):
    prof = get_professor(user)
    qs = ConteudoProgramatico.objects.select_related('professor', 'disciplina').prefetch_related('turmas')
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


def filtrar_conteudos(request, qs):
    filtro_turma_c = request.GET.get('filtro_turma_c', '')
    filtro_disc_c = request.GET.get('filtro_disc_c', '')
    filtro_prof_c = request.GET.get('filtro_prof_c', '')

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

    return qs, " | ".join(resumo)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    prof = get_professor(request.user)
    turmas_qs = prof.get_turmas() if prof else Turma.objects.all()
    disciplinas_qs = prof.get_disciplinas() if prof else Disciplina.objects.all()

    ocorrencias = ocorrencias_do_usuario(request.user)
    total = ocorrencias.count()
    abertas = ocorrencias.filter(status='Aberta').count()
    resolvidas = ocorrencias.filter(status='Resolvida').count()

    oc_filtradas, _ = filtrar_ocorrencias(request, ocorrencias)
    cont_filtrados, _ = filtrar_conteudos(request, conteudos_do_usuario(request.user))

    context = {
        'prof': prof,
        'turmas': turmas_qs,
        'disciplinas': disciplinas_qs,
        'todos_professores': Professor.objects.all(),
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
        'filtro_turma_c': request.GET.get('filtro_turma_c', ''),
        'filtro_disc_c': request.GET.get('filtro_disc_c', ''),
        'filtro_prof_c': request.GET.get('filtro_prof_c', ''),
        'today': date.today().isoformat(),
    }
    # Merge content stats without overwriting ocorrência totals
    context.update(calcular_stats_conteudo(prof))
    return render(request, 'core/dashboard.html', context)


# ──────────────────────────────────────────────
# API: alunos por turma (AJAX)
# ──────────────────────────────────────────────

@login_required
def api_alunos_turma(request, codigo):
    alunos = Aluno.objects.filter(turma__codigo=codigo).values('id', 'nome')
    return JsonResponse(list(alunos), safe=False)


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

    qs = GradeHoraria.objects.filter(turma__codigo=codigo)

    # If logged-in user is a professor (not admin/coord), only show their own disciplines
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
    prof_ids = GradeHoraria.objects.filter(
        turma__codigo=codigo,
        disciplina__pk=disc_id
    ).values_list('professor_id', flat=True).distinct()
    profs = Professor.objects.filter(pk__in=prof_ids).order_by('nome')
    # If the logged-in user is a professor (not admin), limit to themselves
    if prof_logado and not prof_logado.pode_ver_tudo:
        profs = profs.filter(pk=prof_logado.pk)
    return JsonResponse(list(profs.values('id', 'nome')), safe=False)


@login_required
def api_datas_validas(request, codigo, prof_id):
    """Return all school-year dates where prof teaches turma, with 'lancado' flag."""
    from .models import GradeHoraria, ConteudoProgramatico
    import datetime

    # Weekday numbers in GradeHoraria: '1'=Segunda=Monday(0), ..., '5'=Sexta=Friday(4)
    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}

    # Find which days of week this professor teaches this turma
    dias = GradeHoraria.objects.filter(
        turma__codigo=codigo,
        professor__pk=prof_id
    ).values_list('dia_semana', flat=True).distinct()

    if not dias:
        return JsonResponse([], safe=False)

    weekdays = {DIA_TO_WEEKDAY[d] for d in dias if d in DIA_TO_WEEKDAY}

    # School year boundaries (current year)
    ano = date.today().year
    inicio = datetime.date(ano, 2, 3)   # Feb 3
    fim = datetime.date(ano, 12, 18)    # Dec 18

    # Generate all valid school dates (excluding holidays)
    datas_validas = []
    cur = inicio
    while cur <= fim:
        if cur.weekday() in weekdays and cur not in FERIADOS_2026:
            datas_validas.append(cur)
        cur += datetime.timedelta(days=1)

    # Find which dates already have a content entry for this professor+turma
    lancados = set(
        ConteudoProgramatico.objects.filter(
            professor__pk=prof_id,
            turmas__codigo=codigo
        ).values_list('data', flat=True)
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


def calcular_stats_conteudo(prof):
    """Return total/preenchidos/faltam content stats.
    - Admin/Diretor/Secretaria: global totals across ALL professors.
    - Professor: totals for their own turmas only.
    - Others (inspetor, etc.): zeros.
    """
    from .models import GradeHoraria, ConteudoProgramatico

    CARGOS_GLOBAIS = ['ADMIN', 'DIRETOR', 'SECRETARIA', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR']

    if not prof:
        # Superuser sem perfil – mostra global
        pass
    elif prof.cargo == 'INSPETOR':
        return {'total_conteudo': 0, 'preenchidos': 0, 'faltam': 0}

    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    ano = date.today().year
    inicio = datetime.date(ano, 2, 3)
    fim = datetime.date(ano, 12, 18)

    # Determine scope: global or per-professor
    global_view = (not prof) or (prof.cargo in CARGOS_GLOBAIS)

    if global_view:
        # All unique (professor, turma) pairs from GradeHoraria
        pares = GradeHoraria.objects.values('professor_id', 'turma__codigo').distinct()
    else:
        # Only this professor's turmas
        pares = GradeHoraria.objects.filter(professor=prof).values('professor_id', 'turma__codigo').distinct()

    total = 0
    preenchidos = 0

    # Cache per (prof_id, turma_codigo) → valid weekdays
    weekdays_por_par = defaultdict(set)
    for par in pares:
        dias = GradeHoraria.objects.filter(
            professor_id=par['professor_id'],
            turma__codigo=par['turma__codigo']
        ).values_list('dia_semana', flat=True).distinct()
        weekdays_por_par[(par['professor_id'], par['turma__codigo'])] = {
            DIA_TO_WEEKDAY[d] for d in dias if d in DIA_TO_WEEKDAY
        }

    for (prof_id, turma_codigo), weekdays in weekdays_por_par.items():
        if not weekdays:
            continue
        cur = inicio
        while cur <= fim:
            if cur.weekday() in weekdays and cur not in FERIADOS_2026:
                total += 1
            cur += datetime.timedelta(days=1)
        lancados = ConteudoProgramatico.objects.filter(
            professor_id=prof_id,
            turmas__codigo=turma_codigo
        ).values('data').distinct().count()
        preenchidos += lancados

    return {
        'total_conteudo': total,
        'preenchidos': preenchidos,
        'faltam': max(0, total - preenchidos)
    }


@login_required
def relatorio_pendencias(request):
    """Summarizes missing content launches for all professors."""
    prof_user = get_professor(request.user)
    if prof_user and not prof_user.pode_ver_tudo:
        return redirect('dashboard')

    from .models import Professor, GradeHoraria, ConteudoProgramatico

    # Only include active professors (those with GradeHoraria entries)
    prof_ids_com_grade = GradeHoraria.objects.values_list('professor_id', flat=True).distinct()
    professores = Professor.objects.filter(pk__in=prof_ids_com_grade).order_by('nome')

    # Filtering
    nome_filtro = request.GET.get('nome', '')
    if nome_filtro:
        professores = professores.filter(nome__icontains=nome_filtro)

    # We reuse calcular_stats_conteudo but it might be slow for many professors.
    # Optimized loop:
    relatorio = []
    for p in professores:
        stats = calcular_stats_conteudo(p)
        if stats['total_conteudo'] > 0:
            p.stats = stats
            relatorio.append(p)

    context = {
        'prof': prof_user,
        'relatorio': relatorio,
        'nome_filtro': nome_filtro,
        'todas_turmas': Turma.objects.all(),
    }
    return render(request, 'core/relatorio_pendencias.html', context)


@login_required
def detalhe_pendencias_professor(request, prof_id):
    """Lists every specific date/turma that is missing content for a professor."""
    prof_user = get_professor(request.user)
    if prof_user and not prof_user.pode_ver_tudo:
        return redirect('dashboard')

    professor = get_object_or_404(Professor, pk=prof_id)
    from .models import GradeHoraria, ConteudoProgramatico
    import datetime

    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    ano = date.today().year
    hoje = datetime.date.today()
    inicio = datetime.date(ano, 2, 3)
    # Pendencies only count up to today
    fim = min(hoje, datetime.date(ano, 12, 18))

    # All (turma, disciplina) pairings for this professor
    grades = GradeHoraria.objects.filter(professor=professor).select_related('turma', 'disciplina')
    
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
            if cur.weekday() in info['weekdays'] and cur not in FERIADOS_2026:
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
        'professor': professor,
        'pendencias': pendencias,
    }
    return render(request, 'core/detalhe_pendencias.html', context)


@login_required
def lancamento_coletivo(request):
    """Bulks create content for all classes on a specific date (Admin only, selected turmas)."""
    prof_user = get_professor(request.user)
    if not prof_user or prof_user.cargo != 'ADMIN':
        messages.error(request, "Apenas administradores podem realizar lançamentos coletivos.")
        return redirect('dashboard')

    if request.method == 'POST':
        data_str = request.POST.get('data')
        descricao = request.POST.get('descricao')
        turma_ids = request.POST.getlist('turmas_coletivo')

        if not data_str or not descricao or not turma_ids:
            messages.error(request, "Data, descrição e pelo menos uma turma são obrigatórias.")
            return redirect('relatorio_pendencias')

        try:
            data_obj = datetime.datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de data inválido.")
            return redirect('relatorio_pendencias')

        # Map weekday (0=Mon, 6=Sun) to GradeHoraria dia_semana ('1'=Mon, '5'=Fri)
        # Weekday 0..4 = '1'..'5'
        wd = data_obj.weekday()
        if wd > 4:
            messages.warning(request, "Não há aulas no fim de semana.")
            return redirect('relatorio_pendencias')
        
        dia_semana_str = str(wd + 1)

        from .models import GradeHoraria, ConteudoProgramatico, Turma
        from django.db import transaction

        # Find all unique (prof, turma, disc) for this day AND selected turmas
        grades = GradeHoraria.objects.filter(
            dia_semana=dia_semana_str,
            turma_id__in=turma_ids
        ).values('professor_id', 'turma_id', 'disciplina_id').distinct()

        if not grades:
            messages.info(request, "Não há aulas cadastradas para este dia da semana.")
            return redirect('relatorio_pendencias')

        criados = 0
        ja_existiam = 0

        with transaction.atomic():
            for g in grades:
                # Check if already exists for this date+prof+disc+turma
                # Note: ConteudoProgramatico.turmas is ManyToMany. 
                # Our simple check: does any Conteudo exist for this date, prof, disc AND contains this turma?
                exists = ConteudoProgramatico.objects.filter(
                    data=data_obj,
                    professor_id=g['professor_id'],
                    disciplina_id=g['disciplina_id'],
                    turmas__id=g['turma_id']
                ).exists()

                if not exists:
                    cp = ConteudoProgramatico.objects.create(
                        data=data_obj,
                        professor_id=g['professor_id'],
                        disciplina_id=g['disciplina_id'],
                        descricao=descricao
                    )
                    cp.turmas.add(g['turma_id'])
                    criados += 1
                else:
                    ja_existiam += 1

        messages.success(request, f"Lançamento coletivo concluído: {criados} novos registros criados. ({ja_existiam} já existiam)")
        return redirect('relatorio_pendencias')

    return redirect('relatorio_pendencias')


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
    professor = get_object_or_404(Professor, pk=prof_id) if prof_id else prof

    oc = Ocorrencia.objects.create(
        data=data, turma=turma, professor=professor,
        disciplina=disciplina, descricao=descricao, status=status
    )
    if alunos_ids:
        oc.alunos.set(Aluno.objects.filter(pk__in=alunos_ids))
    messages.success(request, f'Ocorrência OC-{oc.pk:04d} criada com sucesso!')
    return redirect('dashboard')


@login_required
def ocorrencia_editar(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions
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
    
    # Check permissions
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
    Ocorrencia.objects.filter(pk__in=ids).delete()
    messages.success(request, f'{len(ids)} ocorrência(s) excluída(s).')
    return redirect('dashboard')


@login_required
@require_POST
def ocorrencia_mudar_status(request):
    ids = request.POST.getlist('ids')
    novo_status = request.POST.get('status', 'Resolvida')
    Ocorrencia.objects.filter(pk__in=ids).update(status=novo_status)
    messages.success(request, f'Status alterado para "{novo_status}".')
    return redirect('dashboard')


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
    professor = get_object_or_404(Professor, pk=prof_id) if prof_id else prof_logado

    cont = ConteudoProgramatico.objects.create(
        data=data, professor=professor, disciplina=disciplina, descricao=descricao
    )
    turmas = Turma.objects.filter(codigo__in=turmas_cods)
    cont.turmas.set(turmas)
    messages.success(request, 'Conteúdo lançado com sucesso!')
    return redirect('dashboard')


@login_required
@require_POST
def conteudo_excluir(request, pk):
    cont = get_object_or_404(ConteudoProgramatico, pk=pk)
    cont.delete()
    messages.success(request, 'Conteúdo excluído.')
    return redirect('dashboard')


@login_required
@require_POST
def conteudo_excluir_varios(request):
    ids = request.POST.getlist('ids')
    ConteudoProgramatico.objects.filter(pk__in=ids).delete()
    messages.success(request, f'{len(ids)} conteúdo(s) excluído(s).')
    return redirect('dashboard')


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

def _pdf_response(filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def exportar_ocorrencias_pdf(request):
    response = _pdf_response('ocorrencias.pdf')
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', fontSize=7, leading=9)
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True)
    
    # Logo fallback
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.jpg')

    elems = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=3.5*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Ocorrências - Sistema EME', styles['Title']))
    
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
            oc.disciplina.nome if oc.disciplina else '',
            oc.status,
        ])
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elems.append(t)
    doc.build(elems)
    response.write(buf.getvalue())
    return response


@login_required
def exportar_conteudos_pdf(request):
    response = _pdf_response('conteudos.pdf')
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', fontSize=7, leading=9)
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True)

    # Logo fallback
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.jpg')

    elems = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=3.5*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Conteúdo Programático - Sistema EME', styles['Title']))
    
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
            c.disciplina.nome if c.disciplina else '',
            Paragraph(c.descricao, small),
        ])
    t = Table(data, colWidths=[2*cm, 2*cm, 4*cm, 3*cm, None], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elems.append(t)
    doc.build(elems)
    response.write(buf.getvalue())
    return response


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

    response = _pdf_response('alocacao_professores.pdf')
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, leading=8)
    
    # Logo fallback
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'logo.jpg')

    elems = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=3.5*cm, height=2*cm)
        logo.hAlign = 'LEFT'
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
    
    t = Table(data, colWidths=[2.5*cm, 3.5*cm, 3*cm, 3.7*cm, 3.7*cm, 3.7*cm, 3.7*cm, 3.7*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elems.append(t)
    doc.build(elems)
    response.write(buf.getvalue())
    return response
