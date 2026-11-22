import { showToast } from './toast.js';

//  Вспомогательное переключение активного экрана
function switchView(viewId) {
    $('.app-view').addClass('d-none');
    $(`#${viewId}`).removeClass('d-none');
}

//  Переход к доске задач и отображение имени пользователя
export function showUserProfile(user) {
    switchView('tasks-view');
    $('#current-username').text(user.username);
    $('#app-navbar').removeClass('d-none');
}

//  Возврат к экрану авторизации и сброс полей ввода
export function showAuthForms() {
    switchView('auth-view');
    $('#login-form')[0].reset();
    $('#register-form')[0].reset();
    $('#login-form, #register-form').find('.is-invalid').removeClass('is-invalid');
    $('#app-navbar').addClass('d-none');
    $('#current-username').text('');
}

//  Реакция на устаревшую или недействительную сессию
export function handleSessionExpired() {
    showAuthForms();
    showToast('Сессия истекла. Пожалуйста, войдите снова.');
}