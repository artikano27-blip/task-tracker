
const BASE_URL = '/auth';

$.ajaxSetup({
  xhrFields: {
    withCredentials: true // 🍪 Браузер автоматически прикрепляет куки ко всем запросам
  },
  // другие глобальные настройки при необходимости
});


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

export function getUser(){
    return $.ajax({
        url: `${BASE_URL}/user`,
        method: 'GET',
    });
}

export function logoutUser() {
  return $.ajax({
    url: `${BASE_URL}/session`,
    method: 'DELETE',
    xhrFields: {
      withCredentials: true
    }
  });
}