# Generated for Aulas Extras / Eletivas e Projeto de Vida 1ª série 3º Bimestre 2026
import datetime
from django.db import migrations

AULAS_EXTRAS_1A_3BIM_DATA = [{'data': '2026-07-28', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-07-28', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-07-28', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-07-28', 'turma': '11', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '12', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '13', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-07-28', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-07-28', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-07-28', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-04', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-04', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-04', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-04', 'turma': '11', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '12', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '13', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-04', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-04', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-04', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-04', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-04', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-04', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-11', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-11', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-11', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-11', 'turma': '11', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '12', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '13', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-11', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-11', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-11', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-18', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-18', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-18', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-18', 'turma': '11', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '12', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '13', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-08-18', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-18', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-18', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-08-18', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-18', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-18', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-08-25', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-25', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-25', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-08-25', 'turma': '11', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '12', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '13', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-08-25', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-25', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-08-25', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-09-01', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-01', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-01', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-01', 'turma': '11', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '12', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '13', 'disciplina': 'Artes', 'professor': 'Bruna'}, {'data': '2026-09-01', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-09-01', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-09-01', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Varanda'}, {'data': '2026-09-01', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-09-01', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-09-01', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Diniz'}, {'data': '2026-09-08', 'turma': '11', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-08', 'turma': '12', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-08', 'turma': '13', 'disciplina': 'Comp. Texto', 'professor': 'Thereza'}, {'data': '2026-09-08', 'turma': '11', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '12', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '13', 'disciplina': 'Projeto de Vida', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '11', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '12', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '13', 'disciplina': 'Sociedade e Cidadania', 'professor': 'Gustavo'}, {'data': '2026-09-08', 'turma': '11', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-09-08', 'turma': '12', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}, {'data': '2026-09-08', 'turma': '13', 'disciplina': 'Sustentabilidade e Meio Ambiente', 'professor': 'Fernanda'}]

def populate_aulas_extras_1a_3bim(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    Disciplina = apps.get_model('core', 'Disciplina')
    Professor = apps.get_model('core', 'Professor')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')

    # 1. Garante disciplinas
    d_soc_cid, _ = Disciplina.objects.get_or_create(nome='Sociedade e Cidadania')
    d_sust_meio, _ = Disciplina.objects.get_or_create(nome='Sustentabilidade e Meio Ambiente')
    d_proj_vida, _ = Disciplina.objects.get_or_create(nome='Projeto de Vida')
    d_comp_texto = Disciplina.objects.filter(nome__iexact='Comp. Texto').first()
    d_artes = Disciplina.objects.filter(nome__iexact='Artes').first()

    turmas_1 = list(Turma.objects.filter(codigo__in=['11', '12', '13']))

    p_thereza = Professor.objects.filter(nome__iexact='Thereza').first()
    p_gustavo = Professor.objects.filter(nome__iexact='Gustavo').first()
    p_fernanda = Professor.objects.filter(nome__iexact='Fernanda').first()
    p_varanda = Professor.objects.filter(nome__iexact='Varanda').first()
    p_diniz = Professor.objects.filter(nome__iexact='Diniz').first()
    p_bruna = Professor.objects.filter(nome__iexact='Bruna').first()

    if p_thereza:
        p_thereza.disciplinas.add(d_comp_texto)
        p_thereza.turmas.add(*turmas_1)

    if p_gustavo:
        p_gustavo.disciplinas.add(d_proj_vida, d_soc_cid)
        p_gustavo.turmas.add(*turmas_1)

    if p_fernanda:
        p_fernanda.disciplinas.add(d_sust_meio)
        p_fernanda.turmas.add(*turmas_1)

    if p_varanda:
        p_varanda.disciplinas.add(d_soc_cid)
        p_varanda.turmas.add(*turmas_1)

    if p_diniz:
        p_diniz.disciplinas.add(d_sust_meio)
        p_diniz.turmas.add(*turmas_1)

    if p_bruna:
        p_bruna.disciplinas.add(d_artes)
        p_bruna.turmas.add(*turmas_1)

    # 2. Insere registros
    for item in AULAS_EXTRAS_1A_3BIM_DATA:
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
        ('core', '0039_importar_aulas_extras_2a_serie_3o_bimestre_2026'),
    ]
    operations = [
        migrations.RunPython(populate_aulas_extras_1a_3bim, rollback),
    ]
