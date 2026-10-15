"""HTTP API for the Ames Housing price estimator."""

from contextlib import asynccontextmanager
from typing import Literal
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Support both `python -m backend.app` from the project root and
# `python app.py` from inside the backend directory.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.train_model import CATEGORICAL_FEATURES, NUMERIC_FEATURES, HousePriceModel, train_model


class HouseFeatures(BaseModel):
    """The property fields used by the prediction model."""

    overall_qual: int = Field(default=6, ge=1, le=10)
    living_area: int = Field(default=1500, ge=200, le=10000)
    garage_cars: int = Field(default=2, ge=0, le=5)
    basement_area: int = Field(default=1000, ge=0, le=6000)
    full_baths: int = Field(default=2, ge=0, le=5)
    year_built: int = Field(default=2000, ge=1870, le=2010)
    neighborhood: Literal[
        "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr", "CollgCr", "Crawfor",
        "Edwards", "Gilbert", "IDOTRR", "MeadowV", "Mitchel", "NAmes", "NoRidge",
        "NPkVill", "NridgHt", "NWAmes", "OldTown", "SWISU", "Sawyer", "SawyerW",
        "Somerst", "StoneBr", "Timber", "Veenker",
    ] = "CollgCr"
    kitchen_quality: Literal["Ex", "Gd", "TA", "Fa", "Po"] = "TA"


class Prediction(BaseModel):
    estimated_price: float
    currency: str = "USD"
    model: str = "Ames Housing nearest-neighbor estimate"


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load the local training data once as the API starts."""
    application.state.model, application.state.training_rows = train_model()
    yield


app = FastAPI(
    title="Ames House Price API",
    description="Estimate an Ames, Iowa sale price from selected home features.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str | int]:
    """Return API status and the number of training homes loaded."""
    if getattr(app.state, "model", None) is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {"status": "ok", "training_rows": app.state.training_rows}


@app.post("/api/predict", response_model=Prediction)
def predict(house: HouseFeatures) -> Prediction:
    """Estimate price using the closest comparable training homes."""
    model: HousePriceModel | None = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    payload = house.model_dump()
    input_values = {
        "OverallQual": payload["overall_qual"],
        "GrLivArea": payload["living_area"],
        "GarageCars": payload["garage_cars"],
        "TotalBsmtSF": payload["basement_area"],
        "FullBath": payload["full_baths"],
        "YearBuilt": payload["year_built"],
        "Neighborhood": payload["neighborhood"],
        "KitchenQual": payload["kitchen_quality"],
    }
    if not all(feature in input_values for feature in NUMERIC_FEATURES + CATEGORICAL_FEATURES):
        raise HTTPException(status_code=422, detail="Required house features are missing")
    try:
        price = model.predict_price(input_values)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Could not estimate these home features") from exc
    return Prediction(estimated_price=round(max(0.0, price), 2))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
