from app.services.sdf_parser import parse_sdf_file
from app.services.molecule_registration import (
    DuplicateMoleculeError,
    MoleculeRegistrationError,
    register_molecule_data,
)


def build_registration_data_from_sdf_record(record: dict) -> dict:
    return {
        "name": record["name"],
        "smiles": record["smiles"],
        "canonical_smiles": record["canonical_smiles"],
        "formula": record["formula"],
        "molecular_weight": record["molecular_weight"],
        "inchi": record["inchi"],
        "inchikey": record["inchikey"],
        "molblock": record["molblock"],
    }


def register_molecules_from_sdf(file_path: str, filename: str) -> dict:
    registered = []
    duplicates = []
    failed = []

    parsed_result = parse_sdf_file(file_path)
    parsed_molecules = parsed_result["molecules"]

    for idx, parsed_molecule in enumerate(parsed_molecules, start=1):
        try:
            molecule_data = build_registration_data_from_sdf_record(
                parsed_molecule
            )

            created_molecule = register_molecule_data(molecule_data)

            registered.append({
                "record_index": idx,
                "molecule": created_molecule,
            })

        except DuplicateMoleculeError as e:
            duplicates.append({
                "record_index": idx,
                "name": parsed_molecule.get("name"),
                "detail": e.detail,
            })

        except MoleculeRegistrationError as e:
            failed.append({
                "record_index": idx,
                "name": parsed_molecule.get("name"),
                "error": str(e),
            })

        except Exception as e:
            failed.append({
                "record_index": idx,
                "name": parsed_molecule.get("name") if isinstance(parsed_molecule, dict) else None,
                "error": str(e),
            })

    return {
        "filename": filename,
        "total_records": len(parsed_molecules),
        "registered_count": len(registered),
        "duplicate_count": len(duplicates),
        "failed_count": len(failed),
        "registered": registered,
        "duplicates": duplicates,
        "failed": failed,
    }