import datetime
import logging
from decimal import Decimal, InvalidOperation
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..models import (
    Aluno, AnoLetivo, Configuracao, Disciplina, GradeHoraria, GrupoDisciplina,
    NotaBimestral, Professor, Turma, turma_faz_simulado,
)
from ..utils import get_professor

logger = logging.getLogger('core')


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _pode_lancar_notas(prof, config, bimestre=None):
    """Verifica se o usuário tem permissão de lançar notas agora.

    Regra:
    - ADMIN / DIRETOR / AUX_ADMIN: sempre podem
    - PROFESSOR / COORDENADOR / AUX_COORD: apenas dentro do período
      configurado pela secretaria para o bimestre em questão.
      Não é necessário o flag individual autorizado_lancar_notas.
    """
    if not prof:
        return True  # superuser sem perfil
    if prof.pode_lancar_notas:  # ADMIN, DIRETOR, AUX_ADMIN
        return True
    if prof.cargo in ('PROFESSOR', 'COORDENADOR', 'AUX_COORD'):
        hoje = datetime.date.today()
        if config:
            if bimestre:
                ini, fim = config.periodo_para_bimestre(bimestre)
            else:
                ini, fim = config.periodo_notas_ini, config.periodo_notas_fim
            if ini and fim:
                return ini <= hoje <= fim
    return False


def _pode_ver_notas(prof):
    """Verifica se o usuário pode visualizar notas (sem lançar)."""
    if not prof:
        return True
    return prof.cargo in (
        'ADMIN', 'DIRETOR', 'AUX_ADMIN', 'COORDENADOR',
        'AUX_COORD', 'ORIENTADOR', 'PROFESSOR',
    )


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
    if not _pode_ver_notas(prof):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    import datetime as _dt
    hoje = _dt.date.today()
    config = _get_config(request)

    turmas_qs = prof.get_turmas(
        ano_letivo=request.ano_letivo, escola=request.escola
    ) if prof else Turma.objects.filter(
        ano_letivo=request.ano_letivo, escola=request.escola
    )

    if prof and prof.cargo == 'PROFESSOR':
        from ..models import GradeHoraria
        disc_ids = GradeHoraria.objects.filter(
            professor=prof, turma__ano_letivo=request.ano_letivo
        ).values_list('disciplina_id', flat=True).distinct()
        disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
    else:
        disciplinas = Disciplina.objects.all().order_by('nome')

    # Monta mapa de status por bimestre para o JS usar no cliente
    periodos_status = {}
    for b in (1, 2, 3, 4):
        if config:
            ini, fim = config.periodo_para_bimestre(b)
        else:
            ini, fim = None, None

        if ini and fim:
            if hoje < ini:
                status = 'futuro'
                msg = f'O lançamento do {b}º bimestre ainda não começou. Início em {ini.strftime("%d/%m/%Y")}.'
            elif hoje > fim:
                status = 'encerrado'
                msg = f'O período de lançamento do {b}º bimestre encerrou em {fim.strftime("%d/%m/%Y")}.'
            else:
                status = 'aberto'
                msg = f'Lançamento do {b}º bimestre aberto até {fim.strftime("%d/%m/%Y")}.'
        else:
            status = 'nao_configurado'
            msg = f'O período de lançamento do {b}º bimestre ainda não foi configurado pela secretaria.'
        periodos_status[b] = {'status': status, 'msg': msg}

    return render(request, 'core/notas_index.html', {
        'prof': prof,
        'turmas': turmas_qs,
        'disciplinas': disciplinas,
        'bimestres': [1, 2, 3, 4],
        'config': config,
        'periodos_status': periodos_status,
    })


# ─────────────────────────────────────────────────────────────
# LANÇAMENTO — grade turma × alunos × disciplina × bimestre
# ─────────────────────────────────────────────────────────────

@login_required
def notas_turma(request, codigo, bimestre):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    turma = get_object_or_404(
        Turma, codigo=codigo,
        escola=request.escola, ano_letivo=request.ano_letivo
    )
    config = _get_config(request)
    pode_lancar = _pode_lancar_notas(prof, config, bimestre)

    # Disciplinas visíveis para este professor/turma
    if prof and prof.cargo == 'PROFESSOR':
        from ..models import GradeHoraria
        disc_ids = GradeHoraria.objects.filter(
            turma=turma, professor=prof
        ).values_list('disciplina_id', flat=True).distinct()
        disciplinas = Disciplina.objects.filter(pk__in=disc_ids).order_by('nome')
    elif prof and prof.pode_ver_tudo:
        from ..models import GradeHoraria
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

    # Busca notas existentes
    notas_qs = NotaBimestral.objects.filter(
        aluno__turma=turma,
        bimestre=bimestre,
        ano_letivo=request.ano_letivo,
        disciplina__in=disciplinas,
    ).select_related('aluno', 'disciplina')

    # Mapa: (aluno_pk, disc_pk) → NotaBimestral
    notas_map = {(n.aluno_id, n.disciplina_id): n for n in notas_qs}

    # Monta grade de células para o template
    grade = []
    for disc in disciplinas:
        faz_sim = turma_faz_simulado(turma, disc)
        linha = {
            'disciplina': disc,
            'faz_simulado': faz_sim,
            'celulas': [],
        }
        for aluno in alunos:
            nota = notas_map.get((aluno.pk, disc.pk))
            linha['celulas'].append({
                'aluno': aluno,
                'nota': nota,
            })
        grade.append(linha)

    # Período de lançamento para este bimestre (para exibir no aviso)
    periodo_b = None
    if config:
        p_ini, p_fim = config.periodo_para_bimestre(bimestre)
        if p_ini and p_fim:
            periodo_b = {'ini': p_ini, 'fim': p_fim}

    return render(request, 'core/notas_turma.html', {
        'prof': prof,
        'turma': turma,
        'bimestre': bimestre,
        'bimestres': [1, 2, 3, 4],
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

    aluno_id    = request.POST.get('aluno_id')
    disc_id     = request.POST.get('disciplina_id')
    bimestre    = request.POST.get('bimestre')
    nota_prova_str = request.POST.get('nota_prova', '').strip()
    nota_sim_str   = request.POST.get('nota_simulado', '').strip()

    # Validações básicas
    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        disc  = Disciplina.objects.get(pk=disc_id)
        bimestre = int(bimestre)
        if bimestre not in (1, 2, 3, 4):
            raise ValueError
    except (Aluno.DoesNotExist, Disciplina.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos.'}, status=400)

    # Re-verifica permissão com o bimestre específico
    if not _pode_lancar_notas(prof, config, bimestre):
        return JsonResponse(
            {'ok': False, 'erro': 'Fora do período de lançamento para este bimestre.'},
            status=403
        )

    # Validar notas
    try:
        nota_prova = Decimal(nota_prova_str.replace(',', '.'))
        if not (Decimal('0') <= nota_prova <= Decimal('10')):
            raise ValueError
    except (InvalidOperation, ValueError):
        return JsonResponse(
            {'ok': False, 'erro': 'Nota da prova inválida (0,0 – 10,0).'},
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
            'nao_avaliado': False,  # ao lançar nota válida, limpa N/A
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
# BOLETIM — individual do aluno
# ─────────────────────────────────────────────────────────────

@login_required
def boletim_aluno(request, pk):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    aluno = get_object_or_404(Aluno, pk=pk)
    turma = aluno.turma

    notas_qs = NotaBimestral.objects.filter(
        aluno=aluno,
        ano_letivo=request.ano_letivo,
    ).select_related('disciplina', 'disciplina__grupo')

    # Organiza notas: {disciplina_pk: {bimestre: nota_final_ou_NA}}
    # Se nao_avaliado=True, armazena a string sentinela 'NA' para o template distinguir
    notas_por_disc = defaultdict(dict)
    for nota in notas_qs:
        if nota.nao_avaliado:
            notas_por_disc[nota.disciplina_id][nota.bimestre] = 'NA'
        else:
            notas_por_disc[nota.disciplina_id][nota.bimestre] = nota.nota_final

    def _medias_e_anual(disc_pks):
        """Retorna (lista_medias_b1_b2_b3_b4, media_anual) para um conjunto de disciplinas.
        N/A é contabilizado como 0,0 na média.
        """
        medias = []
        for b in (1, 2, 3, 4):
            valores = []
            for dpk in disc_pks:
                if b in notas_por_disc[dpk]:
                    v = notas_por_disc[dpk][b]
                    valores.append(Decimal('0') if v == 'NA' else v)
            # None = bimestre ainda sem nenhum lançamento (nem nota, nem N/A)
            medias.append(round(sum(valores) / len(valores), 1) if valores else None)
        # Média anual: apenas bimestres já lançados (nota ou N/A)
        vals_validos = [v for v in medias if v is not None]
        media_anual = round(sum(vals_validos) / len(vals_validos), 1) if vals_validos else None
        return medias, media_anual

    # Agrupa para boletim: grupos e disciplinas standalone
    grupos_no_boletim = []

    # 1. Grupos com sub-disciplinas que o aluno tem notas
    grupos = GrupoDisciplina.objects.prefetch_related('disciplinas').order_by('ordem_boletim')
    for grupo in grupos:
        disc_ids_com_nota = [
            d.pk for d in grupo.disciplinas.all()
            if d.pk in notas_por_disc
        ]
        if not disc_ids_com_nota:
            continue
        medias, media_anual = _medias_e_anual(disc_ids_com_nota)
        grupos_no_boletim.append({
            'nome': grupo.nome_boletim,
            'medias': medias,   # lista [b1, b2, b3, b4]
            'media_anual': media_anual,
            'is_grupo': True,
        })

    # 2. Disciplinas standalone (sem grupo) com notas
    discs_standalone = Disciplina.objects.filter(
        pk__in=notas_por_disc.keys(), grupo__isnull=True
    ).order_by('nome')
    for disc in discs_standalone:
        medias, media_anual = _medias_e_anual([disc.pk])
        grupos_no_boletim.append({
            'nome': disc.nome,
            'medias': medias,
            'media_anual': media_anual,
            'is_grupo': False,
        })


    return render(request, 'core/boletim_aluno.html', {
        'prof': prof,
        'aluno': aluno,
        'turma': turma,
        'grupos_no_boletim': grupos_no_boletim,
        'bimestres': [1, 2, 3, 4],
    })


# ─────────────────────────────────────────────────────────────
# BOLETIM — toda a turma
# ─────────────────────────────────────────────────────────────

@login_required
def boletim_turma(request, codigo):
    prof = get_professor(request.user)
    if not _pode_ver_notas(prof):
        messages.error(request, 'Você não tem acesso ao módulo de notas.')
        return redirect('dashboard')

    turma = get_object_or_404(
        Turma, codigo=codigo,
        escola=request.escola, ano_letivo=request.ano_letivo
    )
    alunos = Aluno.objects.filter(turma=turma).order_by('nome')

    return render(request, 'core/boletim_turma.html', {
        'prof': prof,
        'turma': turma,
        'alunos': alunos,
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
                nota_prova=Decimal('0'),
                nota_simulado=None,
                nota_final=Decimal('0'),
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

    # Re-verifica permissão com o bimestre específico
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
