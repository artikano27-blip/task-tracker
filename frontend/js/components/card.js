// Генерация компактной карточки задачи
export function createTaskElement(task) {
    const isCompleted = Boolean(task.is_completed);

    return `
        <div class="card shadow-sm border-0 mb-2 task-card ${isCompleted ? 'is-completed' : ''}" 
             data-task-id="${task.id}" 
             data-main-text="${task.main_text || ''}" 
             data-is-completed="${isCompleted}"
             style="cursor: pointer;">
            <div class="card-body p-2">
                <!-- Абсолютно спозиционированный чекбокс слева -->
                <button type="button" class="task-check-btn" title="${isCompleted ? 'Снять отметку' : 'Отметить выполненной'}"></button>
                
                <!-- Текст карточки, который плавно сдвигается -->
                <span class="task-title fw-semibold text-break small">${task.label_text}</span>
                
                <!-- Кнопка удаления справа -->
                <button class="btn btn-sm btn-link text-danger p-0 text-decoration-none btn-delete-task" title="Удалить">
                    &times;
                </button>
            </div>
        </div>
    `;
}