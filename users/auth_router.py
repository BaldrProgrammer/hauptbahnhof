from fastapi import APIRouter
from users.models import User
from users.schemas import SUserReg

from bezdarsql import insert


router = APIRouter(prefix='/auth')

@router.post('/register')
async def register(user: SUserReg):
    new_user = User(**user.model_dump(), tickets='{1, 2, 3}')
    insert(new_user)
