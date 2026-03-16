import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from core.models import Disciplina, Turma, SugestaoConteudo

def populate():
    # Disciplinas
    mat1, _ = Disciplina.objects.get_or_create(nome='Mat. I')
    mat2, _ = Disciplina.objects.get_or_create(nome='Mat. II')
    mat3, _ = Disciplina.objects.get_or_create(nome='Mat. III')

    # Turmas
    t31, _ = Turma.objects.get_or_create(codigo='31')
    t32, _ = Turma.objects.get_or_create(codigo='32')

    # Mat I Topics
    mat1_topics = [
        "Conjuntos e Intervalos",
        "Funções: Domínio, Contradomínio e Imagem",
        "Função do 1º Grau",
        "Função do 2º Grau",
        "Função Exponencial",
        "Logaritmos e propriedades",
        "Progressão Aritmética (PA)",
        "Progressão Geométrica (PG)",
        "Porcentagem e Juros Simples/Compostos",
    ]

    # Mat II Topics
    mat2_topics = [
        "Matrizes: Definição e Operações",
        "Determinantes",
        "Sistemas Lineares",
        "Trigonometria no Triângulo Retângulo",
        "Ciclo Trigonométrico",
        "Funções Trigonométricas",
        "Análise Combinatória",
        "Probabilidade",
        "Estatística Básica",
    ]

    # Mat III Topics
    mat3_topics = [
        "Geometria Plana: Áreas e Perímetros",
        "Geometria Espacial: Prismas e Pirâmides",
        "Geometria Espacial: Cilindros, Cones e Esferas",
        "Geometria Analítica: Ponto e Reta",
        "Geometria Analítica: Circunferência",
        "Números Complexos",
        "Polinômios",
        "Equações Algébricas",
    ]

    def create_suggestions(disc, topics, turmas):
        for i, text in enumerate(topics):
            sug, created = SugestaoConteudo.objects.get_or_create(
                disciplina=disc,
                texto=text,
                defaults={'ordem': i}
            )
            if created:
                sug.turmas.add(*turmas)
                print(f"Criada sugestão: {text} para {disc}")

    create_suggestions(mat1, mat1_topics, [t31, t32])
    create_suggestions(mat2, mat2_topics, [t31, t32])
    create_suggestions(mat3, mat3_topics, [t31, t32])

if __name__ == '__main__':
    populate()
