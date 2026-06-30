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
from ..utils import get_professor, get_feriados, get_client_ip

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
        return False


def login_view(request):
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

        ip = get_client_ip(request)
        user = authenticate(request, username=usuario, password=senha)
        if user:
            login(request, user)
            logger.info('LOGIN OK: usuário=%s ip=%s', usuario, ip)
            # Salva a escola selecionada na sessão
            if escola_id:
                request.session['escola_id'] = escola_id
            # Limpa tentativas em caso de sucesso
            cache.delete(f'login_attempts_{ip}')
            return redirect('dashboard')
        else:
            # Incrementa tentativas em caso de falha
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            cache.set(cache_key, attempts + 1, 300) # Expira em 5 min
            logger.warning('LOGIN FALHOU: usuário=%s ip=%s tentativa=%d', usuario, ip, attempts + 1)
            messages.error(request, 'Usuário ou senha incorretos!')
    return render(request, 'core/login.html', {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
        'escolas': Escola.objects.all()
    })


@require_POST
def logout_view(request):
    username = request.user.username if request.user.is_authenticated else 'anon'
    logger.info('LOGOUT: usuário=%s', username)
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
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

