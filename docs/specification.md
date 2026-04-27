# Mini ChemReg / Molecule Registration API

## Project Overview

Mini ChemReg is a learning-focused molecule registration API built with FastAPI, SQLite, and optional chemistry tooling such as RDKit.

The goal of this project is to create a small but realistic chemistry registration system where users can upload SDF files, parse molecules, store molecule records in a database, expose CRUD/search endpoints, and optionally generate simple molecule visualizations.

This project is inspired by lightweight chemical registration workflows used in cheminformatics and scientific software platforms.

---

# Project Goals

The application should allow users to:

- Upload SDF files through a FastAPI endpoint
- Parse one or more molecule records from an SDF file
- Store molecule data in SQLite
- Detect duplicate molecules using chemical identifiers
- Expose molecule CRUD endpoints
- Search molecules by basic properties
- Optionally render molecule images for thin visualization

---

# Core Features

## 1. Health Check Endpoint

The application should expose a basic health check endpoint.

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

This confirms the API is running.

---

## 2. SQLite Database

The application should use SQLite as the persistence layer.

A molecule table should store both user-provided metadata and derived chemistry properties.

Example table:

```text
molecules
---------
id                  integer primary key
name                text
smiles              text
canonical_smiles    text
molblock            text
formula             text
molecular_weight    real
inchi               text
inchikey            text
source_filename     text
project             text
chemist             text
notes               text
created_at          text
updated_at          text
```

Optional future fields:

```text
registration_number text
is_active           integer
deleted_at          text
```

---

## 3. Molecule CRUD Endpoints

The API should support basic molecule CRUD operations.

### List Molecules

```http
GET /molecules
```

Optional query parameters:

```text
limit
offset
name
formula
min_mw
max_mw
```

Example:

```http
GET /molecules?name=aspirin
```

---

### Get Molecule by ID

```http
GET /molecules/{molecule_id}
```

Returns one molecule record.

---

### Create Molecule Manually

```http
POST /molecules
```

This endpoint allows a user to register a molecule manually from a SMILES string.

Example request:

```json
{
  "name": "Aspirin",
  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
}
```

The system should derive:

- canonical SMILES
- molecular formula
- molecular weight
- InChI
- InChIKey
- optional molblock

---

### Update Molecule Metadata

```http
PUT /molecules/{molecule_id}
```

This should update molecule metadata.

The chemical structure itself does not need to be editable at first.

Example request:

```json
{
  "name": "Aspirin batch 001",
  "project": "Demo Project",
  "chemist": "Test User",
  "notes": "Loaded during initial API testing"
}
```

---

### Delete Molecule

```http
DELETE /molecules/{molecule_id}
```

For the first version, physical deletion is acceptable.

Later, this can be changed to soft deletion using:

```text
is_active
deleted_at
```

---

## 4. SDF Upload Endpoint

The application should allow users to upload an SDF file.

```http
POST /uploads/sdf
```

The endpoint should:

- accept multipart file uploads
- validate the uploaded file
- parse SDF records
- extract molecule structures
- extract available SDF properties
- calculate derived chemistry properties
- insert valid molecules into the database
- report invalid or duplicate records clearly

Example response:

```json
{
  "filename": "example.sdf",
  "total_records": 10,
  "registered": 8,
  "duplicates": 1,
  "failed": 1,
  "errors": [
    {
      "record_index": 4,
      "reason": "Could not parse molecule"
    }
  ]
}
```

---

## 5. Duplicate Detection

The first duplicate detection strategy should use InChIKey.

Suggested rule:

```text
If a molecule has the same InChIKey as an existing molecule, treat it as a duplicate.
```

Suggested database index:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_molecules_inchikey
ON molecules(inchikey);
```

Example duplicate response:

```json
{
  "status": "duplicate",
  "existing_molecule_id": 12,
  "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
}
```

---

## 6. Search Endpoints

The API should expose search-focused endpoints.

```http
GET /search/molecules
```

Possible query parameters:

```text
q
name
smiles
inchikey
formula
min_mw
max_mw
project
chemist
```

Example searches:

```http
GET /search/molecules?name=aspirin
GET /search/molecules?min_mw=100&max_mw=500
GET /search/molecules?formula=C9H8O4
```

---

## 7. Molecule Image Rendering

Optional visualization endpoint:

```http
GET /molecules/{molecule_id}/image
```

This should return a 2D molecule image.

Possible response type:

```text
image/png
```

or:

```text
image/svg+xml
```

This allows a browser or lightweight UI to display molecular structures without requiring a full frontend application.

---

# Suggested Project Structure

```text
mini_chemreg/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── db.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── molecules.py
│   │   ├── uploads.py
│   │   └── search.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chemistry.py
│   │   ├── sdf_parser.py
│   │   ├── molecule_registration.py
│   │   └── molecule_rendering.py
│   │
│   └── repositories/
│       ├── __init__.py
│       └── molecule_repository.py
│
├── data/
│   ├── mini_chemreg.db
│   └── uploads/
│
├── sample_files/
│   └── example.sdf
│
├── tests/
│   ├── test_health.py
│   ├── test_molecules.py
│   ├── test_search.py
│   └── test_sdf_upload.py
│
├── requirements.txt
├── README.md
├── PROJECT_SPEC.md
└── .gitignore
```

---

# Application Layers

## Routers

Routers define the API endpoints.

Examples:

```text
routers/health.py
routers/molecules.py
routers/uploads.py
routers/search.py
```

Routers should be thin. They should mostly receive requests, call service functions, and return responses.

---

## Services

Services hold the main application logic.

Examples:

```text
services/chemistry.py
services/sdf_parser.py
services/molecule_registration.py
services/molecule_rendering.py
```

This keeps chemistry-specific logic separate from the API routes.

---

## Repositories

Repositories handle database reads and writes.

Example:

```text
repositories/molecule_repository.py
```

This avoids putting raw SQL directly inside route files.

---

## Schemas

Pydantic schemas should define request and response models.

Example schemas:

```text
MoleculeCreate
MoleculeUpdate
MoleculeResponse
MoleculeSearchParams
SdfUploadResponse
SdfRecordError
```

---

# Suggested Build Stages

## Stage 1: Project Setup

Create the initial FastAPI project structure.

Tasks:

- Create project folders
- Add `__init__.py` files
- Create `main.py`
- Create health router
- Confirm FastAPI app runs
- Add `.gitignore`
- Add `requirements.txt`

Success criteria:

```text
GET /health returns {"status": "ok"}
```

---

## Stage 2: Database Setup

Create the SQLite database and molecule table.

Tasks:

- Create `db.py`
- Create SQLite connection helper
- Create database initialization function
- Create `molecules` table
- Add startup database initialization

Success criteria:

```text
The app creates data/mini_chemreg.db automatically.
The molecules table exists.
```

---

## Stage 3: Basic Molecule CRUD

Implement simple molecule CRUD without chemistry parsing yet.

Tasks:

- Create `MoleculeCreate`
- Create `MoleculeUpdate`
- Create `MoleculeResponse`
- Implement `POST /molecules`
- Implement `GET /molecules`
- Implement `GET /molecules/{molecule_id}`
- Implement `PUT /molecules/{molecule_id}`
- Implement `DELETE /molecules/{molecule_id}`

Success criteria:

```text
A molecule can be created, read, updated, listed, and deleted.
```

At this stage, SMILES can be stored as plain text.

---

## Stage 4: Add Chemistry Derivation from SMILES

Add chemistry logic for molecules created from SMILES.

Tasks:

- Install RDKit or choose chemistry library
- Create `services/chemistry.py`
- Parse SMILES
- Generate canonical SMILES
- Calculate molecular formula
- Calculate molecular weight
- Generate InChI
- Generate InChIKey
- Generate molblock if possible

Success criteria:

```text
POST /molecules accepts a SMILES string and stores derived chemistry fields.
```

Example request:

```json
{
  "name": "Aspirin",
  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
}
```

---

## Stage 5: Duplicate Detection

Add duplicate detection using InChIKey.

Tasks:

- Add unique index on `inchikey`
- Check for existing molecule before insert
- Return useful duplicate response
- Prevent duplicate inserts

Success criteria:

```text
Registering the same molecule twice does not create two records.
```

---

## Stage 6: SDF Upload and Parsing

Implement SDF upload.

Tasks:

- Create `POST /uploads/sdf`
- Accept multipart file upload
- Save uploaded file to `data/uploads`
- Parse SDF file
- Loop through molecule records
- Extract molecule name
- Extract SDF properties
- Derive chemistry fields
- Register valid records
- Report duplicates
- Report invalid records

Success criteria:

```text
Uploading an SDF file registers multiple molecules.
The response reports registered, duplicate, and failed records.
```

---

## Stage 7: Search Endpoints

Add molecule search functionality.

Tasks:

- Create `routers/search.py`
- Implement `GET /search/molecules`
- Search by name
- Search by formula
- Search by InChIKey
- Search by molecular weight range
- Search by project
- Search by chemist

Success criteria:

```text
Users can search molecules by basic text and numeric filters.
```

---

## Stage 8: Molecule Image Endpoint

Add optional molecule rendering.

Tasks:

- Create `services/molecule_rendering.py`
- Generate image from SMILES or molblock
- Implement `GET /molecules/{molecule_id}/image`
- Return PNG or SVG response

Success criteria:

```text
Opening /molecules/{id}/image returns a 2D molecule image.
```

---

## Stage 9: Basic Tests

Add tests for the core API.

Tasks:

- Test health endpoint
- Test molecule creation
- Test molecule listing
- Test molecule retrieval
- Test molecule update
- Test molecule deletion
- Test duplicate detection
- Test search endpoint
- Test SDF upload with a sample file

Success criteria:

```text
Core API behavior is covered by tests.
```

---

## Stage 10: Documentation

Improve project documentation.

Tasks:

- Write README
- Document setup instructions
- Document API endpoints
- Document example requests
- Document project structure
- Document known limitations
- Document future enhancements

Success criteria:

```text
A new developer can clone the repo, install dependencies, run the app, and test the API.
```

---

# MVP Definition

The minimum useful version should support:

```text
1. Start FastAPI app
2. Initialize SQLite database
3. Create molecule manually from SMILES
4. Derive basic chemistry fields
5. Detect duplicates by InChIKey
6. Upload SDF file
7. Parse and register molecules
8. List molecules
9. Get molecule by ID
10. Search molecules by name and molecular weight
```

---

# GitHub Issue Breakdown

The following issues can be created in GitHub and worked through in order.

---

## Issue 1: Create Initial FastAPI Project Structure

### Description

Set up the initial folder and file structure for the Mini ChemReg API.

### Tasks

- [ ] Create root project folder
- [ ] Create `app/`
- [ ] Create `app/main.py`
- [ ] Create `app/__init__.py`
- [ ] Create `app/routers/`
- [ ] Create `app/routers/__init__.py`
- [ ] Create `app/services/`
- [ ] Create `app/services/__init__.py`
- [ ] Create `app/repositories/`
- [ ] Create `app/repositories/__init__.py`
- [ ] Create `data/`
- [ ] Create `data/uploads/`
- [ ] Create `sample_files/`
- [ ] Create `tests/`
- [ ] Create `requirements.txt`
- [ ] Create `.gitignore`
- [ ] Create `README.md`
- [ ] Create `PROJECT_SPEC.md`

### Acceptance Criteria

- The folder structure matches the project specification.
- The project can be opened cleanly in VS Code.
- Python recognizes the `app` package.

---

## Issue 2: Add Health Check Endpoint

### Description

Add a basic health check endpoint to confirm that the API is running.

### Tasks

- [ ] Create `app/routers/health.py`
- [ ] Define a router for health endpoints
- [ ] Add `GET /health`
- [ ] Include the health router in `app/main.py`
- [ ] Run the app locally
- [ ] Confirm the endpoint works in the browser or Swagger UI

### Acceptance Criteria

Calling:

```http
GET /health
```

returns:

```json
{
  "status": "ok"
}
```

---

## Issue 3: Add SQLite Database Connection

### Description

Set up SQLite database support for the application.

### Tasks

- [ ] Create `app/db.py`
- [ ] Define database path
- [ ] Create a database connection helper
- [ ] Set `row_factory` so rows can be read like dictionaries
- [ ] Ensure the `data/` folder exists
- [ ] Add a database initialization function

### Acceptance Criteria

- The application can connect to SQLite.
- The database file can be created automatically.
- Other modules can import the database connection helper.

---

## Issue 4: Create Molecules Table

### Description

Create the main database table for molecule records.

### Tasks

- [ ] Add `init_db()` function
- [ ] Create `molecules` table
- [ ] Add fields for name, smiles, canonical smiles, formula, molecular weight, InChI, InChIKey, molblock, source filename, project, chemist, notes, created_at, and updated_at
- [ ] Call `init_db()` when the application starts
- [ ] Confirm the table exists in SQLite

### Acceptance Criteria

The application creates a SQLite database containing a `molecules` table.

---

## Issue 5: Create Molecule Pydantic Schemas

### Description

Define request and response schemas for molecule endpoints.

### Tasks

- [ ] Create `app/schemas.py`
- [ ] Add `MoleculeCreate`
- [ ] Add `MoleculeUpdate`
- [ ] Add `MoleculeResponse`
- [ ] Add optional schemas for search and upload responses

### Acceptance Criteria

- Molecule endpoint input and output models are defined.
- Schemas are reusable from route files.

---

## Issue 6: Create Molecule Repository

### Description

Create a repository layer for molecule database operations.

### Tasks

- [ ] Create `app/repositories/molecule_repository.py`
- [ ] Add function to create molecule
- [ ] Add function to list molecules
- [ ] Add function to get molecule by ID
- [ ] Add function to update molecule
- [ ] Add function to delete molecule
- [ ] Add function to find molecule by InChIKey

### Acceptance Criteria

- Molecule database logic is separated from API route logic.
- CRUD functions can be called from routers or services.

---

## Issue 7: Implement Basic Molecule CRUD Endpoints

### Description

Add API endpoints for creating, listing, reading, updating, and deleting molecules.

### Tasks

- [ ] Create `app/routers/molecules.py`
- [ ] Implement `POST /molecules`
- [ ] Implement `GET /molecules`
- [ ] Implement `GET /molecules/{molecule_id}`
- [ ] Implement `PUT /molecules/{molecule_id}`
- [ ] Implement `DELETE /molecules/{molecule_id}`
- [ ] Include molecule router in `app/main.py`

### Acceptance Criteria

The API supports full basic molecule CRUD.

---

## Issue 8: Add Chemistry Service for SMILES Parsing

### Description

Create a chemistry service that can parse SMILES and derive molecule properties.

### Tasks

- [ ] Add RDKit dependency
- [ ] Create `app/services/chemistry.py`
- [ ] Add function to parse SMILES
- [ ] Add function to generate canonical SMILES
- [ ] Add function to calculate molecular formula
- [ ] Add function to calculate molecular weight
- [ ] Add function to generate InChI
- [ ] Add function to generate InChIKey
- [ ] Add function to generate molblock

### Acceptance Criteria

Given a valid SMILES string, the chemistry service returns derived molecule properties.

---

## Issue 9: Integrate Chemistry Derivation into Molecule Creation

### Description

Update molecule creation so derived chemistry fields are calculated automatically from SMILES.

### Tasks

- [ ] Update `POST /molecules`
- [ ] Validate that the submitted SMILES can be parsed
- [ ] Derive canonical SMILES
- [ ] Derive formula
- [ ] Derive molecular weight
- [ ] Derive InChI
- [ ] Derive InChIKey
- [ ] Store derived fields in the database
- [ ] Return useful error message for invalid SMILES

### Acceptance Criteria

Creating a molecule from SMILES stores both user-provided and derived chemistry data.

---

## Issue 10: Add Duplicate Detection by InChIKey

### Description

Prevent duplicate molecule registration using InChIKey.

### Tasks

- [ ] Add unique index on `inchikey`
- [ ] Check for an existing molecule before insert
- [ ] Return duplicate response when duplicate is detected
- [ ] Avoid creating duplicate molecule rows
- [ ] Handle SQLite integrity errors gracefully

### Acceptance Criteria

Registering the same molecule twice does not create duplicate database records.

---

## Issue 11: Add SDF Upload Router

### Description

Create the upload endpoint for SDF files.

### Tasks

- [ ] Create `app/routers/uploads.py`
- [ ] Add `POST /uploads/sdf`
- [ ] Accept multipart file upload
- [ ] Validate filename or extension
- [ ] Save uploaded file to `data/uploads/`
- [ ] Return basic upload metadata

### Acceptance Criteria

The API accepts an SDF file upload and saves it locally.

---

## Issue 12: Create SDF Parser Service

### Description

Create a service for parsing SDF files into molecule records.

### Tasks

- [ ] Create `app/services/sdf_parser.py`
- [ ] Load SDF file using RDKit
- [ ] Iterate through molecule records
- [ ] Extract molecule name
- [ ] Extract available SDF properties
- [ ] Skip invalid molecules
- [ ] Return parsed molecule objects and parse errors

### Acceptance Criteria

The SDF parser can read a multi-record SDF file and return parsed molecule data.

---

## Issue 13: Register Molecules from SDF Upload

### Description

Connect the SDF upload endpoint to molecule registration logic.

### Tasks

- [ ] Parse uploaded SDF file
- [ ] Loop through parsed molecules
- [ ] Derive chemistry fields
- [ ] Insert valid molecules into the database
- [ ] Detect duplicates
- [ ] Collect failed records
- [ ] Return upload summary response

### Acceptance Criteria

Uploading an SDF file registers valid molecules and returns a summary of registered, duplicate, and failed records.

---

## Issue 14: Create Molecule Registration Service

### Description

Create a service that centralizes molecule registration behavior.

### Tasks

- [ ] Create `app/services/molecule_registration.py`
- [ ] Add function to register molecule from SMILES
- [ ] Add function to register molecule from RDKit molecule object
- [ ] Add duplicate detection
- [ ] Add consistent registration result format
- [ ] Use this service from manual create and SDF upload endpoints

### Acceptance Criteria

Manual molecule creation and SDF upload use the same registration logic.

---

## Issue 15: Add Search Endpoint

### Description

Add a search-focused endpoint for molecule records.

### Tasks

- [ ] Create `app/routers/search.py`
- [ ] Implement `GET /search/molecules`
- [ ] Support search by name
- [ ] Support search by formula
- [ ] Support search by InChIKey
- [ ] Support molecular weight range search
- [ ] Support project and chemist filters
- [ ] Include search router in `app/main.py`

### Acceptance Criteria

Users can search molecules using text and numeric filters.

---

## Issue 16: Add Molecule Image Rendering Endpoint

### Description

Add an optional endpoint that renders a molecule structure image.

### Tasks

- [ ] Create `app/services/molecule_rendering.py`
- [ ] Generate image from canonical SMILES or molblock
- [ ] Add `GET /molecules/{molecule_id}/image`
- [ ] Return PNG or SVG response
- [ ] Handle missing or invalid structure gracefully

### Acceptance Criteria

Opening the image endpoint returns a rendered 2D molecule image.

---

## Issue 17: Add Basic API Tests

### Description

Add basic tests for the main API behavior.

### Tasks

- [ ] Add test for `GET /health`
- [ ] Add test for molecule creation
- [ ] Add test for molecule listing
- [ ] Add test for molecule retrieval by ID
- [ ] Add test for molecule update
- [ ] Add test for molecule delete
- [ ] Add test for duplicate detection
- [ ] Add test for molecule search

### Acceptance Criteria

Core API behavior is covered by automated tests.

---

## Issue 18: Add SDF Upload Tests

### Description

Add tests for SDF upload and registration behavior.

### Tasks

- [ ] Add small sample SDF file
- [ ] Test upload endpoint
- [ ] Test successful molecule registration
- [ ] Test duplicate molecule handling
- [ ] Test invalid record reporting
- [ ] Test upload summary response shape

### Acceptance Criteria

SDF upload behavior is covered by automated tests.

---

## Issue 19: Improve README Documentation

### Description

Write clear setup and usage documentation.

### Tasks

- [ ] Add project description
- [ ] Add setup instructions
- [ ] Add virtual environment instructions
- [ ] Add dependency installation instructions
- [ ] Add run command
- [ ] Add example API requests
- [ ] Add project structure section
- [ ] Add known limitations
- [ ] Add future enhancements

### Acceptance Criteria

A new developer can clone the repo, install dependencies, run the app, and try the API.

---

## Issue 20: Add Known Limitations Section

### Description

Document the limitations of the first version.

### Tasks

- [ ] Mention that salt/parent handling is not implemented
- [ ] Mention that stereochemistry behavior is basic
- [ ] Mention that structure search is not implemented
- [ ] Mention that authentication is not implemented
- [ ] Mention that this is a learning-focused system

### Acceptance Criteria

The README clearly explains what the project does and does not attempt to solve.

---

# Suggested GitHub Milestones

## Milestone 1: App Foundation

Includes:

- Issue 1: Create Initial FastAPI Project Structure
- Issue 2: Add Health Check Endpoint
- Issue 3: Add SQLite Database Connection
- Issue 4: Create Molecules Table

Goal:

```text
A running FastAPI app with a working SQLite database.
```

---

## Milestone 2: Basic Molecule API

Includes:

- Issue 5: Create Molecule Pydantic Schemas
- Issue 6: Create Molecule Repository
- Issue 7: Implement Basic Molecule CRUD Endpoints

Goal:

```text
A molecule can be created, listed, read, updated, and deleted.
```

---

## Milestone 3: Chemistry Registration

Includes:

- Issue 8: Add Chemistry Service for SMILES Parsing
- Issue 9: Integrate Chemistry Derivation into Molecule Creation
- Issue 10: Add Duplicate Detection by InChIKey

Goal:

```text
Molecules can be registered from SMILES with derived chemical properties and duplicate detection.
```

---

## Milestone 4: SDF Upload

Includes:

- Issue 11: Add SDF Upload Router
- Issue 12: Create SDF Parser Service
- Issue 13: Register Molecules from SDF Upload
- Issue 14: Create Molecule Registration Service

Goal:

```text
Users can upload an SDF file and register multiple molecules.
```

---

## Milestone 5: Search and Visualization

Includes:

- Issue 15: Add Search Endpoint
- Issue 16: Add Molecule Image Rendering Endpoint

Goal:

```text
Users can search molecules and optionally view rendered molecule structures.
```

---

## Milestone 6: Testing and Documentation

Includes:

- Issue 17: Add Basic API Tests
- Issue 18: Add SDF Upload Tests
- Issue 19: Improve README Documentation
- Issue 20: Add Known Limitations Section

Goal:

```text
The project is tested, documented, and easier to share on GitHub.
```

---

# Future Enhancements

Possible future improvements:

- Registration numbers
- Compound batches
- Parent/salt handling
- Audit history
- Soft deletion
- Project assignment
- Chemist ownership
- SDF export
- CSV export
- Molecule gallery page
- Structure search
- Substructure search
- Similarity search
- Authentication
- Role-based permissions
- Docker support
- Migration system
- Frontend UI

---

# Recommended Development Order

The recommended order is:

```text
1. Health endpoint
2. Database connection
3. Molecule table
4. Basic molecule CRUD
5. SMILES chemistry parsing
6. Duplicate detection
7. SDF upload
8. SDF parsing
9. Molecule registration service
10. Search
11. Molecule rendering
12. Tests
13. Documentation
```

---

# Final MVP Checklist

The MVP is complete when the application can:

- [ ] Start with FastAPI
- [ ] Initialize a SQLite database
- [ ] Create a molecule manually from SMILES
- [ ] Derive canonical SMILES, formula, molecular weight, InChI, and InChIKey
- [ ] Detect duplicates by InChIKey
- [ ] Upload an SDF file
- [ ] Parse and register molecules from SDF
- [ ] List molecules
- [ ] Get molecule by ID
- [ ] Search molecules by name
- [ ] Search molecules by molecular weight range
- [ ] Return clear errors for invalid molecules
- [ ] Provide basic project documentation