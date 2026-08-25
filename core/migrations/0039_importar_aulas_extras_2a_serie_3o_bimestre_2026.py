# Generated for Aulas Extras / Eletivas e Projeto de Vida 2ª série 3º Bimestre 2026
import datetime
from django.db import migrations

AULAS_EXTRAS_2A_3BIM_DATA = [{'data': '2026-07-28', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-07-28', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-07-28', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-07-28', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-07-28', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-07-28', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-07-28', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-07-28', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-07-28', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-07-28', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-07-28', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-07-28', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-04', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-04', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-04', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-04', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-04', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-04', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-04', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-04', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-04', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-11', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-11', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-11', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-11', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-11', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-11', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-11', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-11', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-11', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-11', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-11', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-11', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-18', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-18', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-18', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-18', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-18', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-18', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-18', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-18', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-18', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-08-25', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-25', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-25', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-08-25', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-25', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-25', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-08-25', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-25', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-25', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-25', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-25', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-08-25', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-09-01', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-01', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-01', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-01', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-01', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-01', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-01', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-09-01', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-09-01', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Luiz Otávio'}, {'data': '2026-09-08', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-08', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-08', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'}, {'data': '2026-09-08', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-08', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-08', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'}, {'data': '2026-09-08', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-08', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-08', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-08', 'turma': '21', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-09-08', 'turma': '22', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}, {'data': '2026-09-08', 'turma': '23', 'disciplina': 'Múltiplas Linguagens', 'professor': 'Lorena'}]

def populate_aulas_extras_2a_3bim(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    Disciplina = apps.get_model('core', 'Disciplina')
    Professor = apps.get_model('core', 'Professor')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')

    # 1. Garante disciplinas
    d_ed_fin, _ = Disciplina.objects.get_or_create(nome='Educação Financeira')
    d_mult_ling, _ = Disciplina.objects.get_or_create(nome='Múltiplas Linguagens')
    d_proj_vida, _ = Disciplina.objects.get_or_create(nome='Projeto de Vida')
    d_artes = Disciplina.objects.filter(nome__iexact='Artes').first()

    turmas_2 = list(Turma.objects.filter(codigo__in=['21', '22', '23']))

    p_silvio = Professor.objects.filter(nome__iexact='Silvio').first()
    p_lorena = Professor.objects.filter(nome__iexact='Lorena').first()
    p_luiz_otavio = Professor.objects.filter(nome__iexact='Luiz Otávio').first()
    p_bruna = Professor.objects.filter(nome__iexact='Bruna').first()

    if p_silvio:
        p_silvio.disciplinas.add(d_ed_fin)
        p_silvio.turmas.add(*turmas_2)

    if p_lorena:
        p_lorena.disciplinas.add(d_proj_vida, d_mult_ling)
        p_lorena.turmas.add(*turmas_2)

    if p_luiz_otavio:
        p_luiz_otavio.disciplinas.add(d_mult_ling)
        p_luiz_otavio.turmas.add(*turmas_2)

    if p_bruna:
        p_bruna.disciplinas.add(d_artes)
        p_bruna.turmas.add(*turmas_2)

    # 2. Insere registros
    for item in AULAS_EXTRAS_2A_3BIM_DATA:
        t = Turma.objects.filter(codigo=item['turma']).first()
        d = Disciplina.objects.filter(nome=item['disciplina']).first()
        p = Professor.objects.filter(nome=item['professor']).first()
        if t and d and p:
            dt = datetime.datetime.strptime(item['data'], '%Y-%m-%d').date()
            AulaExtraProgramada.objects.get_or_create(
                data=dt,
                turma=t,
                disciplina=d,
                professor=p
            )

def rollback(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0038_importar_aulas_extras_1e2_series_2026'),
    ]
    operations = [
        migrations.RunPython(populate_aulas_extras_2a_3bim, rollback),
    ]
