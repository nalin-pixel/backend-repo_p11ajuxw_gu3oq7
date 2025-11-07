from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import Product, ScanResponse, ScanQuery
from database import create_document, get_documents
import random
import datetime

app = FastAPI(title="EcoShopper API", version="1.0.0")

# Allow all origins for sandbox; in production, restrict this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock in-memory enrichment map for demo; real data should come from GS1/OpenFoodFacts
MOCK_DB = {
    '8901063010805': { 'name': 'Whole Wheat Bread', 'manufacturer': 'Healthy Bakes Co.', 'category': 'Food & Beverages' },
    '012345678905': { 'name': 'Sparkle Soda 330ml', 'manufacturer': 'FizzCraft Beverages', 'category': 'Beverages' },
    '9780306406157': { 'name': 'Sustainable Living Guide', 'manufacturer': 'EcoPrint Publishers', 'category': 'Books & Media' },
    '4901234567894': { 'name': 'Bamboo Toothbrush 2-Pack', 'manufacturer': 'GreenSmile', 'category': 'Personal Care' },
    '0012345678905': { 'name': 'Oak Side Table', 'manufacturer': 'HomeCraft Furnishings', 'category': 'Furniture' },
}


def random_in_past_months(months: int = 9) -> datetime.datetime:
    now = datetime.datetime.utcnow()
    delta_months = random.randint(0, months)
    # subtract roughly in days
    days = delta_months * 30 + random.randint(0, 29)
    return now - datetime.timedelta(days=days)


def add_months(d: datetime.datetime, months: int) -> datetime.datetime:
    # naive month add for demo
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
    return datetime.datetime(year, month, day, d.hour, d.minute, d.second, d.microsecond)


@app.get("/test")
async def test():
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
async def scan_product(payload: ScanQuery):
    code = payload.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Invalid barcode")

    base = MOCK_DB.get(code, {"name": "Product", "manufacturer": "Unknown Manufacturer", "category": "General Merchandise"})
    mfg = random_in_past_months(9)
    exp = add_months(mfg, 12 + random.randint(0, 12))

    rating = random.randint(50, 95)
    footprint = round(0.5 + random.random() * 5, 2)

    doc = await create_document(
        "product",
        {
            "code": code,
            "name": base["name"],
            "manufacturer": base["manufacturer"],
            "category": base["category"],
            "mfgDate": mfg.isoformat(),
            "expDate": exp.isoformat(),
            "rating": rating,
            "footprintKgCO2e": footprint,
            "scannedAt": int(datetime.datetime.utcnow().timestamp() * 1000),
        },
    )

    return ScanResponse(
        id=doc.get("_id"),
        code=doc["code"],
        name=doc["name"],
        manufacturer=doc["manufacturer"],
        category=doc["category"],
        mfgDate=doc["mfgDate"],
        expDate=doc["expDate"],
        rating=doc.get("rating"),
        footprintKgCO2e=doc.get("footprintKgCO2e"),
        scannedAt=doc.get("scannedAt"),
    )


@app.get("/history", response_model=List[ScanResponse])
async def history(limit: int = 25):
    docs = await get_documents("product", {}, limit)
    return [
        ScanResponse(
            id=d.get("_id"),
            code=d.get("code"),
            name=d.get("name"),
            manufacturer=d.get("manufacturer"),
            category=d.get("category"),
            mfgDate=d.get("mfgDate"),
            expDate=d.get("expDate"),
            rating=d.get("rating"),
            footprintKgCO2e=d.get("footprintKgCO2e"),
            scannedAt=d.get("scannedAt"),
        )
        for d in docs
    ]
