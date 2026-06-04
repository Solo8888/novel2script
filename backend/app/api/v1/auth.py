from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.security import create_access_token, verify_password, hash_password
from app.api.deps import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# 硬编码测试用户（密码为 "secret" 的哈希）
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGbvGJ.",
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """用户登录，返回 JWT 令牌"""
    user = FAKE_USERS_DB.get(login_data.username)
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
async def get_protected(current_user: dict = Depends(get_current_user)):
    """受保护的测试路由"""
    return {"message": "You are authenticated", "user": current_user}
