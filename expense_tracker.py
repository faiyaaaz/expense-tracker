"""
Expense Tracker
---------------
A command-line tool to record daily expenses in a CSV file and analyze them with pandas.

Usage:
    python expense_tracker.py add 150 food "Lunch at canteen"
    python expense_tracker.py add 1200 bills "Internet" --date 2026-10-01
    python expense_tracker.py list --month 2026-10
    python expense_tracker.py summary
    python expense_tracker.py chart --month 2026-10

Use --file to choose a different CSV (default: expenses.csv), e.g.
    python expense_tracker.py --file sample_expenses.csv summary
"""

import argparse
import csv
from datetime import date, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save charts to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd

COLUMNS = ["date", "amount", "category", "note"]
CATEGORIES = ["food", "transport", "education", "bills", "shopping", "health", "entertainment", "other"]

# Chart colors
BAR_COLOR = "#2a78d6"
TEXT_COLOR = "#0b0b0b"
MUTED_COLOR = "#52514e"


# ---------- argument checks ----------

def positive_amount(text):
    amount = float(text)
    if amount <= 0:
        raise argparse.ArgumentTypeError("amount must be greater than 0")
    return amount


def valid_date(text):
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError("date must look like YYYY-MM-DD, e.g. 2026-10-28")


def valid_month(text):
    try:
        datetime.strptime(text, "%Y-%m")
    except ValueError:
        raise argparse.ArgumentTypeError("month must look like YYYY-MM, e.g. 2026-10")
    return text


# ---------- reading and writing ----------

def add_expense(path, amount, category, note, day):
    is_new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(COLUMNS)
        writer.writerow([day.isoformat(), f"{amount:.2f}", category, note])
    print(f"Added {amount:,.2f} BDT for {category} on {day}.")


def load_expenses(path, month=None):
    """Load the CSV into a DataFrame, optionally keeping only one month (YYYY-MM)."""
    if not path.exists():
        raise SystemExit(f"'{path}' not found. Add an expense first, e.g.:\n"
                         f'  python expense_tracker.py add 150 food "Lunch"')

    df = pd.read_csv(path, parse_dates=["date"])
    df["note"] = df["note"].fillna("")

    if month:
        df = df[df["date"].dt.strftime("%Y-%m") == month]
    if df.empty:
        raise SystemExit("No expenses found" + (f" for {month}." if month else "."))
    return df.sort_values("date")


# ---------- commands ----------

def show_list(df):
    table = df.assign(date=df["date"].dt.strftime("%Y-%m-%d"))
    print(table.to_string(index=False))
    print(f"\n{len(df)} expenses, total {df['amount'].sum():,.2f} BDT")


def show_summary(df):
    total = df["amount"].sum()
    days = (df["date"].max() - df["date"].min()).days + 1
    biggest = df.loc[df["amount"].idxmax()]

    print("=== Summary ===")
    print(f"Period        : {df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y} ({days} days)")
    print(f"Total spent   : {total:,.2f} BDT")
    print(f"Daily average : {total / days:,.2f} BDT")
    print(f"Biggest       : {biggest['amount']:,.2f} BDT ({biggest['category']}, {biggest['note']})")

    print("\n=== By category ===")
    by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    for category, amount in by_category.items():
        print(f"{category:<14} {amount:>10,.2f}  {amount / total:>4.0%}")

    by_month = df.groupby(df["date"].dt.strftime("%Y-%m"))["amount"].sum()
    if len(by_month) > 1:
        print("\n=== By month ===")
        for month, amount in by_month.items():
            print(f"{month:<14} {amount:>10,.2f}")


def save_chart(df, out_file, title):
    by_category = df.groupby("category")["amount"].sum().sort_values()

    fig, ax = plt.subplots(figsize=(8, 0.5 * len(by_category) + 1.5))
    ax.barh(by_category.index, by_category.values, color=BAR_COLOR, height=0.6)
    for y, amount in enumerate(by_category.values):
        ax.text(amount, y, f"  {amount:,.0f}", va="center", color=TEXT_COLOR)

    ax.set_title(title, loc="left", fontsize=13, color=TEXT_COLOR, pad=12)
    ax.set_xlabel("Amount (BDT)", color=MUTED_COLOR)
    ax.tick_params(colors=MUTED_COLOR, length=0)
    ax.set_xlim(0, by_category.max() * 1.18)  # room for the value labels
    for side in ["top", "right", "bottom"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.set_xticks([])

    fig.tight_layout()
    fig.savefig(out_file, dpi=120)
    plt.close(fig)
    print(f"Chart saved to {out_file}")


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="Track and analyze your daily expenses.")
    parser.add_argument("--file", default="expenses.csv", help="CSV file to use (default: expenses.csv)")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record a new expense")
    add.add_argument("amount", type=positive_amount, help="amount in BDT")
    add.add_argument("category", choices=CATEGORIES)
    add.add_argument("note", nargs="?", default="", help="short description (optional)")
    add.add_argument("--date", type=valid_date, default=date.today(), help="YYYY-MM-DD (default: today)")

    for name, help_text in [("list", "show all expenses"),
                            ("summary", "totals by category and month"),
                            ("chart", "save a bar chart of spending by category")]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--month", type=valid_month, help="only this month, YYYY-MM")
    commands.choices["chart"].add_argument("--out", default="spending_by_category.png",
                                           help="image file to save (default: spending_by_category.png)")

    args = parser.parse_args()
    path = Path(args.file)

    if args.command == "add":
        add_expense(path, args.amount, args.category, args.note, args.date)
        return

    df = load_expenses(path, args.month)
    if args.command == "list":
        show_list(df)
    elif args.command == "summary":
        show_summary(df)
    elif args.command == "chart":
        period = args.month or "all time"
        save_chart(df, args.out, f"Spending by category ({period})")


if __name__ == "__main__":
    main()
