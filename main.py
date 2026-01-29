from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from users.auth_router import router as auth_router
from users.router import router as users_router
from relief.router import router as relief_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(relief_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)
