from app.services.molecule_registration import register_molecule_from_smiles

molecule = {
    'smiles': 'CCO'
}

register_molecule_from_smiles(molecule)