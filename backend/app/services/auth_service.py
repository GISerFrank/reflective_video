# backend/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.user import User
from ..config import settings

class AuthService:
    """
    认证服务
    处理用户注册、登录、JWT令牌等认证相关功能
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """对密码进行哈希处理"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT访问令牌"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return {"username": username, "payload": payload}
        except JWTError:
            return None

    def authenticate_user(self, username: str, password: str, db: Session) -> Optional[User]:
        """验证用户登录"""
        user = self.get_user_by_username(username, db)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_username(self, username: str, db: Session) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str, db: Session) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int, db: Session) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    def register_user(self, username: str, email: str, password: str, db: Session) -> Dict:
        """
        用户注册
        """
        # 1. 验证用户名是否已存在
        if self.get_user_by_username(username, db):
            return {
                "success": False,
                "error": "用户名已存在",
                "code": "USERNAME_EXISTS"
            }

        # 2. 验证邮箱是否已存在
        if self.get_user_by_email(email, db):
            return {
                "success": False,
                "error": "邮箱已被注册",
                "code": "EMAIL_EXISTS"
            }

        # 3. 验证密码强度
        password_check = self._validate_password(password)
        if not password_check["valid"]:
            return {
                "success": False,
                "error": password_check["error"],
                "code": "WEAK_PASSWORD"
            }

        # 4. 创建新用户
        hashed_password = self.get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            is_active=True,
            is_verified=False  # 邮箱验证功能可以后续添加
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 5. 创建访问令牌
        access_token = self.create_access_token(
            data={"sub": new_user.username, "user_id": new_user.id}
        )

        return {
            "success": True,
            "user": new_user,
            "access_token": access_token,
            "token_type": "bearer"
        }

    def login_user(self, username: str, password: str, db: Session) -> Dict:
        """
        用户登录
        """
        # 1. 验证用户凭据
        user = self.authenticate_user(username, password, db)
        if not user:
            return {
                "success": False,
                "error": "用户名或密码错误",
                "code": "INVALID_CREDENTIALS"
            }

        # 2. 检查账户状态
        if not user.is_active:
            return {
                "success": False,
                "error": "账户已被禁用",
                "code": "ACCOUNT_DISABLED"
            }

        # 3. 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()

        # 4. 创建访问令牌
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return {
            "success": True,
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }

    def _validate_password(self, password: str) -> Dict:
        """
        验证密码强度
        """
        if len(password) < 8:
            return {"valid": False, "error": "密码长度至少8位"}

        if len(password) > 50:
            return {"valid": False, "error": "密码长度不能超过50位"}

        # 检查是否包含字母和数字
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_letter and has_digit):
            return {"valid": False, "error": "密码必须包含字母和数字"}

        return {"valid": True}

    def change_password(self, user_id: int, old_password: str, new_password: str, db: Session) -> Dict:
        """
        修改密码
        """
        # 1. 获取用户
        user = self.get_user_by_id(user_id, db)
        if not user:
            return {
                "success": False,
                "error": "用户不存在",
                "code": "USER_NOT_FOUND"
            }

        # 2. 验证旧密码
        if not self.verify_password(old_password, user.hashed_password):
            return {
                "success": False,
                "error": "当前密码错误",
                "code": "INVALID_OLD_PASSWORD"
            }

        # 3. 验证新密码强度
        password_check = self._validate_password(new_password)
        if not password_check["valid"]:
            return {
                "success": False,
                "error": password_check["error"],
                "code": "WEAK_PASSWORD"
            }

        # 4. 检查新密码是否与旧密码相同
        if self.verify_password(new_password, user.hashed_password):
            return {
                "success": False,
                "error": "新密码不能与当前密码相同",
                "code": "SAME_PASSWORD"
            }

        # 5. 更新密码
        user.hashed_password = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "message": "密码修改成功"
        }

    def update_user_profile(self, user_id: int, username: Optional[str], email: Optional[str], db: Session) -> Dict:
        """
        更新用户资料
        """
        user = self.get_user_by_id(user_id, db)
        if not user:
            return {
                "success": False,
                "error": "用户不存在",
                "code": "USER_NOT_FOUND"
            }

        # 检查用户名是否已被占用
        if username and username != user.username:
            existing_user = self.get_user_by_username(username, db)
            if existing_user:
                return {
                    "success": False,
                    "error": "用户名已被占用",
                    "code": "USERNAME_EXISTS"
                }
            user.username = username

        # 检查邮箱是否已被占用
        if email and email != user.email:
            existing_user = self.get_user_by_email(email, db)
            if existing_user:
                return {
                    "success": False,
                    "error": "邮箱已被注册",
                    "code": "EMAIL_EXISTS"
                }
            user.email = email
            user.is_verified = False  # 邮箱变更后需要重新验证

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "user": user
        }

    def deactivate_user(self, user_id: int, db: Session) -> Dict:
        """
        停用用户账户
        """
        user = self.get_user_by_id(user_id, db)
        if not user:
            return {
                "success": False,
                "error": "用户不存在"
            }

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "message": "账户已停用"
        }

    def get_user_stats(self, user_id: int, db: Session) -> Optional[Dict]:
        """
        获取用户统计信息
        """
        user = self.get_user_by_id(user_id, db)
        if not user:
            return None

        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "videos_completed": user.videos_completed,
            "reflections_written": user.reflections_written,
            "comments_approved": user.comments_approved,
            "originality_score": user.originality_score,
            "member_since": user.created_at.strftime("%Y-%m-%d") if user.created_at else None,
            "last_login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }

    def validate_token_and_get_user(self, token: str, db: Session) -> Optional[User]:
        """
        验证令牌并返回用户对象
        用于依赖注入的认证中间件
        """
        token_data = self.verify_token(token)
        if not token_data:
            return None

        username = token_data["username"]
        user = self.get_user_by_username(username, db)

        if not user or not user.is_active:
            return None

        return user

    def refresh_token(self, old_token: str, db: Session) -> Dict:
        """
        刷新访问令牌
        """
        token_data = self.verify_token(old_token)
        if not token_data:
            return {
                "success": False,
                "error": "无效的令牌",
                "code": "INVALID_TOKEN"
            }

        username = token_data["username"]
        user = self.get_user_by_username(username, db)

        if not user or not user.is_active:
            return {
                "success": False,
                "error": "用户不存在或已被禁用",
                "code": "USER_INACTIVE"
            }

        # 创建新的访问令牌
        new_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return {
            "success": True,
            "access_token": new_token,
            "token_type": "bearer"
        }