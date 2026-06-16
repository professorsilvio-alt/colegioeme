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

# Tipos predefinidos de ocorrência disponíveis para os professores
TIPOS_OCORRENCIA = [
    'Retirado de Sala',
    'Não fez atividade de casa',
    'Não participou da aula',
    'Sonolento/Dormiu',
    'Celular tocou',
    'Conversando',
    'Não trouxe o material',
    'Atitude inconveniente com o colega',
    'Atitude inconveniente com o professor',
    'Dever de casa incompleto',
    'Utilizando o celular',
    'Outros',
]



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

    if prof.cargo == 'INSPETOR':
        # Inspetor vê apenas ocorrências das suas turmas responsáveis
        turmas_resp = prof.turmas_inspetor.all()
        if turmas_resp.exists():
            qs = qs.filter(turma__in=turmas_resp)
        else:
            return Ocorrencia.objects.none()
    elif prof.pode_ver_tudo:
        # Demais cargos de gestão veem tudo
        pass
    else:
        # Professor comum vê apenas suas próprias ocorrências
        qs = qs.filter(professor=prof)
    return qs

@login_required
@require_POST
def ocorrencia_criar(request):
    prof = get_professor(request.user)
    data = request.POST.get('data')
    turma_cod = request.POST.get('turma')
    alunos_ids = request.POST.getlist('alunos')
    prof_id = request.POST.get('professor')
    disc_id = request.POST.get('disciplina')
    status = request.POST.get('status', 'Aberta')

    # Montar descrição a partir dos tipos predefinidos selecionados
    tipos_selecionados = request.POST.getlist('tipos_ocorrencia')
    descricao_outros = request.POST.get('descricao_outros', '').strip()
    descricao_hidden = request.POST.get('descricao', '').strip()

    # Prioridade: campo oculto preenchido pelo JS (já formatado)
    if descricao_hidden:
        descricao = descricao_hidden
    elif tipos_selecionados:
        partes = [t for t in tipos_selecionados if t != 'Outros']
        if 'Outros' in tipos_selecionados and descricao_outros:
            partes.append(f'Outros: {descricao_outros}')
        descricao = ' | '.join(partes)
    else:
        descricao = descricao_outros  # fallback

    if not descricao:
        messages.error(request, 'Selecione pelo menos um tipo de ocorrência.')
        return redirect('dashboard')

    turma = get_object_or_404(Turma, codigo=turma_cod, escola=request.escola, ano_letivo=request.ano_letivo)
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

    if alunos_ids:
        created_count = 0
        with transaction.atomic():
            for al_id in alunos_ids:
                aluno = get_object_or_404(Aluno, pk=al_id)
                oc = Ocorrencia.objects.create(
                    data=data, turma=turma, professor=professor,
                    disciplina=disciplina, descricao=descricao, status=status
                )
                oc.alunos.add(aluno)
                created_count += 1
                logger.info('OCORRÊNCIA CRIADA INDIVIDUAL: OC-%04d para aluno=%s por usuário=%s turma=%s', oc.pk, aluno.nome, request.user.username, turma_cod)
        messages.success(request, f'{created_count} ocorrência(s) criada(s) com sucesso!')
    else:
        oc = Ocorrencia.objects.create(
            data=data, turma=turma, professor=professor,
            disciplina=disciplina, descricao=descricao, status=status
        )
        logger.info('OCORRÊNCIA CRIADA SEM ALUNO: OC-%04d por usuário=%s turma=%s', oc.pk, request.user.username, turma_cod)
        messages.success(request, f'Ocorrência OC-{oc.pk:04d} criada com sucesso!')
    return redirect('dashboard')


@login_required
def ocorrencia_ver(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions
    if prof:
        if prof.cargo == 'INSPETOR':
            # Inspetor vê apenas ocorrências das suas turmas
            if oc.turma and oc.turma not in prof.turmas_inspetor.all():
                messages.error(request, 'Você não tem permissão para visualizar esta ocorrência.')
                return redirect('dashboard')
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
        messages.error(request, 'Seu cargo permite apenas a visualização e alteração de status desta ocorrência.')
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
        status = request.POST.get('status', 'Aberta')

        # Montar descrição a partir dos tipos predefinidos selecionados
        tipos_selecionados_post = request.POST.getlist('tipos_ocorrencia')
        descricao_outros_post = request.POST.get('descricao_outros', '').strip()
        descricao_hidden_post = request.POST.get('descricao', '').strip()

        if descricao_hidden_post:
            descricao = descricao_hidden_post
        elif tipos_selecionados_post:
            partes = [t for t in tipos_selecionados_post if t != 'Outros']
            if 'Outros' in tipos_selecionados_post and descricao_outros_post:
                partes.append(f'Outros: {descricao_outros_post}')
            descricao = ' | '.join(partes)
        else:
            descricao = descricao_outros_post

        if not descricao:
            messages.error(request, 'Selecione pelo menos um tipo de ocorrência.')
            return redirect(f'/ocorrencia/{oc.pk}/editar/')

        oc.data = data
        oc.turma = get_object_or_404(Turma, codigo=turma_cod, escola=request.escola, ano_letivo=request.ano_letivo)
        oc.disciplina = get_object_or_404(Disciplina, pk=disc_id) if disc_id else None
        oc.professor = get_object_or_404(Professor, pk=prof_id) if prof_id else prof
        oc.descricao = descricao
        oc.status = status
        oc.save()
        if alunos_ids:
            primeiro_id = alunos_ids[0]
            oc.alunos.set(Aluno.objects.filter(pk=primeiro_id))
            
            novos_criados = 0
            with transaction.atomic():
                for al_id in alunos_ids[1:]:
                    aluno = get_object_or_404(Aluno, pk=al_id)
                    nova_oc = Ocorrencia.objects.create(
                        data=data, turma=oc.turma, professor=oc.professor,
                        disciplina=oc.disciplina, descricao=descricao, status=status
                    )
                    nova_oc.alunos.add(aluno)
                    novos_criados += 1
            if novos_criados > 0:
                messages.success(request, f'Ocorrência atualizada e {novos_criados} nova(s) ocorrência(s) criada(s) para os outros alunos.')
            else:
                messages.success(request, 'Ocorrência atualizada!')
        else:
            oc.alunos.clear()
            messages.success(request, 'Ocorrência atualizada!')
        return redirect('dashboard')

    # Parsear a descrição existente para pré-selecionar os chips
    descricao_existente = oc.descricao or ''
    # Os tipos são separados por ' | '
    partes_existentes = [p.strip() for p in descricao_existente.split('|')]
    tipos_selecionados = []
    descricao_outros_texto = ''
    tem_outros = False
    for parte in partes_existentes:
        if parte.startswith('Outros:'):
            tipos_selecionados.append('Outros')
            descricao_outros_texto = parte[len('Outros:'):].strip()
            tem_outros = True
        elif parte in TIPOS_OCORRENCIA:
            tipos_selecionados.append(parte)
        # Se não reconhece o tipo, coloca como "Outros" para não perder informação
        elif parte:
            tipos_selecionados.append('Outros')
            descricao_outros_texto = parte
            tem_outros = True

    alunos_turma = Aluno.objects.filter(turma=oc.turma) if oc.turma else []
    alunos_turma = ordenar_por_nome(alunos_turma)
    context = {
        'oc': oc,
        'turmas': turmas_qs,
        'disciplinas': disciplinas_qs,
        'todos_professores': ordenar_por_nome(Professor.objects.all()),
        'alunos_turma': alunos_turma,
        'tipos_ocorrencia': TIPOS_OCORRENCIA,
        'tipos_selecionados': tipos_selecionados,
        'descricao_outros_texto': descricao_outros_texto,
        'tem_outros': tem_outros,
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
        
    logger.info('OCORRÊNCIA EXCLUÍDA: OC-%04d por usuário=%s', pk, request.user.username)
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
@require_POST
def ocorrencia_mudar_status_direto(request, pk):
    oc = get_object_or_404(Ocorrencia, pk=pk)
    prof = get_professor(request.user)
    
    # Check permissions
    if prof:
        if prof.cargo == 'INSPETOR':
            # Inspetor só altera status das suas turmas
            if oc.turma and oc.turma not in prof.turmas_inspetor.all():
                messages.error(request, 'Sem permissão.')
                return redirect('dashboard')
        elif not prof.pode_ver_tudo:
            if oc.professor != prof:
                messages.error(request, 'Sem permissão.')
                return redirect('dashboard')

    oc.status = 'Resolvida' if oc.status == 'Aberta' else 'Aberta'
    oc.save()
    logger.info('STATUS ALTERADO: OC-%04d para %s por usuário=%s', oc.pk, oc.status, request.user.username)
    messages.success(request, f'Status da OC-{oc.pk:04d} alterado para {oc.status}.')
    return redirect('dashboard')

