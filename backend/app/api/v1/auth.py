from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.security import create_access_token, verify_password
from app.api.deps import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ============== ⚠️ 注意 ==============
# 这是一个模拟登录端点，仅用于演示认证流程
# 在后续 PR 中将连接真实数据库查询用户
#
# 测试凭证:
#   Email: test@example.com
#   Password: secret
# ============== ⚠️ 注意 ==============
FAKE_USERS_DB = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGbvGJ.",
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """[演示用途] 用户登录，返回 JWT 令牌"""
    user = FAKE_USERS_DB.get(login_data.email)
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "user_id": current_user.get("sub"),
        "email": "test@example.com",
        "message": "This is a mock user data for demonstration purposes"
    }
