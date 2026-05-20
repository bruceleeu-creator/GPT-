from fastapi import APIRouter
from app.models import SourceResponse
from app.crud import get_sources

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceResponse])
def list_sources():
    return get_sources()
