from fastapi import APIRouter, Depends, HTTPException, status
from bezdarsql import select, insert, update, delete
from users.auth import get_current_user
from users.schemas import SUserGet
from trains.models import Train
from stations.models import Station
from stations.schemas import SStation
from probnik import get_distance_km

router = APIRouter(prefix='/stations', tags=['/stations'])


@router.get('/')
async def get_all_stations():
    return select(Station, value='*')


@router.get('/distance')
async def get_distance_between(stations: str):
    ids = stations.split(',')
    lat1, lon1 = select(Station, filter_by={Station.id: ids[0]})[0].coordinates.split(', ')
    lat2, lon2 = select(Station, filter_by={Station.id: ids[1]})[0].coordinates.split(', ')

    distance = get_distance_km(float(lat1), float(lon1), float(lat2), float(lon2))
    return {'raw': distance, 'countable': round(distance)}


@router.get('/get_route')
async def get_route(start_station: int, end_station: int):
    all_trains = select(Train, value='*')
    start_station = select(Station, filter_by={Station.id: str(start_station)})[0]
    end_station = select(Station, filter_by={Station.id: str(end_station)})[0]
    result = []
    for train in all_trains:
        start = None
        end = None
        for station in train.schedule:
            if station[0] == start_station.title or start:
                if not start:
                    start = station.copy()
                result.append(station)
                if station[0] == end_station.title:
                    end = station.copy()
                    result.append((train.id, train.model))
                    return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Connections not found.')


@router.get('/{station_id}')
async def get_station_by_id(station_id: str):
    station = select(Station, filter_by={Station.id: station_id})
    if station:
        return station
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='station not found.')


@router.post('/add')
async def add_station(station: SStation, user: SUserGet = Depends(get_current_user)) -> dict:
    if user.role == 'admin':
        if not select(Station, filter_by={Station.id: station.id}):
            new_station = Station(**station.model_dump())
            insert(new_station)
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Station already exists.')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to add stations')


@router.patch('/update')
async def update_station(station_id: str, row: str, value: str, user=Depends(get_current_user)):
    if user.role == 'admin':
        if select(Station, filter_by={Station.id: station_id}):
            update(Station, values={getattr(Station, row): value}, where={Station.id: station_id})
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Station not found.')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to change stations')


@router.delete('/remove/{station_id}')
async def remove_station_by_id(station_id: str, user=Depends(get_current_user)):
    if user.role == 'admin':
        if select(Station, filter_by={Station.id: station_id}):
            delete(Station, where={Station.id: station_id})
            return {'ok': True}
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Station does not exist.')
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='You are not admin and not followed to remove stations')
