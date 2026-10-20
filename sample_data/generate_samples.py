"""Generates small, realistic synthetic sample datasets for the demo."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


def gen_churn(n=250):
    tenure = rng.integers(1, 72, n)
    monthly_charges = np.round(rng.normal(65, 25, n).clip(15, 150), 2)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.25, 0.20])
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.35, 0.45, 0.20])
    support_calls = rng.poisson(1.5, n)
    age = rng.integers(18, 75, n)
    gender = rng.choice(["Male", "Female"], n)
    payment = rng.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], n)

    churn_prob = (
        0.35 * (contract == "Month-to-month")
        + 0.25 * (tenure < 12)
        + 0.15 * (support_calls >= 3)
        + 0.1 * (internet == "Fiber optic")
        + 0.05
    )
    churn = (rng.random(n) < churn_prob).astype(int)
    churn_label = np.where(churn == 1, "Yes", "No")

    total_charges = np.round(monthly_charges * tenure * rng.uniform(0.9, 1.05, n), 2)

    df = pd.DataFrame({
        "customer_id": [f"CUST{i:05d}" for i in range(n)],
        "age": age,
        "gender": gender,
        "tenure_months": tenure,
        "contract_type": contract,
        "internet_service": internet,
        "payment_method": payment,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "support_calls": support_calls,
        "churn": churn_label,
    })
    return df


def gen_sales(n=300):
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    region = rng.choice(["North", "South", "East", "West"], n)
    category = rng.choice(["Electronics", "Clothing", "Home", "Sports", "Books"], n)
    units = rng.integers(1, 50, n)
    unit_price = np.round(rng.uniform(5, 500, n), 2)
    discount_pct = np.round(rng.choice([0, 0, 0, 5, 10, 15, 20], n), 2)
    revenue = np.round(units * unit_price * (1 - discount_pct / 100), 2)
    marketing_spend = np.round(rng.uniform(0, 500, n), 2)
    customer_rating = np.round(rng.normal(4.0, 0.6, n).clip(1, 5), 1)

    df = pd.DataFrame({
        "order_date": dates.strftime("%Y-%m-%d"),
        "region": region,
        "category": category,
        "units_sold": units,
        "unit_price": unit_price,
        "discount_pct": discount_pct,
        "marketing_spend": marketing_spend,
        "customer_rating": customer_rating,
        "revenue": revenue,
    })
    return df


if __name__ == "__main__":
    gen_churn().to_csv("customer_churn_sample.csv", index=False)
    gen_sales().to_csv("sales_sample.csv", index=False)
    print("Generated customer_churn_sample.csv and sales_sample.csv")
