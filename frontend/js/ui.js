
function switchView(viewId) {
    $('.app-view').addClass('d-none');$(`#${viewId}`).removeClass('d-none');
}

export function showError(message) {
    $('#auth-alert').removeClass('d-none alert-success').addClass('alert-danger').text(message);
}

export function showUserProfile(user) {
    switchView('profile-view');
    $('#current-username').text(user.username);
}

export function showAuthForms() {
    switchView('auth-view');
    $('#login-form')[0].reset();
    $('#register-form')[0].reset();
    $('#auth-alert').addClass('d-none');
    $('#current-username').text('');
}

export function handleSessionExpired() {
    showAuthForms();
    showError('Сессия истекла. Пожалуйста, войдите снова.');
}