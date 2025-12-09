document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('palavraInput');
    const button = document.getElementById('tentarBtn');
    const feedback = document.getElementById('feedback');
    const progressBar = document.getElementById('progressBar');
    const tentativas = document.getElementById('tentativas');
    const contador = document.getElementById('contador');
    const giveUpButton = document.getElementById('giveUpButton');

    let totalTentativas = 0;
    let jogoFinalizado = false;

    // Enter para enviar
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !jogoFinalizado) {
            button.click();
        }
    });

    // Função principal de tentativa
    button.addEventListener('click', async () => {
        if (jogoFinalizado) {
            mostrarFeedback('⏰ Você já completou o desafio de hoje!', '#ffa500');
            return;
        }

        const palavra = input.value.trim();
        if (!palavra) {
            mostrarFeedback('❌ Digite uma palavra!', '#ff6b6b');
            return;
        }

        // Valida se é palavra única
        if (palavra.includes(' ')) {
            mostrarFeedback('❌ Apenas palavras únicas (sem espaços)!', '#ff6b6b');
            return;
        }

        try {
            const response = await fetch('/tentar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ palavra })
            });

            const data = await response.json();

            if (data.erro) {
                mostrarFeedback(data.erro, '#ff6b6b');
                return;
            }

            // Incrementa contador
            totalTentativas++;
            contador.textContent = totalTentativas;

            // Adiciona ao histórico
            adicionarTentativa(data.palavra_exibida || palavra, data.similaridade);

            // Atualiza barra de progresso
            atualizarProgressBar(data.similaridade);

            // Verifica vitória
            if (data.venceu) {
                jogoFinalizado = true;
                mostrarVitoria(data.palavra_secreta, data.tempo_proximo);
            } else {
                const emoji = getEmojiTemperatura(data.similaridade);
                mostrarFeedback(`${emoji} ${data.similaridade}% de similaridade`, '#00d4ff');
            }

            input.value = '';
            input.focus();

        } catch (error) {
            console.error('Erro:', error);
            mostrarFeedback('❌ Erro ao processar tentativa', '#ff6b6b');
        }
    });

    // Mostrar feedback
    function mostrarFeedback(texto, cor) {
        feedback.textContent = texto;
        feedback.style.color = cor;
    }

    // Adicionar tentativa ao histórico
    function adicionarTentativa(palavra, similaridade) {
        const div = document.createElement('div');
        div.className = 'tentativa-item';

        const classe = getClasseScore(similaridade);
        const emoji = getEmojiTemperatura(similaridade);

        div.innerHTML = `
            <span class="tentativa-palavra">${palavra}</span>
            <div class="tentativa-score">
                <span class="score-badge ${classe}">${emoji} ${similaridade}%</span>
            </div>
        `;

        tentativas.insertBefore(div, tentativas.firstChild);
    }

    // Atualizar barra de progresso
    function atualizarProgressBar(similaridade) {
        progressBar.style.width = `${similaridade}%`;
        
        if (similaridade > 75) {
            progressBar.style.background = 'linear-gradient(90deg, #fa709a, #fee140)';
        } else if (similaridade > 50) {
            progressBar.style.background = 'linear-gradient(90deg, #4facfe, #00f2fe)';
        } else if (similaridade > 25) {
            progressBar.style.background = 'linear-gradient(90deg, #f093fb, #f5576c)';
        } else {
            progressBar.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
        }
    }

    // Mostrar vitória
    function mostrarVitoria(palavraSecreta, tempoProximo) {
        mostrarFeedback(
            `🎉 PARABÉNS! Você acertou "${palavraSecreta}" em ${totalTentativas} tentativas!`, 
            '#00ff88'
        );
        input.disabled = true;
        button.disabled = true;
        giveUpButton.remove();
        button.style.opacity = '0.5';
        button.style.cursor = 'not-allowed';

        // Mostra mensagem sobre próximo jogo
        setTimeout(() => {
            mostrarFeedback(
                `✅ Desafio completo! Volte em ${tempoProximo} para uma nova palavra.`,
                '#00d4ff'
            );
        }, 2000);
    }

    // Obter classe do score
    function getClasseScore(sim) {
        if (sim > 75) return 'score-fire';
        if (sim > 50) return 'score-hot';
        if (sim > 25) return 'score-warm';
        return 'score-cold';
    }

    // Obter emoji de temperatura
    function getEmojiTemperatura(sim) {
        if (sim > 75) return '🌋';
        if (sim > 50) return '🔥';
        if (sim > 25) return '🧊';
        return '❄️';
    }

    // Carregar estatísticas ao iniciar
    carregarStats();
});

// === FUNÇÕES DOS MODAIS ===

function openModal(modalName) {
    const modal = document.getElementById(`modal${modalName.charAt(0).toUpperCase() + modalName.slice(1)}`);
    modal.classList.add('active');

    // Previne scroll do body
    document.body.style.overflow = 'hidden';
}

function closeModal(modalName) {
    const modal = document.getElementById(`modal${modalName.charAt(0).toUpperCase() + modalName.slice(1)}`);
    modal.classList.remove('active');
    document.body.style.overflow = 'hidden';
}

// Fechar modal clicando fora
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
        document.body.style.overflow = 'hidden';
    }
});

// Revelar palavra (desistir)
async function revealWord() {
    try {
        const response = await fetch('/desistir', { method: 'POST' });
        const data = await response.json();

        if (data.palavra_secreta) {
            // Atualiza o modal com a palavra revelada
            const modalBody = document.querySelector('#modalGiveUp .modal-body');
            modalBody.innerHTML = `
                <p style="text-align: center; font-size: 1.1rem; margin-bottom: 15px;">
                    A palavra secreta era:
                </p>
                <div class="reveal-word">${data.palavra_secreta}</div>
                <p style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    Você fez ${data.total_tentativas} tentativa(s).
                </p>
                <p style="text-align: center; margin-top: 15px; font-size: 0.95rem;">
                    ⏰ Nova palavra disponível em: <strong>${data.tempo_proximo}</strong>
                </p>
                <button class="btn-modal-action" onclick="closeModal('giveUp')">
                    Entendido
                </button>
            `;

            // Desabilita o jogo
            document.getElementById('palavraInput').disabled = true;
            document.getElementById('tentarBtn').disabled = true;
            giveUpButton.remove();
            document.getElementById('tentarBtn').style.opacity = '0.5';
            document.getElementById('feedback').textContent = '⏰ Volte amanhã para uma nova palavra!';
            document.getElementById('feedback').style.color = '#00d4ff';
        }
    } catch (error) {
        console.error('Erro ao revelar palavra:', error);
        alert('❌ Erro ao revelar a palavra. Tente novamente.');
    }
}

// Carregar estatísticas
async function carregarStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();

        if (data.jogo_finalizado) {
            document.getElementById('feedback').textContent = 
                `✅ Desafio completo! Volte em ${data.proximo_reset} para uma nova palavra.`;
            document.getElementById('feedback').style.color = '#00d4ff';
            document.getElementById('palavraInput').disabled = true;
            giveUpButton.remove();
            document.getElementById('tentarBtn').disabled = true;
            document.getElementById('tentarBtn').style.opacity = '0.5';
        }
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

// Fechar modal com ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = 'hidden';
    }
});