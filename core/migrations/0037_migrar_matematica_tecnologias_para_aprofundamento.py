# Migration to migrate 'Matemática e suas tecnologias' (and other *tecnologias areas) to Aprofundamento
from django.db import migrations

def migrar_tecnologias(apps, schema_editor):
    Disciplina = apps.get_model('core', 'Disciplina')
    ConteudoProgramatico = apps.get_model('core', 'ConteudoProgramatico')
    SugestaoConteudo = apps.get_model('core', 'SugestaoConteudo')
    GradeHoraria = apps.get_model('core', 'GradeHoraria')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')
    NotaBimestral = apps.get_model('core', 'NotaBimestral')
    ProvaAuxiliar = apps.get_model('core', 'ProvaAuxiliar')
    Ocorrencia = apps.get_model('core', 'Ocorrencia')
    Professor = apps.get_model('core', 'Professor')
    PontuacaoSubdisciplina = apps.get_model('core', 'PontuacaoSubdisciplina')

    # 1. Garante as 4 disciplinas oficiais de Aprofundamento
    disc_mat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Matemática')
    disc_nat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências da Natureza')
    disc_hum, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências Humanas')
    disc_ling, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Linguagens')

    mapeamento_termos = [
        (['matemática', 'tecnologia'], disc_mat),
        (['matematica', 'tecnologia'], disc_mat),
        (['natureza', 'tecnologia'], disc_nat),
        (['humanas', 'tecnologia'], disc_hum),
        (['linguagens', 'tecnologia'], disc_ling),
    ]

    for d in list(Disciplina.objects.all()):
        nome_lower = d.nome.lower()
        target_disc = None
        for termos, target in mapeamento_termos:
            if all(t in nome_lower for t in termos):
                target_disc = target
                break
        
        if target_disc and d.id != target_disc.id:
            print(f'Migrando {d.nome} (ID {d.id}) -> {target_disc.nome} (ID {target_disc.id})...')
            # Migra relacionamentos
            ConteudoProgramatico.objects.filter(disciplina=d).update(disciplina=target_disc)
            SugestaoConteudo.objects.filter(disciplina=d).update(disciplina=target_disc)
            GradeHoraria.objects.filter(disciplina=d).update(disciplina=target_disc)
            AulaExtraProgramada.objects.filter(disciplina=d).update(disciplina=target_disc)
            NotaBimestral.objects.filter(disciplina=d).update(disciplina=target_disc)
            ProvaAuxiliar.objects.filter(disciplina=d).update(disciplina=target_disc)
            Ocorrencia.objects.filter(disciplina=d).update(disciplina=target_disc)
            PontuacaoSubdisciplina.objects.filter(disciplina=d).update(disciplina=target_disc)
            
            for prof in d.professor_set.all():
                prof.disciplinas.add(target_disc)
                prof.disciplinas.remove(d)
                
            # Deleta a disciplina antiga
            d.delete()

def rollback(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0036_corrigir_aulas_extras_para_aprofundamento'),
    ]
    operations = [
        migrations.RunPython(migrar_tecnologias, rollback),
    ]
