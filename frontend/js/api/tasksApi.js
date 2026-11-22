const BASE_URL = '/tasks';

export function getTasks() {
    return $.ajax({
        url: `${BASE_URL}/`,
        method: 'GET'
    });
}

export function createTask(taskData) {
    return $.ajax({
        url: `${BASE_URL}/`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(taskData)
    });
}

export function updateTask(taskId, taskData) {
    return $.ajax({
        url: `${BASE_URL}/${taskId}`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify(taskData)
    });
}

export function deleteTask(taskId) {
    return $.ajax({
        url: `${BASE_URL}/${taskId}`,
        method: 'DELETE'
    });
}

export function moveTask(taskId, moveData) {
    return $.ajax({
        url: `${BASE_URL}/${taskId}/move`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify(moveData)
    });
}