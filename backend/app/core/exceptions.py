
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
    message = "Auth Service Error: пользователь с таким именем уже существует."
    code = "USER_ALREADY_EXISTS"

class UserEmailAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "Auth Service Error: пользователь с таким email уже существует."
    code = "USER_EMAIL_ALREADY_EXISTS"


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Auth Service Error: неверное имя пользователя или пароль."
    code = "INVALID_CREDENTIALS"


class InvalidTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Auth Service Error: неверный токен"
    code = "INVALID_TOKEN"

class TokenCompromisedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Auth Service Error: Сеанс истек или стал недействительным. Пожалуйста, войдите в систему снова."
    code = "TOKEN_COMPROMISED"


class ExpiredTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Auth Service Error: токен просрочен"
    code = "TOKEN_EXPIRED"

class UnsupportedMediaTypeError(AppException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message = "Auth Service Error: неподдерживаемый формат данных"
    code = "UNSUPPORTED_MEDIA_TYPE"

class TaskNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Task Service Error: задача не найдена"
    code = "TASK_NOT_FOUND"

class TaskAccessDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Task Service Error: доступ к ресурсу запрещен"



