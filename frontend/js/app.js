// 1. 📦 Импорты API-модулей
import { getUser, loginUser, registerUser, logoutUser } from './authApi.js';
import {showError, showUserProfile, showAuthForms, handleSessionExpired, renderTaskList, loadTasks} from "./ui.js";

// 2. ⚙️ Глобальная конфигурация сети (до выполнения любых запросов)
$.ajaxSetup({
    xhrFields: { withCredentials: true },
    statusCode: {
        401: function () {
            if (!this.url.includes('/auth/session') && !this.url.includes('/auth/login')) {
                handleSessionExpired();
            }
        }
    }
});

$('#login-form').on('submit', async function (event) {
    event.preventDefault();
    const data = {
        username: $('#login-username').val(),
        password: $('#login-password').val()
    };
    try {
        const user = await loginUser(data);
        showUserProfile(user);
        await loadTasks()
    } catch (error) {
        const message = error.responseJSON?.message || 'Неверный логин или пароль';
        showError(message);
    }
});

$('#register-form').on('submit', async function (event) {
    event.preventDefault();
    const data = {
        username: $('#reg-username').val(),
        email: $('#reg-email').val(),
        password: $('#reg-password').val()
    };
    if ($('#reg-confirm-password').val() !== data.password) {
        showError('Пароли не совпадают');
        return;
    }
    try {
        await registerUser(data);
        const user = await loginUser({ username: data.username, password: data.password });
        showUserProfile(user);
    } catch (error) {
        const message = error.responseJSON?.message || 'Ошибка сервиса аутентификации';
        showError(message);
    }
});

$('#logout-btn').on('click', async function (event) {
    event.preventDefault();
    try {
        await logoutUser();
        showAuthForms();
    } catch (error) {
        const message = error.responseJSON?.message || 'Ошибка сервиса аутентификации';
        showError(message);
    }
});

async function checkAuth() {
    try {
        const user = await getUser();
        showUserProfile(user);
        await loadTasks();
    } catch (error) {
        showAuthForms();
    }
}

$(checkAuth);