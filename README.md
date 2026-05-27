# Expense Tracker API

A simple FastAPI expense tracker that stores expenses in a local SQLite database.

## Install

```powershell
pip install -r requirements.txt
```

## Run

```powershell
uvicorn main:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

- `POST /expenses` adds an expense.
- `GET /expenses` lists expenses.
- `GET /expenses/summary` returns total count and amount.
- `GET /expenses/{expense_id}` gets one expense.
- `DELETE /expenses/{expense_id}` deletes one expense.

## Example Expense

```json
{
  "title": "Lunch",
  "amount": "250.00",
  "category": "Food",
  "spent_on": "2026-05-27",
  "note": "Office lunch"
}
```
