from fastapi import APIRouter, Depends, HTTPException, status

from relief.models import Relief
from relief.schemas import SReliefGet, SReliefAdd
from users.schemas import SUserGet
from users.auth import get_current_user

from bezdarsql import select, insert, delete

router = APIRouter(prefix='/relief', tags=['/relief'])


@router.get('/current')
async def current_relief(user: SUserGet = Depends(get_current_user)) -> SReliefGet | None:
    if user:
        relief = select(Relief, filter_by={'id': user.ulga})[0]
        return relief
    return None


@router.post('/add')
async def add_relief(new_relief: SReliefAdd, user: SUserGet = Depends(get_current_user)) -> dict:
    if user.role == 'admin':
        relief = Relief(**new_relief.model_dump())
        insert(relief)
        return {'ok': True, 'new_instance': select(Relief, filter_by={'title': new_relief.title})}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin and not followed to create reliefs.')


@router.delete('/{relief_id}')
async def add_relief(relief_id: int, user: SUserGet = Depends(get_current_user)) -> dict:
    if user.role == 'admin':
        delete(Relief, where={'id': relief_id})
        return {'ok': True}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin and not followed to create reliefs.')

