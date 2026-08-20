/**
 * TOTEM INTERATIVO - COLÉGIO EME 2026
 * Módulo Dedicado: Equipe de Inspetores & Apoio Escolar
 */

const INSPETORES_DATA = [
    {
        id: "mariana",
        name: "Inspetora Mariana",
        role: "Inspetora do 6º Ano (1º e 2º Andares)",
        avatar: "imagens/avatar_inspetora_mariana.png",
        floorCategory: "1",
        floorBadge: "1º e 2º Andares • 6º Ano",
        coverage: "Turma 61 (Sala 01), Turma 62 (Sala 02) e Turma 63 (Sala 05)",
        bio: "Responsável pelo acompanhamento das turmas do 6º Ano (61 na Sala 01, 62 na Sala 02 e 63 na Sala 05), acolhendo e orientando com carinho, paciência e atenção aos estudantes nos 1º e 2º Andares.",
        quote: "Receber com um sorriso e fazer cada aluno se sentir seguro e acolhido.",
        accentColor: "#0284c7"
    },
    {
        id: "ozael",
        name: "Inspetor Ozael",
        role: "Inspetor do 7º Ano (2º Andar)",
        avatar: "imagens/avatar_inspetor_ozael.png",
        floorCategory: "2",
        floorBadge: "2º Andar • 7º Ano",
        coverage: "Turmas 71 (Sala 04), 72 (Sala 06), 73 (Sala 07) e apoio à Sala 05 (Turma 63)",
        bio: "Responsável pelo 2º Andar, orienta e acompanha diariamente os estudantes do 7º Ano nas Salas 04, 06 e 07, além de prestar apoio à Turma 63 na Sala 05, promovendo a convivência harmoniosa.",
        quote: "Incentivar a criatividade, o respeito e o aprendizado prático todos os dias.",
        accentColor: "#0d9488"
    },
    {
        id: "josielma",
        name: "Inspetora Josielma",
        role: "Inspetora da Oficina de IA (1º Andar)",
        avatar: "imagens/avatar_inspetora_josielma.png",
        floorCategory: "1",
        floorBadge: "1º Andar • Oficina de IA",
        coverage: "Sala 03 (Oficina de Inteligência Artificial)",
        bio: "Responsável pela Oficina de Inteligência Artificial no 1º Andar (Sala 03), orientando e apoiando os estudantes e visitantes nas atividades práticas e demonstrações de IA.",
        quote: "Apoiar a inovação, o conhecimento e as novas tecnologias para nossos estudantes.",
        accentColor: "#2563eb"
    },
    {
        id: "maria",
        name: "Inspetora Maria",
        role: "Inspetora do 8º Ano (3º Andar)",
        avatar: "imagens/avatar_inspetora_maria.png",
        floorCategory: "3",
        floorBadge: "3º Andar • 8º Ano",
        coverage: "Turma 81 (Sala 08), Turma 82 (Sala 10) e Projetos Integrados (Sala 09)",
        bio: "Muito querida por toda a comunidade escolar, cuida com dedicação e carinho das salas do 3º Andar, orientando as turmas do 8º Ano (Salas 08, 09 e 10) em um ambiente acolhedor e harmonioso.",
        quote: "Cuidar de cada aluno como parte da nossa grande família EME.",
        accentColor: "#f59e0b"
    },
    {
        id: "cleidson",
        name: "Inspetor Cleidson",
        role: "Inspetor do 9º Ano (4º Andar)",
        avatar: "imagens/avatar_inspetor_cleidson.png",
        floorCategory: "4",
        floorBadge: "4º Andar • 9º Ano",
        coverage: "Turmas 91 (Sala 12), 92 (Sala 11), 93 (Sala 14) e Projetos Integrados (Sala 13)",
        bio: "Com diálogo próximo e postura sempre atenciosa no 4º Andar, acompanha diariamente todas as turmas do 9º Ano nas Salas 11, 12, 13 e 14, auxiliando em todas as necessidades pedagógicas e de convivência.",
        quote: "Apoiar nossos jovens rumo ao futuro com responsabilidade e amizade.",
        accentColor: "#8b5cf6"
    },
    {
        id: "araujo",
        name: "Inspetor Araújo",
        role: "Inspetor de Pátio, Portaria & Segurança",
        avatar: "imagens/avatar_inspetor_araujo.png",
        floorCategory: "terreo",
        floorBadge: "Térreo • Pátio Central",
        coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
        bio: "Atua no pátio central e na portaria do colégio, cuidando da segurança, da organização no fluxo de entrada e saída e do convívio saudável de todos os estudantes nos intervalos e eventos.",
        quote: "Apoio constante para garantir a segurança e o bem-estar de toda a escola.",
        accentColor: "#3b82f6"
    },
    {
        id: "carol",
        name: "Inspetora Carol",
        role: "Inspetora de Pátio, Recepção & Entrada/Saída",
        avatar: "imagens/avatar_inspetora_carol.png",
        floorCategory: "terreo",
        floorBadge: "Térreo • Recepção & Pátio",
        coverage: "Pátio Central, Portões de Acesso, Entrada e Saída dos Alunos",
        bio: "Atua na inspetoria de pátio e recepção ao lado do Inspetor Araújo, garantindo a recepção calorosa e segura de alunos e responsáveis, além do acompanhamento diário no pátio e na entrada e saída.",
        quote: "Cuidado, atenção e acolhimento em cada momento da rotina escolar.",
        accentColor: "#14b8a6"
    }
];

let activeFilter = "all";
let idleTimer = null;

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
    updateClock();
    setInterval(updateClock, 1000);

    renderInspectors(activeFilter);
    setupFilterButtons();
    setupIdleManager();
});

// Relógio em tempo real
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

// Renderizar Grade de Cards com Fotos Inteiras
function renderInspectors(filter) {
    const grid = document.getElementById("inspetores-grid");
    if (!grid) return;

    const filtered = (filter === "all")
        ? INSPETORES_DATA
        : INSPETORES_DATA.filter(i => i.floorCategory === filter);

    grid.innerHTML = filtered.map(insp => `
        <article class="insp-card-full" style="--card-accent: ${insp.accentColor};" data-floor="${insp.floorCategory}">
            <div class="insp-card-top-strip"></div>
            
            <!-- Vitrine com Foto Inteira do Inspetor -->
            <div class="insp-photo-showcase">
                <div class="insp-floor-floating-badge">
                    <i class="fa-solid fa-location-dot"></i>
                    <span>${insp.floorBadge}</span>
                </div>
                <div class="insp-verified-pill">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Equipe EME</span>
                </div>
                <img 
                    src="${insp.avatar}" 
                    alt="Foto oficial do ${insp.name}" 
                    class="insp-full-photo-img" 
                    loading="lazy"
                    onerror="this.src='imagens/avatar_inspetor_ozael.png'"
                />
            </div>

            <!-- Informações do Inspetor -->
            <div class="insp-card-body">
                <div class="insp-name-group">
                    <h3 class="insp-full-name">${insp.name}</h3>
                    <span class="insp-full-role">${insp.role}</span>
                </div>

                <div class="insp-coverage-block">
                    <span class="coverage-title"><i class="fa-solid fa-door-open"></i> Salas e Áreas de Atuação:</span>
                    <span class="coverage-rooms">${insp.coverage}</span>
                </div>

                <p class="insp-bio-text">${insp.bio}</p>

                <div class="insp-quote-banner">
                    <i class="fa-solid fa-quote-left"></i>
                    <span>"${insp.quote}"</span>
                </div>

                <div class="insp-card-footer-action">
                    <a href="index.html" class="btn-card-goto-totem">
                        <i class="fa-solid fa-map-location-dot"></i>
                        <span>Ver Salas no Totem</span>
                    </a>
                </div>
            </div>
        </article>
    `).join("");
}

// Configuração dos Botões de Filtro
function setupFilterButtons() {
    const buttons = document.querySelectorAll(".insp-filter-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            activeFilter = btn.getAttribute("data-floor");
            renderInspectors(activeFilter);
            resetIdleTimer();
        });
    });
}

// Gerenciamento de Inatividade (Auto-retorno ao Totem após 60s)
function setupIdleManager() {
    resetIdleTimer();

    ["click", "touchstart", "mousemove", "keydown", "scroll"].forEach(evt => {
        document.addEventListener(evt, () => {
            resetIdleTimer();
        }, { passive: true });
    });
}

function resetIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
        window.location.href = "index.html";
    }, 60000);
}
