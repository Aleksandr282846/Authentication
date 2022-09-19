#FastAPI server
import hashlib
import base64
import hmac
import json

from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response

app = FastAPI()

SECRET_KEY = "9917aee0eb4235619dc1ab751067a0479b7bb36fa80ee229d21ee257cca6023b"
PASSWORD_SALT = "2524014cbb3ff8a60016d646e2be42895ebf6eb710929a56710934fec92a7287"

def sign_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


users = {
    "alexey@user.com": {
        "name": "Алексей",
        "password": "some_password_1",
        "balance": 100_000
    },
    "petr@user.com": {
        "name": "Пётр",
        "password": "some_password_2",    
        "balance": 555_555
    }
}





@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    


    try:
        user = users[valid_username] 
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(
        f"Привет, {users[valid_username]['name']}!<br />"
        f"Баланс: {users[valid_username]['balance']}", 
        media_type="text/html")
    
 
@app.post('/login')
def process_login_page(username : str = Form(...), password : str = Form(...)):
    user = users.get(username)
    if not user or user['password'] != password:
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю!"
            }),
            media_type="application/json")

    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}!<br />Баланс: {user['balance']}"
        }),
        media_type = 'application/json')
    
    username_signed = base64.b64encode(username.encode()).decode() + "." + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
