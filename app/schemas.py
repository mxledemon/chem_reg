from pydantic import BaseModel
from typing import Optional

class MoleculeCreate(BaseModel):
    name: Optional[str] = None
    smiles: str
    

class MoleculeResponse(BaseModel):
    pass 


class MoleculeUpdate(BaseModel):
    pass 


