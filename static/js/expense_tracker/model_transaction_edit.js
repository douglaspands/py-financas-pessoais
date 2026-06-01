function abrirModalEditar(tx) {
    const modal = document.getElementById('modal-editar-transacao');
    const form = document.getElementById('form-editar-transacao');
    
    // Captura o mês filtro atual da URL para manter o usuário na mesma página após salvar
    const urlParams = new URLSearchParams(window.location.search);
    const mesFiltro = urlParams.get('mes_filtro') || '';

    // Define o action do form dinamicamente apontando para a rota do FastAPI
    // Ajuste a rota '/gastos/editar/' conforme a estrutura real do seu backend
    form.action = `/gastos/editar-transacao/${tx.id}?mes_filtro=${mesFiltro}`;

    // Preenche os campos do modal com os dados da transação
    document.getElementById('edit-descricao').value = tx.descricao;
    document.getElementById('edit-valor').value = tx.valor;
    document.getElementById('edit-categoria').value = tx.categoria;
    document.getElementById('edit-conta').value = tx.conta_id;
    if (tx.tipo != 'unica') {
        document.getElementById('modal-alterar-recorrencias').classList.remove('is-hidden');
    } else {
        document.getElementById('modal-alterar-recorrencias').classList.add('is-hidden');
    }

    // Ativa o modal (classe nativa do Bulma)
    modal.classList.add('is-active');
}

function fecharModalEditar() {
    const modal = document.getElementById('modal-editar-transacao');
    modal.classList.remove('is-active');
}
