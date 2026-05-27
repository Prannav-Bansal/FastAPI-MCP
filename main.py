import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


DATABASE_NAME = "expenses.db"

app = FastAPI(title="Expense Tracker API", version="0.1.0")


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    spent_on: date = Field(default_factory=date.today)
    note: Optional[str] = Field(default=None, max_length=255)


class ExpenseRead(ExpenseCreate):
    id: int
    created_at: datetime


class ExpenseSummary(BaseModel):
    total_expenses: int
    total_amount: Decimal


def get_db():
    db = sqlite3.connect(DATABASE_NAME)
    db.row_factory = sqlite3.Row
    init_database(db)
    try:
        yield db
    finally:
        db.close()


def init_database(db: sqlite3.Connection) -> None:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            spent_on TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


@app.on_event("startup")
def startup() -> None:
    with sqlite3.connect(DATABASE_NAME) as db:
        init_database(db)


def row_to_expense(row: sqlite3.Row) -> dict:
    return dict(row)


@app.post("/expenses", response_model=ExpenseRead, status_code=201)
def add_expense(expense: ExpenseCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute(
        """
        INSERT INTO expenses (title, amount, category, spent_on, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            expense.title,
            float(expense.amount),
            expense.category,
            expense.spent_on.isoformat(),
            expense.note,
        ),
    )
    db.commit()

    row = db.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return row_to_expense(row)


@app.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    query = "SELECT * FROM expenses WHERE 1 = 1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND spent_on >= ?"
        params.append(start_date.isoformat())
    if end_date:
        query += " AND spent_on <= ?"
        params.append(end_date.isoformat())

    query += " ORDER BY spent_on DESC, id DESC"

    rows = db.execute(query, params).fetchall()
    return [row_to_expense(row) for row in rows]


@app.get("/expenses/summary", response_model=ExpenseSummary)
def summarize(
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    query = """
        SELECT COUNT(*) AS total_expenses, COALESCE(SUM(amount), 0) AS total_amount
        FROM expenses
        WHERE 1 = 1
    """
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND spent_on >= ?"
        params.append(start_date.isoformat())
    if end_date:
        query += " AND spent_on <= ?"
        params.append(end_date.isoformat())

    row = db.execute(query, params).fetchone()
    return {
        "total_expenses": row["total_expenses"],
        "total_amount": row["total_amount"],
    }


@app.get("/expenses/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return row_to_expense(row)


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
