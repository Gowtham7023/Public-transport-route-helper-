import os
import sys
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from ml.data_generator import generate_historical_delay_dataset
from ml.preprocess import prepare_train_test_split, FEATURE_COLUMNS
from app.database.connection import SessionLocal
from app.models.models import MLModelVersion

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate_models():
    print("=" * 60)
    print("TRAIN DELAY REGRESSION PIPELINE - MODEL TRAINING & EVALUATION")
    print("=" * 60)

    # 1. Dataset Generation / Loading
    dataset_path = backend_dir.parent / "data" / "processed" / "historical_train_delays.csv"
    if dataset_path.exists():
        print(f"Loading existing historical dataset from: {dataset_path}")
        import pandas as pd
        df = pd.read_csv(dataset_path)
    else:
        print("Generating realistic chronological operational delay dataset...")
        df = generate_historical_delay_dataset(num_records=5000, seed=42)
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(dataset_path, index=False)
        print(f"Saved dataset ({len(df)} records) to: {dataset_path}")

    # 2. Chronological Train-Test Split (Zero-leakage)
    X_train, X_test, y_train, y_test = prepare_train_test_split(df, test_ratio=0.2)
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    print(f"Engineered features ({len(FEATURE_COLUMNS)}): {FEATURE_COLUMNS}\n")

    # Historical Baseline (Predict Mean / Median)
    baseline_pred = np.full_like(y_test, y_train.mean())
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
    print(f"[BASELINE] Mean Predictor -> MAE: {baseline_mae:.2f} min, RMSE: {baseline_rmse:.2f} min\n")

    # 3. Model 1: HistGradientBoostingRegressor
    print("Training HistGradientBoostingRegressor...")
    hgbr = HistGradientBoostingRegressor(
        max_iter=150,
        learning_rate=0.08,
        max_depth=6,
        random_state=42
    )
    hgbr.fit(X_train, y_train)
    hgbr_pred = hgbr.predict(X_test)
    hgbr_mae = mean_absolute_error(y_test, hgbr_pred)
    hgbr_rmse = np.sqrt(mean_squared_error(y_test, hgbr_pred))
    hgbr_r2 = r2_score(y_test, hgbr_pred)
    print(f"[MODEL 1: HistGradientBoosting] MAE: {hgbr_mae:.2f} min | RMSE: {hgbr_rmse:.2f} min | R²: {hgbr_r2:.4f}")

    # 4. Model 2: RandomForestRegressor
    print("Training RandomForestRegressor...")
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    rf_r2 = r2_score(y_test, rf_pred)
    print(f"[MODEL 2: RandomForest]         MAE: {rf_mae:.2f} min | RMSE: {rf_rmse:.2f} min | R²: {rf_r2:.4f}\n")

    # 5. Model Selection & Persistence
    best_model_name = "HistGradientBoostingRegressor" if hgbr_mae <= rf_mae else "RandomForestRegressor"
    best_model = hgbr if best_model_name == "HistGradientBoostingRegressor" else rf
    best_mae = min(hgbr_mae, rf_mae)
    best_rmse = hgbr_rmse if best_model_name == "HistGradientBoostingRegressor" else rf_rmse
    best_r2 = hgbr_r2 if best_model_name == "HistGradientBoostingRegressor" else rf_r2

    print(f"Selected Champion Model: {best_model_name} (Lowest MAE: {best_mae:.2f} min)")

    artifact_filename = "hist_gradient_boosting_v1.joblib"
    artifact_path = ARTIFACTS_DIR / artifact_filename
    joblib.dump({
        "model": best_model,
        "model_name": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": {"mae": best_mae, "rmse": best_rmse, "r2": best_r2},
        "training_samples": len(X_train),
        "version": "1.0.0"
    }, artifact_path)
    print(f"Saved champion artifact to: {artifact_path}")

    # 6. Save metadata to database
    try:
        db = SessionLocal()
        # Mark previous versions inactive
        db.query(MLModelVersion).update({MLModelVersion.is_active: False})
        record = MLModelVersion(
            model_name=best_model_name,
            version="1.0.0",
            algorithm=best_model_name,
            mae=round(float(best_mae), 2),
            rmse=round(float(best_rmse), 2),
            r2_score=round(float(best_r2), 4),
            training_records_count=len(X_train),
            artifact_path=str(artifact_path),
            is_active=True
        )
        db.add(record)
        db.commit()
        db.close()
        print("Updated MLModelVersion registry in database.")
    except Exception as e:
        print(f"Notice: database logging skipped ({e})")

    print("=" * 60)
    return best_model, best_mae, best_rmse, best_r2

if __name__ == "__main__":
    train_and_evaluate_models()

