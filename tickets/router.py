from fastapi import APIRouter, Depends, HTTPException, status
from users.schemas import SUserGet
from users.auth import get_current_user

router = APIRouter(prefix='/tickets', tags=['/tickets'])


@router.get('/km_price')
async def get_price_from_km(kilometers: float, user: SUserGet = Depends(get_current_user)):
    if user:
        if kilometers < 40:
            price = 15
        else:
            price = 15 + (kilometers-40)/4
        return (price / 100) * (100-user.ulga.discount)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not authorised.')
