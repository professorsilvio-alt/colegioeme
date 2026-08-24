import datetime
import logging
from decimal import Decimal, InvalidOperation
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..models import (
    Aluno, AnoLetivo, Configuracao, Disciplina, GradeHoraria, GrupoDisciplina,
    PontuacaoSubdisciplina, NotaBimestral, ProvaAuxiliar, RecuperacaoFinal, ConselhoClasse, Professor, Turma, turma_faz_simulado,
)
from ..services.calculo_notas import (
    carregar_dados_boletim_aluno, calcular_notas_disciplina, round_2
)
from ..utils import get_professor

logger = logging.getLogger('core')


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _pode_lancar_notas(prof, config, periodo=None):
    """Verifica se o usuário tem permissão de lançar notas agora.

    Regra:
    - Superuser / ADMIN / DIRETOR / AUX_ADMIN: sempre podem
    - PROFESSOR / COORDENADOR / AUX_COORD / SECRETARIA: apenas se tiverem acesso
      ao módulo de notas e estiverem dentro do período configurado pela secretaria.
    """
    if not prof:
        return True  # superuser sem perfil
    if not prof.pode_acessar_modulo_notas:
        return False
    if prof.pode_lancar_notas:  # ADMIN, DIRETOR, AUX_ADMIN
        return True
    if prof.cargo in ('PROFESSOR', 'COORDENADOR', 'AUX_COORD', 'SECRETARIA'):
        hoje = datetime.date.today()
        if config:
            if periodo:
                ini, fim = config.periodo_para_bimestre(periodo)
            else:
                ini = config.periodo_notas_ini or config.inicio_periodo_letivo
                fim = config.periodo_notas_fim or config.fim_periodo_letivo
            if ini and fim:
                return ini <= hoje <= fim
    return False


def _pode_ver_notas(prof, user=None):
    """Verifica se o usuário pode visualizar notas (sem lançar)."""
    if user and user.is_superuser:
        return True
    if not prof:
        return user is not None and user.is_superuser
    return prof.pode_acessar_modulo_notas


def _get_config(request):
    return Configuracao.objects.filter(
        ano_letivo=request.ano_letivo,
        escola=request.escola
    ).first()


# ─────────────────────────────────────────────────────────────
# INDEX — seleção de turma + bimestre
# ─────────────────────────────────────────────────────────────

@login_required
def notas_index(request):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof, request.user):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    hoje = datetime.date.today()
    config = _get_config(request)

    turmas_qs = prof.get_turmas(
        ano_letivo=request.ano_letivo, escola=request.escola
    ) if prof else Turma.objects.filter(
        ano_letivo=request.ano_letivo, escola=request.escola
    )

    if prof and prof.cargo == 'PROFESSOR':
        disc_ids = GradeHoraria.objects.filter(
            professor=prof, turma__ano_letivo=request.ano_letivo
        ).values_list('disciplina_id', flat=True).distinct()
        disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
    else:
        disciplinas = Disciplina.objects.all().order_by('nome')

    # Monta mapa de status por bimestre/período para o JS usar no cliente
    periodos_status = {}
    periodos_lista = ['1', '2', 'PA1', '3', '4', 'PA2', 'REC']
    
    for p in periodos_lista:
        if p == 'REC':
            nome_display = 'Recuperação Final'
        elif p.isdigit():
            nome_display = f"{p}º Bimestre"
        else:
            nome_display = p
        
        if config:
            ini, fim = config.periodo_para_bimestre(p)
        else:
            ini, fim = None, None

        if ini and fim:
            if hoje < ini:
                status = 'futuro'
                msg = f'O lançamento de {nome_display} ainda não começou. Início em {ini.strftime("%d/%m/%Y")}.'
            elif hoje > fim:
                status = 'encerrado'
                msg = f'O período de lançamento de {nome_display} encerrou em {fim.strftime("%d/%m/%Y")}.'
            else:
                status = 'aberto'
                msg = f'Lançamento de {nome_display} aberto até {fim.strftime("%d/%m/%Y")}.'
        else:
            status = 'nao_configurado'
            msg = f'O período de lançamento de {nome_display} ainda não foi configurado pela secretaria.'
        periodos_status[p] = {'status': status, 'msg': msg}

    return render(request, 'core/notas_index.html', {
        'prof': prof,
        'turmas': turmas_qs,
        'disciplinas': disciplinas,
        'periodos_lista': periodos_lista,
        'config': config,
        'periodos_status': periodos_status,
    })


# ─────────────────────────────────────────────────────────────
# LANÇAMENTO — grade turma × alunos × disciplina × bimestre
# ─────────────────────────────────────────────────────────────

@login_required
def notas_turma(request, codigo, periodo):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof, request.user):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    turma = get_object_or_404(
        Turma, codigo=codigo,
        escola=request.escola, ano_letivo=request.ano_letivo
    )
    config = _get_config(request)
    pode_lancar = _pode_lancar_notas(prof, config, periodo)

    # Disciplinas visíveis para este professor/turma
    if prof and prof.cargo == 'PROFESSOR':
        disc_ids = GradeHoraria.objects.filter(
            turma=turma, professor=prof
        ).values_list('disciplina_id', flat=True).distinct()
        disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
    elif prof and prof.pode_ver_tudo:
        disc_ids = GradeHoraria.objects.filter(
            turma=turma
        ).values_list('disciplina_id', flat=True).distinct()
        disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
    else:
        disciplinas = Disciplina.objects.none()

    filtro_disc = request.GET.get('disciplina')
    if filtro_disc:
        disciplinas = disciplinas.filter(pk=filtro_disc)

    alunos = Aluno.objects.filter(turma=turma).order_by('nome')
    is_pa = str(periodo).startswith('PA')
    is_rec = str(periodo) == 'REC'

    # Busca notas existentes
    if is_pa:
        pa_num = int(str(periodo).replace('PA', ''))
        notas_qs = []
        pa_qs = ProvaAuxiliar.objects.filter(
            aluno__turma=turma,
            numero_pa=pa_num,
            ano_letivo=request.ano_letivo,
            disciplina__in=disciplinas,
        ).select_related('aluno', 'disciplina')
        rec_qs = []
    elif is_rec:
        notas_qs = []
        pa_qs = []
        rec_qs = RecuperacaoFinal.objects.filter(
            aluno__turma=turma,
            ano_letivo=request.ano_letivo,
            disciplina__in=disciplinas,
        ).select_related('aluno', 'disciplina')
    else:
        bimestre = int(periodo)
        notas_qs = NotaBimestral.objects.filter(
            aluno__turma=turma,
            bimestre=bimestre,
            ano_letivo=request.ano_letivo,
            disciplina__in=disciplinas,
        ).select_related('aluno', 'disciplina')
        pa_qs = []
        rec_qs = []

    # Mapas para acesso rápido
    notas_map = {(n.aluno_id, n.disciplina_id): n for n in notas_qs}
    pas_map = {(p.aluno_id, p.disciplina_id): p for p in pa_qs}
    recs_map = {(r.aluno_id, r.disciplina_id): r for r in rec_qs}

    # Monta grade de células para o template
    serie_turma = turma.codigo[0] if turma and turma.codigo else ''
    grade = []
    for disc in disciplinas:
        faz_sim = turma_faz_simulado(turma, disc)
        pontuacao_max = disc.get_pontuacao_maxima(serie=serie_turma, ano_letivo=request.ano_letivo, escola=request.escola)
        linha = {
            'disciplina': disc,
            'faz_simulado': faz_sim,
            'pontuacao_maxima': pontuacao_max,
            'celulas': [],
        }
        for aluno in alunos:
            nota = notas_map.get((aluno.pk, disc.pk))
            pa = pas_map.get((aluno.pk, disc.pk))
            rec = recs_map.get((aluno.pk, disc.pk))
            linha['celulas'].append({
                'aluno': aluno,
                'nota': nota,
                'pa': pa,
                'rec': rec,
            })
        grade.append(linha)

    # Período de lançamento para este período (para exibir no aviso)
    periodo_b = None
    if config:
        p_ini, p_fim = config.periodo_para_bimestre(periodo)
        if p_ini and p_fim:
            periodo_b = {'ini': p_ini, 'fim': p_fim}

    return render(request, 'core/notas_turma.html', {
        'prof': prof,
        'turma': turma,
        'is_pa': is_pa,
        'is_rec': is_rec,
        'periodo': periodo,
        'periodo_nome': 'Recuperação Final' if is_rec else (periodo if is_pa else f"{periodo}º Bimestre"),
        'periodos_lista': ['1', '2', 'PA1', '3', '4', 'PA2', 'REC'],
        'alunos': alunos,
        'grade': grade,
        'pode_lancar': pode_lancar,
        'config': config,
        'periodo_b': periodo_b,
        'tem_simulado': any(g['faz_simulado'] for g in grade),
    })


# ─────────────────────────────────────────────────────────────
# AJAX — salvar nota individual
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def nota_salvar(request):
    prof = get_professor(request.user)
    config = _get_config(request)

    if not _pode_lancar_notas(prof, config):
        return JsonResponse(
            {'ok': False, 'erro': 'Fora do período de lançamento ou sem permissão.'},
            status=403
        )

    aluno_id       = request.POST.get('aluno_id')
    disc_id        = request.POST.get('disciplina_id')
    bimestre       = request.POST.get('bimestre')
    nota_prova_str = request.POST.get('nota_prova', '').strip()
    nota_sim_str   = request.POST.get('nota_simulado', '').strip()

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        disc  = Disciplina.objects.get(pk=disc_id)
        bimestre = int(bimestre)
        if bimestre not in (1, 2, 3, 4):
            raise ValueError
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    if not _pode_lancar_notas(prof, config, bimestre):
        return JsonResponse(
            {'ok': False, 'erro': 'Fora do período de lançamento para este bimestre.'},
            status=403
        )

    serie_aluno = aluno.turma.codigo[0] if aluno.turma and aluno.turma.codigo else ''
    pontuacao_max = disc.get_pontuacao_maxima(serie=serie_aluno, ano_letivo=request.ano_letivo, escola=request.escola)

    try:
        nota_prova = Decimal(nota_prova_str.replace(',', '.'))
        if not (Decimal('0') <= nota_prova <= pontuacao_max):
            raise ValueError
    except (InvalidOperation, ValueError):
        return JsonResponse(
            {'ok': False, 'erro': f'Nota da prova inválida (0,0 – {pontuacao_max}).'},
            status=400
        )

    nota_simulado = None
    if nota_sim_str:
        try:
            nota_simulado = Decimal(nota_sim_str.replace(',', '.'))
            if not (Decimal('0') <= nota_simulado <= Decimal('20')):
                raise ValueError
        except (InvalidOperation, ValueError):
            return JsonResponse(
                {'ok': False, 'erro': 'Nota do simulado inválida (0 – 20).'},
                status=400
            )

    nota, criada = NotaBimestral.objects.update_or_create(
        aluno=aluno,
        disciplina=disc,
        bimestre=bimestre,
        ano_letivo=request.ano_letivo,
        defaults={
            'nota_prova': nota_prova,
            'nota_simulado': nota_simulado,
            'nao_avaliado': False,
            'lancado_por': prof,
        }
    )

    acao = 'criada' if criada else 'atualizada'
    logger.info(
        'NOTA %s: aluno=%s disc=%s B%s final=%s por=%s',
        acao.upper(), aluno.nome, disc.nome, bimestre, nota.nota_final,
        request.user.username
    )

    return JsonResponse({
        'ok': True,
        'nota_final': str(nota.nota_final),
        'nota_prova': str(nota.nota_prova) if nota.nota_prova is not None else '',
        'nota_simulado': str(nota.nota_simulado) if nota.nota_simulado is not None else '',
        'nao_avaliado': nota.nao_avaliado,
    })


# ─────────────────────────────────────────────────────────────
# SALVAR PROVA AUXILIAR (PA1/PA2)
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def pa_salvar(request):
    prof = get_professor(request.user)
    config = _get_config(request)

    if not _pode_lancar_notas(prof, config):
        return JsonResponse({'ok': False, 'erro': 'Fora do período de lançamento ou sem permissão.'}, status=403)

    aluno_id  = request.POST.get('aluno_id')
    disc_id   = request.POST.get('disciplina_id')
    numero_pa = request.POST.get('numero_pa')
    nota_str  = request.POST.get('nota', '').strip()

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        disc  = Disciplina.objects.get(pk=disc_id)
        numero_pa = int(numero_pa)
        if numero_pa not in (1, 2):
            raise ValueError
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    periodo_pa_str = f"PA{numero_pa}"
    if not _pode_lancar_notas(prof, config, periodo_pa_str):
        return JsonResponse({'ok': False, 'erro': f'Fora do período de lançamento para {periodo_pa_str}.'}, status=403)

    if not nota_str:
        ProvaAuxiliar.objects.filter(
            aluno=aluno, disciplina=disc, numero_pa=numero_pa, ano_letivo=request.ano_letivo
        ).delete()
        return JsonResponse({'ok': True, 'nota': ''})

    try:
        nota_val = Decimal(nota_str.replace(',', '.'))
        if not (Decimal('0') <= nota_val <= Decimal('10')):
            raise ValueError
    except (InvalidOperation, ValueError):
        return JsonResponse({'ok': False, 'erro': 'Nota inválida (0,0 – 10,0).'}, status=400)

    pa, criada = ProvaAuxiliar.objects.update_or_create(
        aluno=aluno,
        disciplina=disc,
        numero_pa=numero_pa,
        ano_letivo=request.ano_letivo,
        defaults={'nota': nota_val, 'lancado_por': prof}
    )

    return JsonResponse({'ok': True, 'nota': str(pa.nota)})


# ─────────────────────────────────────────────────────────────
# SALVAR RECUPERAÇÃO FINAL
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def rec_salvar(request):
    prof = get_professor(request.user)
    config = _get_config(request)

    if not _pode_lancar_notas(prof, config, 'REC'):
        return JsonResponse({'ok': False, 'erro': 'Fora do período de lançamento ou sem permissão para REC.'}, status=403)

    aluno_id  = request.POST.get('aluno_id')
    disc_id   = request.POST.get('disciplina_id')
    nota_str  = request.POST.get('nota', '').strip()

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        disc  = Disciplina.objects.get(pk=disc_id)
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    if not nota_str:
        RecuperacaoFinal.objects.filter(
            aluno=aluno, disciplina=disc, ano_letivo=request.ano_letivo
        ).delete()
        return JsonResponse({'ok': True, 'nota': ''})

    try:
        nota_val = Decimal(nota_str.replace(',', '.'))
        if not (Decimal('0') <= nota_val <= Decimal('10')):
            raise ValueError
    except (InvalidOperation, ValueError):
        return JsonResponse({'ok': False, 'erro': 'Nota inválida (0,0 – 10,0).'}, status=400)

    rec, criada = RecuperacaoFinal.objects.update_or_create(
        aluno=aluno,
        disciplina=disc,
        ano_letivo=request.ano_letivo,
        defaults={'nota': nota_val, 'lancado_por': prof}
    )

    return JsonResponse({'ok': True, 'nota': str(rec.nota)})


# ─────────────────────────────────────────────────────────────
# BOLETIM — individual do aluno
# ─────────────────────────────────────────────────────────────

@login_required
def boletim_aluno(request, pk):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof, request.user):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    aluno = get_object_or_404(Aluno, pk=pk)
    turma = aluno.turma

    grupos_no_boletim = carregar_dados_boletim_aluno(aluno, request.ano_letivo)

    pode_editar_conselho = (
        request.user.is_superuser or
        (prof and (prof.pode_ver_tudo or prof.cargo in ('ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD')))
    )

    return render(request, 'core/boletim_aluno.html', {
        'prof': prof,
        'aluno': aluno,
        'turma': turma,
        'grupos_no_boletim': grupos_no_boletim,
        'pode_editar_conselho': pode_editar_conselho,
    })


# ─────────────────────────────────────────────────────────────
# BOLETIM — toda a turma
# ─────────────────────────────────────────────────────────────

@login_required
def boletim_turma(request, codigo):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof, request.user):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    turma = get_object_or_404(
        Turma, codigo=codigo,
        escola=request.escola, ano_letivo=request.ano_letivo
    )
    alunos = Aluno.objects.filter(turma=turma).order_by('nome')

    notas_turma_qs = NotaBimestral.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina', 'disciplina__grupo')

    pas_turma_qs = ProvaAuxiliar.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina')

    recs_turma_qs = RecuperacaoFinal.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina')

    conselhos_turma_qs = ConselhoClasse.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina')

    notas_map = {(n.aluno_id, n.disciplina_id, n.bimestre): n for n in notas_turma_qs}
    pas_map = {(p.aluno_id, p.disciplina_id, p.numero_pa): p.nota for p in pas_qs} if 'pas_qs' in locals() else {(p.aluno_id, p.disciplina_id, p.numero_pa): p.nota for p in pas_turma_qs}
    recs_map = {(r.aluno_id, r.disciplina_id): r.nota for r in recs_turma_qs}
    conselho_map = {(c.aluno_id, c.disciplina_id): c for c in conselhos_turma_qs}

    disc_ids = GradeHoraria.objects.filter(
        turma=turma
    ).values_list('disciplina_id', flat=True).distinct()
    disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('grupo__ordem_boletim', 'nome')

    linhas = []
    for aluno in alunos:
        cols = []
        medias_finais_aluno = []
        for disc in disciplinas:
            res = calcular_notas_disciplina(aluno.pk, disc.pk, notas_map, pas_map, recs_map, conselho_map)
            bim_vals = [res['b1'], res['b2'], res['b3'], res['b4']]
            if res['media_final'] is not None:
                medias_finais_aluno.append(res['media_final'])
            elif res['media_anual'] is not None:
                medias_finais_aluno.append(res['media_anual'])

            cols.append({
                'bimestres': bim_vals,
                'media_anual': res['media_anual'],
                'media_final': res['media_final'],
                'situacao': res['situacao'],
                'promovido_conselho': res['promovido_conselho'],
            })
        
        media_geral = round_2(sum(medias_finais_aluno) / Decimal(str(len(medias_finais_aluno)))) if medias_finais_aluno else None
        linhas.append({'aluno': aluno, 'cols': cols, 'media_geral': media_geral})

    return render(request, 'core/boletim_turma.html', {
        'prof': prof,
        'turma': turma,
        'alunos': alunos,
        'disciplinas': disciplinas,
        'linhas': linhas,
        'bimestres': [1, 2, 3, 4],
    })


# ─────────────────────────────────────────────────────────────
# AJAX — salvar deliberação do Conselho de Classe
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def conselho_salvar(request):
    """Permite salvar deliberação do Conselho de Classe para um aluno em uma disciplina."""
    prof = get_professor(request.user)
    pode_conselho = (
        request.user.is_superuser or
        (prof and (prof.pode_ver_tudo or prof.cargo in ('ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD')))
    )
    if not pode_conselho:
        return JsonResponse({'ok': False, 'erro': 'Sem permissão para registrar decisão de conselho.'}, status=403)

    aluno_id = request.POST.get('aluno_id')
    disc_id = request.POST.get('disciplina_id')
    promovido_str = request.POST.get('promovido', 'false').lower()
    promovido = promovido_str in ('true', '1', 't', 'yes')
    observacao = request.POST.get('observacao', '').strip()

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        disc = Disciplina.objects.get(pk=disc_id)
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist):
        return JsonResponse({'ok': False, 'erro': 'Aluno ou Disciplina inválido.'}, status=400)

    conselho, _ = ConselhoClasse.objects.update_or_create(
        aluno=aluno,
        disciplina=disc,
        ano_letivo=request.ano_letivo,
        defaults={
            'promovido': promovido,
            'observacao': observacao,
            'lancado_por': prof,
        }
    )

    logger.info(
        'CONSELHO CLASSE: aluno=%s disc=%s promovido=%s por=%s',
        aluno.nome, disc.nome, promovido, request.user.username
    )

    return JsonResponse({
        'ok': True,
        'promovido': conselho.promovido,
        'observacao': conselho.observacao,
    })


# ─────────────────────────────────────────────────────────────
# APLICAR N/A — marcar ausentes automaticamente
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def aplicar_na_bimestre(request):
    """
    Cria registros N/A (não avaliado) para todos os alunos de uma turma
    que não possuem nota lançada em uma dada disciplina/bimestre.
    Restrito a admins, diretores e secretaria.
    """
    prof = get_professor(request.user)
    if prof and not prof.pode_lancar_notas:
        return JsonResponse(
            {'ok': False, 'erro': 'Sem permissão para aplicar N/A.'},
            status=403
        )

    turma_codigo = request.POST.get('turma_codigo', '').strip()
    disc_id      = request.POST.get('disciplina_id')
    bimestre_str = request.POST.get('bimestre')

    try:
        turma    = Turma.objects.get(codigo=turma_codigo, escola=request.escola, ano_letivo=request.ano_letivo)
        disc     = Disciplina.objects.get(pk=disc_id)
        bimestre = int(bimestre_str)
        if bimestre not in (1, 2, 3, 4):
            raise ValueError
    except (Turma.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    # Alunos da turma sem nota para esta disciplina/bimestre
    alunos = Aluno.objects.filter(turma=turma)
    ja_tem_nota = set(
        NotaBimestral.objects.filter(
            aluno__turma=turma,
            disciplina=disc,
            bimestre=bimestre,
            ano_letivo=request.ano_letivo,
        ).values_list('aluno_id', flat=True)
    )

    criados = 0
    for aluno in alunos:
        if aluno.pk not in ja_tem_nota:
            NotaBimestral.objects.create(
                aluno=aluno,
                disciplina=disc,
                bimestre=bimestre,
                ano_letivo=request.ano_letivo,
                nota_prova=Decimal('0.00'),
                nota_simulado=None,
                nota_final=Decimal('0.00'),
                nao_avaliado=True,
                lancado_por=prof,
            )
            criados += 1

    logger.info(
        'N/A aplicado: turma=%s disc=%s B%s criados=%d por=%s',
        turma_codigo, disc.nome, bimestre, criados, request.user.username
    )

    return JsonResponse({
        'ok': True,
        'criados': criados,
        'msg': f'{criados} registro(s) N/A criado(s) com sucesso.' if criados else 'Todos os alunos já possuem nota lançada.',
    })


@login_required
@require_POST
def remover_na(request):
    """Remove o status N/A de um registro, permitindo que o professor lance uma nota normal."""
    prof = get_professor(request.user)
    config = _get_config(request)

    if not _pode_lancar_notas(prof, config):
        return JsonResponse({'ok': False, 'erro': 'Fora do período de lançamento ou sem permissão.'}, status=403)

    aluno_id  = request.POST.get('aluno_id')
    disc_id   = request.POST.get('disciplina_id')
    bimestre  = request.POST.get('bimestre')

    try:
        aluno    = Aluno.objects.get(pk=aluno_id)
        disc     = Disciplina.objects.get(pk=disc_id)
        bimestre = int(bimestre)
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    if not _pode_lancar_notas(prof, config, bimestre):
        return JsonResponse({'ok': False, 'erro': 'Fora do período de lançamento para este bimestre.'}, status=403)

    deleted, _ = NotaBimestral.objects.filter(
        aluno=aluno,
        disciplina=disc,
        bimestre=bimestre,
        ano_letivo=request.ano_letivo,
        nao_avaliado=True,
    ).delete()

    return JsonResponse({'ok': True, 'removido': deleted > 0})


# ─────────────────────────────────────────────────────────────
# GESTÃO / DIREÇÃO — COMPOSIÇÃO DE PONTUAÇÃO DE SUBDISCIPLINAS
# ─────────────────────────────────────────────────────────────

def _pode_gerenciar_composicao(user, prof):
    if user.is_superuser or user.is_staff or user.username in ('silvio', 'samuel'):
        return True
    if prof and (prof.pode_editar_tudo or prof.cargo in ('DIRETOR', 'ADMIN', 'COORDENADOR')):
        return True
    return False


@login_required
def escola_composicao_disciplinas(request):
    prof = get_professor(request.user)
    if not _pode_gerenciar_composicao(request.user, prof):
        messages.error(request, 'Acesso restrito à Direção e Administradores.')
        return redirect('dashboard')

    series_disponiveis = PontuacaoSubdisciplina.SERIE_CHOICES
    serie_sel = request.GET.get('serie', '8')

    if request.method == 'POST':
        serie_post = request.POST.get('serie', serie_sel)
        disciplinas_com_grupo = Disciplina.objects.filter(grupo__isnull=False).select_related('grupo')
        count_salvo = 0
        for disc in disciplinas_com_grupo:
            field_name = f'pontuacao_{disc.pk}'
            val_str = request.POST.get(field_name, '').strip()
            if val_str:
                try:
                    val_dec = Decimal(val_str.replace(',', '.'))
                    if Decimal('0') <= val_dec <= Decimal('10'):
                        PontuacaoSubdisciplina.objects.update_or_create(
                            ano_letivo=request.ano_letivo,
                            escola=request.escola,
                            serie=serie_post,
                            disciplina=disc,
                            defaults={'pontuacao_maxima': val_dec}
                        )
                        count_salvo += 1
                except (InvalidOperation, ValueError):
                    pass
        nome_serie = dict(series_disponiveis).get(serie_post, serie_post)
        messages.success(request, f'Pontuações das subdisciplinas para {nome_serie} salvas com sucesso!')
        return redirect(f"{reverse('escola_composicao_disciplinas')}?serie={serie_post}")

    grupos_qs = GrupoDisciplina.objects.prefetch_related('disciplinas').order_by('ordem_boletim')
    pontuacoes_existentes = {
        p.disciplina_id: p.pontuacao_maxima
        for p in PontuacaoSubdisciplina.objects.filter(
            ano_letivo=request.ano_letivo,
            escola=request.escola,
            serie=serie_sel
        )
    }

    grupos_data = []
    for grp in grupos_qs:
        subdiscs = []
        soma_grupo = Decimal('0.00')
        for d in grp.disciplinas.all():
            val = pontuacoes_existentes.get(d.pk, Decimal('10.00'))
            soma_grupo += val
            subdiscs.append({
                'disciplina': d,
                'pontuacao_maxima': val,
            })
        if subdiscs:
            grupos_data.append({
                'grupo': grp,
                'subdisciplinas': subdiscs,
                'soma_grupo': soma_grupo,
                'soma_ok': soma_grupo == Decimal('10.00'),
            })

    context = {
        'prof': prof,
        'series_disponiveis': series_disponiveis,
        'serie_sel': serie_sel,
        'grupos_data': grupos_data,
    }
    return render(request, 'core/composicao_disciplinas.html', context)

