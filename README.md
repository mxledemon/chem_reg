# ChemREG Lite / Mini ChemReg

ChemREG Lite is a small FastAPI molecule registration API. It stores molecule records in SQLite, derives chemical identifiers with RDKit, supports SDF upload/registration, provides search endpoints, and can render molecule structures as PNG images.

This project is a learning/prototype implementation of a lightweight chemical registration backend.

## Current Features

- FastAPI application with Swagger UI
- SQLite database initialized on application startup
- Health check endpoint
- Molecule CRUD endpoints
- Molecule creation from SMILES
- RDKit-derived molecule properties:
  - canonical SMILES
  - molecular formula
  - molecular weight
  - InChI
  - InChIKey
  - MolBlock
- Duplicate detection by InChIKey
- SDF upload endpoint
- SDF parsing and batch molecule registration
- Search endpoint with text and numeric filters
- PNG molecule rendering endpoint
- Local sample SDF files for manual testing

## Project Structure

This structure was generated from the current project zip.

```text
chem_reg/
├── .gitignore
├── PROJECT_SPEC.md
├── README.md
├── requirements.txt
├── test.py
├── test_render.py
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── schemas.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── molecule_repository.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── molecules.py
│   │   ├── search.py
│   │   └── uploads.py
│   └── services/
│       ├── __init__.py
│       ├── chemistry.py
│       ├── molecule_registration.py
│       ├── molecule_rendering.py
│       ├── sdf_parser.py
│       └── sdf_registration.py
├── data/
│   ├── chemreg.db
│   ├── renders/
│   │   └── ethanol.png
│   ├── samples/
│   │   ├── aspirin.sdf
│   │   ├── bad.txt
│   │   ├── caffeine.sdf
│   │   ├── ethanol.sdf
│   │   ├── ibuprofen.sdf
│   │   ├── pubchem_short_multi.sdf
│   │   └── twenty_molecules.sdf
│   └── uploads/
│       ├── aspirin.sdf
│       └── twenty_molecules.sdf
├── docs/
│   └── specification.md
├── sample_files/
└── tests/
```

### Application Files

- `app/main.py` creates the FastAPI app, includes routers, and initializes the database on startup.
- `app/db.py` manages the SQLite connection and creates the `molecules` table.
- `app/schemas.py` contains the Pydantic models used by the API.
- `app/repositories/molecule_repository.py` contains database access functions.

### Routers

- `__init__.py`
- `health.py`
- `molecules.py`
- `search.py`
- `uploads.py`

### Services

- `__init__.py`
- `chemistry.py`
- `molecule_registration.py`
- `molecule_rendering.py`
- `sdf_parser.py`
- `sdf_registration.py`

### Data Files

Sample SDF files currently included:

- `aspirin.sdf`
- `bad.txt`
- `caffeine.sdf`
- `ethanol.sdf`
- `ibuprofen.sdf`
- `pubchem_short_multi.sdf`
- `twenty_molecules.sdf`

Uploaded example files currently included:

- `aspirin.sdf`
- `twenty_molecules.sdf`

Rendered example files currently included:

- `ethanol.png`

## Requirements

The code imports the following main third-party packages:

- `fastapi`
- `uvicorn`
- `rdkit`
- `pydantic`
- `python-multipart`
- `Pillow` / `pillow`, usually pulled in by RDKit image rendering but useful to have explicitly

Important: `requirements.txt` currently exists but is empty. Until dependencies are added there, install them manually with the command below or update `requirements.txt` first.

```bash
pip install fastapi uvicorn rdkit python-multipart pillow
```

If RDKit installation gives you trouble with `pip`, Conda is often the safer route:

```bash
conda install -c conda-forge rdkit
```

## Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd chem_reg
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell or Command Prompt:

```bash
.venv\Scriptsctivate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies.

If `requirements.txt` has been populated:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is still empty:

```bash
pip install fastapi uvicorn rdkit python-multipart pillow
```

## Run the API

From the project root, run:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

ReDoc is available at:

```text
http://127.0.0.1:8000/redoc
```

The database is initialized automatically on startup by `app.main.startup()`, which calls `init_db()` from `app/db.py`.

## Database

The SQLite database path is:

```text
data/chemreg.db
```

The `molecules` table contains these fields:

- `id`
- `name`
- `smiles`
- `canonical_smiles`
- `formula`
- `molecular_weight`
- `inchi`
- `inchikey`
- `molblock`
- `source_filename`
- `project`
- `chemist`
- `notes`
- `created_at`
- `updated_at`

A unique index is created on `inchikey` for duplicate detection.

## API Endpoints

### Root

```http
GET /
```

Example response:

```json
{
  "message": "API ChemReg lite is running"
}
```

### Health Check

```http
GET /health/
```

Example response:

```json
{
  "status": "ok"
}
```

### Create Molecule

```http
POST /molecules
```

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/molecules" ^
  -H "Content-Type: application/json" ^
  -d "{"name":"ethanol","smiles":"CCO","project":"demo","chemist":"alice","notes":"test molecule"}"
```

macOS/Linux version:

```bash
curl -X POST "http://127.0.0.1:8000/molecules"   -H "Content-Type: application/json"   -d '{"name":"ethanol","smiles":"CCO","project":"demo","chemist":"alice","notes":"test molecule"}'
```

The API derives chemical properties from the submitted SMILES using `app/services/chemistry.py`.

### List Molecules

```http
GET /molecules?limit=10&offset=0
```

Example:

```bash
curl "http://127.0.0.1:8000/molecules?limit=10&offset=0"
```

### Get Molecule by ID

```http
GET /molecules/{molecule_id}
```

Example:

```bash
curl "http://127.0.0.1:8000/molecules/1"
```

### Update Molecule

```http
PUT /molecules/{molecule_id}
```

The repository currently allows updating these fields:

- `name`
- `project`
- `chemist`
- `notes`

Example:

```bash
curl -X PUT "http://127.0.0.1:8000/molecules/1" ^
  -H "Content-Type: application/json" ^
  -d "{"name":"ethyl alcohol","project":"demo-updated"}"
```

macOS/Linux version:

```bash
curl -X PUT "http://127.0.0.1:8000/molecules/1"   -H "Content-Type: application/json"   -d '{"name":"ethyl alcohol","project":"demo-updated"}'
```

Note: `MoleculeUpdate` includes `smiles`, but the repository update allow-list does not currently update `smiles` or recalculate derived properties.

### Delete Molecule

```http
DELETE /molecules/{molecule_id}
```

Example:

```bash
curl -X DELETE "http://127.0.0.1:8000/molecules/1"
```

Example response:

```json
{
  "deleted": true
}
```

### Render Molecule Image

```http
GET /molecules/{molecule_id}/image
```

Example:

```bash
curl "http://127.0.0.1:8000/molecules/1/image" --output molecule.png
```

The endpoint returns a PNG image generated by `app/services/molecule_rendering.py`. It first attempts to render from `molblock`, then falls back to `canonical_smiles`.

### Search Molecules

```http
GET /search/molecules
```

Supported query parameters in `app/routers/search.py`:

- `name`
- `formula`
- `inchikey`
- `min_weight`
- `max_weight`
- `project`
- `chemist`

Examples:

```bash
curl "http://127.0.0.1:8000/search/molecules?name=ethanol"
```

```bash
curl "http://127.0.0.1:8000/search/molecules?formula=C2H6O"
```

```bash
curl "http://127.0.0.1:8000/search/molecules?inchikey=LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
```

```bash
curl "http://127.0.0.1:8000/search/molecules?min_weight=40&max_weight=50"
```

```bash
curl "http://127.0.0.1:8000/search/molecules?project=demo&chemist=alice"
```

If both `min_weight` and `max_weight` are provided and `min_weight > max_weight`, the API returns a `400` error.

### Upload SDF

```http
POST /uploads/sdf
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/uploads/sdf" ^
  -F "file=@data\samplesspirin.sdf"
```

macOS/Linux version:

```bash
curl -X POST "http://127.0.0.1:8000/uploads/sdf"   -F "file=@data/samples/aspirin.sdf"
```

The upload endpoint:

1. Requires a filename.
2. Requires the file extension to be `.sdf`.
3. Saves the file into `data/uploads/`.
4. Calls `register_molecules_from_sdf()` from `app/services/sdf_registration.py`.
5. Returns file metadata plus a registration summary.

Example response shape:

```json
{
  "filename": "aspirin.sdf",
  "content_type": "application/octet-stream",
  "size_bytes": 3630,
  "saved_path": "data/uploads/aspirin.sdf",
  "registration": {
    "filename": "aspirin.sdf",
    "total_records": 1,
    "registered_count": 1,
    "duplicate_count": 0,
    "failed_count": 0,
    "registered": [],
    "duplicates": [],
    "failed": []
  }
}
```

## Duplicate Detection

Molecule duplicates are detected by InChIKey.

During single molecule registration, `register_molecule_from_smiles()` derives molecule properties from SMILES and then checks for an existing molecule with the same InChIKey.

During SDF registration, `register_molecule_data()` performs the same duplicate check for each parsed molecule record.

Example duplicate response for `POST /molecules`:

```json
{
  "detail": {
    "message": "Duplicate molecule detected",
    "formula": "C2H6O",
    "inchikey": "LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
    "existing_molecule_id": 1
  }
}
```

Expected status code:

```text
409 Conflict
```

## Local Helper Scripts

The repo currently includes two top-level helper scripts:

- `test.py`
- `test_render.py`

These appear to be manual/local testing scripts rather than formal pytest test modules.

## Automated Tests

A `tests/` directory exists, but it is currently empty in the provided zip.

When automated tests are added, they can likely be run with:

```bash
pytest
```

A useful future test suite would cover:

- `GET /health/`
- molecule creation
- molecule listing
- molecule retrieval by ID
- molecule update
- molecule deletion
- duplicate detection
- molecule search
- SDF upload
- molecule image rendering

## Known Limitations

- `requirements.txt` is currently empty and should be populated for reproducible setup.
- `tests/` exists but has no committed automated tests yet.
- The app uses SQLite, which is fine for local development but not ideal for concurrent production workloads.
- Authentication and authorization are not implemented.
- Uploaded files are stored locally under `data/uploads/`.
- The SQLite database file is stored locally at `data/chemreg.db`.
- SDF processing is synchronous and may not be suitable for very large files.
- The upload route validates file extension but does not perform deep content validation before saving.
- Duplicate detection is based on InChIKey only.
- The update endpoint currently updates metadata fields but does not recalculate chemical properties if `smiles` changes.
- No pagination is currently implemented on the search endpoint.
- Advanced chemical search, such as substructure or similarity search, is not implemented.

## Future Enhancements

- Populate `requirements.txt` with all runtime and development dependencies.
- Add automated pytest coverage.
- Add test database isolation for API tests.
- Add Docker support.
- Add Alembic or another migration strategy.
- Add PostgreSQL support.
- Add authentication and authorization.
- Add user/project/chemist management endpoints.
- Add pagination and sorting to search results.
- Add substructure search.
- Add similarity search.
- Add molecule export endpoints.
- Add better SDF validation and error reporting.
- Add background processing for larger SDF uploads.
- Add structured logging.
- Add CI workflow for automated tests.

## Developer Quick Start

```bash
git clone <your-repository-url>
cd chem_reg
python -m venv .venv
.venv\Scriptsctivate
pip install fastapi uvicorn rdkit python-multipart pillow
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

From Swagger UI, try:

1. `GET /health/`
2. `POST /molecules`
3. `GET /molecules`
4. `GET /search/molecules`
5. `POST /uploads/sdf`
6. `GET /molecules/{molecule_id}/image`


## Known Limitations

This project is a first-version, learning-focused molecule registration API. It demonstrates core registration workflows, API design, SDF upload handling, duplicate detection, and basic chemistry property generation, but it is not intended to be a production-ready chemical registration system.

Current limitations include:

- **Salt and parent handling is not implemented**  
  Molecules are registered as provided. The system does not currently strip salts, identify parent structures, normalize mixtures, or manage salt/solvate relationships.

- **Stereochemistry handling is basic**  
  The system relies on RDKit-derived identifiers and canonicalization, but it does not implement advanced stereochemistry review, manual curation, enhanced stereo groups, or business-specific stereochemical rules.

- **Structure search is not implemented**  
  The API supports text and property-based search, but it does not currently support substructure search, similarity search, exact structure search, or chemical drawing/query workflows.

- **Authentication and authorization are not implemented**  
  The API does not currently include login, user roles, permissions, audit trails, or access control.

- **This is a learning-focused system**  
  The goal of the project is to explore FastAPI, SQLite, RDKit, testing, API design, and molecule registration concepts. It intentionally keeps the scope small and understandable rather than attempting to match enterprise cheminformatics platforms.