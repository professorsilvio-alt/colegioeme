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
    
    # Fallback apenas para 2026 se o ano for compatível ou não informado
    if not ano_letivo or getattr(ano_letivo, 'ano', None) == 2026 or ano_letivo == 2026:
        import datetime
        return {
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


import unicodedata

def remover_acentos(texto):
    """Remove acentos e converte para minúsculas para comparação."""
    if not texto:
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()


def ordenar_por_nome(objs, key_func=lambda x: x.nome):
    """Ordena uma lista/queryset de objetos de forma alfabética sem diferenciar acentos."""
    return sorted(objs, key=lambda x: remover_acentos(key_func(x)))

