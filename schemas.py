from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    code: str = Field(..., description="Barcode value")
    name: str
    manufacturer: str
    category: str
    mfgDate: Optional[str] = None
    expDate: Optional[str] = None
    rating: Optional[int] = None
    footprintKgCO2e: Optional[float] = None

class ScanResponse(Product):
    id: Optional[str] = None
    scannedAt: Optional[int] = None

class ScanQuery(BaseModel):
    code: str
