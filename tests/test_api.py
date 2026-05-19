import os
from pathlib import Path
import sqlite3

TEST_DB_PATH = Path('data/test_chemreg.db')

os.environ['CHEMREG_DB_PATH'] = str(TEST_DB_PATH)

from fastapi.testclient import TestClient
from app.main import app


def reset_test_db():
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("DELETE FROM molecules")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'molecules'")
    conn.commit()
    conn.close()


def test_health_check():
    with TestClient(app) as client: # Use TestClient context manager to ensure startup events occur, e.g. create db
        response = client.get('/health')

        assert response.status_code == 200
        assert response.json()['status'] == 'ok'




def test_create_molecule():
    reset_test_db()

    test_molecules = [
        {
            "name": "ethanol",
            "smiles": "CCO",
            "project": "solvent-screen",
            "chemist": "alice",
            "notes": "Simple alcohol test molecule",
        },
        {
            "name": "caffeine",
            "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
            "project": "stimulants",
            "chemist": "bob",
        },
        {
            "name": "aspirin",
            "smiles": "CC(=O)Oc1ccccc1C(=O)O",
            "notes": "Common benchmark molecule",
        },
        {
            "name": "benzene",
            "smiles": "c1ccccc1",
            "project": "aromatics",
        },
        {
            "name": "acetic acid",
            "smiles": "CC(=O)O",
        },
    ]

    with TestClient(app) as client:
        for molecule in test_molecules:
            response = client.post('/molecules', json=molecule)

            assert response.status_code == 200, f'Failed to create {molecule['name']}: {response.text}'

            data = response.json()

            assert data["id"] is not None
            assert data["name"] == molecule["name"]
            assert data["smiles"] == molecule["smiles"]

            assert data["canonical_smiles"] is not None
            assert data["formula"] is not None
            assert data["molecular_weight"] is not None
            assert data["inchi"] is not None
            assert data["inchikey"] is not None
            assert data["molblock"] is not None

            assert data.get("project") == molecule.get("project")
            assert data.get("chemist") == molecule.get("chemist")
            assert data.get("notes") == molecule.get("notes")


def test_list_molecules():
    reset_test_db()
    test_molecules = [
        {
            "name": "benzene",
            "smiles": "c1ccccc1",
            "project": "aromatics",
        },
        {
            "name": "acetone",
            "smiles": "CC(=O)C",
            "project": "solvents",
            "notes": "Used for list endpoint test",
        },
    ]

    with TestClient(app) as client:
        for molecule in test_molecules:
            response = client.post("/molecules", json=molecule)

            assert response.status_code == 200, (
                f"Failed to create {molecule['name']}: {response.text}"
            )

        response = client.get("/molecules")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    names = {molecule["name"] for molecule in data}

    assert "benzene" in names
    assert "acetone" in names


def test_molecule_by_id():
    reset_test_db()

    with TestClient(app) as client:

        # Creates a molecule in teh db
        created_response = client.post('/molecules', 
                               json={
                                   "name": "ethanol",
                                    "smiles": "CCO",
                                    "project": "solvent-screen",
                                    "chemist": "alice",
                                    "notes": "Created for retrieval test",
                               })
        assert created_response.status_code == 200, created_response.text

        created = created_response.json()

        molecule_id = created['id']

        response = client.get(f'/molecules/{molecule_id}')

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == molecule_id
        assert data["name"] == "ethanol"
        assert data["smiles"] == "CCO"
        assert data["canonical_smiles"] == "CCO"
        assert data["formula"] == "C2H6O"
        assert data["inchikey"] == "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
        assert data["project"] == "solvent-screen"
        assert data["chemist"] == "alice"
        assert data["notes"] == "Created for retrieval test"


def test_update_molecule():
    reset_test_db()

    with TestClient(app) as client:
        create_response = client.post(
            "/molecules",
            json={
                "name": "ethanol",
                "smiles": "CCO",
                "project": "old-project",
                "chemist": "alice",
                "notes": "Original notes",
            },
        )

        assert create_response.status_code == 200, create_response.text

        molecule_id = create_response.json()["id"]

        update_response = client.put(
            f"/molecules/{molecule_id}",
            json={
                "name": "updated ethanol",
                "project": "updated-project",
                "chemist": "bob",
                "notes": "Updated notes from automated test",
            },
        )

        assert update_response.status_code == 200, update_response.text

        data = update_response.json()

        assert data["id"] == molecule_id
        assert data["name"] == "updated ethanol"
        assert data["smiles"] == "CCO"
        assert data["formula"] == "C2H6O"
        assert data["project"] == "updated-project"
        assert data["chemist"] == "bob"
        assert data["notes"] == "Updated notes from automated test"



def test_delete_molecule():
    reset_test_db()

    with TestClient(app) as client:
        create_response = client.post(
            "/molecules",
            json={
                "name": "ethanol",
                "smiles": "CCO",
                "project": "delete-test",
                "notes": "Created for delete endpoint test",
            },
        )

        assert create_response.status_code == 200, create_response.text

        molecule_id = create_response.json()["id"]

        delete_response = client.delete(f"/molecules/{molecule_id}")

        assert delete_response.status_code == 200, delete_response.text

        get_response = client.get(f"/molecules/{molecule_id}")

        assert get_response.status_code == 404



def test_duplicate_molecule_detection():
    reset_test_db()

    with TestClient(app) as client:
        first_response = client.post(
            "/molecules",
            json={
                "name": "ethanol",
                "smiles": "CCO",
            },
        )

        assert first_response.status_code == 200, first_response.text

        duplicate_response = client.post(
            "/molecules",
            json={
                "name": "duplicate ethanol",
                "smiles": "CCO",
            },
        )

        assert duplicate_response.status_code == 409, duplicate_response.text

        data = duplicate_response.json()

        assert data["detail"]["message"] == "Duplicate molecule detected"
        assert data["detail"]["formula"] == "C2H6O"
        assert data["detail"]["inchikey"] == "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
        assert data["detail"]["existing_molecule_id"] == first_response.json()["id"]


def test_search_molecules_by_name():
    reset_test_db()

    with TestClient(app) as client:
        molecules = [
            {
                "name": "ethanol",
                "smiles": "CCO",
                "project": "solvents",
                "chemist": "alice",
            },
            {
                "name": "benzene",
                "smiles": "c1ccccc1",
                "project": "aromatics",
                "chemist": "bob",
            },
            {
                "name": "aspirin",
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "project": "reference",
                "chemist": "alice",
            },
        ]

        for molecule in molecules:
            create_response = client.post("/molecules", json=molecule)
            assert create_response.status_code == 200, create_response.text

        search_response = client.get("/search/molecules", params={"name": "ethanol"})

        assert search_response.status_code == 200, search_response.text

        data = search_response.json()

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "ethanol"
        assert data[0]["formula"] == "C2H6O"
        assert data[0]["project"] == "solvents"
        assert data[0]["chemist"] == "alice"