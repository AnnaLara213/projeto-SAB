// Base URL da API
const API_BASE_URL = "http://localhost:5000";

// Função para carregar recursos
async function carregarRecursos() {
    const response = await fetch(`${API_BASE_URL}/recursos`);
    const data = await response.json();

    const tabelaRecursos = document.querySelector("#recursos-table tbody");
    tabelaRecursos.innerHTML = "";

    data.forEach(recurso => {
        const row = `
            <tr>
                <td>${recurso.nome}</td>
                <td>${recurso.quantidade}</td>
            </tr>
        `;
        tabelaRecursos.innerHTML += row;
    });
}

// Função para doar recursos
async function doarRecurso(event) {
    event.preventDefault();

    const categoria = document.getElementById("doar-categoria").value;
    const quantidade = document.getElementById("doar-quantidade").value;

    const response = await fetch(`${API_BASE_URL}/doacoes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ nome: categoria, quantidade: parseInt(quantidade) }),
    });

    if (response.ok) {
        alert("Doação realizada com sucesso!");
        carregarRecursos();
    } else {
        alert("Erro ao realizar a doação.");
    }
}

// Função para emprestar recursos
async function emprestarRecurso(event) {
    event.preventDefault();

    const categoria = document.getElementById("emprestar-categoria").value;
    const quantidade = document.getElementById("emprestar-quantidade").value;

    const response = await fetch(`${API_BASE_URL}/emprestimos`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ nome: categoria, quantidade: parseInt(quantidade) }),
    });

    if (response.ok) {
        alert("Empréstimo realizado com sucesso!");
        carregarRecursos();
    } else {
        alert("Erro ao realizar o empréstimo.");
    }
}

// Eventos
document.getElementById("doar-recursos-form").addEventListener("submit", doarRecurso);
document.getElementById("emprestar-recursos-form").addEventListener("submit", emprestarRecurso);

// Carregar recursos ao abrir a página
carregarRecursos();
