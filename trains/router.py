from fastapi import APIRouter
from bezdarsql import select
from trains.models import Train

router = APIRouter(prefix='/trains', tags=['/trains'])


@router.get('/')
async def get_all_trains():
    return select(Train, value='*')
