#!/usr/bin/env python3
"""Example: CRUD with SQLite using only the pydba Database facade."""

from __future__ import annotations
import datetime
import time

from pydba.database import DB
from pydba.query.enums.type import TypeEnum

# 1. Define the debug callback
def debug_callback(query: str, starttime: float, error: str | None):
    if error:
        print(f"[ERROR] {error}")
    else:
        elapsed = time.time() - starttime
        print(f"[SQL] {query} ({elapsed:.4f}s)")

db = DB.connect_sqlite("database.sqlite", debug_callback=debug_callback)

# 2. Create a table using the fluent builder
db.create_table("users").if_not_exists().identity("id").string("name", not_null=True).int("age").execute()

# 2b. Also create a "posts" table with a foreign key to users
db.create_table("posts").if_not_exists().identity("id").string("title", not_null=True).text("body").int("user_id").foreign_key_constraint("user_id", "users", "id", referential_actions=["ON DELETE CASCADE"]).execute()

# 2c. Add a column to users using the ALTER TABLE fluent builder
db.alter_table("users").add_string("email", size=255).execute()

# 2d. Add a unique constraint on email (SQLite doesn't support this — see error)
try:
    db.alter_table("users").add_unique_constraint(["email"], name="uq_users_email").execute()
except Exception as e:
    print(f"\n[Expected] SQLite limitation: {e}")

# 3. INSERT two rows (execute() is wired via db.select/insert/update/delete)
db.insert("users").values(
    {"name": "Alice", "age": datetime.datetime.now()},
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
db.update("users").updates({"age": 26}).where_equals("name", "Bob").where_group(lambda group: group.where_not_equals('name', 'Alice')).execute()
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

# 9. DROP TABLE examples using the fluent builder
print("\nDropping 'posts' table...")
db.drop_table("posts").if_exists().execute()

print("\nDropping 'users' table...")
db.drop_table("users").if_exists().execute()

# 10. Verify tables are gone (query will fail — that's expected)
try:
    result = db.select("users").execute()
    print("\nUsers after drop:")
    for u in result.fetch_dicts():
        print(f"  {u}")
except Exception as e:
    print(f"\n[Expected] Table 'users' no longer exists: {e}")
