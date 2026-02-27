from fastapi import APIRouter, Depends, HTTPException, status

from reliefs.models import Relief
from reliefs.schemas import SReliefGet, SReliefAdd
from users.schemas import SUserGet
from users.auth import get_current_user

from bezdarsql import select, insert, update, delete

router = APIRouter(prefix='/reliefs', tags=['/reliefs'])


@router.get('/{relief_id}')
async def get_relief_by_id(relief_id: int):
    relief = select(Relief, filter_by={Relief.id: relief_id})
    if not relief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='relief not found.')
    return relief[0]


@router.post('/add')
async def add_relief(new_relief: SReliefAdd, user: SUserGet = Depends(get_current_user)) -> dict:
    if user.role == 'admin':
        relief = Relief(**new_relief.model_dump())
        insert(relief)
        return {'ok': True, 'new_instance': select(Relief, filter_by={Relief.title: new_relief.title})}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to create reliefs.')


@router.patch('/update')
async def update_relief(relief_id: str, row: str, value: str, user: SUserGet = Depends(get_current_user)):
    if user.role == 'admin':
        if select(Relief, filter_by={Relief.id: relief_id}):
            update(Relief, values={getattr(Relief, row): value}, where={Relief.id: relief_id})
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Relief not found.')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to change reliefs')


@router.delete('/remove/{relief_id}')
async def remove_relief_by_id(relief_id: int, user: SUserGet = Depends(get_current_user)) -> dict:
    if user.role == 'admin':
        if select(Relief, filter_by={Relief.id: relief_id}):
            delete(Relief, where={Relief.id: relief_id})
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'relief id={relief_id} doesn\'t exists.')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to create reliefs.')
