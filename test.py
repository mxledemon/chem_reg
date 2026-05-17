from app.services.sdf_registration import register_molecules_from_sdf
from pprint import pprint
import sqlite3


TEST_INCHIKEYS = [
    "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",  # aspirin / 2-acetoxybenzoic acid
    "RYYVLZVUVIJVGH-UHFFFAOYSA-N",  # caffeine
    "LFQSCWFLJHTTHZ-UHFFFAOYSA-N",  # ethanol
]


conn = sqlite3.connect("data/chemreg.db")
cursor = conn.cursor()

cursor.execute(
    """
    DELETE FROM molecules
    WHERE inchikey IN (?, ?, ?)
    """,
    TEST_INCHIKEYS,
)

conn.commit()
conn.close()


result = register_molecules_from_sdf(
    "data/samples/pubchem_short_multi.sdf",
    "pubchem_short_multi.sdf"
)

pprint(result, sort_dicts=False)