// JavaScript para o Sistema de Manutenção

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Adiciona confirmação para formulários de deleção
    const deleteForms = document.querySelectorAll('form[action*="/deletar"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Tem certeza que deseja deletar este item?')) {
                e.preventDefault();
            }
        });
    });

    // Validação de formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Formatação de valores monetários
    const custoInputs = document.querySelectorAll('input[name="custo"]');
    custoInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Adiciona tooltip do Bootstrap em elementos com data-bs-toggle="tooltip"
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Filtro de tabelas (busca simples)
    addTableSearch();
});

// Função para adicionar busca em tabelas
function addTableSearch() {
    const tables = document.querySelectorAll('table[id]');
    
    tables.forEach(table => {
        // Cria campo de busca
        const searchDiv = document.createElement('div');
        searchDiv.className = 'mb-3';
        searchDiv.innerHTML = `
            <div class="input-group">
                <span class="input-group-text">
                    <i class="bi bi-search"></i>
                </span>
                <input type="text" class="form-control" placeholder="Buscar na tabela..." id="search-${table.id}">
            </div>
        `;
        
        // Insere antes da tabela
        table.parentElement.insertBefore(searchDiv, table);
        
        // Adiciona evento de busca
        const searchInput = document.getElementById(`search-${table.id}`);
        searchInput.addEventListener('keyup', function() {
            filterTable(table, this.value);
        });
    });
}

// Função para filtrar tabela
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Função para formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Função para formatar data
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR').format(date);
}

// Função para exibir loading
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    spinner.setAttribute('role', 'status');
    element.prepend(spinner);
    element.disabled = true;
}

// Função para remover loading
function hideLoading(element) {
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
    element.disabled = false;
}

// Função para fazer requisições AJAX
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Função para exibir notificação
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

function atualizarAno() {
    const ano = new Date().getFullYear();
    document.getElementById("ano-atual").textContent = ano;
  }
  
  atualizarAno();  

  function confirmarDelecao(manutencaoId, equipamentoCodigo) {
    document.getElementById('equipamentoCodigo').textContent = equipamentoCodigo;
    document.getElementById('formDelecao').action = `/manutencoes/${manutencaoId}/deletar`;
    
    const modal = new bootstrap.Modal(document.getElementById('modalDelecao'));
    modal.show();
}

function aplicarPredefinicao(valor) {
    const hoje = new Date();
    let inicio = new Date();
    let fim = new Date();
    
    // Zera horas para evitar problemas de fuso
    hoje.setHours(0,0,0,0);
    
    switch(valor) {
        case 'mes_atual':
            inicio = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
            fim = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0);
            break;
            
        case 'ultimos_3_meses':
            inicio = new Date(hoje.getFullYear(), hoje.getMonth() - 2, 1);
            fim = hoje;
            break;
            
        case 'ano_atual':
            inicio = new Date(hoje.getFullYear(), 0, 1);
            fim = new Date(hoje.getFullYear(), 11, 31);
            break;
            
        case 'ano_passado':
            inicio = new Date(hoje.getFullYear() - 1, 0, 1);
            fim = new Date(hoje.getFullYear() - 1, 11, 31);
            break;
            
        default:
            // Se for 'Personalizado', não altera as datas automaticamente
            return;
    }
    
    // Formata para o input date (YYYY-MM-DD)
    if (valor) {
        document.getElementById('data_inicio').value = inicio.toISOString().split('T')[0];
        document.getElementById('data_fim').value = fim.toISOString().split('T')[0];
    }
}



// Exporta funções para uso global
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.fetchAPI = fetchAPI;
window.showNotification = showNotification;
