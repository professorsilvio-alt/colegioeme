import time
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse, resolve


# Caminhos técnicos que nunca devem ser interceptados
CAMINHOS_TECNICOS = ('/static/', '/media/', '/favicon', '/painel-gestao-eme/', '/password_reset/', '/reset/', '/recuperar-senha/')
# Nomes de views que são isentas de troca de senha
VIEWS_ISENTAS = ('forcar_troca_senha', 'logout', 'login', 'cadastrar_email', 'password_reset', 'recuperar_senha', 'recuperar_senha_enviada', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete')


class SecurityHeadersMiddleware:
    """
    Middleware para adicionar Content Security Policy (CSP) e
    suprimir headers que expõem a infraestrutura.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # CSP básica: permite apenas mesma origem e estilos inline seguros
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # Tenta remover headers que expõem o servidor (PythonAnywhere/Nginx)
        # Nota: Alguns headers são injetados pelo Proxy e podem não ser removíveis aqui
        for h in ['Server', 'X-Powered-By', 'X-AspNet-Version']:
            if h in response:
                del response[h]
        
        return response


class LoginRateLimitMiddleware:
    """Implementa rate limiting básico para a rota de login."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == reverse('login') and request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 5: # Máximo 5 tentativas
                return HttpResponseForbidden("Muitas tentativas de login. Tente novamente em alguns minutos.")
            
            # Incrementa o contador na view se o login falhar (controlado na view)
        return self.get_response(request)


class ForcarTrocaSenhaMiddleware:
    """
    Middleware que obriga usuários com a flag deve_trocar_senha a
    redefinirem sua senha no primeiro acesso.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path

            # Pula arquivos estáticos e admin
            if any(path.startswith(p) for p in CAMINHOS_TECNICOS):
                return self.get_response(request)

            try:
                # Resolve a view atual para conferir se é isenta
                match = resolve(path)
                if match.view_name in VIEWS_ISENTAS:
                    return self.get_response(request)

                # Verifica o perfil do professor
                prof = getattr(request.user, 'professor', None)
                if prof and prof.deve_trocar_senha:
                    # Somente redireciona se não for uma rota técnica filtrada acima
                    return redirect('forcar_troca_senha')

            except Exception:
                # Se não resolver (404) ou o usuário não for professor, deixa passar
                pass

        return self.get_response(request)
