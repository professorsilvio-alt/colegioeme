import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..models import Configuracao, Escola, AnoLetivo
from ..utils import get_professor


@login_required
def config_periodos_notas(request):
    """Tela para Secretaria/Diretor configurar os períodos de lançamento por bimestre."""
    prof = get_professor(request.user)

    pode_configurar = (
        request.user.is_superuser
        or (prof and prof.cargo in ('SECRETARIA', 'DIRETOR', 'ADMIN', 'COORDENADOR', 'AUX_COORD'))
    )
    if not pode_configurar:
        messages.error(request, 'Você não tem permissão para configurar períodos.')
        return redirect('dashboard')

    config, _ = Configuracao.objects.get_or_create(
        escola=request.escola,
        ano_letivo=request.ano_letivo,
        defaults={
            'inicio_periodo_letivo': datetime.date(datetime.date.today().year, 2, 3),
            'fim_periodo_letivo': datetime.date(datetime.date.today().year, 12, 18),
        }
    )

    if request.method == 'POST':
        def parse_date(field):
            val = request.POST.get(field, '').strip()
            try:
                return datetime.date.fromisoformat(val) if val else None
            except ValueError:
                return None

        config.notas_b1_ini = parse_date('notas_b1_ini')
        config.notas_b1_fim = parse_date('notas_b1_fim')
        config.notas_b2_ini = parse_date('notas_b2_ini')
        config.notas_b2_fim = parse_date('notas_b2_fim')
        config.notas_b3_ini = parse_date('notas_b3_ini')
        config.notas_b3_fim = parse_date('notas_b3_fim')
        config.notas_b4_ini = parse_date('notas_b4_ini')
        config.notas_b4_fim = parse_date('notas_b4_fim')
        config.save()
        messages.success(request, 'Períodos de lançamento atualizados com sucesso!')
        return redirect('config_periodos_notas')

    hoje = datetime.date.today()

    def status_periodo(ini, fim):
        if not ini or not fim:
            return 'nao_configurado'
        if hoje < ini:
            return 'futuro'
        if hoje > fim:
            return 'encerrado'
        return 'aberto'

    bimestres = []
    for b in range(1, 5):
        ini, fim = config.periodo_para_bimestre(b)
        bimestres.append({
            'numero': b,
            'ini_field': f'notas_b{b}_ini',
            'fim_field': f'notas_b{b}_fim',
            'ini': getattr(config, f'notas_b{b}_ini'),
            'fim': getattr(config, f'notas_b{b}_fim'),
            'status': status_periodo(getattr(config, f'notas_b{b}_ini'), getattr(config, f'notas_b{b}_fim')),
        })

    return render(request, 'core/config_periodos_notas.html', {
        'config': config,
        'bimestres': bimestres,
        'hoje': hoje,
    })
