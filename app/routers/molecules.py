from fastapi import APIRouter, HTTPException
from app.schemas import MoleculeCreate, MoleculeResponse, MoleculeUpdate
from app.repositories import molecule_repository as mr

router = APIRouter(prefix='/molecules', tags=['molecules'])

@router.post('', response_model=MoleculeResponse)
def create_molecule(molecule: MoleculeCreate):
    molecule_data = molecule.model_dump()
    created_molecule = mr.create_molecule(molecule_data)
    if created_molecule is None:
        raise HTTPException(status_code=500, detail='Failed to create molecule')
    return created_molecule


@router.get('/{molecule_id}', response_model=MoleculeResponse)
def get_molecule_by_id(molecule_id: int):
    result = mr.get_molecule_by_id(molecule_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f'Could not retrieve molecule with id {molecule_id}')
    return result


@router.get('', response_model=list[MoleculeResponse])
def get_molecules(limit: int = 10, offset: int = 0):
    result = mr.list_molecules(limit, offset)
    return result


@router.put('/{molecule_id}', response_model=MoleculeResponse)
def update_molecule(molecule_id: int, molecule_data: MoleculeUpdate):
    data = molecule_data.model_dump(exclude_unset=True)
    result = mr.update_molecule(molecule_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail='Could not update molecule')
    return result


@router.delete('/{molecule_id}')
def delete_molecule(molecule_id: int):
    result = mr.delete_molecule(molecule_id)
    if not result:
        raise HTTPException(status_code=404, detail=f'Could not delete molecule with id {molecule_id}')
    return {"deleted": True}