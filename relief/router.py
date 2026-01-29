from fastapi import APIRouter, Depends

from relief.models import Relief
from relief.schemas import SReliefGet
from users.schemas import SUserGet
from users.auth import get_current_user

from bezdarsql import select

router = APIRouter(prefix='/relief', tags=['/relief'])


@router.get('/current')
async def current_relief(user: SUserGet = Depends(get_current_user)) -> SReliefGet | None:
    print(user)
    if user:
        relief = select(Relief, filter_by={'id': user.ulga})[0]
        return relief
    return None
