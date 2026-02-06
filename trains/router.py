from fastapi import APIRouter, Depends, HTTPException, status
from bezdarsql import select
from trains.models import Train
from trains.schemas import STrain
from users.schemas import SUserGet
from users.auth import get_current_user

router = APIRouter(prefix='/trains', tags=['/trains'])


@router.get('/')
async def get_all_trains() -> list[STrain]:
    return select(Train, value='*')


@router.get('/{train_id}')
async def get_relief_by_id(train_id: str) -> STrain:
    train = select(Train, filter_by={Train.id: train_id})
    if train:
        return train
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='train not found.')
