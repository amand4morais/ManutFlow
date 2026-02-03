// JavaScript para o Sistema de Manutenção ManutFlow

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica de Tema Claro/Escuro ---
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    // Verificar tema salvo no localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-fill');
        } else {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    }

    // --- Funcionalidades Originais Mantidas ---
    
    // Auto-hide alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Confirmação para formulários de deleção
    const deleteForms = document.querySelectorAll('form[action*="/deletar"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Tem certeza que deseja deletar este item?')) {
                e.preventDefault();
            }
        });
    });

    // Validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Filtro de tabelas (se houver tabelas com ID)
    addTableSearch();
});

// Função para adicionar busca em tabelas
function addTableSearch() {
    const tables = document.querySelectorAll('table[id]');
    tables.forEach(table => {
        if (document.getElementById(`search-${table.id}`)) return;

        const searchDiv = document.createElement('div');
        searchDiv.className = 'mb-3 animate-fade-in';
        searchDiv.innerHTML = `
            <div class="input-group">
                <span class="input-group-text bg-transparent border-end-0">
                    <i class="bi bi-search text-muted"></i>
                </span>
                <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar na tabela..." id="search-${table.id}">
            </div>
        `;
        
        table.parentElement.insertBefore(searchDiv, table);
        
        const searchInput = document.getElementById(`search-${table.id}`);
        searchInput.addEventListener('keyup', function() {
            const term = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
            });
        });
    });
}

// Funções Utilitárias
function togglePassword(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        icon.classList.replace("bi-eye-slash", "bi-eye");
    } else {
        input.type = "password";
        icon.classList.replace("bi-eye", "bi-eye-slash");
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

// Exportar para uso global
window.togglePassword = togglePassword;
window.formatCurrency = formatCurrency;
