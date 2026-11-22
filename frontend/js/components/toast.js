//  Bootstrap Toast
const toastEl = document.getElementById('errorToast');
const errorToast = bootstrap.Toast.getOrCreateInstance(toastEl, {
    delay: 4000
});

export function showToast(message) {
    $('#errorToastText').text(message);
    errorToast.show();
}