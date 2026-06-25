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
    filtro_aluno = request.GET.get('filtro_aluno', '').strip()
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
    if filtro_aluno:
        qs = qs.filter(alunos__nome__icontains=filtro_aluno)
        resumo.append(f"Aluno: {filtro_aluno}")
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
        resumo.append(f"Início: {filtro_data_ini}")
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
        resumo.append(f"Fim: {filtro_data_fim}")

    return qs.distinct(), " | ".join(resumo)


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
@require_POST
def conteudo_criar(request):
    prof_logado = get_professor(request.user)

    # Secretaria não lança conteúdos programáticos
    if prof_logado and prof_logado.cargo == 'SECRETARIA':
        messages.error(request, 'Seu cargo não permite lançar conteúdos programáticos.')
        return redirect('dashboard')

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
            
            # Busca registro existente para possível mesclagem/substituição
            existing = ConteudoProgramatico.objects.filter(
                data=data,
                professor=professor,
                disciplina=disciplina,
                turmas__codigo=t_cod
            ).first()

            if res == 'mesclar' and existing:
                existing.descricao += f"\n\n[MESCLADO EM {datetime.date.today().strftime('%d/%m/%Y')}]: {descricao}"
                existing.save()
            elif res == 'sobrescrever' and existing:
                existing.descricao = descricao
                existing.save()
            elif not existing:
                cont = ConteudoProgramatico.objects.create(
                    data=data, professor=professor, disciplina=disciplina, descricao=descricao
                )
                cont.turmas.add(Turma.objects.get(codigo=t_cod, escola=request.escola, ano_letivo=request.ano_letivo))

    logger.info('CONTEÚDO CRIADO: por usuário=%s turmas=%s disc=%s data=%s',
                request.user.username, ','.join(turmas_cods), disc_id, data)
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
        
        turmas = list(Turma.objects.filter(codigo__in=turmas_cods, escola=request.escola, ano_letivo=request.ano_letivo))
        if turmas:
            cont.turmas.set(turmas)
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
        'todos_professores': ordenar_por_nome(Professor.objects.all()),
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

    logger.info('CONTEÚDO EXCLUÍDO: pk=%d por usuário=%s', pk, request.user.username)
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

    professores = ordenar_por_nome(Professor.objects.filter(cargo='PROFESSOR'))
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
