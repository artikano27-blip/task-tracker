import { requestWithAuth } from './apiClient.js';

const BASE_URL = '/tasks';

export async function getTasks() {
    return await requestWithAuth('/tasks/', {
        method: 'GET'
    });
}

export async function createTask(taskData) {
    return await requestWithAuth(`${BASE_URL}/`, {
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(taskData)
    });
}

export async function updateTaskStatus(taskId, status) {
    return await requestWithAuth(`${BASE_URL}/${taskId}`, {
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ status })
    });
}

export function deleteTask(taskId) {
    return requestWithAuth(`/tasks/${taskId}`, { method: 'DELETE' });
}


