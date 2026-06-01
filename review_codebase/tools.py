"""
TeleConnect Agent Tools
-----------------------
Tool implementations for the retention agent.
"""
import pandas as pd
import pickle
import numpy as np
from model_pipeline import FEATURE_COLS

CUSTOMER_DATA = pd.read_csv("data/customers.csv")


def lookup_customer(customer_id: str) -> dict:
    row = CUSTOMER_DATA[CUSTOMER_DATA["customer_id"] == customer_id]
    if len(row) == 0:
        return {"error": "Customer not found"}
    return row.iloc[0].to_dict()


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
        "churn_probability": round(float(probability), 3),
        "risk_tier": risk_tier,
        "top_risk_factors": top_factors,
    }


OFFER_CATALOG = [
    {"id": "OFF-001", "name": "10% monthly discount", "type": "discount", "duration": "6 months", "contract_required": "One year"},
    {"id": "OFF-002", "name": "Free speed upgrade", "type": "upgrade", "duration": "12 months", "contract_required": None},
    {"id": "OFF-003", "name": "20% monthly discount", "type": "discount", "duration": "12 months", "contract_required": "Two year"},
    {"id": "OFF-004", "name": "Free premium channels", "type": "addon", "duration": "3 months", "contract_required": None},
    {"id": "OFF-005", "name": "Waive early termination fee", "type": "waiver", "duration": "one-time", "contract_required": None},
    {"id": "OFF-006", "name": "30% monthly discount", "type": "discount", "duration": "12 months", "contract_required": "Two year"},
]


def get_retention_offers(risk_tier: str, contract_type: str = None) -> dict:
    return {"offers": OFFER_CATALOG}


interaction_log = []


def log_interaction(customer_id: str, offer_made: str = None, outcome: str = None, notes: str = None) -> dict:
    entry = {
        "customer_id": customer_id,
        "offer_made": offer_made,
        "outcome": outcome,
        "notes": notes,
    }
    interaction_log.append(entry)
    return {"status": "logged", "entry": entry}


def escalate_to_supervisor(reason: str, conversation_summary: str = None) -> dict:
    return {
        "status": "escalated",
        "message": f"Case escalated. Reason: {reason}",
    }
