from app.services.chemistry import derive_molecule_properties_from_smiles

try:
    props = derive_molecule_properties_from_smiles('not_a_smiles')
except ValueError as e:
    print(e)
for key, value in props.items():
    print("\n---", key, "---")
    print(value)