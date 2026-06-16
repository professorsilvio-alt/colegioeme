from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_periodos_notas_por_bimestre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notabimestral',
            name='nota_prova',
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=4,
                null=True,
                verbose_name='Nota da Prova',
            ),
        ),
        migrations.AddField(
            model_name='notabimestral',
            name='nao_avaliado',
            field=models.BooleanField(
                default=False,
                help_text='Quando verdadeiro, o aluno não realizou a avaliação. A nota final é contabilizada como 0,0.',
                verbose_name='Não Avaliado (ausente)',
            ),
        ),
    ]
