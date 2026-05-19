import os
from pathlib import Path
import sqlite3

TEST_DB_PATH = Path('data/test_chemreg.db')

os.environ['CHEMREG_DB_PATH'] = str(TEST_DB_PATH)

from fastapi.testclient import TestClient
from app.main import app


TEST_DATA_DIR = Path(__file__).parent / 'data'


def reset_test_db():
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("DELETE FROM molecules")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'molecules'")
    conn.commit()
    conn.close()


def upload_sdf(client: TestClient, filename: str):
    sdf_path = TEST_DATA_DIR / filename

    with open(sdf_path, 'rb') as sdf_file:
        return client.post(
            '/uploads/sdf',
            files={
                'file': (
                    filename,
                    sdf_file,
                    'chemical/x-mdl-sdfile',
                )
            },
        )


def get_registration(data: dict) -> dict:
    assert 'registration' in data
    assert isinstance(data['registration'], dict)

    return data['registration']


def test_upload_sdf_endpoint_accepts_sdf_file():
    reset_test_db()

    with TestClient(app) as client:
        response = upload_sdf(client, 'sample_molecules.sdf')

    assert response.status_code == 200, response.text

    data = response.json()

    assert data['filename'] == 'sample_molecules.sdf'
    assert data['content_type'] == 'chemical/x-mdl-sdfile'
    assert data['size_bytes'] > 0
    assert data['saved_path'] is not None
    assert 'registration' in data


def test_upload_sdf_registers_molecules_successfully():
    reset_test_db()

    with TestClient(app) as client:
        response = upload_sdf(client, 'sample_molecules.sdf')

    assert response.status_code == 200, response.text

    data = response.json()
    registration = get_registration(data)

    assert registration['total_records'] == 1
    assert registration['registered_count'] == 1
    assert registration['duplicate_count'] == 0
    assert registration['failed_count'] == 0

    assert len(registration['registered']) == 1
    assert registration['duplicates'] == []
    assert registration['failed'] == []


def test_upload_sdf_reports_duplicate_molecules():
    reset_test_db()

    with TestClient(app) as client:
        first_response = upload_sdf(client, 'sample_molecules.sdf')
        duplicate_response = upload_sdf(client, 'sample_molecules.sdf')

    assert first_response.status_code == 200, first_response.text
    assert duplicate_response.status_code == 200, duplicate_response.text

    data = duplicate_response.json()
    registration = get_registration(data)

    assert registration['total_records'] == 1
    assert registration['registered_count'] == 0
    assert registration['duplicate_count'] == 1
    assert registration['failed_count'] == 0

    assert registration['registered'] == []
    assert len(registration['duplicates']) == 1
    assert registration['failed'] == []


def test_upload_sdf_handles_invalid_records():
    reset_test_db()

    with TestClient(app) as client:
        response = upload_sdf(client, 'invalid_record.sdf')

    assert response.status_code == 200, response.text

    data = response.json()
    registration = get_registration(data)

    # Current parser/RDKit behavior:
    # the malformed record is skipped before registration,
    # so it does not become a failed registration record.
    assert registration['total_records'] == 0
    assert registration['registered_count'] == 0
    assert registration['duplicate_count'] == 0
    assert registration['failed_count'] == 0

    assert registration['registered'] == []
    assert registration['duplicates'] == []
    assert registration['failed'] == []


def test_upload_sdf_summary_response_shape():
    reset_test_db()

    with TestClient(app) as client:
        response = upload_sdf(client, 'sample_molecules.sdf')

    assert response.status_code == 200, response.text

    data = response.json()

    assert set(data.keys()) == {
        'filename',
        'content_type',
        'size_bytes',
        'saved_path',
        'registration',
    }

    assert isinstance(data['filename'], str)
    assert isinstance(data['content_type'], str)
    assert isinstance(data['size_bytes'], int)
    assert isinstance(data['saved_path'], str)
    assert isinstance(data['registration'], dict)

    registration = data['registration']

    assert set(registration.keys()) == {
        'filename',
        'total_records',
        'registered_count',
        'duplicate_count',
        'failed_count',
        'registered',
        'duplicates',
        'failed',
    }

    assert isinstance(registration['filename'], str)
    assert isinstance(registration['total_records'], int)
    assert isinstance(registration['registered_count'], int)
    assert isinstance(registration['duplicate_count'], int)
    assert isinstance(registration['failed_count'], int)
    assert isinstance(registration['registered'], list)
    assert isinstance(registration['duplicates'], list)
    assert isinstance(registration['failed'], list)


def test_upload_sdf_rejects_non_sdf_file():
    reset_test_db()

    with TestClient(app) as client:
        response = client.post(
            '/uploads/sdf',
            files={
                'file': (
                    'not_an_sdf.txt',
                    b'this is not an sdf file',
                    'text/plain',
                )
            },
        )

    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'Only .sdf files are supported.'