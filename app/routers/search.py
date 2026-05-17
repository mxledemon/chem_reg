from fastapi import APIRouter, HTTPException, Query
from app.repositories import molecule_repository as mr

router = APIRouter(prefix='/search')

@router.get('/molecules')
def search_molecules(
    name: str | None = Query(default=None),
    formula: str | None = Query(default=None),
    inchikey: str | None = Query(default=None),
    min_weight: float | None = Query(default=None, ge=0),
    max_weight: float | None = Query(default=None, ge=0),
    project: str | None = Query(default=None),
    chemist: str | None = Query(default=None),
):
    
    if (
        min_weight is not None
        and max_weight is not None
        and min_weight > max_weight
    ):
        raise HTTPException(status_code=400, detail='min_weight cannot be greater than max_weight')

    return mr.search_molecules(
        name=name,
        formula=formula,
        inchikey=inchikey,
        min_weight=min_weight,
        max_weight=max_weight,
        project=project,
        chemist=chemist,
    )