import { loginUser, registerUser, logoutUser } from '../api/authApi.js';
import { showUserProfile, showAuthForms } from '../components/views.js';
import { loadBoard } from '../components/board.js';
import { showToast } from '../components/toast.js';

//  Инициализация обработчиков авторизации и регистрации
export function initAuthHandlers() {
    //  Очистка подсветки ошибок валидации при начале ввода
    $('#register-form, #login-form').on('input', '.form-control', function () {
        $(this).removeClass('is-invalid');
    });

    //  Вход в систему
    $('#login-form').on('submit', async function (event) {
        event.preventDefault();
        const data = {
            username: $('#login-username').val().trim(),
            password: $('#login-password').val().trim()
        };

        $('#login-username, #login-password').removeClass('is-invalid');
        $('#loginBtn').prop('disabled', true);

        try {
            const user = await loginUser(data);
            showUserProfile(user);
            await loadBoard();
        } catch (error) {
            if (error.responseJSON?.code === 'INVALID_CREDENTIALS') {
                $('#login-username, #login-password').addClass('is-invalid');
            } else {
                const message = error.responseJSON?.message || 'Ошибка авторизации';
                showToast(message);
            }
        } finally {
            $('#loginBtn').prop('disabled', false);
        }
    });

    //  Регистрация нового аккаунта
    $('#register-form').on('submit', async function (event) {
        event.preventDefault();
        const data = {
            username: $('#reg-username').val(),
            email: $('#reg-email').val(),
            password: $('#reg-password').val()
        };

        $('#reg-username, #reg-email, #reg-confirm-password').removeClass('is-invalid');
        $('#regBtn').prop('disabled', true);

        if ($('#reg-confirm-password').val() !== data.password) {
            $('#reg-confirm-password').addClass('is-invalid');
            $('#regBtn').prop('disabled', false);
            return;
        }

        try {
            await registerUser(data);
            const user = await loginUser({ username: data.username, password: data.password });
            showUserProfile(user);
            await loadBoard();
        } catch (error) {
            if (error.responseJSON?.code === 'USER_ALREADY_EXISTS') {
                $('#reg-username').addClass('is-invalid');
            } else if (error.responseJSON?.code === 'USER_EMAIL_ALREADY_EXISTS') {
                $('#reg-email').addClass('is-invalid');
            } else {
                const message = error.responseJSON?.message || 'Ошибка регистрации';
                showToast(message);
            }
        } finally {
            $('#regBtn').prop('disabled', false);
        }
    });

    //  Выход из профиля
    $('#logout-btn').on('click', async function (event) {
        event.preventDefault();
        try {
            await logoutUser();
            showAuthForms();
        } catch (error) {
            const message = error.responseJSON?.message || 'Ошибка сервиса аутентификации';
            showToast(message);
        }
    });
}