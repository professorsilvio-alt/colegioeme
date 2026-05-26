import os
import sys
import django
import datetime

# Inicializar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from core.models import Escola, AnoLetivo, Turma, Professor, Configuracao

def main():
    print("--- Inicializando Escola e Ano Letivo no Banco de Dados ---")

    # 1. Criar Escola padrão
    escola, esc_created = Escola.objects.get_or_create(
        nome="Colégio EME",
        defaults={"cor_primaria": "#1e3a8a"}
    )
    print(f"Escola: {escola.nome} ({'Criada' if esc_created else 'Já existia'})")

    # 2. Criar Ano Letivo padrão
    ano_letivo, ano_created = AnoLetivo.objects.get_or_create(
        ano=2026,
        defaults={"atual": True}
    )
    print(f"Ano Letivo: {ano_letivo.ano} ({'Criado' if ano_created else 'Já existia'})")

    # 3. Vincular Turmas à Escola e ao Ano Letivo
    turmas_sem_escola = Turma.objects.filter(escola__isnull=True)
    count_te = turmas_sem_escola.update(escola=escola)
    print(f"Turmas vinculadas à nova Escola: {count_te}")

    turmas_sem_ano = Turma.objects.filter(ano_letivo__isnull=True)
    count_ta = turmas_sem_ano.update(ano_letivo=ano_letivo)
    print(f"Turmas vinculadas ao novo Ano Letivo: {count_ta}")

    # 4. Vincular Professores à Escola
    profs = Professor.objects.all()
    count_pe = 0
    for p in profs:
        if not p.escolas.filter(id=escola.id).exists():
            p.escolas.add(escola)
            count_pe += 1
    print(f"Professores vinculados à Escola: {count_pe}")

    # 5. Criar Configuração Padrão se não existir
    config, conf_created = Configuracao.objects.get_or_create(
        escola=escola,
        ano_letivo=ano_letivo,
        defaults={
            "inicio_periodo_letivo": datetime.date(2026, 2, 3),
            "fim_periodo_letivo": datetime.date(2026, 12, 18),
        }
    )
    print(f"Configuração do Ano Letivo ({'Criada' if conf_created else 'Já existia'})")
    print("--- Inicialização concluída com sucesso! ---")

if __name__ == "__main__":
    main()
