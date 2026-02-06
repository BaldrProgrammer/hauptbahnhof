from fastapi import APIRouter, Depends, HTTPException, status
from bezdarsql import select, insert
from trains.models import Train
from trains.schemas import STrain
from users.schemas import SUserGet
from users.auth import get_current_user

router = APIRouter(prefix='/trains', tags=['/trains'])


@router.get('/')
async def get_all_trains() -> list[STrain]:
    return select(Train, value='*', count=-1)


@router.get('/{train_id}')
async def get_relief_by_id(train_id: str) -> STrain:
    train = select(Train, filter_by={Train.id: train_id})[0]
    if train:
        return train
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='train not found.')


@router.post('/add')
async def add_train(train: STrain, user: SUserGet = Depends(get_current_user)):
    if not select(Train, filter_by={Train.id: train.id}):
        if user.role == 'admin':
            new_instance = Train(**train.model_dump())
            insert(new_instance)
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin and not followed to change stations')
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='train already exists.')
