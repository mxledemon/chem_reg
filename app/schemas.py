from pydantic import BaseModel
from typing import Optional

class MoleculeCreate(BaseModel):
    name: Optional[str] = None
    smiles: str
    project: Optional[str] = None
    chemist: Optional[str] = None
    notes: Optional[str] = None
    

class MoleculeResponse(BaseModel):
    id: int
    name: Optional[str] = None
    smiles: str
    canonical_smiles: Optional[str] = None
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    inchi: Optional[str] = None
    inchikey: Optional[str] = None
    molblock: Optional[str] = None
    source_filename: Optional[str] = None
    project: Optional[str] = None
    chemist: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str 


class MoleculeUpdate(BaseModel):
    name: Optional[str] = None
    smiles: Optional[str] = None
    project: Optional[str] = None
    chemist: Optional[str] = None
    notes: Optional[str] = None


class MoleculeSearchParams(BaseModel):
    name: Optional[str] = None
    formula: Optional[str] = None
    project: Optional[str] = None
    chemist: Optional[str] = None
    min_molecular_weight: Optional[float] = None
    max_molecular_weight: Optional[float] = None
    limit: int = 10
    offset: int = 0

class MoleculeSearchResponse(BaseModel):
    results: list[MoleculeResponse]
    total: int
    limit: int
    offset: int

class MoleculeUploadResponse(BaseModel):
    filename: str
    molecules_created: int
    molecule_ids: list[int]
    errors: list[str]