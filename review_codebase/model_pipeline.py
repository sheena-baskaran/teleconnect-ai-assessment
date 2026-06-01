"""
TeleConnect Churn Prediction Pipeline
--------------------------------------
Trains and serves the churn prediction model used by the retention agent.
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder


def load_and_prepare_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["gender"] = df["gender"].str.lower().str.strip()
    df["gender"] = df["gender"].map({"male": 0, "m": 0, "female": 1, "f": 1})
    df["contract_type"] = LabelEncoder().fit_transform(df["contract_type"])
    df["internet_service"] = LabelEncoder().fit_transform(df["internet_service"].fillna("None"))
    df["phone_service"] = df["phone_service"].str.lower().map({"yes": 1, "y": 1, "no": 0, "n": 0})
    df["payment_method"] = LabelEncoder().fit_transform(df["payment_method"].fillna("Unknown"))
    df.fillna(df.mean(numeric_only=True), inplace=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df["charge_per_tenure"] = df["monthly_charges"] / (df["tenure_months"] + 1)
    df["avg_charges_by_contract"] = df.groupby("contract_type")["monthly_charges"].transform("mean")
    df["churn_rate_by_contract"] = df.groupby("contract_type")["churned"].transform("mean")
    df["tenure_bucket"] = pd.cut(df["tenure_months"], bins=[0, 12, 24, 48, 120], labels=[0, 1, 2, 3])
    df["tenure_bucket"] = df["tenure_bucket"].astype(float)
    df["interaction_recency"] = (
        pd.to_datetime("2024-07-01") - pd.to_datetime(df["last_interaction_date"])
    ).dt.days
    df["total_expected_charges"] = df["monthly_charges"] * df["tenure_months"]
    df["charge_discrepancy"] = df["total_charges"] - df["total_expected_charges"]
    return df


FEATURE_COLS = [
    "age", "tenure_months", "monthly_charges", "total_charges",
    "avg_monthly_gb_used", "num_support_tickets", "avg_monthly_minutes",
    "satisfaction_score", "num_additional_services", "gender",
    "contract_type", "internet_service", "phone_service", "payment_method",
    "charge_per_tenure", "avg_charges_by_contract", "churn_rate_by_contract",
    "tenure_bucket", "interaction_recency", "charge_discrepancy",
]


def train_model(data_path: str, model_output: str = "churn_model.pkl"):
    df = load_and_prepare_data(data_path)
    df = engineer_features(df)

    X = df[FEATURE_COLS]
    y = df["churned"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"AUC-ROC:  {roc_auc_score(y_test, y_pred):.4f}")

    with open(model_output, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_output}")
    return model


def predict_churn(customer_data: dict) -> dict:
    with open("churn_model.pkl", "rb") as f:
        model = pickle.load(f)

    features = pd.DataFrame([customer_data])[FEATURE_COLS]
    probability = model.predict_proba(features)[0][1]

    if probability > 0.7:
        risk_tier = "high"
    elif probability > 0.4:
        risk_tier = "medium"
    else:
        risk_tier = "low"

    importances = model.feature_importances_
    top_indices = np.argsort(importances)[-3:][::-1]
    top_factors = [FEATURE_COLS[i] for i in top_indices]

    return {
        "churn_probability": round(probability, 3),
        "risk_tier": risk_tier,
        "top_risk_factors": top_factors,
    }


if __name__ == "__main__":
    train_model("data/customers.csv")
