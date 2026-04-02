from django.db import migrations, models

FERIADOS_2026_TEXTO = """\
# ─── Feriados Nacionais Fixos ───────────────────────────────
2026-01-01  # Confraternização Universal
2026-04-21  # Tiradentes
2026-05-01  # Dia do Trabalho
2026-09-07  # Independência do Brasil
2026-10-12  # Nossa Senhora Aparecida
2026-11-02  # Finados
2026-11-15  # Proclamação da República
2026-11-20  # Consciência Negra (nacional)
2026-12-25  # Natal

# ─── Feriados Nacionais Móveis (2026) ───────────────────────
2026-02-16  # Carnaval (segunda)
2026-02-17  # Carnaval (terça)
2026-04-02  # Sexta-feira Santa
2026-04-04  # Páscoa
2026-06-04  # Corpus Christi

# ─── Estaduais — Rio de Janeiro ─────────────────────────────
2026-04-23  # São Jorge (padroeiro do RJ)

# ─── Municipais — Nova Iguaçu ───────────────────────────────
2026-01-15  # Aniversário de Nova Iguaçu
2026-04-25  # Dia de São Marcos (padroeiro)
"""


def popular_feriados(apps, schema_editor):
    Configuracao = apps.get_model('core', 'Configuracao')
    for config in Configuracao.objects.all():
        if not config.feriados:
            config.feriados = FERIADOS_2026_TEXTO
            config.save()


def reverter_feriados(apps, schema_editor):
    Configuracao = apps.get_model('core', 'Configuracao')
    for config in Configuracao.objects.all():
        config.feriados = ''
        config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_configuracao'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracao',
            name='feriados',
            field=models.TextField(
                blank=True,
                default='',
                help_text=(
                    'Liste os feriados, um por linha, no formato AAAA-MM-DD. '
                    'Linhas iniciadas com # são tratadas como comentários e ignoradas.'
                ),
                verbose_name='Feriados',
            ),
        ),
        migrations.RunPython(popular_feriados, reverter_feriados),
    ]
