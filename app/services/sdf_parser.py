from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

# Parse the RDKit molecule into a dictionary for return data.


def get_molecule_name(mol: Chem.Mol, record_index: int) -> str:
    if mol.HasProp('PUBCHEM_IUPAC_TRADITIONAL_NAME'):
        name = mol.GetProp('PUBCHEM_IUPAC_TRADITIONAL_NAME').strip()
        if name:
            return name
        
    if mol.HasProp('_Name'):
        name = mol.GetProp('_Name').strip()
        if name:
            return name
    
    return f'record_{record_index}'



def parse_mol(mol: Chem.Mol, record_index: int) -> dict:
    name = get_molecule_name(mol, record_index)

    sdf_properties = {
        prop_name: mol.GetProp(prop_name) 
        for prop_name in mol.GetPropNames() 
        if prop_name not in ('PUBCHEM_IUPAC_TRADITIONAL_NAME', '_Name')
    }

    return {
        'record_index': record_index,
        'name': name,
        'smiles': Chem.MolToSmiles(mol, canonical=True),
        'canonical_smiles': Chem.MolToSmiles(mol, canonical=True),
        'formula': rdMolDescriptors.CalcMolFormula(mol),
        'molecular_weight': round(Descriptors.MolWt(mol), 3),
        'inchi': Chem.MolToInchi(mol),
        'inchikey': Chem.MolToInchiKey(mol),
        'molblock': Chem.MolToMolBlock(mol),
        'sdf_properties': sdf_properties,
    }

def parse_sdf_file(file_path: str) -> dict:
    molecules = []
    errors = []

    supplier = Chem.SDMolSupplier(file_path)

    for record_index, mol in enumerate(supplier, start=1):
        if mol is None:
            errors.append({
                'record_index': record_index,
                'message': 'Invalid molecule record'
            })
            continue
        try:
            molecules.append(parse_mol(mol, record_index))
        except Exception as e:
            errors.append({
                'record_index': record_index,
                'message': str(e)
            })

    return {
        'molecules': molecules,
        'errors': errors
    }