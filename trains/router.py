from fastapi import APIRouter, Depends, HTTPException, status
from bezdarsql import select, insert, update, delete
from trains.models import Train
from trains.schemas import STrain
from users.schemas import SUserGet
from users.auth import get_current_user

router = APIRouter(prefix='/trains', tags=['/trains'])


@router.get('/')
async def get_all_trains() -> list[STrain]:
    return select(Train, value='*', count=-1)


@router.get('/{train_id}')
async def get_train_by_id(train_id: str) -> STrain:
    train = select(Train, filter_by={Train.id: train_id})[0]
    if train:
        return train
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Train not found.')


@router.post('/add')
async def add_train(train: STrain, user: SUserGet = Depends(get_current_user)):
    if user:
        if not select(Train, filter_by={Train.id: train.id}):
            if user.role == 'admin':
                new_instance = Train(**train.model_dump())
                insert(new_instance)
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You are not admin and not followed to add trains')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Train already exists.')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')


@router.patch('/update')
async def update_train(train_id: str, row: str, value: str, user=Depends(get_current_user)):
    if user:
        if user.role == 'admin':
            if select(Train, filter_by={Train.id: train_id}):
                update(Train, values={getattr(Train, row): value}, where={Train.id: train_id})
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Train not found.')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin and not followed to change trains')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')


@router.delete('/remove/{station_id}')
async def remove_station_by_id(train_id: str, user=Depends(get_current_user)):
    if user:
        if user.role == 'admin':
            if select(Train, filter_by={Train.id: train_id}):
                delete(Train, where={Train.id: train_id})
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Train does not exist.')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin and not followed to remove trains')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')
