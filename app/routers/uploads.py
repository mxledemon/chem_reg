from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

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

    return {
        'filename': safe_filename,
        'content_type': file.content_type,
        'size_bytes': len(contents),
        'saved_path': str(destination)
    }