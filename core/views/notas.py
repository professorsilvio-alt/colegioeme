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
    Aluno, AnoLetivo, Configuracao, Disciplina, GrupoDisciplina,
    NotaBimestral, Professor, Turma, turma_faz_simulado,
)
from ..utils import get_professor

logger = logging.getLogger('core')


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _pode_lancar_notas(prof, config):
    """Verifica se o usuário tem permissão de lançar notas agora."""
    if not prof:
        return True  # superuser sem perfil
    if prof.pode_lancar_notas:  # ADMIN, DIRETOR, AUX_ADMIN
        return True
    if prof.cargo == 'PROFESSOR' and prof.autorizado_lancar_notas:
        hoje = datetime.date.today()
        if config and config.periodo_notas_ini and config.periodo_notas_fim:
            return config.periodo_notas_ini <= hoje <= config.periodo_notas_fim
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

    config = _get_config(request)
    pode_lancar = _pode_lancar_notas(prof, config)

    turmas_qs = prof.get_turmas(
        ano_letivo=request.ano_letivo, escola=request.escola
    ) if prof else Turma.objects.filter(
        ano_letivo=request.ano_letivo, escola=request.escola
    )

    return render(request, 'core/notas_index.html', {
        'prof': prof,
        'turmas': turmas_qs,
        'bimestres': [1, 2, 3, 4],
        'pode_lancar': pode_lancar,
        'config': config,
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
    pode_lancar = _pode_lancar_notas(prof, config)

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

    return render(request, 'core/notas_turma.html', {
        'prof': prof,
        'turma': turma,
        'bimestre': bimestre,
        'bimestres': [1, 2, 3, 4],
        'alunos': alunos,
        'grade': grade,
        'pode_lancar': pode_lancar,
        'config': config,
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
            if not (Decimal('0') <= nota_simulado <= Decimal('10')):
                raise ValueError
        except (InvalidOperation, ValueError):
            return JsonResponse(
                {'ok': False, 'erro': 'Nota do simulado inválida (0,0 – 10,0).'},
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
        'nota_prova': str(nota.nota_prova),
        'nota_simulado': str(nota.nota_simulado) if nota.nota_simulado is not None else '',
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

    # Organiza notas: {disciplina_pk: {bimestre: nota_final}}
    notas_por_disc = defaultdict(dict)
    for nota in notas_qs:
        notas_por_disc[nota.disciplina_id][nota.bimestre] = nota.nota_final

    def _medias_e_anual(disc_pks):
        """Retorna (lista_medias_b1_b2_b3_b4, media_anual) para um conjunto de disciplinas."""
        medias = []
        for b in (1, 2, 3, 4):
            valores = [
                notas_por_disc[dpk][b]
                for dpk in disc_pks
                if b in notas_por_disc[dpk]
            ]
            medias.append(round(sum(valores) / len(valores), 1) if valores else None)
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
