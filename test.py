from app.services.sdf_parser import *

result = parse_sdf_file('data/samples/pubchem_short_multi.sdf')

print('Molecules:', len(result['molecules']))
print('Errors:', len(result['errors']))

for molecule in result['molecules']:
    print(
        molecule['record_index'],
        molecule['name'],
        molecule['formula'],
        molecule['inchikey'],
        len(molecule['sdf_properties'])
    )