from fastapi import APIRouter, Depends
from users.auth import get_current_user
from users.schemas import SUserGet

router = APIRouter(prefix='/users', tags=['/users'])


@router.get('/current')
async def current_user(user: SUserGet = Depends(get_current_user)):
    return user
