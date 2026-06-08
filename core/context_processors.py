from .utils import get_professor
from .models import AnoLetivo, Escola

def prof_context(request):
    """Makes 'prof', 'ano_letivo', 'escola' and lists available in all templates."""
    context = {
        'prof': None,
        'ano_letivo': getattr(request, 'ano_letivo', None),
        'anos_disponiveis': [],
        'escola': getattr(request, 'escola', None),
        'escolas_disponiveis': []
    }
    
    if request.user.is_authenticated:
        prof = get_professor(request.user)
        context['prof'] = prof
        
        # Lógica de anos disponíveis
        qs_anos = AnoLetivo.objects.all()
        if prof and not prof.pode_editar_tudo:
            ano_atual_obj = AnoLetivo.objects.filter(atual=True).first()
            if ano_atual_obj:
                qs_anos = qs_anos.filter(ano__lte=ano_atual_obj.ano, ano__gte=ano_atual_obj.ano - 1)
        context['anos_disponiveis'] = qs_anos

        # Cor primária — guard contra request.escola ausente
        escola = getattr(request, 'escola', None)
        context['cor_primaria'] = escola.cor_primaria if escola else '#1e3a8a'
        
        # Lógica de escolas disponíveis
        if request.user.is_superuser:
            context['escolas_disponiveis'] = Escola.objects.all()
        elif prof:
            context['escolas_disponiveis'] = prof.escolas.all()
        
    return context
