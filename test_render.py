from pathlib import Path

from app.services.molecule_rendering import render_molecule_png


image_bytes = render_molecule_png(
    canonical_smiles="CCO",
    molblock=None,
)

output_path = Path("data/renders/ethanol.png")
output_path.write_bytes(image_bytes)

print(f"Wrote {output_path}")
print(f"Bytes: {len(image_bytes)}")