import { createTaskElement } from './card.js';

//  Генерация разметки колонки со списком карточек
export function createColumnElement(column) {
    // Сортируем задачи внутри колонки по их позиции
    const sortedTasks = (column.tasks || []).sort((a, b) => a.position - b.position);
    const tasksHtml = sortedTasks.map(createTaskElement).join('');

    return `
        <div class="kanban-column card bg-body-secondary shadow-sm flex-shrink-0" 
             data-column-id="${column.id}">
            <div class="card-body p-2 d-flex flex-column">
                
                <!-- Заголовок колонки -->
                <div class="column-header d-flex justify-content-between align-items-center px-1 mb-2 flex-shrink-0">
                    <h6 class="column-title flex-grow-1 me-2 fw-bold mb-0 text-truncate">${column.title}</h6>
                    <button class="btn btn-sm btn-link text-secondary p-0 text-decoration-none btn-delete-column" title="Удалить колонку">
                        &times;
                    </button>
                </div>

                <!-- Прокручиваемый список задач -->
                <div class="tasks-container overflow-y-auto flex-grow-1 pe-1">
                    ${tasksHtml}
                </div>

                <!-- Кнопка быстрого создания задачи -->
                <button class="btn btn-sm border-0 text-secondary w-100 text-start btn-add-card flex-shrink-0">
                    + Добавить карточку
                </button>
                
                <!-- Форма быстрого создания задачи -->
                <div class="form-add-card flex-shrink-0 d-none">
                    <textarea class="form-control form-control-sm mb-2 card-title-input" rows="2" placeholder="Введите название карточки..." style="resize:none;"></textarea>
                    <div class="d-flex align-items-center gap-2">
                        <button class="btn btn-primary btn-sm btn-submit-card">Добавить карточку</button>
                        <button class="btn btn-link text-secondary p-0 text-decoration-none btn-cancel-card fs-5">&times;</button>
                    </div> 
                </div>

            </div>
        </div>
    `;
}