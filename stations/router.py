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
    return select(Station, value='*', count=-1)


@router.get('/distance')
async def get_distance_between(stations: str):
    ids = stations.split(',')
    lat1, lon1 = select(Station, filter_by={Station.id: ids[0]})[0].coordinates.split(', ')
    lat2, lon2 = select(Station, filter_by={Station.id: ids[1]})[0].coordinates.split(', ')

    distance = get_distance_km(float(lat1), float(lon1), float(lat2), float(lon2))
    return {'raw': distance, 'countable': round(distance)}


@router.get('/get_route')
async def get_route(start_station: int, end_station: int) -> list:
    all_trains = select(Train, value='*', count=-1)
    start_station = select(Station, filter_by={Station.id: str(start_station)})
    end_station = select(Station, filter_by={Station.id: str(end_station)})
    if start_station and end_station:
        start_station, end_station = start_station[0], end_station[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stations does not exist.')
    result = []
    distance = 0
    for train in all_trains:
        start = None
        for station in train.schedule:
            if station[0] == start_station.title or start:
                if not start:
                    start = station.copy()
                if result:
                    lat1, lon1 = select(Station, filter_by={Station.title: result[-1][0]})[0].coordinates.split(', ')
                    lat2, lon2 = select(Station, filter_by={Station.title: station[0]})[0].coordinates.split(', ')
                    distance += get_distance_km(float(lat1), float(lon1), float(lat2), float(lon2))
                result.append(station)
                if station[0] == end_station.title:
                    result.append((train.id, train.model, distance))
                    return result
        result.clear()
        distance = 0
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Connections not found.')


def _parse_hm(value: str) -> int | None:
    try:
        h, m = value.strip().split(':', 1)
        return int(h) * 60 + int(m)
    except Exception:
        return None


@router.get('/get_routes')
async def get_routes(start_station: int, end_station: int) -> list[dict]:
    """
    Returns multiple connections (one per train) between two stations.

    Response item:
      - train_id, train_model
      - distance_km (float)
      - route: list of schedule rows from start to end (inclusive)
    """
    all_trains = select(Train, value='*', count=-1)
    start_station = select(Station, filter_by={Station.id: str(start_station)})
    end_station = select(Station, filter_by={Station.id: str(end_station)})
    if start_station and end_station:
        start_station, end_station = start_station[0], end_station[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stations does not exist.')

    connections: list[dict] = []

    for train in all_trains:
        result = []
        distance = 0.0
        started = False

        for station in train.schedule:
            if station[0] == start_station.title or started:
                if not started:
                    started = True

                if result:
                    prev = result[-1][0]
                    try:
                        lat1, lon1 = select(Station, filter_by={Station.title: prev})[0].coordinates.split(', ')
                        lat2, lon2 = select(Station, filter_by={Station.title: station[0]})[0].coordinates.split(', ')
                        distance += get_distance_km(float(lat1), float(lon1), float(lat2), float(lon2))
                    except Exception:
                        pass

                result.append(station)

                if station[0] == end_station.title:
                    connections.append(
                        {
                            'train_id': train.id,
                            'train_model': train.model,
                            'distance_km': distance,
                            'route': result,
                        }
                    )
                    break

    if not connections:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Connections not found.')

    # Sort by departure time (route first row time) if possible
    def _sort_key(conn: dict):
        route = conn.get('route') or []
        if route and len(route[0]) > 1:
            t = _parse_hm(str(route[0][1]))
            return t if t is not None else 10**9
        return 10**9

    connections.sort(key=_sort_key)
    return connections


@router.get('/{station_id}')
async def get_station_by_id(station_id: str):
    station = select(Station, filter_by={Station.id: station_id})
    if station:
        return station
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='station not found.')


@router.post('/add')
async def add_station(station: SStation, user: SUserGet = Depends(get_current_user)) -> dict:
    if user:
        if user.role == 'admin':
            if not select(Station, filter_by={Station.id: station.id}):
                new_station = Station(**station.model_dump())
                insert(new_station)
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Station already exists.')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin and not followed to add stations')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')


@router.patch('/update')
async def update_station(station_id: str, row: str, value: str, user=Depends(get_current_user)):
    if user:
        if user.role == 'admin':
            if select(Station, filter_by={Station.id: station_id}):
                update(Station, values={getattr(Station, row): value}, where={Station.id: station_id})
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Station not found.')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin and not followed to change stations')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')


@router.delete('/remove/{station_id}')
async def remove_station_by_id(station_id: str, user=Depends(get_current_user)):
    if user:
        if user.role == 'admin':
            if select(Station, filter_by={Station.id: station_id}):
                delete(Station, where={Station.id: station_id})
                return {'ok': True}
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Station does not exist.')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin and not followed to remove stations')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')
