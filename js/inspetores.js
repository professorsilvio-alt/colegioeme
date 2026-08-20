/**
 * TOTEM INTERATIVO - COLÉGIO EME 2026
 * Módulo Dedicado: Equipe de Inspetores & Apoio Escolar
 */

const INSPETORES_DATA = [
    {
        id: "ozael",
        name: "Inspetor Ozael",
        role: "Inspetor do 1º Andar (Bloco Ozael) & Sala Maker",
        avatar: "imagens/avatar_inspetor_ozael.png",
        floorCategory: "1",
        floorBadge: "1º Andar • Bloco Ozael",
        coverage: "Salas 01, 02, 03, 18, 19, 20 (7º Ano e 2ª Série EM) & Sala Maker",
        bio: "Responsável pelo 1º Andar e pela Sala Maker, acompanha diariamente os estudantes do 7º Ano e da 2ª Série do Ensino Médio, além de incentivar as atividades práticas e projetos inovadores do Espaço Maker.",
        quote: "Incentivar a criatividade, o respeito e o aprendizado prático todos os dias.",
        accentColor: "#0284c7"
    },
    {
        id: "maria",
        name: "Inspetora Maria",
        role: "Inspetora do 2º Andar (Bloco Maria)",
        avatar: "imagens/avatar_inspetora_maria.png",
        floorCategory: "2",
        floorBadge: "2º Andar • Bloco Maria",
        coverage: "Salas 04, 05, 06 e 07 (7º, 8º Anos e 3ª Série EM)",
        bio: "Muito querida por toda a comunidade escolar, cuida com dedicação e carinho das salas do 2º Andar, orientando as turmas do 7º e 8º Anos e da 3ª Série do Ensino Médio em um ambiente acolhedor e harmonioso.",
        quote: "Cuidar de cada aluno como parte da nossa grande família EME.",
        accentColor: "#10b981"
    },
    {
        id: "claudio",
        name: "Inspetor Cláudio",
        role: "Inspetor do 3º Andar (Bloco Cláudio)",
        avatar: "imagens/avatar_inspetor_claudio.png",
        floorCategory: "3",
        floorBadge: "3º Andar • Bloco Cláudio",
        coverage: "Salas 08, 09 e 10 (8º e 9º Anos, 1ª e 3ª Séries EM)",
        bio: "Com presença marcante e liderança positiva no 3º Andar, apoia de perto os estudantes do 8º e 9º Anos e as turmas de Ensino Médio (1ª e 3ª séries), fortalecendo a disciplina, o companheirismo e a união escolar.",
        quote: "Educação, respeito e disciplina caminham juntos na formação do estudante.",
        accentColor: "#f59e0b"
    },
    {
        id: "cleidson",
        name: "Inspetor Cleidson",
        role: "Inspetor do 4º Andar (Bloco Cleydson)",
        avatar: "imagens/avatar_inspetor_cleidson.png",
        floorCategory: "4",
        floorBadge: "4º Andar • Bloco Cleydson",
        coverage: "Salas 11, 12, 13 e 14 (9º Ano e 1ª Série EM)",
        bio: "Com diálogo próximo e postura sempre atenciosa no 4º Andar, acompanha diariamente as turmas do 9º Ano e da 1ª Série do Ensino Médio, auxiliando em todas as necessidades pedagógicas e de convivência.",
        quote: "Apoiar nossos jovens rumo ao futuro com responsabilidade e amizade.",
        accentColor: "#8b5cf6"
    },
    {
        id: "neide",
        name: "Inspetora Neide",
        role: "Inspetora do 4º Andar (Bloco Cleydson / 9º Anos)",
        avatar: "imagens/avatar_inspetora_neide.png",
        floorCategory: "4",
        floorBadge: "4º Andar • Bloco Cleydson",
        coverage: "Salas 11, 12, 13 e 14 (Turmas Integradas e 9º Ano)",
        bio: "Atua no 4º Andar com carinho, atenção aos detalhes e dedicação constante, garantindo suporte, disciplina e acolhimento para as turmas e professores.",
        quote: "Zelo e dedicação para que cada jovem alcance o seu melhor potencial.",
        accentColor: "#ec4899"
    },
    {
        id: "mariana",
        name: "Inspetora Mariana",
        role: "Inspetora do Bloco Anexo (Térreo - 6º Anos)",
        avatar: "imagens/avatar_inspetora_mariana.png",
        floorCategory: "terreo",
        floorBadge: "Térreo • Bloco Anexo",
        coverage: "Salas 15, 16 e 17 (Turmas dos 6º Anos: 61, 62 e 63)",
        bio: "Responsável pelo Bloco Anexo no piso térreo, acolhe e orienta diariamente os estudantes dos 6º Anos (Turmas 61, 62 e 63) nas salas 15, 16 e 17 com enorme carinho, paciência e atenção aos estudantes.",
        quote: "Receber com um sorriso e fazer cada aluno se sentir seguro e acolhido.",
        accentColor: "#06b6d4"
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
        id: "karol",
        name: "Inspetora Karol",
        role: "Inspetora de Pátio, Entrada & Saída",
        avatar: "imagens/avatar_inspetora_karol.png",
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
