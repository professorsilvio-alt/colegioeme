/**
 * Totem Interativo - Feira das Ciências Colégio EME 2026
 * Lógica principal da aplicação, dados estruturados e interações touch-friendly.
 */

// Base de Dados Completa da Feira das Ciências
const TOTEM_DATA = {
    schoolName: "Colégio EME",
    eventTitle: "Feira das Ciências 2026",
    eventDate: "22 de Outubro de 2026",
    classes: [
        {
            id: "61",
            code: "61",
            grade: "6º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 15",
            floor: "Térreo (Bloco Anexo)",
            block: "Bloco Anexo",
            floorKey: "0",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Estudos Atmosféricos, Meteorologia e Sustentabilidade",
            description: "Projetos investigativos sobre uso de drones no monitoramento atmosférico, meteorologia e chuvas, desmatamento ilegal e poluição urbana.",
            image: "imagens/sala_15.png",
            images: [
                { src: "imagens/sala_15.png", label: "Entrada Sala 15 (Turma 61)" },
                { src: "imagens/terreo.png", label: "Acesso Bloco Anexo (Térreo)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "GRUPO 01",
                    theme: "06. Drones e questão ambiental atmosférica",
                    members: ["Isabela", "Luiza Dantas", "Maria Clara", "Valentina Martins"]
                },
                {
                    number: "02",
                    name: "GRUPO 02",
                    theme: "01. Meteorologia: as chuvas",
                    members: ["Marcos Pedro", "Otávio", "Guilherme", "Davi", "João Pereira"]
                },
                {
                    number: "03",
                    name: "GRUPO 03",
                    theme: "12. Desmatamento ilegal e os impactos atmosféricos",
                    members: ["Natasha Saba", "Isa Ceciliano", "Larissa de Almeida", "Vitória Chiabai"]
                },
                {
                    number: "04",
                    name: "GRUPO 04",
                    theme: "09. Poluição atmosférica na cidade",
                    members: ["Henry", "Joacy Júnior", "Eduardo Afonso", "Gabriel", "Eduardo Gaio"]
                }
            ],
            color: "#0284c7",
            route: "No piso térreo, dirija-se ao Bloco Anexo. A Sala 15 é a primeira porta de acesso às salas dos 6º anos no anexo."
        },
        {
            id: "62",
            code: "62",
            grade: "6º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 16",
            floor: "Térreo (Bloco Anexo)",
            block: "Bloco Anexo",
            floorKey: "0",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Sustentabilidade, Energia Renovável, Efeito Estufa e Clima",
            description: "Projetos investigativos sobre os 5R's da sustentabilidade, efeito estufa e aquecimento global, o ciclo hidrológico, energia renovável e clima, e riscos climáticos urbanos.",
            image: "imagens/sala_16.png",
            images: [
                { src: "imagens/sala_16.png", label: "Entrada Sala 16 (Turma 62)" },
                { src: "imagens/terreo.png", label: "Acesso Bloco Anexo (Térreo)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "GRUPO 01",
                    theme: "16. Os 5R´s",
                    members: ["Nicolas Santos", "Gabriel", "Artur", "Guilherme"]
                },
                {
                    number: "02",
                    name: "GRUPO 02",
                    theme: "04. Efeito Estufa e aquecimento global",
                    members: ["Julia", "Camila", "Ana", "Maitê", "Maria Eduarda"]
                },
                {
                    number: "03",
                    name: "GRUPO 03",
                    theme: "03. O Ciclo da Água",
                    members: ["Bernardo", "Nicolas", "Davi Silva", "Davi dos Santos"]
                },
                {
                    number: "04",
                    name: "GRUPO 04",
                    theme: "Energia renovável e o clima",
                    members: ["Maria Luiza", "Maria Carolina", "Sara", "Manuela", "Maria Clara"]
                },
                {
                    number: "05",
                    name: "GRUPO 05",
                    theme: "13. Riscos climáticos em ambientes urbanos",
                    members: ["Sofia", "Lara", "Luiza", "Rafael"]
                }
            ],
            color: "#0284c7",
            route: "No piso térreo, dirija-se ao Bloco Anexo. A Sala 16 fica posicionada no corredor central do anexo, ao lado da Sala 15."
        },
        {
            id: "63",
            code: "63",
            grade: "6º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 17",
            floor: "Térreo (Bloco Anexo)",
            block: "Bloco Anexo",
            floorKey: "0",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Conforto Térmico, Clima, Transição Energética e Adaptação",
            description: "Projetos investigativos sobre conforto térmico urbano, fenômenos climáticos extremos, estudos climáticos por desenhos, transição energética e estratégias de adaptação.",
            image: "imagens/sala_17.png",
            images: [
                { src: "imagens/sala_17.png", label: "Entrada Sala 17 (Turma 63)" },
                { src: "imagens/terreo.png", label: "Acesso Bloco Anexo (Térreo)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "GRUPO 01",
                    theme: "08. Conforto térmico em ambiente urbano",
                    members: ["Betina", "Rebeca", "Manuela", "Mariana", "Ana Clara"]
                },
                {
                    number: "02",
                    name: "GRUPO 02",
                    theme: "05. Fenômenos climáticos extremos",
                    members: ["Sofia", "Juliana"]
                },
                {
                    number: "03",
                    name: "GRUPO 03",
                    theme: "14. Os desenhos e os estudos climáticos",
                    members: ["Artur", "Alice", "Rafael", "Bernardo de O.", "João Gabriel", "João Pedro"]
                },
                {
                    number: "04",
                    name: "GRUPO 04",
                    theme: "15. Transição energética e o clima",
                    members: ["Bernardo Martins", "Daniel", "Sara", "Maria Eduarda Oliveira", "Maria Eduarda Bitencurt"]
                },
                {
                    number: "05",
                    name: "GRUPO 05",
                    theme: "17. Adaptação às mudanças climáticas",
                    members: ["Giovanna", "Luíza", "Lara", "Isabely", "Eduarda"]
                }
            ],
            color: "#0284c7",
            route: "No piso térreo, siga até o Bloco Anexo. A Sala 17 fica logo após a Sala 16 no corredor do anexo."
        },
        {
            id: "71",
            code: "71",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 04",
            floor: "2º Andar",
            block: "Bloco Maria",
            floorKey: "2",
            inspector: "Inspetora Maria",
            inspectorAvatar: "imagens/avatar_inspetora_maria.png",
            theme: "A Nova Era Sonora",
            description: "Exploração da Inteligência Artificial aplicada ao áudio e à música: sensibilidade musical artificial, composição generativa de canções e testes auditivos de identificação de autoria.",
            image: "imagens/sala_4.png",
            images: [
                { src: "imagens/sala_4.png", label: "Entrada Sala 04 (Turma 71)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Maria)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "Pesquisadores da IA",
                    theme: "A IA pode sentir a música?",
                    members: []
                },
                {
                    number: "02",
                    name: "Compositores da IA",
                    theme: "Como gerar músicas com IA?",
                    members: []
                },
                {
                    number: "03",
                    name: "Estação da Audição",
                    theme: "Quem compôs essa música? IA ou humano?",
                    members: []
                }
            ],
            color: "#0d9488",
            route: "Suba até o 2º Andar pelo Bloco Maria. Caminhe até o final do corredor; a Sala 04 fica localizada exatamente no fundo do corredor."
        },
        {
            id: "72",
            code: "72",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 06",
            floor: "2º Andar",
            block: "Bloco Maria",
            floorKey: "2",
            inspector: "Inspetora Maria",
            inspectorAvatar: "imagens/avatar_inspetora_maria.png",
            theme: "A Revolução Visual",
            description: "Investigação sobre IA generativa de imagens, engenharia de prompts criativos, debates conceituais sobre arte e pixels, e games comparando fotos reais e geradas por IA.",
            image: "imagens/sala_6.png",
            images: [
                { src: "imagens/sala_6.png", label: "Entrada Sala 06 (Turma 72)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Maria)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "Pesquisadores da IA",
                    theme: "A IA faz arte ou só combina pixels?",
                    members: []
                },
                {
                    number: "02",
                    name: "Os Prompters",
                    theme: "Como gerar imagens com IA?",
                    members: []
                },
                {
                    number: "03",
                    name: "Game Interativo",
                    theme: "Foto real vs Foto de IA",
                    members: []
                }
            ],
            color: "#0d9488",
            route: "Suba ao 2º Andar pelo Bloco Maria. A Sala 06 fica no corredor logo à frente da Sala 07."
        },
        {
            id: "73",
            code: "73",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 07",
            floor: "2º Andar",
            block: "Bloco Maria",
            floorKey: "2",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "IA no Audiovisual",
            description: "Apresentações sobre deepfakes e manipulação de imagem, detecção de vídeos sintéticos, direção de vídeos e animações com IA e o Game 'Tribunal da IA'.",
            image: "imagens/sala_7.png",
            images: [
                { src: "imagens/sala_7.png", label: "Entrada Sala 07 (Turma 73)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Maria)" }
            ],
            groups: [
                {
                    number: "01",
                    name: "Os Teóricos",
                    theme: "As deepfakes e manipulação digital",
                    members: []
                },
                {
                    number: "02",
                    name: "Os Detetives",
                    theme: "Guia prático para detectar mentiras em vídeos de IA",
                    members: []
                },
                {
                    number: "03",
                    name: "Diretores de IA",
                    theme: "Criação de vídeos e animações com IA",
                    members: []
                },
                {
                    number: "04",
                    name: "Game Interativo",
                    theme: "Tribunal da IA: Desvendando um mistério",
                    members: []
                }
            ],
            color: "#0d9488",
            route: "Suba ao 2º Andar pelo Bloco Maria. A Sala 07 fica logo na entrada do corredor, na primeira porta à direita."
        },
        {
            id: "81",
            code: "81",
            grade: "8º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 08",
            floor: "3º Andar",
            block: "Bloco Cláudio",
            floorKey: "3",
            inspector: "Inspetor Cláudio",
            inspectorAvatar: "imagens/avatar_inspetor_claudio.png",
            theme: "Astronomia, Telescópios e a Corrida Espacial",
            description: "Planetário portátil, modelos do sistema solar em escala e simulação de órbitas gravitacionais.",
            image: "imagens/sala_8.png",
            images: [
                { src: "imagens/sala_8.png", label: "Entrada Sala 08 (Turma 81)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Cláudio)" }
            ],
            color: "#d97706",
            route: "Suba até o 3º Andar. A Sala 08 fica logo na entrada do Bloco Cláudio, ao lado do bebedouro."
        },
        {
            id: "82",
            code: "82",
            grade: "8º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 10",
            floor: "3º Andar",
            block: "Bloco Cláudio",
            floorKey: "3",
            inspector: "Inspetor Cláudio",
            inspectorAvatar: "imagens/avatar_inspetor_claudio.png",
            theme: "Inteligência Artificial e Tecnologias do Futuro",
            description: "Demonstrações com visão computacional, reconhecimento de voz e debates éticos sobre IA.",
            image: "imagens/sala_10.png",
            images: [
                { src: "imagens/sala_10.png", label: "Entrada Sala 10 (Turma 82)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Cláudio)" }
            ],
            color: "#d97706",
            route: "Suba até o 3º Andar. Passe a Sala 08 e continue pelo corredor até a Sala 10, à direita."
        },
        {
            id: "8_grp",
            code: "81/82",
            grade: "8º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 09",
            floor: "3º Andar",
            block: "Bloco Cláudio",
            floorKey: "3",
            inspector: "Inspetor Cláudio",
            inspectorAvatar: "imagens/avatar_inspetor_claudio.png",
            theme: "Projetos Integrados 8º Ano (81 & 82)",
            description: "Apresentações e projetos integrados desenvolvidos conjuntamente pelas turmas 81 e 82.",
            image: "imagens/sala_9.png",
            images: [
                { src: "imagens/sala_9.png", label: "Entrada Sala 09 (Turmas 81/82)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Cláudio)" }
            ],
            color: "#d97706",
            route: "Suba até o 3º Andar. A Sala 09 fica entre a Sala 08 e a Sala 10 no Bloco Cláudio."
        },
        {
            id: "91",
            code: "91",
            grade: "9º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 12",
            floor: "4º Andar",
            block: "Bloco Cleydson",
            floorKey: "4",
            inspector: "Inspetor Cleidson",
            inspectorAvatar: "imagens/avatar_inspetor_cleidson.png",
            theme: "Soluções Sustentáveis para Grandes Metrópoles",
            description: "Projetos de arquitetura bioclimática, tratamento de efluentes e mobilidade urbana inteligente.",
            image: "imagens/sala_12.png",
            images: [
                { src: "imagens/sala_12.png", label: "Entrada Sala 12 (Turma 91)" },
                { src: "imagens/corredor_4_andar.png", label: "Corredor 4º Andar (Bloco Cleydson)" }
            ],
            color: "#7c3aed",
            route: "Suba até o 4º Andar (recomenda-se o elevador para acessibilidade). A Sala 12 fica à direita do saguão."
        },
        {
            id: "92",
            code: "92",
            grade: "9º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 11",
            floor: "4º Andar",
            block: "Bloco Cleydson",
            floorKey: "4",
            inspector: "Inspetor Cleidson",
            inspectorAvatar: "imagens/avatar_inspetor_cleidson.png",
            theme: "Mudanças Climáticas e a Acidificação dos Oceanos",
            description: "Simulação de corais marinhos, sensores de qualidade do ar e monitoramento de dióxido de carbono.",
            image: "imagens/sala_11.png",
            images: [
                { src: "imagens/sala_11.png", label: "Entrada Sala 11 (Turma 92)" },
                { src: "imagens/corredor_4_andar.png", label: "Corredor 4º Andar (Bloco Cleydson)" }
            ],
            color: "#7c3aed",
            route: "Suba até o 4º Andar. A Sala 11 fica à esquerda logo após sair das escadas do Bloco Cleydson."
        },
        {
            id: "93",
            code: "93",
            grade: "9º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 14",
            floor: "4º Andar",
            block: "Bloco Cleydson",
            floorKey: "4",
            inspector: "Inspetor Cleidson",
            inspectorAvatar: "imagens/avatar_inspetor_cleidson.png",
            theme: "Engenharia Biomédica e Próteses Biônicas",
            description: "Demonstração de sensores mioelétricos, próteses impressas em 3D e tecnologia em saúde.",
            image: "imagens/sala_14.png",
            images: [
                { src: "imagens/sala_14.png", label: "Entrada Sala 14 (Turma 93)" },
                { src: "imagens/corredor_4_andar.png", label: "Corredor 4º Andar (Bloco Cleydson)" }
            ],
            color: "#7c3aed",
            route: "Suba até o 4º Andar. Siga pelo corredor principal até o fundo; a Sala 14 é a última porta."
        },
        {
            id: "9_grp",
            code: "91/92/93",
            grade: "9º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 13",
            floor: "4º Andar",
            block: "Bloco Cleydson",
            floorKey: "4",
            inspector: "Inspetora Neide",
            inspectorAvatar: "imagens/avatar_inspetora_neide.png",
            theme: "Projetos Integrados 9º Ano (91, 92 & 93)",
            description: "Grandes projetos e apresentações integradas desenvolvidos conjuntamente pelas turmas do 9º Ano.",
            image: "imagens/sala_13.png",
            images: [
                { src: "imagens/sala_13.png", label: "Entrada Sala 13 (Turmas 91/92/93)" },
                { src: "imagens/corredor_4_andar.png", label: "Corredor 4º Andar (Bloco Cleydson)" }
            ],
            color: "#7c3aed",
            route: "Suba até o 4º Andar. A Sala 13 fica localizada próxima à Sala 12 no Bloco Cleydson."
        }
    ],
    specialSpaces: [
        {
            id: "fachada",
            code: "Entrada",
            title: "Entrada & Portaria Principal",
            category: "Ponto de Partida",
            room: "Hall Principal",
            floor: "Térreo",
            block: "Portaria Principal",
            floorKey: "0",
            inspector: "Inspetora Mariana & Recepção",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Credenciamento, Totem de Informações e Acolhimento",
            description: "Ponto de partida do visitante. Aqui você encontra totens interativos de consulta, mapas e orientação geral da Feira das Ciências.",
            image: "imagens/fachada.png",
            images: [
                { src: "imagens/fachada.png", label: "Fachada & Entrada Principal" },
                { src: "imagens/varanda.png", label: "Varanda de Acesso & Jardim" },
                { src: "imagens/terreo.png", label: "Pátio Central & Térreo" }
            ],
            color: "#002b49",
            route: "Você está exatamente aqui no Totem da Entrada! Use a tela touch para navegar por todas as salas."
        },
        {
            id: "patio",
            code: "Pátio",
            title: "Pátio Central & Área de Convivência",
            category: "Espaço Integrador",
            room: "Pátio Térreo",
            floor: "Térreo",
            block: "Área Central",
            floorKey: "0",
            inspector: "Inspetor Araújo & Apoio",
            inspectorAvatar: "imagens/avatar_inspetor_araujo.png",
            theme: "Área de Convivência, Painéis Culturais e Escadaria Motivacional",
            description: "Amplo espaço de convivência estudantil com mesas de estudo, escadaria temática com frases inspiradoras e painéis de Ciência & Inovação.",
            image: "imagens/terreo.png",
            images: [
                { src: "imagens/terreo.png", label: "Pátio Central (Térreo)" },
                { src: "imagens/varanda.png", label: "Varanda Externa" }
            ],
            color: "#0284c7",
            route: "A partir da entrada, siga em frente pelo corredor de acesso principal até o amplo hall do Pátio Central."
        },
        {
            id: "maker",
            code: "SALA Maker",
            title: "SALA Maker EME",
            category: "Espaço Especial",
            room: "Sala Maker",
            floor: "1º Andar",
            block: "Bloco Ozael",
            floorKey: "1",
            inspector: "Inspetor Ozael & Equipe Maker",
            inspectorAvatar: "imagens/avatar_inspetor_ozael.png",
            theme: "APRESENTAÇÃO SURPRESA",
            description: "Apresentação Surpresa interativa e projetos especiais de experimentação no Laboratório Maker.",
            image: "imagens/maker.png",
            images: [
                { src: "imagens/maker.png", label: "Espaço Maker EME" },
                { src: "imagens/corredor_maker.png", label: "Corredor Espaço Maker" },
                { src: "imagens/acesso_maker.png", label: "Hall de Acesso Maker" }
            ],
            color: "#2563eb",
            route: "Suba ao 1º Andar. Siga para a ala direita do Bloco Ozael, logo na entrada identificada como Espaço Maker."
        },
        {
            id: "quadra",
            code: "QUADRA",
            title: "Quadra Poliesportiva",
            category: "Área de Grandes Apresentações",
            room: "Quadra Coberta",
            floor: "Térreo / Área Externa",
            block: "Complexo Esportivo",
            floorKey: "0",
            inspector: "Inspetores Araújo & Karol (Pátio)",
            inspectorAvatar: "imagens/avatar_inspetor_araujo.png",
            theme: "APRESENTAÇÃO SURPRESA",
            description: "Apresentação Surpresa imperdível e grandes demonstrações preparadas no complexo esportivo.",
            image: "imagens/quadra.png",
            images: [
                { src: "imagens/quadra.png", label: "Quadra Poliesportiva" }
            ],
            color: "#059669",
            route: "No piso térreo, siga em direção ao pátio externo dos fundos. A entrada da quadra estará sinalizada à frente."
        }
    ],
    floorsInfo: {
        "0": {
            name: "Térreo & Bloco Anexo",
            sub: "Salas 15, 16, 17 (Turmas 61, 62, 63 com Inspetora Mariana), Pátio & Portaria (Araújo e Karol) e Quadra",
            icon: "fa-school",
            highlights: ["Turma 61 (Sala 15 - Anexo)", "Turma 62 (Sala 16 - Anexo)", "Turma 63 (Sala 17 - Anexo)", "Pátio & Portaria (Araújo e Karol)", "QUADRA (Apresentação Surpresa)"]
        },
        "1": {
            name: "1º Andar – Bloco Ozael",
            sub: "Salas 01, 02, 03, 18, 19 e 20 (7º Ano e 2ª Série EM) & SALA Maker",
            icon: "fa-layer-group",
            highlights: ["SALA Maker (Apresentação Surpresa)", "Salas 01, 02 e 03 (7º Ano)", "Salas 18, 19 e 20 (2ª Série EM)"]
        },
        "2": {
            name: "2º Andar – Bloco Maria",
            sub: "Salas 04, 05, 06 e 07 (7º, 8º Anos e 3ª Série EM)",
            icon: "fa-flask",
            highlights: ["Turma 71 (Sala 04)", "Turma 72 (Sala 06)", "Turma 73 (Sala 07)", "Sala 05 (8º Ano / 3ª Série EM)"]
        },
        "3": {
            name: "3º Andar – Bloco Cláudio",
            sub: "Salas 08, 09 e 10 (9º Ano, 1ª e 3ª Séries EM)",
            icon: "fa-satellite",
            highlights: ["Turma 81 (Sala 08)", "Turmas 81/82 (Sala 09)", "Turma 82 (Sala 10)"]
        },
        "4": {
            name: "4º Andar – Bloco Cleydson",
            sub: "Salas 11, 12, 13 e 14 (9º Ano e 1ª Série EM)",
            icon: "fa-microchip",
            highlights: ["Turma 92 (Sala 11)", "Turma 91 (Sala 12)", "Turmas 91/92/93 (Sala 13)", "Turma 93 (Sala 14)"]
        }
    },
    inspectors: [
        {
            id: "ozael",
            name: "Inspetor Ozael",
            role: "Inspetor do 1º Andar (Bloco Ozael) & Sala Maker",
            avatar: "imagens/avatar_inspetor_ozael.png",
            floor: "1º Andar",
            coverage: "Salas 01, 02, 03, 18, 19, 20 (7º Ano e 2ª Série EM) & Sala Maker",
            bio: "Responsável pelo 1º Andar e pela Sala Maker, acompanha diariamente os estudantes do 7º Ano e da 2ª Série do Ensino Médio, além de incentivar as atividades práticas e projetos inovadores do Espaço Maker.",
            quote: "Incentivar a criatividade, o respeito e o aprendizado prático todos os dias."
        },
        {
            id: "maria",
            name: "Inspetora Maria",
            role: "Inspetora do 2º Andar (Bloco Maria)",
            avatar: "imagens/avatar_inspetora_maria.png",
            floor: "2º Andar",
            coverage: "Salas 04, 05, 06 e 07 (7º, 8º Anos e 3ª Série EM)",
            bio: "Muito querida por toda a comunidade escolar, cuida com dedicação e carinho das salas do 2º Andar, orientando as turmas do 7º e 8º Anos e da 3ª Série do Ensino Médio em um ambiente acolhedor e harmonioso.",
            quote: "Cuidar de cada aluno como parte da nossa grande família EME."
        },
        {
            id: "claudio",
            name: "Inspetor Cláudio",
            role: "Inspetor do 3º Andar (Bloco Cláudio)",
            avatar: "imagens/avatar_inspetor_claudio.png",
            floor: "3º Andar",
            coverage: "Salas 08, 09 e 10 (9º Ano, 1ª e 3ª Séries EM)",
            bio: "Com presença marcante e liderança positiva no 3º Andar, apoia de perto os estudantes do 9º Ano e as turmas de Ensino Médio (1ª e 3ª séries), fortalecendo a disciplina e a união escolar.",
            quote: "Educação, respeito e disciplina caminham juntos na formação do estudante."
        },
        {
            id: "cleidson",
            name: "Inspetor Cleidson",
            role: "Inspetor do 4º Andar (Bloco Cleydson)",
            avatar: "imagens/avatar_inspetor_cleidson.png",
            floor: "4º Andar",
            coverage: "Salas 11, 12, 13 e 14 (9º Ano e 1ª Série EM)",
            bio: "Com diálogo próximo e postura sempre atenciosa no 4º Andar, acompanha diariamente as turmas do 9º Ano e da 1ª Série do Ensino Médio, auxiliando em todas as necessidades pedagógicas e de convivência.",
            quote: "Apoiar nossos jovens rumo ao futuro com responsabilidade e amizade."
        },
        {
            id: "neide",
            name: "Inspetora Neide",
            role: "Inspetora do 4º Andar (Bloco Cleydson / 9º Anos)",
            avatar: "imagens/avatar_inspetora_neide.png",
            floor: "4º Andar",
            coverage: "Salas 11, 12, 13 e 14 (Turmas Integradas e 9º Ano)",
            bio: "Atua no 4º Andar com carinho, atenção aos detalhes e dedicação constante, garantindo suporte, disciplina e acolhimento para as turmas e professores.",
            quote: "Zelo e dedicação para que cada jovem alcance o seu melhor potencial."
        },
        {
            id: "mariana",
            name: "Inspetora Mariana",
            role: "Inspetora do Bloco Anexo (Térreo)",
            avatar: "imagens/avatar_inspetora_mariana.png",
            floor: "Térreo (Anexo)",
            coverage: "Salas 15, 16 e 17 (Turmas dos 6º Anos: 61, 62 e 63)",
            bio: "Responsável pelo Bloco Anexo no piso térreo, acolhe e orienta diariamente os estudantes dos 6º Anos (Turmas 61, 62 e 63) nas salas 15, 16 e 17 com enorme carinho, paciência e atenção.",
            quote: "Receber com um sorriso e fazer cada aluno se sentir seguro e acolhido."
        },
        {
            id: "araujo",
            name: "Inspetor Araújo",
            role: "Inspetor de Pátio, Entrada & Saída",
            avatar: "imagens/avatar_inspetor_araujo.png",
            floor: "Térreo / Pátio",
            coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
            bio: "Atua no pátio central e na portaria do colégio, cuidando da segurança, da organização no fluxo de entrada e saída e do convívio saudável de todos os estudantes nos intervalos e eventos.",
            quote: "Apoio constante para garantir a segurança e o bem-estar de toda a escola."
        },
        {
            id: "karol",
            name: "Inspetora Karol",
            role: "Inspetora de Pátio, Entrada & Saída",
            avatar: "imagens/avatar_inspetora_karol.png",
            floor: "Térreo / Pátio",
            coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
            bio: "Atua na inspetoria de pátio ao lado do Inspetor Araújo, garantindo a recepção calorosa e segura de alunos e responsáveis, além do acompanhamento diário no pátio e na entrada e saída.",
            quote: "Cuidado, atenção e acolhimento em cada momento da rotina escolar."
        }
    ]
};

// Estado da Aplicação
const AppState = {
    activeGradeFilter: "all",
    activeFloorFilter: "all",
    searchQuery: "",
    isKeyboardOpen: false,
    selectedItem: null,
    highContrast: false,
    fontSizeLevel: 1, // 0: normal, 1: grande, 2: extra grande
    idleTimer: null,
    idleCountdown: null
};

// Efeitos sonoros sutis usando Web Audio API (Touch Feedback)
class SoundFX {
    static init() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        } catch (e) {
            console.warn("Web Audio não suportado", e);
        }
    }

    static playTap() {
        if (!this.ctx) return;
        if (this.ctx.state === "suspended") {
            this.ctx.resume();
        }
        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(480, this.ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.05);

            gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + 0.05);
        } catch (e) {}
    }

    static playOpen() {
        if (!this.ctx) return;
        if (this.ctx.state === "suspended") {
            this.ctx.resume();
        }
        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "triangle";
            osc.frequency.setValueAtTime(320, this.ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(640, this.ctx.currentTime + 0.1);

            gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.12);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + 0.12);
        } catch (e) {}
    }
}

// Inicialização Geral
document.addEventListener("DOMContentLoaded", () => {
    SoundFX.init();
    updateClock();
    setInterval(updateClock, 1000);

    renderGradeFilters();
    renderFloorNavigator();
    renderCards();
    setupEventListeners();
    setupIdleManager();
    setupKeyboard();
});

// Relógio em Tempo Real
function updateClock() {
    const clockEl = document.getElementById("totem-clock");
    const dateEl = document.getElementById("totem-date");
    if (!clockEl || !dateEl) return;

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    clockEl.textContent = `${hours}:${minutes}:${seconds}`;

    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const dateFormatted = now.toLocaleDateString('pt-BR', options);
    dateEl.textContent = dateFormatted.charAt(0).toUpperCase() + dateFormatted.slice(1);
}

// Renderizar Abas de Filtros de Turmas
function renderGradeFilters() {
    const container = document.getElementById("grade-filters");
    if (!container) return;

    const filters = [
        { id: "all", label: "🌟 Todas as Turmas", badge: "61 ao 93" },
        { id: "6", label: "6º Ano", badge: "61, 62, 63" },
        { id: "7", label: "7º Ano", badge: "71, 72, 73" },
        { id: "8", label: "8º Ano", badge: "81, 82" },
        { id: "9", label: "9º Ano", badge: "91, 92, 93" },
        { id: "special", label: "✨ Espaços Especiais", badge: "Maker, Quadra" }
    ];

    container.innerHTML = filters.map(f => `
        <button class="filter-tab-btn ${AppState.activeGradeFilter === f.id ? 'active' : ''}" data-filter="${f.id}">
            <span class="tab-title">${f.label}</span>
            <span class="tab-badge">${f.badge}</span>
        </button>
    `).join("");

    container.querySelectorAll(".filter-tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            SoundFX.playTap();
            AppState.activeGradeFilter = btn.getAttribute("data-filter");
            document.querySelectorAll(".filter-tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            resetIdleTimer();
            renderCards();
        });
    });
}

// Renderizar Navegador Interativo por Andares
function renderFloorNavigator() {
    const container = document.getElementById("floors-nav-container");
    if (!container) return;

    const floors = [
        { key: "all", name: "Todos os Andares", icon: "🏢" },
        { key: "0", name: "Térreo & Anexo (Mariana, Araújo, Karol)", icon: "🌳" },
        { key: "1", name: "1º Andar (Ozael & Maker)", icon: "1️⃣" },
        { key: "2", name: "2º Andar (Maria)", icon: "2️⃣" },
        { key: "3", name: "3º Andar (Cláudio)", icon: "3️⃣" },
        { key: "4", name: "4º Andar (Cleydson)", icon: "4️⃣" }
    ];

    container.innerHTML = floors.map(floor => `
        <button class="floor-pill-btn ${AppState.activeFloorFilter === floor.key ? 'active' : ''}" data-floor="${floor.key}">
            <span class="floor-icon">${floor.icon}</span>
            <span class="floor-name">${floor.name}</span>
        </button>
    `).join("");

    container.querySelectorAll(".floor-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            SoundFX.playTap();
            AppState.activeFloorFilter = btn.getAttribute("data-floor");
            document.querySelectorAll(".floor-pill-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            resetIdleTimer();
            renderCards();
        });
    });
}

// Renderizar Cards de Turmas e Espaços
function renderCards() {
    const grid = document.getElementById("cards-grid");
    const countBadge = document.getElementById("results-count");
    if (!grid) return;

    let items = [];
    if (AppState.activeGradeFilter === "special") {
        items = [...TOTEM_DATA.specialSpaces];
    } else {
        items = [...TOTEM_DATA.classes];
        if (AppState.activeGradeFilter === "all") {
            items = [...TOTEM_DATA.classes, ...TOTEM_DATA.specialSpaces];
        }
    }

    if (AppState.activeGradeFilter !== "all" && AppState.activeGradeFilter !== "special") {
        items = items.filter(item => item.grade && item.grade.startsWith(AppState.activeGradeFilter));
    }

    if (AppState.activeFloorFilter !== "all") {
        items = items.filter(item => item.floorKey === AppState.activeFloorFilter);
    }

    if (AppState.searchQuery.trim() !== "") {
        const query = AppState.searchQuery.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        items = items.filter(item => {
            const groupsText = item.groups 
                ? item.groups.map(g => `${g.number || ''} ${g.name || ''} ${g.theme || ''} ${(g.members || []).join(' ')}`).join(' ')
                : '';

            const searchableText = [
                item.code || "",
                item.title || "",
                item.grade || "",
                item.room || "",
                item.floor || "",
                item.block || "",
                item.inspector || "",
                item.theme || "",
                item.description || "",
                groupsText
            ].join(" ").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

            return searchableText.includes(query);
        });
    }

    if (countBadge) {
        countBadge.textContent = `${items.length} ${items.length === 1 ? 'local encontrado' : 'locais encontrados'}`;
    }

    if (items.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>Nenhuma turma ou espaço encontrado</h3>
                <p>Tente buscar por <strong>61</strong>, <strong>Robótica</strong>, <strong>Isabela</strong>, <strong>Drones</strong> ou selecione outra categoria acima.</p>
                <button class="btn-clear-search-pill" id="btn-reset-filters">Limpar filtros de busca</button>
            </div>
        `;
        document.getElementById("btn-reset-filters")?.addEventListener("click", () => {
            clearSearch();
        });
        return;
    }

    grid.innerHTML = items.map(item => {
        const isSpecial = !item.grade;
        const mainBadge = isSpecial ? (item.category || "Especial") : item.grade;
        const codeDisplay = item.code || item.id;
        const roomDisplay = item.room || "Sala Principal";
        const hasGroups = item.groups && item.groups.length > 0;

        return `
            <article class="totem-card ${isSpecial ? 'special-card' : ''}" data-id="${item.id}" tabindex="0" role="button" aria-label="Abrir detalhes da turma ${codeDisplay}">
                <div class="card-header">
                    <div class="card-code-badge" style="background-color: ${item.color || '#002b49'};">
                        <span class="badge-prefix">${isSpecial ? '⭐' : 'TURMA'}</span>
                        <span class="code-number">${codeDisplay}</span>
                    </div>
                    <div class="card-tags">
                        <span class="tag-grade">${mainBadge}</span>
                        <span class="tag-floor"><i class="fa-solid fa-location-dot"></i> ${item.floor}</span>
                    </div>
                </div>

                <div class="card-body">
                    <div class="card-room-info">
                        <span class="room-pill">${roomDisplay}</span>
                        <span class="block-text">${item.block || ''}</span>
                        ${hasGroups ? `<span class="groups-count-pill"><i class="fa-solid fa-users"></i> ${item.groups.length} Grupos</span>` : ''}
                    </div>
                    
                    <h3 class="card-theme-title">${item.theme || item.title}</h3>
                    
                    <p class="card-desc-preview">${item.description || ''}</p>
                </div>

                <div class="card-footer">
                    <div class="card-inspector">
                        <img src="${item.inspectorAvatar || 'imagens/avatar_inspetor_ozael.png'}" class="card-inspector-avatar" alt="${item.inspector || 'Inspetor'}" onerror="this.src='imagens/avatar_inspetor_ozael.png'">
                        <span>${item.inspector || 'Equipe EME'}</span>
                    </div>
                    <div class="card-action-cue">
                        <span>Ver Como Chegar</span>
                        <i class="fa-solid fa-arrow-right"></i>
                    </div>
                </div>
            </article>
        `;
    }).join("");

    grid.querySelectorAll(".totem-card").forEach(card => {
        card.addEventListener("click", () => {
            SoundFX.playOpen();
            const id = card.getAttribute("data-id");
            openDetailModal(id);
        });

        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                card.click();
            }
        });
    });
}

// Abrir Modal de Detalhes da Turma / Espaço
function openDetailModal(itemId) {
    resetIdleTimer();
    const item = [...TOTEM_DATA.classes, ...TOTEM_DATA.specialSpaces].find(i => i.id === itemId);
    if (!item) return;

    AppState.selectedItem = item;
    const modal = document.getElementById("detail-modal");
    if (!modal) return;

    const modalGrade = document.getElementById("modal-grade");
    const modalCode = document.getElementById("modal-code");
    const modalRoom = document.getElementById("modal-room");
    const modalFloor = document.getElementById("modal-floor");
    const modalBlock = document.getElementById("modal-block");
    const modalInspector = document.getElementById("modal-inspector");
    const modalInspectorAvatar = document.getElementById("modal-inspector-avatar");
    const modalTheme = document.getElementById("modal-theme");
    const modalDesc = document.getElementById("modal-desc");
    const modalRoute = document.getElementById("modal-route");
    const modalImageContainer = document.getElementById("modal-image-container");
    const modalGroupsWrapper = document.getElementById("modal-groups-wrapper");

    if (modalGrade) modalGrade.textContent = item.grade ? `${item.grade} • ${item.segment}` : (item.category || "Espaço EME");
    if (modalCode) modalCode.textContent = item.code || item.id;
    if (modalRoom) modalRoom.textContent = item.room;
    if (modalFloor) modalFloor.textContent = item.floor;
    if (modalBlock) modalBlock.textContent = item.block;
    if (modalInspector) modalInspector.textContent = item.inspector;
    if (modalInspectorAvatar) {
        modalInspectorAvatar.src = item.inspectorAvatar || "imagens/avatar_inspetor_ozael.png";
        modalInspectorAvatar.alt = item.inspector || "Avatar Inspetor";
    }
    if (modalTheme) modalTheme.textContent = item.theme || item.title;
    if (modalDesc) modalDesc.textContent = item.description;
    if (modalRoute) modalRoute.textContent = item.route;

    // Renderizar Seção de Grupos da Turma
    if (modalGroupsWrapper) {
        if (item.groups && item.groups.length > 0) {
            modalGroupsWrapper.style.display = "block";
            modalGroupsWrapper.innerHTML = `
                <div class="groups-card-container">
                    <div class="groups-card-header">
                        <h4><i class="fa-solid fa-users-viewfinder"></i> Grupos &amp; Temas de Apresentação (${item.groups.length})</h4>
                    </div>
                    <div class="groups-list-grid">
                        ${item.groups.map(g => `
                            <div class="group-presentation-item">
                                <div class="group-header-row">
                                    <span class="group-number-pill">${g.name}</span>
                                    <span class="group-theme-text">${g.theme}</span>
                                </div>
                                ${(g.members && g.members.length > 0) ? `
                                    <div class="group-members-list">
                                        <span class="members-label"><i class="fa-solid fa-user-graduate"></i> Integrantes:</span>
                                        <div class="members-chips-wrap">
                                            ${g.members.map(m => `
                                                <span class="member-chip">
                                                    <i class="fa-solid fa-circle-user"></i> ${m}
                                                </span>
                                            `).join("")}
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        `).join("")}
                    </div>
                </div>
            `;
        } else {
            modalGroupsWrapper.style.display = "none";
            modalGroupsWrapper.innerHTML = "";
        }
    }

    if (modalImageContainer) {
        const imagesList = item.images && item.images.length > 0 
            ? item.images 
            : [{ src: item.image || "imagens/fachada.png", label: item.room || "Ambiente" }];

        const firstImg = imagesList[0];

        modalImageContainer.innerHTML = `
            <div class="modal-gallery-card">
                <div class="modal-photo-wrapper">
                    <img id="modal-active-img" src="${firstImg.src}" alt="${item.theme || item.title}" class="modal-real-photo" onerror="this.src='imagens/fachada.png'">
                    <div class="photo-overlay-tag" id="modal-photo-caption">
                        <i class="fa-solid fa-camera"></i> ${firstImg.label}
                    </div>
                </div>

                ${imagesList.length > 1 ? `
                    <div class="gallery-selector-tabs">
                        <span class="gallery-tabs-label"><i class="fa-solid fa-images"></i> Visualizar Fotos do Ambiente:</span>
                        <div class="gallery-tabs-buttons">
                            ${imagesList.map((img, idx) => `
                                <button class="gallery-tab-btn ${idx === 0 ? 'active' : ''}" data-src="${img.src}" data-label="${img.label}">
                                    <i class="fa-solid fa-image"></i> ${img.label}
                                </button>
                            `).join("")}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        // Ativar troca de fotos na galeria
        modalImageContainer.querySelectorAll(".gallery-tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                SoundFX.playTap();
                const src = btn.getAttribute("data-src");
                const label = btn.getAttribute("data-label");
                
                const activeImg = document.getElementById("modal-active-img");
                const caption = document.getElementById("modal-photo-caption");
                
                if (activeImg) {
                    activeImg.style.opacity = "0.3";
                    activeImg.src = src;
                    activeImg.onload = () => {
                        activeImg.style.opacity = "1";
                    };
                }
                if (caption) {
                    caption.innerHTML = `<i class="fa-solid fa-camera"></i> ${label}`;
                }

                modalImageContainer.querySelectorAll(".gallery-tab-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                resetIdleTimer();
            });
        });
    }

    updateMiniFloorMap(item);

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
}

// Fechar Modal
function closeDetailModal() {
    SoundFX.playTap();
    const modal = document.getElementById("detail-modal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
    AppState.selectedItem = null;
}

// Renderizar Grade de Inspetores na Tela Dedicada
function renderInspectorsGrid() {
    const container = document.getElementById("inspectors-list-grid");
    if (!container) return;

    const inspectors = TOTEM_DATA.inspectors || [];
    container.innerHTML = inspectors.map(insp => `
        <article class="inspector-profile-card">
            <div class="inspector-card-top">
                <div class="inspector-avatar-frame">
                    <img src="${insp.avatar}" alt="${insp.name}" class="inspector-avatar-img" onerror="this.src='imagens/avatar_inspetor_ozael.png'">
                </div>
                <div class="inspector-header-info">
                    <h3 class="inspector-profile-name">${insp.name}</h3>
                    <span class="inspector-profile-role">${insp.role}</span>
                    <span class="inspector-coverage-pill"><i class="fa-solid fa-location-dot"></i> ${insp.coverage}</span>
                </div>
            </div>

            <div class="inspector-bio-box">
                <p>${insp.bio}</p>
            </div>

            <div class="inspector-quote-box">
                <i class="fa-solid fa-quote-left"></i>
                <span>"${insp.quote}"</span>
            </div>
        </article>
    `).join("");
}

// Abrir Modal / Tela de Inspetores
function openInspectorsModal() {
    resetIdleTimer();
    SoundFX.playOpen();
    const modal = document.getElementById("inspectors-modal");
    if (!modal) return;

    renderInspectorsGrid();
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
}

// Fechar Modal de Inspetores
function closeInspectorsModal() {
    SoundFX.playTap();
    const modal = document.getElementById("inspectors-modal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

// Atualizar Mini Mapa Esquemático do Andar
function updateMiniFloorMap(item) {
    const mapContainer = document.getElementById("modal-floor-map");
    if (!mapContainer) return;

    const floorInfo = TOTEM_DATA.floorsInfo[item.floorKey] || TOTEM_DATA.floorsInfo["0"];
    
    mapContainer.innerHTML = `
        <div class="floor-schematic-card">
            <div class="schematic-header">
                <div class="schematic-badge"><i class="fa-solid fa-map-location-dot"></i> Mapa do Andar</div>
                <h4>${floorInfo.name}</h4>
                <p class="schematic-sub">${floorInfo.sub}</p>
            </div>
            
            <div class="floor-rooms-schematic">
                ${floorInfo.highlights.map(h => {
                    const isCurrent = h.includes(item.room) || h.includes(item.code);
                    return `
                        <div class="schematic-room-box ${isCurrent ? 'highlight-target' : ''}">
                            <span class="room-indicator ${isCurrent ? 'active-dot' : ''}"></span>
                            <span class="room-name-label">${h}</span>
                            ${isCurrent ? '<span class="you-are-here-tag">📍 DESTINO SELECIONADO</span>' : ''}
                        </div>
                    `;
                }).join("")}
            </div>

            <div class="navigation-banner">
                <div class="banner-icon">🚶‍♂️</div>
                <div class="banner-text">
                    <strong>Como Chegar a partir do Totem:</strong>
                    <span>${item.route}</span>
                </div>
            </div>
        </div>
    `;
}

// Configurar Event Listeners Globais
function setupEventListeners() {
    const searchInput = document.getElementById("search-input");
    const clearBtn = document.getElementById("btn-clear-search");
    const toggleKeypadBtn = document.getElementById("btn-toggle-keypad");



    document.getElementById("btn-close-inspectors-modal")?.addEventListener("click", () => {
        closeInspectorsModal();
    });

    document.getElementById("inspectors-modal-backdrop")?.addEventListener("click", () => {
        closeInspectorsModal();
    });

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            AppState.searchQuery = e.target.value;
            if (clearBtn) {
                clearBtn.style.display = AppState.searchQuery ? "flex" : "none";
            }
            resetIdleTimer();
            renderCards();
        });

        searchInput.addEventListener("focus", () => {
            resetIdleTimer();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            SoundFX.playTap();
            clearSearch();
        });
    }

    if (toggleKeypadBtn) {
        toggleKeypadBtn.addEventListener("click", () => {
            SoundFX.playTap();
            toggleOnScreenKeyboard();
        });
    }

    document.getElementById("modal-close-btn")?.addEventListener("click", closeDetailModal);
    document.getElementById("modal-backdrop")?.addEventListener("click", closeDetailModal);

    // Tecla ESC para fechar modais
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeDetailModal();
            closeInspectorsModal();
            toggleOnScreenKeyboard(false);
        }
    });

    document.getElementById("btn-home-totem")?.addEventListener("click", () => {
        SoundFX.playTap();
        resetTotemToHome();
    });

    ["click", "touchstart", "mousemove", "keydown"].forEach(evt => {
        document.addEventListener(evt, () => {
            resetIdleTimer();
        }, { passive: true });
    });
}

function clearSearch() {
    const searchInput = document.getElementById("search-input");
    const clearBtn = document.getElementById("btn-clear-search");
    AppState.searchQuery = "";
    if (searchInput) searchInput.value = "";
    if (clearBtn) clearBtn.style.display = "none";
    renderCards();
}

function setupKeyboard() {
    const keyboardContainer = document.getElementById("touch-keyboard");
    if (!keyboardContainer) return;

    const keysLayout = [
        ["61", "62", "63", "71", "72", "73", "81", "82", "91", "92", "93"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M", "MAKER", "QUADRA"],
        ["ESPAÇO", "APAGAR", "LIMPAR", "FECHAR"]
    ];

    keyboardContainer.innerHTML = `
        <div class="virtual-keypad-inner">
            <div class="keypad-top-bar">
                <span class="keypad-title"><i class="fa-solid fa-keyboard"></i> Teclado na Tela do Totem</span>
                <span class="keypad-hint">Toque nas turmas ou digite o tema</span>
                <button class="keypad-close-x" id="keypad-close-x"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="keypad-rows">
                ${keysLayout.map((row, rIdx) => `
                    <div class="keypad-row row-${rIdx}">
                        ${row.map(k => {
                            let extraClass = "";
                            let label = k;
                            if (["61","62","63","71","72","73","81","82","91","92","93"].includes(k)) {
                                extraClass = "key-turma";
                            } else if (k === "ESPAÇO") {
                                extraClass = "key-space";
                            } else if (k === "APAGAR") {
                                extraClass = "key-backspace";
                                label = "⌫ Apagar";
                            } else if (k === "LIMPAR") {
                                extraClass = "key-clear";
                                label = "🗑 Limpar";
                            } else if (k === "FECHAR") {
                                extraClass = "key-close";
                                label = "✕ Fechar";
                            } else if (k === "MAKER" || k === "QUADRA") {
                                extraClass = "key-quick-place";
                            }
                            return `<button class="v-key ${extraClass}" data-key="${k}">${label}</button>`;
                        }).join("")}
                    </div>
                `).join("")}
            </div>
        </div>
    `;

    keyboardContainer.querySelectorAll(".v-key").forEach(keyBtn => {
        keyBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            SoundFX.playTap();
            const key = keyBtn.getAttribute("data-key");
            handleVirtualKeyPress(key);
        });
    });

    document.getElementById("keypad-close-x")?.addEventListener("click", (e) => {
        e.stopPropagation();
        SoundFX.playTap();
        toggleOnScreenKeyboard(false);
    });
}

function toggleOnScreenKeyboard(forceState) {
    const keyboardContainer = document.getElementById("touch-keyboard");
    const toggleBtn = document.getElementById("btn-toggle-keypad");
    if (!keyboardContainer) return;

    AppState.isKeyboardOpen = (typeof forceState === "boolean") ? forceState : !AppState.isKeyboardOpen;
    keyboardContainer.classList.toggle("open", AppState.isKeyboardOpen);
    if (toggleBtn) {
        toggleBtn.classList.toggle("active", AppState.isKeyboardOpen);
    }
}

function handleVirtualKeyPress(key) {
    const searchInput = document.getElementById("search-input");
    if (!searchInput) return;

    if (key === "FECHAR") {
        toggleOnScreenKeyboard(false);
        return;
    }

    if (key === "LIMPAR") {
        clearSearch();
        return;
    }

    if (key === "APAGAR") {
        AppState.searchQuery = AppState.searchQuery.slice(0, -1);
    } else if (key === "ESPAÇO") {
        AppState.searchQuery += " ";
    } else if (["61","62","63","71","72","73","81","82","91","92","93"].includes(key)) {
        AppState.searchQuery = key;
    } else if (key === "MAKER") {
        AppState.searchQuery = "Maker";
    } else if (key === "QUADRA") {
        AppState.searchQuery = "Quadra";
    } else {
        AppState.searchQuery += key;
    }

    searchInput.value = AppState.searchQuery;
    const clearBtn = document.getElementById("btn-clear-search");
    if (clearBtn) clearBtn.style.display = AppState.searchQuery ? "flex" : "none";

    resetIdleTimer();
    renderCards();
}

function setupIdleManager() {
    resetIdleTimer();
}

function resetIdleTimer() {
    clearInterval(AppState.idleCountdown);
    clearTimeout(AppState.idleTimer);
    hideIdleOverlay();

    // 45 segundos de inatividade aciona a contagem de 10 segundos
    AppState.idleTimer = setTimeout(() => {
        startIdleCountdown(10);
    }, 45000);
}

function startIdleCountdown(seconds) {
    let remaining = seconds;
    showIdleOverlay(remaining);

    AppState.idleCountdown = setInterval(() => {
        remaining -= 1;
        updateIdleOverlayCount(remaining);

        if (remaining <= 0) {
            clearInterval(AppState.idleCountdown);
            resetTotemToHome();
        }
    }, 1000);
}

function showIdleOverlay(count) {
    let overlay = document.getElementById("idle-reset-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "idle-reset-overlay";
        overlay.className = "idle-reset-overlay";
        document.body.appendChild(overlay);
    }

    overlay.innerHTML = `
        <div class="idle-modal-box">
            <div class="idle-icon-animated">⏳</div>
            <h3>Ainda está aí?</h3>
            <p>Por inatividade, o totem retornará à tela inicial em:</p>
            <div class="idle-seconds" id="idle-seconds-num">${count}</div>
            <p class="idle-sub">Toque em qualquer lugar da tela para continuar navegando.</p>
            <button class="btn-keep-browsing" id="btn-keep-browsing">Continuar Navegando</button>
        </div>
    `;

    overlay.classList.add("visible");
    document.getElementById("btn-keep-browsing")?.addEventListener("click", () => {
        SoundFX.playTap();
        resetIdleTimer();
    });
}

function updateIdleOverlayCount(count) {
    const el = document.getElementById("idle-seconds-num");
    if (el) el.textContent = count;
}

function hideIdleOverlay() {
    const overlay = document.getElementById("idle-reset-overlay");
    if (overlay) {
        overlay.classList.remove("visible");
    }
}

function resetTotemToHome() {
    closeDetailModal();
    closeInspectorsModal();
    toggleOnScreenKeyboard(false);
    clearSearch();
    AppState.activeGradeFilter = "all";
    AppState.activeFloorFilter = "all";

    renderGradeFilters();
    renderFloorNavigator();
    renderCards();
    hideIdleOverlay();

    window.scrollTo({ top: 0, behavior: 'smooth' });
}
