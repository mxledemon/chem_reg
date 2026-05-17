from fastapi import APIRouter, HTTPException, Response
from app.schemas import MoleculeCreate, MoleculeResponse, MoleculeUpdate
from app.repositories import molecule_repository as mr
from app.services.chemistry import derive_molecule_properties_from_smiles
from app.services.molecule_registration import register_molecule_from_smiles, InvalidMoleculeError, DuplicateMoleculeError, MoleculeRegistrationError
from app.services.molecule_rendering import render_molecule_png
import sqlite3

router = APIRouter(prefix='/molecules', tags=['molecules'])

@router.post('', response_model=MoleculeResponse)
def create_molecule(molecule: MoleculeCreate):
    try:
        return register_molecule_from_smiles(molecule.model_dump())
    except InvalidMoleculeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateMoleculeError as e:
        raise HTTPException(status_code=409, detail=e.detail)
    except MoleculeRegistrationError as e:
        raise HTTPException(status_code=500, detail=str(e))


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


#-------- VISUALIZATION ----------------

@router.get("/{molecule_id}/image")
def get_molecule_image(molecule_id: int):
    molecule = mr.get_molecule_by_id(molecule_id)

    if molecule is None:
        raise HTTPException(status_code=404, detail="Molecule not found")

    try:
        image_bytes = render_molecule_png(
            canonical_smiles=molecule["canonical_smiles"],
            molblock=molecule["molblock"],
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return Response(content=image_bytes, media_type="image/png")