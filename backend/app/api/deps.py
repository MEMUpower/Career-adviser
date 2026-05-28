from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.models.models import User, UserRole
from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.logging import log_audit
from typing import List

# Header key
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header)
) -> User:
    if not token:
        raise AuthenticationError("Authorization 헤더가 누락되었습니다.")
    
    # Check if "Bearer " format
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("유효하지 않거나 만료된 토큰입니다.")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("토큰 페이로드가 누락되었습니다.")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("해당 유저를 찾을 수 없습니다.")
        
    # Store IP for audit
    request.state.user_id = user.id
    request.state.user_role = user.role
    
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise PermissionDeniedError(f"허용되지 않은 역할입니다. 필요한 권한: {[r.value for r in self.allowed_roles]}")
        return current_user
