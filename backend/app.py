from flask import Flask, jsonify
import pandas as pd

# --------------------------------------------------
# 1️⃣ Create Flask App FIRST
# --------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------
# 2️⃣ Load Data ONCE (not inside routes)
# --------------------------------------------------
df = pd.read_csv("../data/processed/featured_data.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"])

# --------------------------------------------------
# 3️⃣ Executive Overview API
# --------------------------------------------------
@app.route("/api/executive-overview")
def executive_overview():

    monthly = (
        df.groupby(pd.Grouper(key="Order Date", freq="ME"))
        .agg({
            "Sales": "sum",
            "Profit": "sum",
            "Discount": "mean"
        })
        .reset_index()
    )

    return jsonify({
        "kpis": {
            "total_sales": float(monthly["Sales"].sum()),
            "total_profit": float(monthly["Profit"].sum()),
            "avg_discount": float(monthly["Discount"].mean())
        },
        "trend": monthly.to_dict(orient="records")
    })


# --------------------------------------------------
# 4️⃣ Run Flask App
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
