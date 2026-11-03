import numpy as np
import pandas as pd
from typing import Tuple, List

FEATURE_COLUMNS = [
    "priority_tier",
    "distance_km",
    "scheduled_duration_min",
    "prev_segment_delay_min",
    "sin_hour", "cos_hour",
    "sin_dow", "cos_dow",
    "sin_month", "cos_month",
    "type_VANDE_BHARAT",
    "type_SHATABDI",
    "type_SUPERFAST",
    "type_MAIL_EXPRESS",
    "type_EXPRESS"
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw operational fields into engineered features for regression."""
    df_feat = pd.DataFrame(index=df.index)

    # Priority & duration
    df_feat["priority_tier"] = df["priority_tier"].astype(float)
    df_feat["distance_km"] = df["distance_km"].astype(float)
    df_feat["scheduled_duration_min"] = df["scheduled_duration_min"].astype(float)
    df_feat["prev_segment_delay_min"] = df.get("prev_segment_delay_min", 0.0).astype(float)

    # Cyclical hour encoding
    hour = df["scheduled_dep_hour"].astype(float)
    df_feat["sin_hour"] = np.sin(2 * np.pi * hour / 24.0)
    df_feat["cos_hour"] = np.cos(2 * np.pi * hour / 24.0)

    # Cyclical day-of-week encoding
    dow = df["day_of_week"].astype(float)
    df_feat["sin_dow"] = np.sin(2 * np.pi * dow / 7.0)
    df_feat["cos_dow"] = np.cos(2 * np.pi * dow / 7.0)

    # Cyclical month encoding
    month = df["month"].astype(float)
    df_feat["sin_month"] = np.sin(2 * np.pi * month / 12.0)
    df_feat["cos_month"] = np.cos(2 * np.pi * month / 12.0)

    # One-hot encoded train types
    train_types = ["VANDE_BHARAT", "SHATABDI", "SUPERFAST", "MAIL_EXPRESS", "EXPRESS"]
    for t in train_types:
        df_feat[f"type_{t}"] = (df["train_type"] == t).astype(float)

    # Ensure all required columns exist
    for col in FEATURE_COLUMNS:
        if col not in df_feat.columns:
            df_feat[col] = 0.0

    return df_feat[FEATURE_COLUMNS]

def prepare_train_test_split(df: pd.DataFrame, test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Chronological split to ensure no future data leakage."""
    split_idx = int(len(df) * (1 - test_ratio))
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = engineer_features(train_df)
    y_train = train_df["arrival_delay_min"]

    X_test = engineer_features(test_df)
    y_test = test_df["arrival_delay_min"]

    return X_train, X_test, y_train, y_test

