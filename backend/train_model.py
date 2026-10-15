"""Load the Ames CSV and prepare a Python-only nearest-neighbor model."""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "train.csv"

NUMERIC_FEATURES = ["OverallQual", "GrLivArea", "GarageCars", "TotalBsmtSF", "FullBath", "YearBuilt"]
CATEGORICAL_FEATURES = ["Neighborhood", "KitchenQual"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "SalePrice"
NEIGHBOR_COUNT = 25


def _number(value: Any) -> float | None:
    """Parse a CSV number, treating blank and NA markers as missing."""
    if value is None or str(value).strip().upper() in {"", "NA", "N/A", "NONE"}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


@dataclass
class HousePriceModel:
    """K-nearest-neighbor regression over the selected training features."""

    rows: list[dict[str, Any]]
    numeric_ranges: dict[str, float]
    neighbor_count: int = NEIGHBOR_COUNT

    def predict_price(self, house: dict[str, Any]) -> float:
        distances: list[tuple[float, float]] = []
        feature_count = len(FEATURES)
        for row in self.rows:
            squared_distance = 0.0
            for feature in NUMERIC_FEATURES:
                delta = (float(house[feature]) - row[feature]) / self.numeric_ranges[feature]
                squared_distance += delta * delta
            for feature in CATEGORICAL_FEATURES:
                if house[feature] != row[feature]:
                    squared_distance += 1.0
            distance = (squared_distance / feature_count) ** 0.5
            distances.append((distance, row[TARGET]))

        nearest = sorted(distances, key=lambda item: item[0])[: self.neighbor_count]
        weighted_total = 0.0
        total_weight = 0.0
        for distance, price in nearest:
            weight = 1.0 / (distance * distance + 0.0025)
            weighted_total += weight * price
            total_weight += weight
        if total_weight == 0:
            raise ValueError("Could not find comparable training homes")
        return weighted_total / total_weight


def train_model(data_path: Path = DEFAULT_DATA_PATH) -> tuple[HousePriceModel, int]:
    """Load, validate, and prepare the data used by the predictor."""
    if not data_path.is_file():
        raise FileNotFoundError(f"Training data not found at {data_path}. Place the Ames train.csv in data/.")

    with data_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("train.csv is empty or has no header row.")
        missing_columns = [name for name in FEATURES + [TARGET] if name not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"train.csv is missing required columns: {', '.join(missing_columns)}")
        source_rows = list(reader)

    parsed_rows: list[dict[str, Any]] = []
    numeric_values: dict[str, list[float]] = {feature: [] for feature in NUMERIC_FEATURES}
    categorical_values: dict[str, list[str]] = {feature: [] for feature in CATEGORICAL_FEATURES}
    for source in source_rows:
        target = _number(source.get(TARGET))
        if target is None:
            continue
        row: dict[str, Any] = {TARGET: target}
        for feature in NUMERIC_FEATURES:
            value = _number(source.get(feature))
            row[feature] = value
            if value is not None:
                numeric_values[feature].append(value)
        for feature in CATEGORICAL_FEATURES:
            value = (source.get(feature) or "").strip()
            if not value or value.upper() == "NA":
                value = ""
            row[feature] = value
            if value:
                categorical_values[feature].append(value)
        parsed_rows.append(row)

    if not parsed_rows:
        raise ValueError("train.csv has no rows with a valid SalePrice value.")
    numeric_medians: dict[str, float] = {}
    numeric_ranges: dict[str, float] = {}
    for feature, values in numeric_values.items():
        if not values:
            raise ValueError(f"train.csv has no usable values for {feature}.")
        numeric_medians[feature] = _median(values)
        numeric_ranges[feature] = max(max(values) - min(values), 1.0)

    categorical_modes: dict[str, str] = {}
    for feature, values in categorical_values.items():
        if not values:
            raise ValueError(f"train.csv has no usable values for {feature}.")
        categorical_modes[feature] = max(set(values), key=values.count)

    for row in parsed_rows:
        for feature in NUMERIC_FEATURES:
            if row[feature] is None:
                row[feature] = numeric_medians[feature]
        for feature in CATEGORICAL_FEATURES:
            if not row[feature]:
                row[feature] = categorical_modes[feature]

    return HousePriceModel(parsed_rows, numeric_ranges), len(parsed_rows)
