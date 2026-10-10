import uuid

from fastapi import status

class AppException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Внутренняя ошибка сервера"
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str | None = None, **kwargs):
        if message:
            self.message = message
        self.extra = kwargs
        super().__init__(self.message)


class UserAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "Ошибка сервиса аутентификации: пользователь с таким именем уже существует."
    code = "USER_ALREADY_EXISTS"

class UserEmailAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "Ошибка сервиса аутентификации: пользователь с таким email уже существует."
    code = "USER_EMAIL_ALREADY_EXISTS"


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Ошибка сервиса аутентификации: неверное имя пользователя или пароль."
    code = "INVALID_CREDENTIALS"


class InvalidTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Ошибка сервиса аутентификации: неверный токен"
    code = "INVALID_TOKEN"

class TokenCompromisedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Ошибка сервиса аутентификации: Сеанс истек или стал недействительным. Пожалуйста, войдите в систему снова. "
    code = "TOKEN_COMPROMISED"


class ExpiredTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Ошибка сервиса аутентификации: токен просрочен"
    code = "TOKEN_EXPIRED"

class UnsupportedMediaTypeError(AppException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message = "Ошибка сервиса аутентификации: неподдерживаемый формат данных"
    code = "UNSUPPORTED_MEDIA_TYPE"






