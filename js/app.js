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
            room: "Sala 01",
            floor: "1º Andar",
            block: "1º Andar",
            floorKey: "1",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Estudos Atmosféricos, Meteorologia e Sustentabilidade",
            description: "Projetos investigativos sobre uso de drones no monitoramento atmosférico, meteorologia e chuvas, desmatamento ilegal e poluição urbana.",
            image: "imagens/sala_1.png",
            images: [
                { src: "imagens/sala_1.png", label: "Entrada Sala 01 (Turma 61)" },
                { src: "imagens/corredor_1_andar.png", label: "Corredor 1º Andar" }
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
            route: "Suba até o 1º Andar. A Turma 61 está localizada na Sala 01."
        },
        {
            id: "62",
            code: "62",
            grade: "6º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 02",
            floor: "1º Andar",
            block: "1º Andar",
            floorKey: "1",
            inspector: "Inspetora Mariana",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Sustentabilidade, Energia Renovável, Efeito Estufa e Clima",
            description: "Projetos investigativos sobre os 5R's da sustentabilidade, efeito estufa e aquecimento global, o ciclo hidrológico, energia renovável e clima, e riscos climáticos urbanos.",
            image: "imagens/sala_2.png",
            images: [
                { src: "imagens/sala_2.png", label: "Entrada Sala 02 (Turma 62)" },
                { src: "imagens/corredor_1_andar.png", label: "Corredor 1º Andar" }
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
            route: "Suba até o 1º Andar. A Turma 62 fica localizada na Sala 02, ao lado da Sala 01."
        },
        {
            id: "63",
            code: "63",
            grade: "6º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 05",
            floor: "2º Andar",
            block: "2º Andar",
            floorKey: "2",
            inspector: "Inspetora Mariana & Inspetor Ozael",
            inspectorAvatar: "imagens/avatar_inspetora_mariana.png",
            theme: "Conforto Térmico, Clima, Transição Energética e Adaptação",
            description: "Projetos investigativos sobre conforto térmico urbano, fenômenos climáticos extremos, estudos climáticos por desenhos, transição energética e estratégias de adaptação.",
            image: "imagens/sala_5.png",
            images: [
                { src: "imagens/sala_5.png", label: "Entrada Sala 05 (Turma 63)" },
                { src: "imagens/corredor_2_andar.png", label: "Corredor 2º Andar" }
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
            route: "Suba até o 2º Andar. A Turma 63 fica localizada na Sala 05."
        },
        {
            id: "71",
            code: "71",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 04",
            floor: "2º Andar",
            block: "Bloco Ozael",
            floorKey: "2",
            inspector: "Inspetor Ozael",
            inspectorAvatar: "imagens/avatar_inspetor_ozael.png",
            theme: "A Nova Era Sonora",
            description: "Exploração da Inteligência Artificial aplicada ao áudio e à música: sensibilidade musical artificial, composição generativa de canções e testes auditivos de identificação de autoria.",
            image: "imagens/sala_4.png",
            images: [
                { src: "imagens/sala_4.png", label: "Entrada Sala 04 (Turma 71)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Ozael)" }
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
            route: "Suba até o 2º Andar. Caminhe pelo corredor do 2º Andar; a Sala 04 fica localizada no corredor das turmas do 7º Ano."
        },
        {
            id: "72",
            code: "72",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 06",
            floor: "2º Andar",
            block: "Bloco Ozael",
            floorKey: "2",
            inspector: "Inspetor Ozael",
            inspectorAvatar: "imagens/avatar_inspetor_ozael.png",
            theme: "A Revolução Visual",
            description: "Investigação sobre IA generativa de imagens, engenharia de prompts criativos, debates conceituais sobre arte e pixels, e games comparando fotos reais e geradas por IA.",
            image: "imagens/sala_6.png",
            images: [
                { src: "imagens/sala_6.png", label: "Entrada Sala 06 (Turma 72)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Ozael)" }
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
            route: "Suba ao 2º Andar. A Sala 06 fica no corredor do 2º Andar, próxima à Sala 07."
        },
        {
            id: "73",
            code: "73",
            grade: "7º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 07",
            floor: "2º Andar",
            block: "Bloco Ozael",
            floorKey: "2",
            inspector: "Inspetor Ozael",
            inspectorAvatar: "imagens/avatar_inspetor_ozael.png",
            theme: "IA no Audiovisual",
            description: "Apresentações sobre deepfakes e manipulação de imagem, detecção de vídeos sintéticos, direção de vídeos e animações com IA e o Game 'Tribunal da IA'.",
            image: "imagens/sala_7.png",
            images: [
                { src: "imagens/sala_7.png", label: "Entrada Sala 07 (Turma 73)" },
                { src: "imagens/corredor_2_andar.png?v=2", label: "Corredor 2º Andar (Bloco Ozael)" }
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
            route: "Suba ao 2º Andar. A Sala 07 fica logo na entrada do corredor do 2º Andar."
        },
        {
            id: "81",
            code: "81",
            grade: "8º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 08",
            floor: "3º Andar",
            block: "Bloco Maria",
            floorKey: "3",
            inspector: "Inspetora Maria",
            inspectorAvatar: "imagens/avatar_inspetora_maria.png",
            theme: "Astronomia, Telescópios e a Corrida Espacial",
            description: "Planetário portátil, modelos do sistema solar em escala e simulação de órbitas gravitacionais.",
            image: "imagens/sala_8.png",
            images: [
                { src: "imagens/sala_8.png", label: "Entrada Sala 08 (Turma 81)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Maria)" }
            ],
            color: "#d97706",
            route: "Suba até o 3º Andar. A Sala 08 fica logo na entrada do 3º Andar, ao lado do bebedouro."
        },
        {
            id: "82",
            code: "82",
            grade: "8º Ano",
            segment: "Ensino Fundamental II",
            room: "Sala 10",
            floor: "3º Andar",
            block: "Bloco Maria",
            floorKey: "3",
            inspector: "Inspetora Maria",
            inspectorAvatar: "imagens/avatar_inspetora_maria.png",
            theme: "Inteligência Artificial e Tecnologias do Futuro",
            description: "Demonstrações com visão computacional, reconhecimento de voz e debates éticos sobre IA.",
            image: "imagens/sala_10.png",
            images: [
                { src: "imagens/sala_10.png", label: "Entrada Sala 10 (Turma 82)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Maria)" }
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
            block: "Bloco Maria",
            floorKey: "3",
            inspector: "Inspetora Maria",
            inspectorAvatar: "imagens/avatar_inspetora_maria.png",
            theme: "Projetos Integrados 8º Ano (81 & 82)",
            description: "Apresentações e projetos integrados desenvolvidos conjuntamente pelas turmas 81 e 82.",
            image: "imagens/sala_9.png",
            images: [
                { src: "imagens/sala_9.png", label: "Entrada Sala 09 (Turmas 81/82)" },
                { src: "imagens/corredor_3_andar.png", label: "Corredor 3º Andar (Bloco Maria)" }
            ],
            color: "#d97706",
            route: "Suba até o 3º Andar. A Sala 09 fica entre a Sala 08 e a Sala 10 no 3º Andar."
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
            inspector: "Inspetor Cleidson",
            inspectorAvatar: "imagens/avatar_inspetor_cleidson.png",
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
            inspector: "Inspetores Araújo & Carol",
            inspectorAvatar: "imagens/avatar_inspetor_araujo.png",
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
            inspector: "Inspetores Araújo & Carol",
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
            id: "oficina_ia",
            code: "Oficina IA",
            title: "Oficina de Inteligência Artificial",
            category: "Espaço Especial & Demonstrações",
            room: "Sala 03",
            floor: "1º Andar",
            block: "1º Andar",
            floorKey: "1",
            inspector: "Inspetora Josielma",
            inspectorAvatar: "imagens/avatar_inspetora_josielma.png",
            theme: "Oficina Prática de Inteligência Artificial",
            description: "Espaço dedicado a demonstrações interativas, oficinas práticas e experimentação com ferramentas de Inteligência Artificial para todos os visitantes da Feira.",
            image: "imagens/sala_4.png",
            images: [
                { src: "imagens/sala_4.png", label: "Entrada Sala 03 (Oficina de IA)" },
                { src: "imagens/corredor_1_andar.png", label: "Corredor 1º Andar" }
            ],
            color: "#2563eb",
            route: "Suba ao 1º Andar. A Sala 03 (Oficina de IA) fica localizada no corredor do 1º Andar, ao lado da Sala 02."
        },
        {
            id: "maker",
            code: "SALA Maker",
            title: "SALA Maker EME",
            category: "Espaço Especial",
            room: "Sala Maker",
            floor: "1º Andar",
            block: "1º Andar",
            floorKey: "1",
            inspector: "Inspetora Josielma & Equipe Maker",
            inspectorAvatar: "imagens/avatar_inspetora_josielma.png",
            theme: "APRESENTAÇÃO SURPRESA",
            description: "Apresentação Surpresa interativa e projetos especiais de experimentação no Laboratório Maker.",
            image: "imagens/maker.png",
            images: [
                { src: "imagens/maker.png", label: "Espaço Maker EME" },
                { src: "imagens/corredor_maker.png", label: "Corredor Espaço Maker" },
                { src: "imagens/acesso_maker.png", label: "Hall de Acesso Maker" }
            ],
            color: "#2563eb",
            route: "Suba ao 1º Andar. Siga para a ala direita do 1º Andar, logo na entrada identificada como Espaço Maker."
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
            inspector: "Inspetores Araújo & Carol (Pátio)",
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
            name: "Térreo & Complexo Esportivo",
            sub: "Pátio Central, Portaria & Recepção (Araújo e Carol) e Quadra Poliesportiva",
            icon: "fa-school",
            highlights: ["Pátio Central & Portaria (Araújo e Carol)", "QUADRA POLIESPORTIVA (Apresentação Surpresa)", "Entrada & Credenciamento"]
        },
        "1": {
            name: "1º Andar – 6º Ano & Oficina de IA",
            sub: "Salas 01, 02 (Turmas 61 e 62 com Inspetora Mariana), Sala 03 (Oficina de IA com Inspetora Josielma) e Sala Maker",
            icon: "fa-layer-group",
            highlights: ["Turma 61 (Sala 01 - Mariana)", "Turma 62 (Sala 02 - Mariana)", "Oficina de IA (Sala 03 - Josielma)", "SALA MAKER (Apresentação Surpresa)"]
        },
        "2": {
            name: "2º Andar – 7º Ano & Turma 63",
            sub: "Salas 04, 06, 07 (Turmas 71, 72, 73 com Inspetor Ozael) e Sala 05 (Turma 63 com Mariana & Ozael)",
            icon: "fa-flask",
            highlights: ["Turma 71 (Sala 04 - Ozael)", "Turma 63 (Sala 05 - Mariana & Ozael)", "Turma 72 (Sala 06 - Ozael)", "Turma 73 (Sala 07 - Ozael)"]
        },
        "3": {
            name: "3º Andar – 8º Ano (Bloco Maria)",
            sub: "Salas 08, 09 e 10 (Turmas 81, 82 e Projetos Integrados com Inspetora Maria)",
            icon: "fa-satellite",
            highlights: ["Turma 81 (Sala 08 - Maria)", "Turmas 81/82 Integradas (Sala 09 - Maria)", "Turma 82 (Sala 10 - Maria)"]
        },
        "4": {
            name: "4º Andar – 9º Ano (Bloco Cleydson)",
            sub: "Salas 11, 12, 13 e 14 (Turmas 91, 92, 93 e Projetos Integrados com Inspetor Cleidson)",
            icon: "fa-microchip",
            highlights: ["Turma 92 (Sala 11 - Cleidson)", "Turma 91 (Sala 12 - Cleidson)", "Turmas 91/92/93 Integradas (Sala 13 - Cleidson)", "Turma 93 (Sala 14 - Cleidson)"]
        }
    },
    inspectors: [
        {
            id: "mariana",
            name: "Inspetora Mariana",
            role: "Inspetora do 6º Ano (1º e 2º Andares)",
            avatar: "imagens/avatar_inspetora_mariana.png",
            floor: "1º e 2º Andares",
            coverage: "Turma 61 (Sala 01), Turma 62 (Sala 02) e Turma 63 (Sala 05)",
            bio: "Responsável pelo acompanhamento das turmas do 6º Ano (61 na Sala 01, 62 na Sala 02 e 63 na Sala 05), acolhendo e orientando com carinho, paciência e atenção aos estudantes.",
            quote: "Receber com um sorriso e fazer cada aluno se sentir seguro e acolhido."
        },
        {
            id: "ozael",
            name: "Inspetor Ozael",
            role: "Inspetor do 7º Ano (2º Andar)",
            avatar: "imagens/avatar_inspetor_ozael.png",
            floor: "2º Andar",
            coverage: "Turmas 71 (Sala 04), 72 (Sala 06), 73 (Sala 07) e apoio à Sala 05 (Turma 63)",
            bio: "Responsável pelo 2º Andar, orienta e acompanha diariamente os estudantes do 7º Ano nas Salas 04, 06 e 07, além de prestar apoio à Turma 63 na Sala 05.",
            quote: "Incentivar a criatividade, o respeito e o aprendizado prático todos os dias."
        },
        {
            id: "josielma",
            name: "Inspetora Josielma",
            role: "Inspetora da Oficina de IA (1º Andar)",
            avatar: "imagens/avatar_inspetora_josielma.png",
            floor: "1º Andar",
            coverage: "Sala 03 (Oficina de Inteligência Artificial)",
            bio: "Responsável pela Oficina de Inteligência Artificial no 1º Andar (Sala 03), orientando e apoiando os estudantes e visitantes nas atividades práticas e demonstrações de IA.",
            quote: "Apoiar a inovação, o conhecimento e as novas tecnologias para nossos estudantes."
        },
        {
            id: "maria",
            name: "Inspetora Maria",
            role: "Inspetora do 8º Ano (3º Andar)",
            avatar: "imagens/avatar_inspetora_maria.png",
            floor: "3º Andar",
            coverage: "Turma 81 (Sala 08), Turma 82 (Sala 10) e Projetos Integrados (Sala 09)",
            bio: "Muito querida por toda a comunidade escolar, cuida com dedicação e carinho das salas do 3º Andar, orientando as turmas do 8º Ano em um ambiente acolhedor e harmonioso.",
            quote: "Cuidar de cada aluno como parte da nossa grande família EME."
        },
        {
            id: "cleidson",
            name: "Inspetor Cleidson",
            role: "Inspetor do 9º Ano (4º Andar)",
            avatar: "imagens/avatar_inspetor_cleidson.png",
            floor: "4º Andar",
            coverage: "Turmas 91 (Sala 12), 92 (Sala 11), 93 (Sala 14) e Projetos Integrados (Sala 13)",
            bio: "Com diálogo próximo e postura sempre atenciosa no 4º Andar, acompanha diariamente as turmas do 9º Ano, auxiliando em todas as necessidades pedagógicas e de convivência.",
            quote: "Apoiar nossos jovens rumo ao futuro com responsabilidade e amizade."
        },
        {
            id: "araujo",
            name: "Inspetor Araújo",
            role: "Inspetor de Pátio, Portaria & Segurança",
            avatar: "imagens/avatar_inspetor_araujo.png",
            floor: "Térreo / Pátio",
            coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
            bio: "Atua no pátio central e na portaria do colégio, cuidando da segurança, da organização no fluxo de entrada e saída e do convívio saudável de todos os estudantes.",
            quote: "Apoio constante para garantir a segurança e o bem-estar de toda a escola."
        },
        {
            id: "carol",
            name: "Inspetora Carol",
            role: "Inspetora de Pátio, Recepção & Entrada/Saída",
            avatar: "imagens/avatar_inspetora_carol.png",
            floor: "Térreo / Pátio",
            coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
            bio: "Atua na inspetoria de pátio e recepção ao lado do Inspetor Araújo, garantindo a recepção calorosa e segura de alunos e responsáveis, além do acompanhamento diário no pátio e na entrada e saída.",
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
        { key: "0", name: "Térreo & Pátio (Araújo e Carol)", icon: "🌳" },
        { key: "1", name: "1º Andar (61, 62 & Oficina IA - Mariana e Josielma)", icon: "1️⃣" },
        { key: "2", name: "2º Andar (71, 72, 73 & 63 - Ozael e Mariana)", icon: "2️⃣" },
        { key: "3", name: "3º Andar (81, 82 & GRP 8º - Maria)", icon: "3️⃣" },
        { key: "4", name: "4º Andar (91, 92, 93 & GRP 9º - Cleidson)", icon: "4️⃣" }
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
