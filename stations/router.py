from fastapi import APIRouter, HTTPException, status
from bezdarsql import select
from stations.models import Station

router = APIRouter(prefix='/stations', tags=['/stations'])


@router.get('/{station_id}')
async def get_station_by_id(station_id: str):
    station = select(Station, filter_by={Station.id: station_id})
    if station:
        return select(Station, filter_by={Station.id: station_id})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='station not found.')
