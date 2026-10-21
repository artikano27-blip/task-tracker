import { getTasks } from './tasksApi.js';

function switchView(viewId) {
    $('.app-view').addClass('d-none');$(`#${viewId}`).removeClass('d-none');
}

export function showError(message) {
    $('#auth-alert').removeClass('d-none alert-success').addClass('alert-danger').text(message);
}

export function showUserProfile(user) {
    switchView('tasks-view');
    $('#current-username').text(user.username);
    $('#app-navbar').removeClass('d-none')
}

export function showAuthForms() {
    switchView('auth-view');
    $('#login-form')[0].reset();
    $('#register-form')[0].reset();
    $('#auth-alert').addClass('d-none');
    $('#app-navbar').addClass('d-none');
    $('#current-username').text('');
}

export function handleSessionExpired() {
    showAuthForms();
    showError('Сессия истекла. Пожалуйста, войдите снова.');
}

function createTaskElement(task) {
    const isCompleted = task.status === 'COMPLETED';
    const badgeClass = isCompleted ? 'bg-success' : 'bg-warning text-dark';
    const statusText = isCompleted ? 'Выполнена' : 'В работе';

    const formattedDate = task.timestamp
        ? new Date(task.timestamp).toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
        : '';

    // Получаем никнейм из вложенного объекта author или фоллбэк на author_id
    const authorName = task.author?.username || (task.author_id ? `ID: ${task.author_id.slice(0, 6)}...` : 'Неизвестен');

    return `
        <div class="card mb-3 shadow-sm task-card border-${isCompleted ? 'success' : 'light'}" data-task-id="${task.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title mb-0 ${isCompleted ? 'text-decoration-line-through text-muted' : 'text-dark'}">
                        ${task.label_text}
                    </h5>
                    <span class="badge ${badgeClass}">${statusText}</span>
                </div>

                <p class="card-text text-secondary mb-3">${task.main_text || '<em>Без описания</em>'}</p>

                <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                    <div class="small text-muted d-flex align-items-center gap-2">
                        <span class="badge bg-light text-dark border">
                            👤 ${authorName}
                        </span>
                        ${formattedDate ? `<span>🕒 ${formattedDate}</span>` : ''}
                    </div>

                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-${isCompleted ? 'secondary' : 'success'} btn-toggle-status">
                            ${isCompleted ? 'Вернуть' : 'Завершить'}
                        </button>
                        <button class="btn btn-outline-danger btn-delete">
                            Удалить
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

export function renderTaskList(tasks) {
    const $container = $('#tasks-list'); // проверьте ваш id в index.html
    $container.empty();

    if (!tasks || tasks.length === 0) {
        $container.html('<p class="text-muted text-center py-4">Список задач пуст</p>');
        return;
    }

    const html = tasks.map(createTaskElement).join('');
    $container.html(html);
}

export async function loadTasks() {
    try {
        const tasks = await getTasks()
        renderTaskList(tasks)
    } catch (error) {
        showError(error);
    }
}