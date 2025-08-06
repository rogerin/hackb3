// GitHub Analyzer - JavaScript principal

// Configuração global
const API_BASE = '/api';

// Utilitários
class APIClient {
    static async request(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    static async get(endpoint) {
        return this.request(`${API_BASE}${endpoint}`);
    }

    static async post(endpoint, data = {}) {
        return this.request(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Notificações
class NotificationManager {
    static show(message, type = 'info', duration = 5000) {
        // Remove notificações existentes
        const existing = document.querySelectorAll('.alert-notification');
        existing.forEach(el => el.remove());

        // Cria nova notificação
        const alert = document.createElement('div');
        alert.className = `alert alert-${this.getBootstrapClass(type)} alert-dismissible fade show alert-notification`;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1060;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;

        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getIcon(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.appendChild(alert);

        // Auto-remove após duração especificada
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
    }

    static getBootstrapClass(type) {
        const classes = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classes[type] || 'info';
    }

    static getIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Loading Manager
class LoadingManager {
    static show(target, message = 'Carregando...') {
        const spinner = document.createElement('div');
        spinner.className = 'text-center py-4 loading-spinner';
        spinner.innerHTML = `
            <div class="spinner-border text-primary mb-2" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="text-muted">${message}</p>
        `;

        if (typeof target === 'string') {
            target = document.getElementById(target);
        }

        target.innerHTML = '';
        target.appendChild(spinner);
    }

    static hide(target) {
        if (typeof target === 'string') {
            target = document.getElementById(target);
        }

        const spinner = target.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Repository Manager
class RepositoryManager {
    static async loadAll() {
        try {
            const repositories = await APIClient.get('/repositories');
            return repositories;
        } catch (error) {
            console.error('Erro ao carregar repositórios:', error);
            throw error;
        }
    }

    static async setupWebhook(owner, repo) {
        try {
            const result = await APIClient.post(`/repositories/${owner}/${repo}/select`);
            return result;
        } catch (error) {
            console.error('Erro ao configurar webhook:', error);
            throw error;
        }
    }

    static formatLanguageBadge(language) {
        if (!language) return '';
        
        const color = this.getLanguageColor(language);
        return `<span class="badge" style="background-color: ${color};">${language}</span>`;
    }

    static getLanguageColor(language) {
        const colors = {
            'JavaScript': '#f1e05a',
            'Python': '#3572A5',
            'Java': '#b07219',
            'TypeScript': '#2b7489',
            'C#': '#239120',
            'PHP': '#4F5D95',
            'C++': '#f34b7d',
            'C': '#555555',
            'Go': '#00ADD8',
            'Rust': '#dea584',
            'Ruby': '#701516',
            'Swift': '#ffac45',
            'Kotlin': '#F18E33',
            'Dart': '#00B4AB',
            'HTML': '#e34c26',
            'CSS': '#1572B6'
        };
        
        return colors[language] || '#6c757d';
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

// Inicialização global
document.addEventListener('DOMContentLoaded', function() {
    // Configurar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configurar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Event listeners globais
    document.addEventListener('click', function(e) {
        // Fechar dropdowns quando clicar fora
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target) && !dropdown.previousElementSibling.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });
});

// Adicionar animações CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
`;
document.head.appendChild(style);

// Exposar utilitários globalmente
window.NotificationManager = NotificationManager;
window.LoadingManager = LoadingManager;
window.RepositoryManager = RepositoryManager;
window.APIClient = APIClient;