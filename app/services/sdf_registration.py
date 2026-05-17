from app.services.sdf_parser import parse_sdf_file
from app.services.chemistry import derive_molecule_properties_from_smiles
from app.repositories import molecule_repository as mr
from rdkit import Chem


def register_molecules_from_sdf(file_path: str, filename: str):
    registered = []
    duplicates = []
    failed = []

    parsed_result = parse_sdf_file(file_path)

    # print(parsed_result['molecules'])
    print(parsed_result.keys())

    for idx, parsed_molecule in enumerate(parsed_result['molecules'], start=1):
        try:

            derived_data = derive_molecule_properties_from_smiles(parsed_molecule['smiles'])

            molecule_data = {
                'name': parsed_molecule['name'],
                **derived_data,
            }

            # Check if duplicate using the inchikey check function from molecule repository
            # If duplicate, add to duplicates and continue to next
            # If new move to register

            existing_molecule = mr.find_molecule_by_inchikey(molecule_data['inchikey'])

            if existing_molecule:
                duplicates.append(molecule_data)
                continue
            mr.create_molecule(molecule_data)
            registered.append(molecule_data)

        except Exception as e:
            failed.append({
                'record_index': idx,
                'name': parsed_molecule['name'] if isinstance(parsed_molecule, dict) else None,
                'error': str(e)
            })
    
    return {
        'filename': filename,
        'total_records': len(parsed_result['molecules']),
        'registered_count': len(registered),
        'duplicate_count': len(duplicates),
        'failed_count': len(failed),
        'registered': registered,
        'duplicates': duplicates,
        'failed': failed
    }