from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

# JWT 配置
JWT_SECRET = settings.secret_key
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 天


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class CreateGuestRequest(BaseModel):
    username: str
    password: str
    allowed_emby_users: list[str] = []
    allowed_libraries: list[str] = []


class UpdateGuestRequest(BaseModel):
    password: Optional[str] = None
    allowed_emby_users: Optional[list[str]] = None
    allowed_libraries: Optional[list[str]] = None


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    allowed_emby_users: list[str]
    allowed_libraries: list[str]

    class Config:
        from_attributes = True


def hash_password(password: str) -> str:
    """哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


def create_token(user_id: int, username: str, is_admin: bool) -> str:
    """创建 JWT token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的 Token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前登录用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")
    
    payload = decode_token(credentials.credentials)
    user_id = payload.get("user_id")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """获取当前用户（可选）"""
    if not credentials:
        return None
    
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except:
        return None


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_token(user.id, user.username, user.is_admin)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "allowed_emby_users": user.allowed_emby_users or [],
            "allowed_libraries": user.allowed_libraries or [],
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return user


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    if not verify_password(request.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    user.password_hash = hash_password(request.new_password)
    await db.commit()
    
    return {"success": True, "message": "密码修改成功"}


# ============ 管理员功能 ============

@router.get("/guests", response_model=list[UserResponse])
async def get_guests(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有访客用户"""
    result = await db.execute(select(User).where(User.is_admin == False))
    return result.scalars().all()


@router.post("/guests", response_model=UserResponse)
async def create_guest(
    request: CreateGuestRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建访客用户"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    guest = User(
        username=request.username,
        password_hash=hash_password(request.password),
        is_admin=False,
        allowed_emby_users=request.allowed_emby_users,
        allowed_libraries=request.allowed_libraries,
    )
    db.add(guest)
    await db.commit()
    await db.refresh(guest)
    
    return guest


@router.put("/guests/{guest_id}", response_model=UserResponse)
async def update_guest(
    guest_id: int,
    request: UpdateGuestRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新访客用户"""
    result = await db.execute(select(User).where(User.id == guest_id, User.is_admin == False))
    guest = result.scalar_one_or_none()
    
    if not guest:
        raise HTTPException(status_code=404, detail="访客用户不存在")
    
    if request.password:
        guest.password_hash = hash_password(request.password)
    if request.allowed_emby_users is not None:
        guest.allowed_emby_users = request.allowed_emby_users
    if request.allowed_libraries is not None:
        guest.allowed_libraries = request.allowed_libraries
    
    await db.commit()
    await db.refresh(guest)
    
    return guest


@router.delete("/guests/{guest_id}")
async def delete_guest(
    guest_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除访客用户"""
    result = await db.execute(select(User).where(User.id == guest_id, User.is_admin == False))
    guest = result.scalar_one_or_none()
    
    if not guest:
        raise HTTPException(status_code=404, detail="访客用户不存在")
    
    await db.delete(guest)
    await db.commit()
    
    return {"success": True}


@router.post("/init")
async def init_admin(db: AsyncSession = Depends(get_db)):
    """初始化管理员账户（仅在没有管理员时可用）"""
    # 检查是否已有管理员
    result = await db.execute(select(User).where(User.is_admin == True))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="管理员已存在")
    
    # 从环境变量获取管理员账户
    admin_username = settings.admin_username
    admin_password = settings.admin_password
    
    if not admin_username or not admin_password:
        raise HTTPException(status_code=400, detail="请在环境变量中设置 ADMIN_USERNAME 和 ADMIN_PASSWORD")
    
    admin = User(
        username=admin_username,
        password_hash=hash_password(admin_password),
        is_admin=True,
        allowed_emby_users=[],
        allowed_libraries=[],
    )
    db.add(admin)
    await db.commit()
    
    return {"success": True, "message": "管理员账户创建成功"}


@router.get("/check-init")
async def check_init(db: AsyncSession = Depends(get_db)):
    """检查是否需要初始化"""
    result = await db.execute(select(User).where(User.is_admin == True))
    has_admin = result.scalar_one_or_none() is not None
    return {"initialized": has_admin}
