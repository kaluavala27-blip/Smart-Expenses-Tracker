import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date
import random

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Smart Expenses Tracker",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# DATABASE
# ============================================================

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Expense table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            payment_method TEXT NOT NULL
        )
    """)

    # Budget table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


# ============================================================
# OOP - EXPENSE CLASS
# ============================================================

class Expense:

    def __init__(
        self,
        title,
        amount,
        category,
        expense_date,
        payment_method
    ):
        self.title = title
        self.amount = float(amount)
        self.category = category
        self.expense_date = str(expense_date)
        self.payment_method = payment_method


# ============================================================
# OOP - BUDGET MANAGER
# ============================================================

class BudgetManager:

    @staticmethod
    def set_budget(category, amount):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO budgets(category, amount)
            VALUES (?, ?)
        """, (category, float(amount)))

        conn.commit()
        conn.close()


    @staticmethod
    def get_budgets():

        conn = get_connection()

        df = pd.read_sql_query(
            "SELECT * FROM budgets",
            conn
        )

        conn.close()

        return df


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def add_expense(expense):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (title, amount, category, expense_date, payment_method)
        VALUES (?, ?, ?, ?, ?)
    """, (
        expense.title,
        expense.amount,
        expense.category,
        expense.expense_date,
        expense.payment_method
    ))

    conn.commit()
    conn.close()


def get_all_expenses():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            title,
            amount,
            category,
            expense_date,
            payment_method
        FROM expenses
        ORDER BY expense_date DESC
    """, conn)

    conn.close()

    return df


def get_total_expenses():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_expense_count():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM expenses
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


def clear_expenses():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()


# ============================================================
# 10,000 DEMO DATA GENERATOR
# ============================================================

def generate_demo_data():

    conn = get_connection()
    cursor = conn.cursor()

    # Check current records
    cursor.execute("SELECT COUNT(*) FROM expenses")

    count = cursor.fetchone()[0]

    # Generate only if database has less than 10,000 records
    if count >= 10000:

        conn.close()
        return

    categories = [
        "Food & Dining",
        "Transport",
        "Shopping",
        "Utilities",
        "Entertainment",
        "Others"
    ]

    payment_methods = [
        "UPI",
        "Cash",
        "Credit Card",
        "Debit Card"
    ]

    titles = {
        "Food & Dining": [
            "Lunch",
            "Dinner",
            "Breakfast",
            "Restaurant",
            "Coffee",
            "Groceries"
        ],

        "Transport": [
            "Uber",
            "Rapido",
            "Ola",
            "Bus",
            "Metro",
            "Fuel"
        ],

        "Shopping": [
            "Amazon",
            "Myntra",
            "Clothes",
            "Shoes",
            "Electronics",
            "Accessories"
        ],

        "Utilities": [
            "Electricity",
            "Internet",
            "Mobile Recharge",
            "Water Bill",
            "Gas Bill"
        ],

        "Entertainment": [
            "Movie",
            "Netflix",
            "Game",
            "Concert",
            "Event"
        ],

        "Others": [
            "Medicine",
            "Books",
            "Education",
            "Gift",
            "Miscellaneous"
        ]
    }

    data = []

    for i in range(count + 1, 10001):

        category = random.choice(categories)

        title = random.choice(
            titles[category]
        )

        amount = random.randint(50, 5000)

        random_year = random.randint(
            2025,
            2026
        )

        random_month = random.randint(
            1,
            12
        )

        random_day = random.randint(
            1,
            28
        )

        expense_date = (
            f"{random_year}-"
            f"{random_month:02d}-"
            f"{random_day:02d}"
        )

        payment_method = random.choice(
            payment_methods
        )

        data.append((
            title,
            amount,
            category,
            expense_date,
            payment_method
        ))

    cursor.executemany("""
        INSERT INTO expenses
        (title, amount, category, expense_date, payment_method)
        VALUES (?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE 10,000 DATASETS
# ============================================================

if "data_initialized" not in st.session_state:

    with st.spinner(
        "Preparing expense database..."
    ):
        generate_demo_data()

    st.session_state.data_initialized = True


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💰 Smart Expenses Tracker")

menu_choice = st.sidebar.radio(
    "SELECT ACTION",
    [
        "📊 Dashboard",
        "➕ Add Expense",
        "🎯 Set Budget",
        "📋 Expense History",
        "📈 Analytics",
        "⚠️ Budget Alerts"
    ]
)

st.sidebar.markdown("---")

# Display record count

record_count = get_expense_count()

st.sidebar.metric(
    "Total Records",
    f"{record_count:,}"
)


# ============================================================
# DASHBOARD
# ============================================================

if menu_choice == "📊 Dashboard":

    st.title("💰 Smart Expenses Tracker")

    st.subheader(
        "📊 Expense Dashboard"
    )

    df = get_all_expenses()

    if df.empty:

        st.info(
            "No expenses found. "
            "Please add an expense."
        )

    else:

        # Convert date

        df["expense_date"] = pd.to_datetime(
            df["expense_date"]
        )

        # ----------------------------------------------------
        # KPI CALCULATIONS
        # ----------------------------------------------------

        total_spent = df["amount"].sum()

        transaction_count = len(df)

        average_expense = (
            df["amount"].mean()
        )

        highest_expense = (
            df["amount"].max()
        )

        # Budget

        budget_df = BudgetManager.get_budgets()

        if budget_df.empty:

            total_budget = 0

        else:

            total_budget = (
                budget_df["amount"].sum()
            )

        remaining = (
            total_budget - total_spent
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💰 Total Spent",
            f"₹{total_spent:,.0f}"
        )

        col2.metric(
            "🎯 Total Budget",
            f"₹{total_budget:,.0f}"
        )

        col3.metric(
            "💵 Remaining",
            f"₹{remaining:,.0f}"
        )

        col4.metric(
            "🧾 Transactions",
            f"{transaction_count:,}"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # PIE CHART
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🍕 Expenses by Category"
            )

            category_data = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        with col2:

            st.subheader(
                "📊 Category Spending"
            )

            fig2 = px.bar(
                category_data,
                x="category",
                y="amount",
                text_auto=True
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # ----------------------------------------------------
        # MONTHLY TREND
        # ----------------------------------------------------

        st.subheader(
            "📈 Monthly Spending Trend"
        )

        df["month"] = (
            df["expense_date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_data = (
            df.groupby("month")["amount"]
            .sum()
            .reset_index()
        )

        fig3 = px.line(
            monthly_data,
            x="month",
            y="amount",
            markers=True
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # ----------------------------------------------------
        # BUDGET PROGRESS
        # ----------------------------------------------------

        st.subheader(
            "🎯 Budget Usage"
        )

        if budget_df.empty:

            st.info(
                "No budgets set yet."
            )

        else:

            for _, row in budget_df.iterrows():

                category = row["category"]

                limit = row["amount"]

                spent = df.loc[
                    df["category"] == category,
                    "amount"
                ].sum()

                percentage = (
                    spent / limit
                    if limit > 0
                    else 0
                )

                st.write(
                    f"**{category}** — "
                    f"₹{spent:,.0f} / "
                    f"₹{limit:,.0f}"
                )

                st.progress(
                    min(percentage, 1.0)
                )

                if spent > limit:

                    st.error(
                        f"🚨 {category} "
                        f"budget exceeded!"
                    )

                elif spent >= limit * 0.8:

                    st.warning(
                        f"⚠️ {category} "
                        f"is approaching the budget."
                    )

        st.markdown("---")

        # ----------------------------------------------------
        # RECENT EXPENSES
        # ----------------------------------------------------

        st.subheader(
            "🧾 Recent Expenses"
        )

        recent = df.head(10).copy()

        recent["expense_date"] = (
            recent["expense_date"]
            .dt.strftime("%Y-%m-%d")
        )

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ADD EXPENSE
# ============================================================

elif menu_choice == "➕ Add Expense":

    st.title("➕ Add New Expense")

    st.info(
        "Your expense will be permanently "
        "stored in the SQLite database."
    )

    with st.form("expense_form"):

        title = st.text_input(
            "Expense Title",
            placeholder="Example: Lunch"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=1.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food & Dining",
                "Transport",
                "Shopping",
                "Utilities",
                "Entertainment",
                "Others"
            ]
        )

        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "UPI",
                "Cash",
                "Credit Card",
                "Debit Card"
            ]
        )

        submitted = st.form_submit_button(
            "ADD EXPENSE"
        )

        if submitted:

            if not title:

                st.error(
                    "Please enter an expense title."
                )

            elif amount <= 0:

                st.error(
                    "Amount must be greater than 0."
                )

            else:

                expense = Expense(
                    title,
                    amount,
                    category,
                    expense_date,
                    payment_method
                )

                add_expense(expense)

                st.success(
                    f"Expense '{title}' "
                    f"of ₹{amount:,.2f} added successfully!"
                )

                st.rerun()


# ============================================================
# SET BUDGET
# ============================================================

elif menu_choice == "🎯 Set Budget":

    st.title(
        "🎯 Set Monthly Budget"
    )

    category = st.selectbox(
        "Select Category",
        [
            "Food & Dining",
            "Transport",
            "Shopping",
            "Utilities",
            "Entertainment",
            "Others"
        ]
    )

    budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        step=100.0
    )

    if st.button("SET BUDGET"):

        if budget <= 0:

            st.error(
                "Enter a budget greater than 0."
            )

        else:

            BudgetManager.set_budget(
                category,
                budget
            )

            st.success(
                f"Budget for {category} "
                f"set to ₹{budget:,.0f}"
            )

            st.rerun()

    st.markdown("---")

    st.subheader(
        "Current Budgets"
    )

    budget_df = BudgetManager.get_budgets()

    if budget_df.empty:

        st.info(
            "No budgets have been set."
        )

    else:

        st.dataframe(
            budget_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# EXPENSE HISTORY
# ============================================================

elif menu_choice == "📋 Expense History":

    st.title(
        "📋 Expense History"
    )

    df = get_all_expenses()

    if df.empty:

        st.warning(
            "No expenses available."
        )

    else:

        # Filters

        col1, col2 = st.columns(2)

        with col1:

            categories = st.multiselect(
                "Filter by Category",
                sorted(
                    df["category"].unique()
                )
            )

        with col2:

            payment_methods = st.multiselect(
                "Filter by Payment Method",
                sorted(
                    df["payment_method"].unique()
                )
            )

        filtered_df = df.copy()

        if categories:

            filtered_df = filtered_df[
                filtered_df["category"].isin(
                    categories
                )
            ]

        if payment_methods:

            filtered_df = filtered_df[
                filtered_df["payment_method"].isin(
                    payment_methods
                )
            ]

        st.write(
            f"Showing "
            f"**{len(filtered_df):,}** records"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        if st.button(
            "🗑️ Clear All Expenses"
        ):

            clear_expenses()

            st.success(
                "All expenses deleted."
            )

            st.rerun()


# ============================================================
# ANALYTICS
# ============================================================

elif menu_choice == "📈 Analytics":

    st.title(
        "📈 Expense Analytics"
    )

    df = get_all_expenses()

    if df.empty:

        st.info(
            "No data available."
        )

    else:

        df["expense_date"] = pd.to_datetime(
            df["expense_date"]
        )

        # ----------------------------------------------------
        # BASIC STATISTICS
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Expense",
            f"₹{df['amount'].mean():,.2f}"
        )

        col2.metric(
            "Highest Expense",
            f"₹{df['amount'].max():,.2f}"
        )

        col3.metric(
            "Lowest Expense",
            f"₹{df['amount'].min():,.2f}"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # PAYMENT METHOD ANALYSIS
        # ----------------------------------------------------

        st.subheader(
            "💳 Spending by Payment Method"
        )

        payment_data = (
            df.groupby("payment_method")["amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            payment_data,
            x="payment_method",
            y="amount",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # CATEGORY ANALYSIS
        # ----------------------------------------------------

        st.subheader(
            "📊 Category Analysis"
        )

        category_data = (
            df.groupby("category")
            .agg(
                Total_Spent=("amount", "sum"),
                Average_Spent=("amount", "mean"),
                Transactions=("amount", "count")
            )
            .reset_index()
        )

        category_data = category_data.sort_values(
            "Total_Spent",
            ascending=False
        )

        st.dataframe(
            category_data,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # TOP 10 EXPENSES
        # ----------------------------------------------------

        st.subheader(
            "🔥 Top 10 Highest Expenses"
        )

        top_expenses = (
            df.sort_values(
                "amount",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_expenses,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# BUDGET ALERTS
# ============================================================

elif menu_choice == "⚠️ Budget Alerts":

    st.title(
        "⚠️ Budget Alerts"
    )

    df = get_all_expenses()

    budget_df = BudgetManager.get_budgets()

    if budget_df.empty:

        st.info(
            "No budgets have been set."
        )

    else:

        for _, row in budget_df.iterrows():

            category = row["category"]

            limit = row["amount"]

            spent = df.loc[
                df["category"] == category,
                "amount"
            ].sum()

            percentage = (
                (spent / limit) * 100
                if limit > 0
                else 0
            )

            st.subheader(
                category
            )

            st.write(
                f"Spent: ₹{spent:,.2f}"
            )

            st.write(
                f"Budget: ₹{limit:,.2f}"
            )

            st.write(
                f"Used: {percentage:.1f}%"
            )

            if spent > limit:

                st.error(
                    f"🚨 OVER BUDGET! "
                    f"Exceeded by "
                    f"₹{spent - limit:,.2f}"
                )

            elif spent >= limit * 0.8:

                st.warning(
                    "⚠️ You have used more than "
                    "80% of this budget."
                )

            else:

                st.success(
                    "✅ Budget is under control."
                )

            st.markdown("---")