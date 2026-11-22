
const BASE_URL = '/columns';

export function getColumns() {
    return $.ajax({
        url: `${BASE_URL}/`,
        method: 'GET'
    });
}

export function createColumn(columnData) {
    return $.ajax({
        url: `${BASE_URL}/`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(columnData)
    });
}

export function deleteColumn(columnId) {
    return $.ajax({
        url: `${BASE_URL}/${columnId}`,
        method: 'DELETE'
    });
}

export function moveColumn(columnId, moveData) {
    return $.ajax({
        url: `${BASE_URL}/${columnId}/move`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify(moveData)
    });
}

export function updateColumn(columnId, columnData) {
    return $.ajax({
        url: `${BASE_URL}/${columnId}`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify(columnData)
    });
}