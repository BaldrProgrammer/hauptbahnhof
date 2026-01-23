from fastapi import APIRouter, Response, status
from fastapi.exceptions import HTTPException
from users.auth import jwt_encode, get_hash_password, verify_password
from users.models import User
from users.schemas import SUserReg, SUserLog

from bezdarsql import select, insert

router = APIRouter(prefix='/auth')


@router.post('/register')
async def register(user: SUserReg):
    if not select(User, filter_by={'username': user.username}):
        user.password = await get_hash_password(user.password)
        new_user = User(**user.model_dump(), tickets='{}')
        insert(new_user)
        return {'ok': True}

    return HTTPException(
        status.HTTP_409_CONFLICT,
        'пользователь уже существует'
    )


@router.post('/login')
async def login(auth_data: SUserLog, response: Response):
    if user := select(User, filter_by={'username': auth_data.username}):
        if await verify_password(auth_data.password, user[0].password):
            token = await jwt_encode({'uid': user[0].id})
            response.set_cookie('access_token', token)
            return {'ok': True}

        return HTTPException(
            status.HTTP_403_FORBIDDEN,
            'неправильный логин или пароль'
        )

    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        'пользователя не существует'
    )

