from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.services.sdf_registration import register_molecules_from_sdf

router = APIRouter(prefix='/uploads', tags=['uploads'])

UPLOAD_DIR = Path('data/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post('/sdf')
def upload_sdf(file: UploadFile = File(...)):
    # Validate file name or extension
    if not file.filename:
        raise HTTPException(status_code=400, detail='No filename provided')
    
    if not file.filename.lower().endswith('.sdf'):
        raise HTTPException(status_code=400, detail='Only .sdf files are supported.')
    
    # Strip any directory/path information from the uploaded filename
    safe_filename = Path(file.filename).name

    # Build full destination path
    destination = UPLOAD_DIR / safe_filename

    # Read uploaded file as bytes
    contents = file.file.read()

    # Save file to disk
    with open(destination, 'wb') as buffer:
        buffer.write(contents)

    try:
        registration_result = register_molecules_from_sdf(
            file_path=str(destination),
            filename=safe_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to register molecules from SDF: {e}') from e

    return {
        'filename': safe_filename,
        'content_type': file.content_type,
        'size_bytes': len(contents),
        'saved_path': str(destination),
        'registration': registration_result
    }