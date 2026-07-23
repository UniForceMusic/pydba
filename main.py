#!/usr/bin/env python3
"""Example: CRUD with SQLite using only the pydba Database facade."""

from __future__ import annotations

from pydba.database import DB
from pydba.query.enums.type import TypeEnum

# 1. Connect (creates in-memory SQLite database automatically)
db = DB.connect("sqlite", ":memory:")

# 2. Create a table
db.exec(
    db.dialect.create_table(
        if_not_exists=False,
        table="users",
        columns=[
            {"name": "id",   "type": TypeEnum.INT, "auto_increment": True, "not_null": True},
            {"name": "name", "type": "TEXT", "not_null": True},
            {"name": "age",  "type": "INTEGER"},
        ],
        primary_keys=["id"],
        constraints=None,
    ).query
)

# 3. INSERT two rows (execute() is wired via db.select/insert/update/delete)
db.insert("users").values(
    {"name": "Alice", "age": 30},
    {"name": "Bob",   "age": 25},
).execute()

print("Inserted 2 users.")

# 4. SELECT all users
result = db.select("users").execute()
users: list[dict] = result.fetch_dicts()
print("\nAll users after insert:")
for u in users:
    print(f"  {u}")

# 5. UPDATE: Bob turns 26
db.update("users").updates({"age": 26}).where_equals("name", "Bob").execute()
print("\nUpdated Bob's age to 26.")

# 6. SELECT only Bob to verify
result = db.select("users").where_equals("name", "Bob").execute()
print("\nBob after update:", result.fetch_dict())

# 7. DELETE Alice
db.delete("users").where_equals("name", "Alice").execute()
print("\nDeleted Alice.")

# 8. Final state
result = db.select("users").execute()
print("\nFinal users in table:")
for u in result.fetch_dicts():
    print(f"  {u}")
