from fastapi import APIRouter, HTTPException, status
from bezdarsql import select, insert
from stations.models import Station
from stations.schemas import SStation

router = APIRouter(prefix='/stations', tags=['/stations'])


@router.get('/')
async def get_all_stations():
    return select(Station, value='*')


@router.get('/{station_id}')
async def get_station_by_id(station_id: str):
    station = select(Station, filter_by={Station.id: station_id})
    if station:
        return station
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='station not found.')


@router.post('/add')
async def add_station(station: SStation) -> dict:
    new_station = Station(**station.model_dump())
    insert(new_station)
    return {'ok': True}
