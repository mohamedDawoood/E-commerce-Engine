from typing import Annotated
from fastapi import Depends
from app.models.user import User
from app.core.security import get_current_user, is_admin

user_dependency = Annotated[User, Depends(get_current_user)]
admin_user = Annotated[User, Depends(is_admin)]