import { sendRefreshTokenRequest } from './authApi.js';
import { handleSessionExpired } from '../components/views.js';

let refreshPromise = null;

//  Настройка передачи сессионных cookies для всех запросов
$.ajaxSetup({
    xhrFields: { withCredentials: true }
});

const originalAjax = $.ajax;

//  Глобальный перехватчик для бесшовного обновления токена
$.ajax = async function (options) {
    try {
        return await originalAjax(options);
    } catch (error) {
        const originalRequest = options;
        const url = originalRequest.url || '';

        // Пропускаем ошибки не 401 или служебные роуты авторизации
        if (
            error.status !== 401 ||
            url.includes('/auth/login') ||
            url.includes('/auth/session') ||
            url.includes('/auth/refresh')
        ) {
            throw error;
        }

        try {
            // Если процесс обновления ещё не запущен — создаём единый промис для очереди
            if (!refreshPromise) {
                refreshPromise = Promise.resolve(sendRefreshTokenRequest()).finally(() => {
                    refreshPromise = null;
                });
            }

            // Ожидаем завершения обновления токена
            await refreshPromise;

            // Повторяем исходный запрос с обновлённой сессией
            return await originalAjax(originalRequest);
        } catch (refreshErr) {
            handleSessionExpired();
            throw refreshErr;
        }
    }
};