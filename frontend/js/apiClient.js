import { handleSessionExpired } from './ui.js';
import { sendRefreshTokenRequest } from './authApi.js';

let refreshPromise = null;

export async function requestWithAuth(url, options = {}) {
    try {
        return await $.ajax({
            url,
            ...options
        });
    } catch (error) {
        // Если ошибка не 401 или это упал сам запрос рефреша — выбрасываем ошибку дальше
        if (error.status !== 401 || url.includes('/refresh')) {
            throw error;
        }

        // Если рефреш уже выполняется другим запросом, ждём его завершения
        if (!refreshPromise) {
            refreshPromise = sendRefreshTokenRequest()
                .finally(() => {
                    refreshPromise = null;
                });
        }

        try {
            await refreshPromise;
            // Повторяем исходный запрос после успешного обновления
            return await $.ajax({
                url,
                ...options
            });
        } catch (refreshError) {
            // Рефреш-токен невалиден — завершаем сессию
            handleSessionExpired();
            throw refreshError;
        }
    }
}