<<<<<<< HEAD
# Hearth: House Price Prediction

A full stack learning project for estimating Ames, Iowa home sale prices. The FastAPI backend loads the local CSV and uses a Python-only nearest-neighbor model. The React and Vite frontend collects property features and displays the prediction.

## Project layout

```text
house_price_prediction/
├── data/train.csv                 # Ames Housing training data
├── backend/
│   ├── app.py                    # FastAPI application and API routes
│   ├── main.py                   # Compatibility entry point
│   ├── train_model.py            # Data validation and model training
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
├── .gitignore
└── README.md
```

Keep one Python environment at the project root (`venv/`).

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer and npm
- `data/train.csv`

## Start the backend (PowerShell)

Run these commands from the project root:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app:app --reload
```

The API listens at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

## API endpoints

- `GET /api/health` returns status and training row count.
- `POST /api/predict` accepts `overall_qual`, `living_area`, `garage_cars`, `basement_area`, `full_baths`, `year_built`, `neighborhood`, and `kitchen_quality`; it returns `estimated_price` in USD.

Example request body:

```json
{
  "overall_qual": 7,
  "living_area": 1900,
  "garage_cars": 2,
  "basement_area": 1050,
  "full_baths": 2,
  "year_built": 2005,
  "neighborhood": "CollgCr",
  "kitchen_quality": "Gd"
}
```

This dataset contains historical sales in Ames, Iowa. Predictions are for learning and exploration, not a formal appraisal. Dataset: [Kaggle House Prices competition](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data).
=======
# House_Price_Prediction
This Project describe the house price with multiple data inputs
>>>>>>> c711bd1c0d7326c49d06559ab5669207ecb155b1
