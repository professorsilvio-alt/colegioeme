import os
import django
import sys

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
    django.setup()
    from core.models import SugestaoConteudo, Disciplina, Turma
    print("Django inicializado com sucesso.")
except Exception as e:
    print(f"Erro na inicialização do Django: {e}")
    sys.exit(1)

DATA = [
    # ... (Data is already here, keeping it)
]

def run_import():
    print(f"Iniciando importação de {len(DATA)} sugestões...")
    
    # Verificar se as tabelas bases têm dados
    if not Disciplina.objects.exists():
        print("ERRO: Não existem disciplinas cadastradas no banco! Importe as disciplinas primeiro.")
        return
    if not Turma.objects.exists():
        print("ERRO: Não existem turmas cadastradas no banco!")
        return

    created_count = 0
    updated_count = 0
    
    for item in DATA:
        disc_nome = item['disc']
        texto = item['texto']
        turmas_cods = item['turmas']
        
        try:
            # 1. Obter ou criar a disciplina (com tratamento de erro)
            disciplina, _ = Disciplina.objects.get_or_create(nome=disc_nome)
            
            # 2. Criar a sugestão
            sugestao, created = SugestaoConteudo.objects.get_or_create(
                disciplina=disciplina,
                texto=texto
            )
            
            # 3. Vincular as turmas
            if turmas_cods:
                turmas = Turma.objects.filter(codigo__in=turmas_cods)
                if not turmas.exists():
                    print(f"Aviso: Turmas {turmas_cods} não encontradas para '{texto[:30]}'")
                sugestao.turmas.set(turmas)
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as ex:
            print(f"Erro ao importar item '{texto[:20]}': {ex}")

    print(f"Processo finalizado!")
    print(f"- Criadas: {created_count}")
    print(f"- Atualizadas: {updated_count}")

if __name__ == "__main__":
    run_import()
  {
    "disc": "Mat. I",
    "texto": "1. Divis\u00e3o Euclidiana",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Conjuntos e Intervalos",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Fun\u00e7\u00f5es: Dom\u00ednio, Contradom\u00ednio e Imagem",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Fun\u00e7\u00e3o do 1\u00ba Grau",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Fun\u00e7\u00e3o do 2\u00ba Grau",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Fun\u00e7\u00e3o Exponencial",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Logaritmos e propriedades",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Progress\u00e3o Aritm\u00e9tica (PA)",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Progress\u00e3o Geom\u00e9trica (PG)",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. I",
    "texto": "Porcentagem e Juros Simples/Compostos",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Matrizes: Defini\u00e7\u00e3o e Opera\u00e7\u00f5es",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Determinantes",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Sistemas Lineares",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Trigonometria no Tri\u00e2ngulo Ret\u00e2ngulo",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Ciclo Trigonom\u00e9trico",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Fun\u00e7\u00f5es Trigonom\u00e9tricas",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "An\u00e1lise Combinat\u00f3ria",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Probabilidade",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. II",
    "texto": "Estat\u00edstica B\u00e1sica",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Geometria Plana: \u00c1reas e Per\u00edmetros",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Geometria Espacial: Prismas e Pir\u00e2mides",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Geometria Espacial: Cilindros, Cones e Esferas",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Geometria Anal\u00edtica: Ponto e Reta",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Geometria Anal\u00edtica: Circunfer\u00eancia",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "N\u00fameros Complexos",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Polin\u00f4mios",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Mat. III",
    "texto": "Equa\u00e7\u00f5es Alg\u00e9bricas",
    "turmas": [
      "31",
      "32"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Fra\u00e7\u00f5es",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. N\u00fameros decimais",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. O ponto",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. O que \u00e9 probabilidade?",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. O que \u00e9 uma grandeza?",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Pesquisa",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Poliedros",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Potencia\u00e7\u00e3o",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Sequ\u00eancias",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. Sistema de numera\u00e7\u00e3o",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "1. \u00c2ngulos",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Crit\u00e9rios de divisibilidade",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. E o nosso sistema de numera\u00e7\u00e3o?",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Entendendo a probabilidade",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Fra\u00e7\u00f5es equivalentes",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. O inverso da potencia\u00e7\u00e3o",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. O que \u00e9 medir?",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Opera\u00e7\u00f5es com n\u00fameros decimais",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Opera\u00e7\u00f5es inversas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Pol\u00edgonos",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Registro e organiza\u00e7\u00e3o de uma pesquisa",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Reta, semirreta e segmento de reta",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "2. Vistas de um poliedro",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Analisando igualdades",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Compara\u00e7\u00e3o de fra\u00e7\u00f5es",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Fra\u00e7\u00f5es, n\u00fameros decimais e porcentagem",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. M\u00faltiplos e divisores de um n\u00famero natural",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. O Sistema internacional de unidades (SI)",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Organigramas e fluxogramas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Os n\u00fameros naturais",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Plano",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Poliedro especiais",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Pot\u00eancia de base 10",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Representando a probabilidade",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "3. Tri\u00e2ngulos",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Express\u00f5es num\u00e9ricas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. N\u00fameros primos e n\u00fameros compostos",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Opera\u00e7\u00f5es com n\u00fameros fracion\u00e1rios",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Opera\u00e7\u00f5es com n\u00fameros naturais",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Outras medidas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Quadril\u00e1teros",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "4. Volume de poliedros",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "5. Estrat\u00e9gias de c\u00e1lculo",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "5. Semelhan\u00e7a de figuras planas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "6. Plantas baixas",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  },
  {
    "disc": "Matem\u00e1tica",
    "texto": "T\u00f3picos",
    "turmas": [
      "61",
      "62",
      "63"
    ]
  }
]
    # Full data will be injected here or provided to the user
]

def run_import():
    print(f"Iniciando importação de {len(DATA)} sugestões...")
    created_count = 0
    
    for item in DATA:
        disc_nome = item['disc']
        texto = item['texto']
        turmas_cods = item['turmas']
        
        # 1. Obter ou criar a disciplina
        disciplina, _ = Disciplina.objects.get_or_create(nome=disc_nome)
        
        # 2. Criar a sugestão (usando get_or_create para evitar duplicidade)
        sugestao, created = SugestaoConteudo.objects.get_or_create(
            disciplina=disciplina,
            texto=texto
        )
        
        # 3. Vincular as turmas
        if turmas_cods:
            turmas = Turma.objects.filter(codigo__in=turmas_cods)
            sugestao.turmas.set(turmas)
            
        if created:
            created_count += 1

    print(f"Importação concluída! {created_count} novas sugestões criadas.")

if __name__ == "__main__":
    run_import()
