import { createColumnElement } from './column.js';
import { getColumns } from '../api/columnsApi.js';
import { showToast } from './toast.js';
import { initBoardSortable } from '../handlers/dnd.js';

//  Отрисовка разметки доски и кнопки добавления нового списка
export function renderBoard(columns) {
    const $container = $('#board-columns');
    $container.empty();

    // 1. Отрисовываем колонки, отсортированные по позиции
    if (columns && columns.length > 0) {
        const sortedColumns = [...columns].sort((a, b) => a.position - b.position);
        sortedColumns.forEach(column => {
            $container.append(createColumnElement(column));
        });
    }

    // 2. Добавляем форму создания новой колонки в конец ряда
    $container.append(`
        <div id="new-column-wrapper" class="flex-shrink-0" style="width: 280px;">
            <button type="button" id="btn-show-add-column" class="btn btn-outline-secondary w-100 text-start py-2">
                + Добавить список
            </button>

            <div id="add-column-form" class="card bg-body-secondary shadow-sm p-2 d-none">
                <input type="text" 
                       id="new-column-title-input" 
                       class="form-control form-control-sm mb-2" 
                       placeholder="Введите имя списка..." 
                       autocomplete="off">
                <div class="d-flex align-items-center gap-2">
                    <button type="button" id="btn-submit-column" class="btn btn-primary btn-sm">
                        Добавить список
                    </button>
                    <button type="button" id="btn-cancel-column" class="btn btn-link text-secondary p-0 fs-4 text-decoration-none lh-1" title="Отмена">
                        &times;
                    </button>
                </div>
            </div>
        </div>
    `);
}

//  Загрузка данных доски с сервера и повторный запуск Drag-and-Drop
export async function loadBoard() {
    try {
        const columns = await getColumns();
        renderBoard(columns);
        initBoardSortable();
    } catch (error) {
        const message = error.responseJSON?.message || error.message || 'Не удалось загрузить доску';
        showToast(message);
    }
}