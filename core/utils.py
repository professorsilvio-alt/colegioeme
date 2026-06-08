"""
Utilitários compartilhados do app core.

Centraliza funções usadas por views, context_processors e middleware
para evitar dependências circulares.
"""

import datetime
import functools
import logging
from collections import defaultdict

from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger('core')


def get_professor(user):
    """Retorna o Professor ligado ao user, ou None (admin sem perfil)."""
    try:
        return user.professor
    except Exception:
        return None


def get_client_ip(request):
    """
    Extrai o IP real do cliente, considerando o header X-Forwarded-For
    quando atrás de um proxy reverso (PythonAnywhere/Nginx).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For pode conter múltiplos IPs: client, proxy1, proxy2
        # O primeiro é o IP real do cliente
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def get_feriados(ano_letivo=None, escola=None):
    """
    Retorna o conjunto de datas de feriados a partir da Configuracao.
    Sem fallback hardcoded — retorna set() vazio se não houver configuração.
    """
    try:
        from .models import Configuracao
        config = Configuracao.objects.filter(
            ano_letivo=ano_letivo, escola=escola
        ).first()
        if config:
            feriados = config.get_feriados()
            if feriados:
                return feriados
    except Exception:
        pass
    return set()


def requires_cargo(*cargos_permitidos):
    """
    Decorator que restringe acesso a views com base no cargo do professor.

    Uso:
        @requires_cargo('ADMIN', 'DIRETOR')
        def minha_view(request):
            ...

    Se o usuário não tiver perfil de professor ou não tiver o cargo adequado,
    redireciona ao dashboard com mensagem de erro.
    Superusers sempre passam.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            prof = get_professor(request.user)
            if not prof or prof.cargo not in cargos_permitidos:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
