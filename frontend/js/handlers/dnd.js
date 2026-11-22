import { moveTask } from '../api/tasksApi.js';
import { moveColumn } from '../api/columnsApi.js';
import { showToast } from '../components/toast.js';
import { loadBoard } from '../components/board.js';

//  Инициализация перетаскивания карточек задач
export function initTasksSortable() {
    $('.tasks-container').each(function () {
        new Sortable(this, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'task-ghost',
            filter: '.task-check-btn',
            swapThreshold: 1,
            invertSwap: false,
            emptyInsertThreshold: 100,

            forceFallback: true,                 // отключает стандартный HTML5 DnD и рисует элемент вручную
            fallbackClass: 'sortable-fallback',  // класс для карточки под курсором
            fallbackOnBody: true,                // выносит карточку в body, чтобы overflow колонки её не резал

            onEnd: async function (evt) {
                const taskId = $(evt.item).data('task-id');
                const columnId = $(evt.to).closest('.kanban-column').data('column-id');
                const newPosition = evt.newIndex;

                try {
                    await moveTask(taskId, { target_column_id: columnId, new_position: newPosition });
                } catch (error) {
                    const message = error.responseJSON?.message || 'Ошибка сервиса';
                    showToast(message);
                    await loadBoard();
                }
            }
        });
    });
}

//  Инициализация перетаскивания колонок по горизонтали
export function initColumnsSortable() {
    const boardEl = $('#board-columns')[0];
    if (!boardEl) return;

    const existingSortable = Sortable.get(boardEl);
    if (existingSortable) {
        existingSortable.destroy();
    }

    new Sortable(boardEl, {
        animation: 200,
        easing: 'cubic-bezier(0.25, 1, 0.5, 1)',
        direction: 'horizontal',
        swapThreshold: 0.5,
        handle: '.column-header',
        draggable: '.kanban-column',
        filter: '.btn-delete-column, input',
        preventOnFilter: false,
        ghostClass: 'column-ghost',
        forceFallback: true,
        fallbackClass: 'sortable-fallback',

        onEnd: async function (evt) {
            // Если колонка осталась на исходном месте — прерываем выполнение
            if (evt.newIndex === evt.oldIndex) {
                return;
            }

            const columnId = $(evt.item).data('column-id');
            const newPosition = evt.newIndex;

            try {
                await moveColumn(columnId, { new_position: newPosition });
            } catch (error) {
                const message = error.responseJSON?.message || 'Ошибка сервиса';
                showToast(message);
                await loadBoard();
            }
        }
    });
}

//  Единая точка запуска Drag-and-Drop для доски
export function initBoardSortable() {
    initTasksSortable();
    initColumnsSortable();
}