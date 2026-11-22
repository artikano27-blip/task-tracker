import { createColumn, deleteColumn, updateColumn } from '../api/columnsApi.js';
import { createTask, deleteTask, updateTask } from '../api/tasksApi.js';
import { loadBoard } from '../components/board.js';
import { showToast } from '../components/toast.js';

//  Инициализация всех пользовательских действий на доске
export function initBoardHandlers() {

    // ---  УПРАВЛЕНИЕ КОЛОНКАМИ ---

    //  Показ формы создания колонки
    $(document).on('click', '#btn-show-add-column', function (event) {
        event.preventDefault();
        $(this).addClass('d-none');
        $('#add-column-form').removeClass('d-none');
        $('#new-column-title-input').trigger('focus');
    });

    //  Отмена создания колонки
    $(document).on('click', '#btn-cancel-column', function (event) {
        event.preventDefault();
        $('#new-column-title-input').val('');
        $('#add-column-form').addClass('d-none');
        $('#btn-show-add-column').removeClass('d-none');
    });

    //  Отправка новой колонки
    $(document).on('click', '#btn-submit-column', async function (event) {
        event.preventDefault();
        const title = $('#new-column-title-input').val().trim();
        if (!title) return;

        try {
            await createColumn({ title });
            $('#new-column-title-input').val('');
            await loadBoard();
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка сервиса';
            showToast(message);
        }
    });

    //  Удаление колонки
    $(document).on('click', '.btn-delete-column', async function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $column = $(this).closest('.kanban-column');
        const columnId = $column.data('column-id');

        if (!columnId) return;

        const isConfirmed = confirm('Вы уверены, что хотите удалить эту колонку и все карточки в ней?');
        if (!isConfirmed) return;

        try {
            await deleteColumn(columnId);
            $column.remove();
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка удаления';
            showToast(message);
        }
    });

    //  Редактирование названия колонки по клику
    $(document).on('click', '.column-header', function (event) {
        event.preventDefault();
        if ($(this).find('input').length > 0) return;

        const $currentTitle = $(this).find('.column-title');
        const currentText = $currentTitle.text();

        $currentTitle.html(`<input type="text" class="form-control form-control-sm" value="${currentText}" data-old="${currentText}">`);
        $currentTitle.find('input').trigger('focus').select();
    });

    //  Сохранение названия колонки при потере фокуса
    $(document).on('blur', '.column-title input', async function (event) {
        event.preventDefault();
        const $currentTitle = $(this).closest('.column-title');
        const newText = $(this).val().trim();
        const oldText = $(this).data('old');
        const $column = $(this).closest('.kanban-column');
        const columnId = $column.data('column-id');

        const finalText = newText.length === 0 ? oldText : newText;
        $currentTitle.text(finalText);
        if (finalText === oldText) return;

        try {
            await updateColumn(columnId, { title: finalText });
        } catch (error) {
            $currentTitle.text(oldText);
            const message = error.responseJSON?.message || 'Ошибка редактирования';
            showToast(message);
        }
    });

    // Обработка Enter и Escape при редактировании названия колонки
    $(document).on('keydown', '.column-title input', function (event) {
        if (event.key === 'Enter') {
            $(this).trigger('blur');
        } else if (event.key === 'Escape') {
            const oldText = $(this).data('old');
            $(this).val(oldText);
            $(this).trigger('blur');
        }
    });


    // ---  УПРАВЛЕНИЕ КАРТОЧКАМИ ---

    //  Показ формы создания задачи (с автоскроллом)
    $(document).on('click', '.btn-add-card', function (event) {
        event.preventDefault();

        // Закрываем другие открытые формы создания карточек, если они есть
        $('.form-add-card:not(.d-none)').each(function () {
            $(this).addClass('d-none');
            $(this).find('.card-title-input').val('').css('height', '');
            $(this).prev('.btn-add-card').removeClass('d-none');
        });

        $(this).addClass('d-none');

        const $column = $(this).closest('.kanban-column');
        const $form = $(this).next('.form-add-card');

        $form.removeClass('d-none');
        $form.find('.card-title-input').trigger('focus');

        const $tasksContainer = $column.find('.tasks-container');
        if ($tasksContainer.length) {
            $tasksContainer.animate({ scrollTop: $tasksContainer[0].scrollHeight }, 250);
        }
    });

    //  Создание новой задачи (УМНЫЙ РЕЖИМ С ВОССТАНОВЛЕНИЕМ)
    $(document).on('click', '.btn-submit-card', async function (event) {
        event.preventDefault();

        const $form = $(this).closest('.form-add-card');
        const $input = $form.find('.card-title-input');
        const title = $input.val().trim();
        const columnId = $(this).closest('.kanban-column').data('column-id');

        if (!title || !columnId) return;

        try {
            $(this).prop('disabled', true); // Блокируем от двойного клика

            await createTask({ label_text: title, column_id: columnId });
            await loadBoard();

            //  Восстановление состояния открытой формы
            const $column = $(`.kanban-column[data-column-id="${columnId}"]`);
            if ($column.length) {
                $column.find('.btn-add-card').addClass('d-none');
                const $newForm = $column.find('.form-add-card').removeClass('d-none');

                $newForm.find('.card-title-input')
                    .val('')
                    .css('height', '')
                    .trigger('focus');

                const $tasksContainer = $column.find('.tasks-container');
                $tasksContainer.scrollTop($tasksContainer[0].scrollHeight);
            }
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка сервиса';
            showToast(message);
        } finally {
            $(this).prop('disabled', false);
        }
    });

    //  Быстрое сохранение по нажатию Enter
    $(document).on('keydown', '.card-title-input', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            $(this).closest('.form-add-card').find('.btn-submit-card').trigger('click');
        } else if (event.key === 'Escape') {
            $(this).closest('.form-add-card').find('.btn-cancel-card').trigger('click');
        }
    });

    //  Скрытие формы создания задачи
    $(document).on('click', '.btn-cancel-card', function (event) {
        event.preventDefault();
        const $form = $(this).closest('.form-add-card');
        $form.addClass('d-none');
        $form.find('.card-title-input').val('').css('height', '');
        $form.prev('.btn-add-card').removeClass('d-none');
    });

    //  Закрытие формы создания задачи при клике за её пределами
    $(document).on('mousedown', function (event) {
        const $openForms = $('.form-add-card:not(.d-none)');
        if (!$openForms.length) return;

        if ($(event.target).closest('.form-add-card, .btn-add-card').length === 0) {
            $openForms.each(function () {
                $(this).addClass('d-none');
                $(this).find('.card-title-input').val('').css('height', '');
                $(this).prev('.btn-add-card').removeClass('d-none');
            });
        }
    });

    // 🗑 Удаление задачи
    $(document).on('click', '.btn-delete-task', async function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $card = $(this).closest('.task-card');
        const taskId = $card.data('task-id');

        if (!taskId) return;

        try {
            await deleteTask(taskId);
            $card.remove();
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка удаления';
            showToast(message);
        }
    });

    //  Переключение чекбокса выполнения задачи
    $(document).on('click', '.task-check-btn', async function (event) {
        event.preventDefault();
        event.stopPropagation();

        const $btn = $(this);
        const $task = $btn.closest('.task-card');
        const taskId = $task.data('taskId');
        const isCompleted = Boolean($task.data('isCompleted'));
        const newStatus = !isCompleted;

        $btn.prop('disabled', true);
        $task.toggleClass('is-completed', newStatus);
        $task.data('isCompleted', newStatus);

        try {
            await updateTask(taskId, { is_completed: newStatus });
        } catch (error) {
            $task.toggleClass('is-completed', isCompleted);
            $task.data('isCompleted', isCompleted);

            const message = error.responseJSON?.message || 'Ошибка редактирования';
            showToast(message);
        } finally {
            $btn.prop('disabled', false);
        }
    });

    // ---  МОДАЛЬНОЕ ОКНО И АВТОРЕСАЙЗ ---

    //  Открытие модального окна задачи
    $(document).on('click', '.task-card', function () {
        const $card = $(this);
        const $modal = $('#cardModal');
        const taskId = $(this).data('taskId');
        $modal.data('taskId', taskId);
        $modal.data('activeCard', $card);

        const taskTitle = $(this).find('.task-title').text().trim();
        const mainText = $(this).data('mainText');

        $('#modalCardTitle').val(taskTitle);
        $('#modalCardDescription').val(mainText);
        bootstrap.Modal.getOrCreateInstance('#cardModal').show();
    });

    //  Сохранение изменений из модального окна
    $('#btnSaveCard').on('click', async function () {
        const $btn = $(this);
        const $modal = $('#cardModal');
        const $titleInput = $('#modalCardTitle');
        const taskId = $modal.data('taskId');
        const $card = $modal.data('activeCard');
        const newTitle = $titleInput.val().trim();

        $titleInput.removeClass('is-invalid');

        if (!newTitle) {
            $titleInput.addClass('is-invalid');
            return;
        }
        const newDescription = $('#modalCardDescription').val().trim();

        $btn.prop('disabled', true);

        try {
            await updateTask(taskId, { label_text: newTitle, main_text: newDescription });

            $card.find('.task-title').text(newTitle);
            $card.data('mainText', newDescription);

            bootstrap.Modal.getInstance('#cardModal').hide();
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка редактирования';
            showToast(message);
        } finally {
            $btn.prop('disabled', false);
        }
    });

    //  Очистка валидации в модалке при вводе
    $('#cardModal').on('input', '.form-control', function () {
        $(this).removeClass('is-invalid');
    });

    //  Автоматическое изменение высоты textarea
    $(document).on('input', '.card-title-input, #modalCardTitle, #modalCardDescription', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    //  Сброс и подгонка высоты полей при открытии/закрытии модалки
    $('#cardModal').on('hidden.bs.modal', function () {
        $('#modalCardTitle, #modalCardDescription').css('height', '');
    });

    $('#cardModal').on('shown.bs.modal', function () {
        $('#modalCardTitle, #modalCardDescription').trigger('input');
    });
}