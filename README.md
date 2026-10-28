# Expense Tracker

A command-line tool for tracking daily expenses. Each expense is saved to a CSV file, and **pandas** turns that file into summaries and charts. Useful for any student who wants to know where their money goes each month.

![Spending by category](docs/spending_by_category.png)

## Features

- **add**: record an expense with an amount, category, optional note and date
- **list**: show every expense, or one month's expenses
- **summary**: total spent, daily average, biggest expense, a breakdown by category and by month
- **chart**: save a bar chart of spending by category
- Input checking: negative amounts, unknown categories and badly formatted dates are rejected with a clear message

## How to run

```bash
pip install -r requirements.txt

python expense_tracker.py add 150 food "Lunch at canteen"
python expense_tracker.py add 1000 bills "Internet" --date 2026-10-01
python expense_tracker.py list --month 2026-10
python expense_tracker.py summary
python expense_tracker.py chart --month 2026-10
```

Your expenses are saved in `expenses.csv`. To try the tool with the included sample data (two months of made-up student expenses), add `--file sample_expenses.csv`:

```bash
python expense_tracker.py --file sample_expenses.csv summary
```

```
=== Summary ===
Period        : 01 Sep 2026 to 27 Oct 2026 (57 days)
Total spent   : 22,840.00 BDT
Daily average : 400.70 BDT
Biggest       : 1,500.00 BDT (shopping, Headphones)

=== By category ===
food             9,350.00   41%
shopping         4,250.00   19%
bills            3,000.00   13%
transport        2,840.00   12%
education        1,700.00    7%
entertainment    1,200.00    5%
health             500.00    2%

=== By month ===
2026-09         12,430.00
2026-10         10,410.00
```

Categories: `food`, `transport`, `education`, `bills`, `shopping`, `health`, `entertainment`, `other`

## Concepts used

Reading and appending CSV files (`csv` module) · subcommands with `argparse` · custom input validation · `pd.read_csv` with date parsing · filtering by month with `.dt.strftime` · `groupby` and `sum` · `idxmax` · horizontal bar charts in matplotlib
