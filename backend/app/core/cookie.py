from starlette.responses import Response

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")

def delete_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")