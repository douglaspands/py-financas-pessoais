// Função para alternar a visibilidade do card e salvar no LocalStorage
function toggleCard(contentId, buttonId) {
    const conteudo = document.getElementById(contentId);
    const botao = document.getElementById(buttonId);

    conteudo.classList.toggle('is-minimized');

    // Verifica se o card ficou minimizado após o clique
    const estaMinimizado = conteudo.classList.contains('is-minimized');

    if (estaMinimizado) {
        botao.textContent = '+';
    } else {
        botao.textContent = '-';
    }

    // Salva o estado atual (true para minimizado, false para visível) no LocalStorage
    localStorage.setItem(contentId, estaMinimizado);
}

// Função que roda automaticamente assim que a página termina de carregar
document.addEventListener("DOMContentLoaded", function () {
    const cards = [
        { contentId: 'conteudo-categoria', buttonId: 'btn-cat' },
        { contentId: 'conteudo-conta', buttonId: 'btn-conta' },
        { contentId: 'conteudo-form-transacao', buttonId: 'btn-form-tx' },
        { contentId: 'conteudo-form-conta', buttonId: 'btn-form-conta' },
        { contentId: 'conteudo-extrato', buttonId: 'btn-extrato' }
    ];

    cards.forEach(card => {
        const conteudo = document.getElementById(card.contentId);
        const botao = document.getElementById(card.buttonId);
        const estadoSalvo = localStorage.getItem(card.contentId);

        if (estadoSalvo === "true") {
            conteudo.classList.add('is-minimized');
            botao.textContent = '+';
        } else {
            conteudo.classList.remove('is-minimized');
            botao.textContent = '-';
        }
    });
});

// Função para atualizar os campos de repetição com base no tipo de transação selecionado
function atualizarCamposRepeticao() {
    const tipo = document.getElementById('tipo_transacao').value;
    const campoRepeticao = document.getElementById('campo-repeticao');
    const labelRepeticao = document.getElementById('label-repeticao');
    const inputRepeticao = document.getElementById('quantidade_repeticoes');

    if (tipo === 'unica') {
        campoRepeticao.style.display = 'none';
        inputRepeticao.value = "1";
    } else if (tipo === 'parcelada') {
        campoRepeticao.style.display = 'block';
        labelRepeticao.innerText = 'Quantidade de Parcelas';
        inputRepeticao.placeholder = 'Ex: 12';
    } else if (tipo === 'recorrente') {
        campoRepeticao.style.display = 'block';
        labelRepeticao.innerText = 'Repetir por quantos meses?';
        inputRepeticao.placeholder = 'Ex: 6 (vazio para ilimitado)';
    }
}
