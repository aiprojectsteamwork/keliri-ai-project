from fastapi import APIRouter
from app.api.v1.routes import brands, branches, offers, location

api_router = APIRouter()

api_router.include_router(brands.router)
api_router.include_router(branches.router)
api_router.include_router(offers.router)
api_router.include_router(location.router)
