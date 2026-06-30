from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Aviso
from ..utils import get_professor

@login_required
def mural_avisos(request):
    avisos = Aviso.objects.filter(ativo=True).select_related('autor').order_by('-criado_em')
    prof = get_professor(request.user)
    
    # Checa se o professor atual tem permissão para criar avisos
    pode_criar = False
    if prof and prof.cargo in ('DIRETOR', 'COORDENADOR', 'AUX_COORD'):
        pode_criar = True

    return render(request, 'core/mural_avisos.html', {
        'avisos': avisos,
        'pode_criar': pode_criar,
        'prof': prof,
    })

@login_required
def mural_criar_aviso(request):
    prof = get_professor(request.user)
    if not prof or prof.cargo not in ('DIRETOR', 'COORDENADOR', 'AUX_COORD'):
        messages.error(request, 'Você não tem permissão para criar avisos.')
        return redirect('mural_avisos')

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        mensagem = request.POST.get('mensagem')
        
        if titulo and mensagem:
            Aviso.objects.create(
                titulo=titulo,
                mensagem=mensagem,
                autor=prof
            )
            messages.success(request, 'Aviso publicado com sucesso!')
            return redirect('mural_avisos')
        else:
            messages.error(request, 'Preencha todos os campos.')

    return render(request, 'core/mural_criar_aviso.html', {
        'prof': prof
    })
