from io import BytesIO

from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor


def render_molecule_png(
    canonical_smiles: str | None,
    molblock: str | None,
) -> bytes:
    mol = None

    if molblock:
        mol = Chem.MolFromMolBlock(molblock, sanitize=True, removeHs=False)

    if mol is None and canonical_smiles:
        mol = Chem.MolFromSmiles(canonical_smiles)

    if mol is None:
        raise ValueError("No valid molecule structure available for rendering")

    rdDepictor.Compute2DCoords(mol)

    image = Draw.MolToImage(mol, size=(400, 300))

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()