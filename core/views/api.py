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

from ..models import (Aluno, AnoLetivo, AulaExtraProgramada, ConteudoProgramatico, Disciplina,
                     Escola, GradeHoraria, Ocorrencia, Professor,
                     SugestaoConteudo, Turma, Configuracao)
from ..utils import get_professor, get_feriados, get_client_ip, ordenar_por_nome

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
    if not secret:
        # Chave não configurada no servidor — bloqueia por segurança
        logger.warning('reCAPTCHA: RECAPTCHA_SECRET_KEY não configurada. Bloqueando requisição.')
        return False
    if not token:
        # Token ausente — usuário não completou o reCAPTCHA
        logger.warning('reCAPTCHA: token ausente na requisição. Bloqueando.')
        return False
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
@login_required
def api_alunos_turma(request, codigo):
    alunos = Aluno.objects.filter(turma__codigo=codigo, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola)
    alunos = ordenar_por_nome(alunos)
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
    profs = ordenar_por_nome(profs)
    return JsonResponse([{'id': p.pk, 'nome': p.nome} for p in profs], safe=False)


@login_required
def api_disciplinas_turma(request, codigo):
    """Return disciplines taught in a given turma (from GradeHoraria), filtered by logged-in professor."""
    prof_logado = get_professor(request.user)
    is_extra = request.GET.get('extra') == '1'

    if is_extra:
        # Modo Aula Extra: ignora a grade horária.
        # Mostra as disciplinas que o professor pode lecionar (se não for admin)
        if prof_logado and not prof_logado.pode_ver_tudo and not prof_logado.todas_disciplinas:
            discs = prof_logado.disciplinas.all()
        else:
            discs = Disciplina.objects.all()

        turmas_1_ano = ['11', '12', '13']
        turmas_2_ano = ['21', '22', '23']
        turmas_3_ano = ['31', '32']

        if codigo in turmas_1_ano:
            areas = [
                'Sociedade e Cidadania', 'Sociedade e Cidadania I', 'Sociedade e Cidadania II',
                'Sustentabilidade e Meio Ambiente', 'Sustentabilidade e Meio Ambiente I', 'Sustentabilidade e Meio Ambiente II',
                'Projeto de Vida', 'Comp. Texto', 'Artes',
                'Física', 'Física I', 'História', 'História I'
            ]
            extras = Disciplina.objects.filter(nome__in=areas)
            discs = (discs | extras).distinct()
            
        elif codigo in turmas_2_ano:
            areas = [
                'Educação Financeira', 'Múltiplas Linguagens', 'Múltiplas Linguagens I', 'Múltiplas Linguagens II',
                'Projeto de Vida', 'Artes',
                'Física', 'Física I', 'História', 'História I'
            ]
            extras = Disciplina.objects.filter(nome__in=areas)
            discs = (discs | extras).distinct()
            
        elif codigo in turmas_3_ano:
            areas = [
                'Aprofundamento em Matemática',
                'Aprofundamento em Ciências da Natureza',
                'Aprofundamento em Ciências Humanas',
                'Aprofundamento em Linguagens'
            ]
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
        qs_gh = GradeHoraria.objects.filter(turma__codigo=codigo, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola)
        qs_ae = AulaExtraProgramada.objects.filter(turma__codigo=codigo, turma__ano_letivo=request.ano_letivo, turma__escola=request.escola)
        if prof_logado and not prof_logado.pode_ver_tudo:
            qs_gh = qs_gh.filter(professor=prof_logado)
            qs_ae = qs_ae.filter(professor=prof_logado)
        disc_ids = set(qs_gh.values_list('disciplina_id', flat=True)) | set(qs_ae.values_list('disciplina_id', flat=True))
        discs = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
        
    return JsonResponse(list(discs.values('id', 'nome')), safe=False)


@login_required
def api_professores_turma_disc(request, codigo, disc_id):
    """Return professors who teach a given discipline in a given turma."""

    prof_logado = get_professor(request.user)
    is_extra = request.GET.get('extra') == '1'

    if is_extra:
        # Modo Aula extra: ignora a grade. Todos os professores aptos (ou si mesmo).
        profs = Professor.objects.all()
    else:
        prof_ids_gh = GradeHoraria.objects.filter(
            turma__codigo=codigo,
            turma__ano_letivo=request.ano_letivo,
            turma__escola=request.escola,
            disciplina__pk=disc_id
        ).values_list('professor_id', flat=True)
        prof_ids_ae = AulaExtraProgramada.objects.filter(
            turma__codigo=codigo,
            turma__ano_letivo=request.ano_letivo,
            turma__escola=request.escola,
            disciplina__pk=disc_id
        ).values_list('professor_id', flat=True)
        prof_ids = set(prof_ids_gh) | set(prof_ids_ae)
        profs = Professor.objects.filter(pk__in=prof_ids)
        
    # If the logged-in user is a professor (not admin/coord), limit to themselves
    if prof_logado and not prof_logado.pode_ver_tudo:
        profs = profs.filter(pk=prof_logado.pk)
        
    profs = ordenar_por_nome(profs)
    return JsonResponse([{'id': p.pk, 'nome': p.nome} for p in profs], safe=False)


@login_required
def api_datas_validas(request, codigo, prof_id):
    """Return all school-year dates where prof teaches turma, with 'lancado' flag."""

    import datetime

    # Proteção IDOR: professor comum só consulta seus próprios dados
    prof_logado = get_professor(request.user)
    if prof_logado and not prof_logado.pode_ver_tudo and prof_logado.pk != prof_id:
        return JsonResponse([], safe=False)

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


    # Proteção IDOR: professor comum só consulta seus próprios dados
    prof_logado = get_professor(request.user)
    if prof_logado and not prof_logado.pode_ver_tudo and prof_logado.pk != prof_id:
        return JsonResponse({}, safe=False)

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
