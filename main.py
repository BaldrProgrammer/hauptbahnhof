from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from users.auth_router import router as auth_router
from users.router import router as users_router
from reliefs.router import router as reliefs_router
from stations.router import router as stations_router
from trains.router import router as trains_router
from tickets.router import router as tickets_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reliefs_router)
app.include_router(stations_router)
app.include_router(trains_router)
app.include_router(tickets_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
