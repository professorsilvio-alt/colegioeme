from .views import get_professor

def prof_context(request):
    """Makes 'prof' available in all templates."""
    if request.user.is_authenticated:
        return {'prof': get_professor(request.user)}
    return {'prof': None}
