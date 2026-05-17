from app.services.chemistry import derive_molecule_properties_from_smiles
from app.repositories import molecule_repository as mr
import sqlite3

class DuplicateMoleculeError(Exception):
    def __init__(self, detail: dict):
        self.detail = detail
        super().__init__(self.detail['message'])

class InvalidMoleculeError(Exception):
    pass


class MoleculeRegistrationError(Exception):
    pass


def build_duplicate_detail(
    molecule_data: dict,
    existing_molecule: dict | None,
) -> dict:
    return {
        "message": 'Duplicate molecule detected',
        "formula": molecule_data['formula'],
        "inchikey": molecule_data['inchikey'],
        "existing_molecule_id": existing_molecule['id'] if existing_molecule else None,
    }


def register_molecule_from_smiles(molecule_data: dict) -> dict:
    try:
        derived_data = derive_molecule_properties_from_smiles(molecule_data['smiles'])
    except ValueError as e:
        raise InvalidMoleculeError(str(e))
    
    registration_data = {
        **molecule_data,
        **derived_data
    }

    return register_molecule_data(registration_data)


def register_molecule_data(molecule_data: dict) -> dict:
    existing_molecule = mr.find_molecule_by_inchikey(molecule_data['inchikey'])

    if existing_molecule:
        raise DuplicateMoleculeError(build_duplicate_detail(molecule_data, existing_molecule))
    
    try:
        created_molecule = mr.create_molecule(molecule_data)
    except sqlite3.IntegrityError:
        existing_molecule = mr.find_molecule_by_inchikey(molecule_data['inchikey'])
        raise DuplicateMoleculeError(build_duplicate_detail(molecule_data, existing_molecule))

    if created_molecule is None:
        raise MoleculeRegistrationError('Failed to create molecule')
    
    return created_molecule


