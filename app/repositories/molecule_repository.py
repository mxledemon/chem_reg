from app.db import get_conn
from app.schemas import MoleculeCreate, MoleculeResponse


def create_molecule(molecule_data):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
            insert into molecules (
                name, smiles, canonical_smiles, formula, molecular_weight,
                inchi, inchikey, molblock, source_filename, project,
                chemist, notes
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                molecule_data.get('name'),
                molecule_data.get('smiles'),
                molecule_data.get('canonical_smiles'),
                molecule_data.get('formula'),
                molecule_data.get('molecular_weight'),
                molecule_data.get('inchi'),
                molecule_data.get('inchikey'),
                molecule_data.get('molblock'),
                molecule_data.get('source_filename'),
                molecule_data.get('project'),
                molecule_data.get('chemist'),
                molecule_data.get('notes')
            ))
        conn.commit()
        last_id = cur.lastrowid
        row = cur.execute('select * from molecules where id = ?', (last_id,)).fetchone()
        return dict(row) if row else None
    

def get_molecule_by_id(molecule_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
                    select * from molecules where id = ?''', (molecule_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
def list_molecules(limit: int = 10, offset: int = 0):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
                    select * from molecules order by id desc limit ? offset ?''', (limit, offset))
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    
def find_molecule_by_inchikey(inchikey: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
                    select * from molecules where inchikey = ?''', (inchikey,))
        row = cur.fetchone()
        return dict(row) if row else None
    
def delete_molecule(molecule_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
                delete from molecules where id = ?''', (molecule_id,))
        conn.commit()
        return cur.rowcount > 0
    
def update_molecule(molecule_id: int, molecule_data: dict):
    allowed_fields = [
        'name',
        'project',
        'chemist',
        'notes'
    ]
    fields_to_update = [field for field in allowed_fields if field in molecule_data]
    if not fields_to_update:
        return get_molecule_by_id(molecule_id)
    values = [molecule_data[field] for field in fields_to_update]
    clauses = []

    for field in fields_to_update:
        clauses.append(f'{field} = ?')
    clauses.append(f'updated_at = current_timestamp')
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f'''
                update molecules
                    set {', '.join(clauses)} where id = ?''', (
                        *values, molecule_id,
                    ))
        conn.commit()
        return get_molecule_by_id(molecule_id)
