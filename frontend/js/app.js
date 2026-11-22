//  Инициализация сетевого слоя и интерцептора токенов
import './api/client.js';

//  API и компоненты интерфейса
import { getUser } from './api/authApi.js';
import { showUserProfile, showAuthForms } from './components/views.js';
import { loadBoard } from './components/board.js';
import { showToast } from './components/toast.js';

// 🖱 Обработчики событий
import { initAuthHandlers } from './handlers/authHandlers.js';
import { initBoardHandlers } from './handlers/boardHandlers.js';

//  Проверка сессии при запуске приложения
async function checkAuth() {
    try {
        const user = await getUser();
        showUserProfile(user);
        await loadBoard();
    } catch (error) {
        const message = error.responseJSON?.message || 'Ошибка аутентификации, повторите вход';
        showToast(message);
        showAuthForms();
    }
}

//  Запуск приложения после готовности DOM-дерева
$(() => {
    initAuthHandlers();
    initBoardHandlers();
    checkAuth();
});