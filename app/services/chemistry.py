from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Descriptors, AllChem


def parse_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'Invalid SMILES: {smiles}')
    return mol


def generate_canonical_smiles(mol):
    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
    return canonical_smiles


def calculate_molecular_formula(mol):
    formula = rdMolDescriptors.CalcMolFormula(mol)
    return formula


def calculate_molecular_weight(mol):
    mw = Descriptors.MolWt(mol)
    return mw


def generate_inchi(mol):
    inchi = Chem.MolToInchi(mol)
    return inchi


def generate_inchikey(mol):
    inchikey = Chem.MolToInchiKey(mol)
    return inchikey


def generate_molblock(mol):
    AllChem.Compute2DCoords(mol)
    molblock = Chem.MolToMolBlock(mol)
    return molblock




def derive_molecule_properties_from_smiles(smiles: str):
    mol = parse_smiles(smiles)
    canonical_smiles = generate_canonical_smiles(mol)
    formula = calculate_molecular_formula(mol)
    molecular_weight = calculate_molecular_weight(mol)

    inchi = generate_inchi(mol)
    inchikey = generate_inchikey(mol)
    molblock = generate_molblock(mol)

    return {
        'smiles': smiles,
        'canonical_smiles': canonical_smiles,
        'formula': formula,
        'molecular_weight': molecular_weight,
        'inchi': inchi,
        'inchikey': inchikey,
        'molblock': molblock,
    }