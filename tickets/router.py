from fastapi import APIRouter, Depends, HTTPException, status
from users.schemas import SUserGet
from users.auth import get_current_user

router = APIRouter(prefix='/tickets')


@router.get('/km_price')
async def get_price_from_km(kilometers: float, user: SUserGet = Depends(get_current_user)):
    if kilometers < 40:
        price = 15
    else:
        price = 15 + (kilometers-40)/4
    return price
