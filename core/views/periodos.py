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
        config.notas_pa1_ini = parse_date('notas_pa1_ini')
        config.notas_pa1_fim = parse_date('notas_pa1_fim')
        config.notas_b3_ini = parse_date('notas_b3_ini')
        config.notas_b3_fim = parse_date('notas_b3_fim')
        config.notas_b4_ini = parse_date('notas_b4_ini')
        config.notas_b4_fim = parse_date('notas_b4_fim')
        config.notas_pa2_ini = parse_date('notas_pa2_ini')
        config.notas_pa2_fim = parse_date('notas_pa2_fim')
        config.notas_rec_final_ini = parse_date('notas_rec_final_ini')
        config.notas_rec_final_fim = parse_date('notas_rec_final_fim')
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

    periodos_lista = []
    lista_db = [
        ('1', '1º', 'Bimestre', 'notas_b1_ini', 'notas_b1_fim'),
        ('2', '2º', 'Bimestre', 'notas_b2_ini', 'notas_b2_fim'),
        ('PA1', 'PA 1', 'Prova Auxiliar', 'notas_pa1_ini', 'notas_pa1_fim'),
        ('3', '3º', 'Bimestre', 'notas_b3_ini', 'notas_b3_fim'),
        ('4', '4º', 'Bimestre', 'notas_b4_ini', 'notas_b4_fim'),
        ('PA2', 'PA 2', 'Prova Auxiliar', 'notas_pa2_ini', 'notas_pa2_fim'),
        ('REC', 'Rec.', 'Recuperação Final', 'notas_rec_final_ini', 'notas_rec_final_fim'),
    ]

    for p_id, p_prin, p_sec, f_ini, f_fim in lista_db:
        periodos_lista.append({
            'id': p_id,
            'nome_principal': p_prin,
            'nome_secundario': p_sec,
            'ini_field': f_ini,
            'fim_field': f_fim,
            'ini': getattr(config, f_ini),
            'fim': getattr(config, f_fim),
            'status': status_periodo(getattr(config, f_ini), getattr(config, f_fim)),
        })

    return render(request, 'core/config_periodos_notas.html', {
        'config': config,
        'periodos': periodos_lista,
        'hoje': hoje,
    })
