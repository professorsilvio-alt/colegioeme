from django.db import migrations, models


def ativar_troca_para_todos(apps, schema_editor):
    """Marca todos os professors (não-superusers) para trocar a senha."""
    Professor = apps.get_model('core', 'Professor')
    for prof in Professor.objects.select_related('user').all():
        # Superusuários gerenciam sua própria senha — não forçar
        if not prof.user.is_superuser:
            prof.deve_trocar_senha = True
            prof.save()


def reverter_troca_senha(apps, schema_editor):
    Professor = apps.get_model('core', 'Professor')
    Professor.objects.update(deve_trocar_senha=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_merge_main_e_configuracao'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='deve_trocar_senha',
            field=models.BooleanField(
                default=False,
                help_text='Força o usuário a criar uma nova senha no próximo acesso.',
                verbose_name='Deve trocar senha',
            ),
        ),
        migrations.RunPython(ativar_troca_para_todos, reverter_troca_senha),
    ]
