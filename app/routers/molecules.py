from fastapi import APIRouter, HTTPException
from app.schemas import MoleculeCreate, MoleculeResponse, MoleculeUpdate
from app.repositories import molecule_repository as mr
from app.services.chemistry import derive_molecule_properties_from_smiles
import sqlite3

router = APIRouter(prefix='/molecules', tags=['molecules'])

@router.post('', response_model=MoleculeResponse)
def create_molecule(molecule: MoleculeCreate):
    molecule_data = molecule.model_dump()

    try:
        derived_molecule_data = derive_molecule_properties_from_smiles(
            molecule_data['smiles']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    molecule_data.update(derived_molecule_data)

    search_result = mr.find_molecule_by_inchikey(
        derived_molecule_data['inchikey']
    )

    if search_result is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Duplicate molecule detected",
                "formula": derived_molecule_data["formula"],
                "inchikey": derived_molecule_data["inchikey"],
                "existing_molecule_id": search_result["id"],
            },
        )
    try:
        created_molecule = mr.create_molecule(molecule_data)
    except sqlite3.IntegrityError as e:
        existing_molecule = mr.find_molecule_by_inchikey(derived_molecule_data['inchikey'])
        raise HTTPException(status_code=409, detail={
            'message': 'Duplicate molecule detected',
            'formula': derived_molecule_data['formula'],
            'inchikey': derived_molecule_data['inchikey'],
            'existing_molecule_id': existing_molecule['id'] if existing_molecule else None,
        })

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