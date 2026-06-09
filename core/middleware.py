from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import resolve

from .utils import get_client_ip


# Caminhos técnicos que nunca devem ser interceptados
CAMINHOS_TECNICOS = ('/static/', '/media/', '/favicon', '/painel-gestao-eme/', '/password_reset/', '/reset/', '/recuperar-senha/')
# Nomes de views que são isentas de troca de senha
VIEWS_ISENTAS = ('forcar_troca_senha', 'logout', 'login', 'cadastrar_email', 'password_reset', 'recuperar_senha', 'recuperar_senha_enviada', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete')

# Caminho literal da view de login (evita chamar reverse() no ciclo de inicialização)
LOGIN_PATH = '/login/'


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
            "script-src 'self' 'unsafe-inline' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-src https://www.google.com/recaptcha/; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # Tenta remover headers que expõem o servidor (PythonAnywhere/Nginx)
        for h in ['Server', 'X-Powered-By', 'X-AspNet-Version']:
            try:
                del response[h]
            except KeyError:
                pass
        
        return response


class LoginRateLimitMiddleware:
    """Implementa rate limiting básico para a rota de login."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Usa caminho literal para evitar chamar reverse() a cada request
        if request.path == LOGIN_PATH and request.method == 'POST':
            ip = get_client_ip(request)
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 5:  # Máximo 5 tentativas por 5 minutos
                return HttpResponseForbidden("Muitas tentativas de login. Tente novamente em alguns minutos.")
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


class EscolaMiddleware:
    """
    Middleware que gerencia a Escola selecionada na sessão.
    Permite trocar a escola via parâmetro GET ?set_escola=...
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from .models import Escola
            
            # 1. Troca de escola via GET
            set_escola = request.GET.get('set_escola')
            if set_escola:
                try:
                    esc_obj = Escola.objects.get(id=set_escola)
                    # Verifica se o usuário tem acesso a esta escola
                    prof = getattr(request.user, 'professor', None)
                    pode_ver = False
                    if request.user.is_superuser:
                        pode_ver = True
                    elif prof and prof.escolas.filter(id=set_escola).exists():
                        pode_ver = True
                    
                    if pode_ver:
                        request.session['escola_id'] = esc_obj.id
                except (Escola.DoesNotExist, ValueError):
                    pass

            # 2. Recupera a escola da sessão ou define o padrão
            esc_id = request.session.get('escola_id')
            esc_obj = None
            if esc_id:
                esc_obj = Escola.objects.filter(id=esc_id).first()
            
            if not esc_obj:
                # Fallback para a primeira escola do professor
                prof = getattr(request.user, 'professor', None)
                if prof:
                    esc_obj = prof.escolas.first()
                elif request.user.is_superuser:
                    esc_obj = Escola.objects.first()
                
                if esc_obj:
                    request.session['escola_id'] = esc_obj.id
            
            request.escola = esc_obj
        else:
            request.escola = None

        return self.get_response(request)


class AnoLetivoMiddleware:
    """
    Middleware que gerencia o Ano Letivo selecionado na sessão.
    Permite trocar o ano via parâmetro GET ?set_ano=...
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from .models import AnoLetivo
            
            # 1. Troca de ano via GET
            set_ano = request.GET.get('set_ano')
            if set_ano:
                try:
                    ano_obj = AnoLetivo.objects.get(ano=set_ano)
                    # Verifica se o usuário tem permissão para ver este ano
                    prof = getattr(request.user, 'professor', None)
                    pode_ver = True
                    if prof and not prof.pode_editar_tudo:
                        ano_atual = AnoLetivo.objects.filter(atual=True).first()
                        if ano_atual:
                            if not (ano_atual.ano - 1 <= int(set_ano) <= ano_atual.ano):
                                pode_ver = False
                    
                    if pode_ver:
                        request.session['ano_letivo_id'] = ano_obj.id
                except (AnoLetivo.DoesNotExist, ValueError):
                    pass

            # 2. Recupera o ano da sessão ou define o padrão
            ano_id = request.session.get('ano_letivo_id')
            ano_obj = None
            if ano_id:
                ano_obj = AnoLetivo.objects.filter(id=ano_id).first()
            
            if not ano_obj:
                # Fallback para o ano marcado como atual
                ano_obj = AnoLetivo.objects.filter(atual=True).first()
                if not ano_obj:
                    # Fallback final para o ano mais recente
                    ano_obj = AnoLetivo.objects.order_by('-ano').first()
                
                if ano_obj:
                    request.session['ano_letivo_id'] = ano_obj.id
            
            request.ano_letivo = ano_obj
        else:
            request.ano_letivo = None

        return self.get_response(request)
