import {requestWithAuth} from "./apiClient.js";

const BASE_URL = '/auth';

export function registerUser(userData) {
    return $.ajax({
        url: `${BASE_URL}/user`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(userData),
    });
}

export function loginUser(credentials) {
    return $.ajax({
        url: `${BASE_URL}/session`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(credentials),
    });
}

export function getUser() {
    return requestWithAuth(`${BASE_URL}/user`, { method: 'GET' });
}

export function logoutUser() {
    return requestWithAuth('/session/', { method: 'POST' });
}

export function sendRefreshTokenRequest() {
    return $.ajax({
        url: `${BASE_URL}/refresh`,
        method: 'POST',
    });
}