from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from users.models import User
from users.schemas import SUserReg

from bezdarsql import select, insert

router = APIRouter(prefix='/auth')


@router.post('/register')
async def register(user: SUserReg):
    if not select(User, filter_by={'username': user.username}):
        new_user = User(**user.model_dump(), tickets='{}')
        insert(new_user)
        return {'ok': True}
    else:
        return HTTPException(
            status.HTTP_409_CONFLICT,
            'пользователь уже существует'
        )
