from django.shortcuts import redirect
from django.urls import reverse, resolve


# Caminhos técnicos que nunca devem ser interceptados
CAMINHOS_TECNICOS = ('/static/', '/media/', '/favicon', '/admin/', '/password_reset/', '/reset/', '/recuperar-senha/')
# Nomes de views que são isentas
VIEWS_ISENTAS = ('forcar_troca_senha', 'logout', 'login', 'cadastrar_email', 'password_reset', 'recuperar_senha', 'recuperar_senha_enviada', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete')


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
