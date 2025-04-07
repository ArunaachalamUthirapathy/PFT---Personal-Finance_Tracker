import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px

# --- FILE SETUP ---
DATA_FILE = "transactions.csv"
CATEGORIES = ["Food", "Transport", "Entertainment", "Health", "Bills", "Shopping", "Others"]

# --- LOAD OR CREATE CSV ---
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# --- PAGE SETUP ---
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("💰 Personal Finance Tracker")

# --- SIDEBAR FILTER ---
st.sidebar.header("📊 Filters")
category_filter = st.sidebar.multiselect("Filter by Category", CATEGORIES, default=CATEGORIES)
filtered_df = df[df["Category"].isin(category_filter)]

# --- ADD TRANSACTION FORM ---
st.header("➕ Add New Transaction")
with st.form("transaction_form"):
    date = st.date_input("Date")
    amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
    category = st.selectbox("Category", CATEGORIES)
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        new_data = {
            "Date": str(date.strftime("%Y-%m-%d")),
            "Amount": float(amount),
            "Category": str(category),
            "Description": str(description).strip()
        }
        df = df._append(new_data, ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Transaction added successfully!")

# --- BUDGET ALERTS ---
st.sidebar.header("📌 Budget Alerts")
budget_limits = {cat: st.sidebar.number_input(f"Max ₹ for {cat}", value=1000.0, step=100.0) for cat in CATEGORIES}
alerts = []
for cat in CATEGORIES:
    total_spent = df[df["Category"] == cat]["Amount"].sum()
    if total_spent > budget_limits[cat]:
        alerts.append(f"⚠️ Over budget in {cat}: Spent ₹{total_spent:.2f} > ₹{budget_limits[cat]:.2f}")
if alerts:
    st.warning("\n".join(alerts))

# --- TRANSACTION TABLE ---
st.header("📄 All Transactions")
st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True)

# --- EXPORT TO EXCEL ---
st.download_button(
    label="📥 Export to Excel",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="transactions_export.csv",
    mime="text/csv"
)

# --- SPENDING SUMMARY ---
st.header("📈 Spending Breakdown")
if not filtered_df.empty:
    category_sum = filtered_df.groupby("Category")["Amount"].sum()
    fig, ax = plt.subplots()
    ax.pie(category_sum, labels=category_sum.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    total = category_sum.sum()
    st.markdown(f"### 💵 Total Spent: ₹ {total:.2f}")
else:
    st.info("No transactions to show for the selected filter.")

# --- MONTHLY BAR CHART ---
st.header("📅 Monthly Expense Overview")
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M")
monthly_summary = df.groupby("Month")["Amount"].sum().reset_index()
monthly_summary["Month"] = monthly_summary["Month"].astype(str)
fig2 = px.bar(monthly_summary, x="Month", y="Amount", title="Monthly Expenses")
st.plotly_chart(fig2)

# --- FOOTER ---
st.markdown("---")
st.markdown("Made by ❤️ Arunaachalam using Streamlit")
