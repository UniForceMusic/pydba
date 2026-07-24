#!/usr/bin/env python3
"""Example: CRUD with SQLite using only the pydba Database facade."""

from __future__ import annotations
import datetime
import time

from pydba.database import DB
from pydba.query.enums.type import TypeEnum
from pydba.query._condition_group import WhereGroup, HavingGroup
from pydba.query._condition import Condition as Cond
from pydba.query.enums.condition import ConditionEnum
from pydba.query.enums.chain import ChainEnum
from pydba.query.expressions.excluded import Values

# 1. Define the debug callback
def debug_callback(query: str, starttime: float, error: str | None):
    elapsed = (time.time() * 10000) - starttime

    print(f"[SQL] {query}")
    print(f"[TIME] {elapsed:.4f}s")

    if error:
        print(f"[ERROR] {error}")

db = DB.connect_sqlite(":memory:", debug_callback=debug_callback)

# 2. Create a table using the fluent builder
db.create_table("users").if_not_exists().identity("id").string("name", not_null=True).integer("age").execute()

# 2b. Also create a "posts" table with a foreign key to users
db.create_table("posts").if_not_exists().identity("id").string("title", not_null=True).text("body").integer("user_id").foreign_key_constraint("user_id", "users", "id", referential_actions=["ON DELETE CASCADE"]).execute()

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
subquery = db.select("users").columns(['id'])
result = db.select("users").where_exists(subquery).execute()
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

# ──────────────────────────────────────────────
# 9. GIANT SELECT with every condition type
# ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("GIANT SELECT — every condition type + joins + group/having + unions")
print("=" * 70)

# Sub-query references used in EXISTS / IN clauses
subq_active = db.select("users").columns(["id"]).where_equals("active", 1)
subq_young  = db.select("users").columns(["id"]).where_less_than("age", 30)

result = db.select("users").columns(["id", "name", "email", "age", "created_at", "score"])

# ── GIANT SELECT — every condition type + joins + group/having + unions ──
bigQuery = db.select("users").columns(["id", "name", "email", "age", "created_at", "score"])

# Sub-query references used in EXISTS / IN clauses
subq_active = db.select("users").columns(["id"]).where_equals("active", 1)
subq_young  = db.select("users").columns(["id"]).where_less_than("age", 30)

# ── DISTINCT ──
bigQuery.distinct()

# ── JOINS (every join type) ──
# Note: join methods return a Join object; call .on() separately then continue on bigQuery
join_posts = bigQuery.inner_join("posts", "p")
join_posts.on(
    Cond(condition=ConditionEnum.EQUALS, identifier="p", value="user_id"),
)
join_comments = bigQuery.left_join("comments", "c")
join_comments.on(
    Cond(condition=ConditionEnum.EQUALS, identifier="c", value="post_id"),
)
bigQuery.cross_join("sessions")

# ── WHERE — every public condition method ──
bigQuery = (
    bigQuery
    .where_equals("active", True)
    .or_where_equals("status", "pending")
    .where_not_equals("role", "banned")
    .or_where_not_equals("role", "archived")
    .where_is_null("deleted_at")
    .or_where_is_null("suspended_at")
    .where_is_not_null("email")
    .or_where_is_not_null("phone")
    .where_like("name", "Alice%")
    .or_where_like("email", "%@example.com")
    .where_not_like("name", "test%")
    .or_where_not_like("email", "%@spam.com")
    .where_starts_with("username", "admin")
    .or_where_starts_with("username", "mod")
    .where_ends_with("filename", ".pdf")
    .or_where_ends_with("filename", ".docx")
    .where_contains("bio", "engineer")
    .or_where_contains("bio", "developer")
    .where_not_contains("bio", "script kiddie")
    .or_where_not_contains("bio", "spammer")
    .where_in("id", [1, 2, 3])
    .or_where_in("id", [10, 20, 30, 40])
    .where_not_in("id", [999, 888])
    .or_where_not_in("id", [777])
    .where_less_than("age", 18)
    .or_where_less_than("age", 13)
    .where_less_than_or_equals("age", 65)
    .or_where_less_than_or_equals("age", 0)
    .where_greater_than("score", 100)
    .or_where_greater_than("score", 999)
    .where_greater_than_or_equals("score", 0)
    .or_where_greater_than_or_equals("score", 1000)
    .where_between("age", 18, 65)
    .or_where_between("age", 1, 17)
    .where_not_between("age", 0, 17)
    .or_where_not_between("age", 66, 120)
    .where_empty("middle_name")
    .or_where_empty("nickname")
    .where_not_empty("full_name")
    .or_where_not_empty("display_name")
    .where_regex("email", r"^[a-z]+@")
    .or_where_regex("phone", r"^\+?1-")
    .where_not_regex("email", r"^test@")
    .or_where_not_regex("email", r"spam@")
    .where_exists(subq_active)
    .or_where_exists(subq_young)
    .where_not_exists(subq_active)
    .or_where_not_exists(subq_young)

    # ── NESTED CONDITION GROUPS (3 levels deep) ──
    .where_group(
        lambda g: (
            g
            .where_equals("plan", "premium")
            .or_where_group(
                lambda g2: (
                    g2
                    .where_equals("plan", "free")
                    .where_group(
                        lambda g3: (
                            g3
                            .where_greater_than("trial_days", 0)
                            .or_where_is_null("trial_ends")
                        )
                    )
                )
            )
        )
    )
    .or_where_not_group(
        lambda g: g.where_equals("role", "internal")
    )

    # ── RAW conditions ──
    .where_raw("EXTRACT(YEAR FROM created_at) = ?", [2026])
    .or_where_raw("last_login IS NOT NULL")

    # ── CUSTOM OPERATOR ──
    .where_operator("json_data", "@>", '{"vip": true}')
    .or_where_operator("point", "<@", "circle(0,0,100)")

    # ── GROUP BY ──
    .group_by(["plan", "status"])

    # ── HAVING — subset of conditions ──
    .having_equals("plan", "enterprise")
    .or_having_equals("plan", "startup")
    .having_not_equals("status", "archived")
    .or_having_not_equals("status", "deleted")
    .having_greater_than("score", 500)
    .or_having_greater_than("score", 1000)
    .having_less_than("score", 99999)
    .having_between("age", 0, 150)
    .or_having_between("age", 18, 35)
    .having_not_between("age", 0, 17)
    .or_having_not_between("age", 100, 200)
    .having_is_null("deleted_at")
    .or_having_is_null("suspended_at")
    .having_is_not_null("email")
    .or_having_is_not_null("phone")
    .having_like("email", "%@corp.com")
    .or_having_like("email", "%@org")
    .having_not_like("email", "%@spam.com")
    .or_having_not_like("email", "%@temp")
    .having_starts_with("domain", "internal")
    .or_having_starts_with("domain", "corp")
    .having_ends_with("filename", ".csv")
    .or_having_ends_with("filename", ".xlsx")
    .having_contains("description", "urgent")
    .or_having_contains("description", "priority")
    .having_not_contains("description", "obsolete")
    .or_having_not_contains("description", "deprecated")
    .having_in("region", ["US", "EU", "APAC"])
    .or_having_in("region", ["LATAM"])
    .having_not_in("region", ["ANON"])
    .or_having_not_in("region", ["BLOCKED"])
    .having_empty("middle_name")
    .or_having_empty("nickname")
    .having_not_empty("full_name")
    .or_having_not_empty("display_name")
    .having_regex("email", r"\.com$")
    .or_having_regex("email", r"\.org$")
    .having_not_regex("email", r"\.test$")
    .or_having_not_regex("email", r"\.local$")
    .having_exists(subq_active)
    .or_having_exists(subq_young)
    .having_not_exists(subq_active)
    .or_having_not_exists(subq_young)

    # Nested HAVING groups
    .having_group(
        lambda g: (
            g
            .where_greater_than("score", 1000)
            .or_where_group(
                lambda g2: g2
                .where_equals("vip", True)
                .where_in("tier", ["gold", "platinum"])
            )
        )
    )
    .or_having_not_group(
        lambda g: g.where_equals("status", "internal")
    )
    .having_raw("AVG(rating) >= ?", [4.5])
    .or_having_raw("MAX(logins) > 100")
    .having_raw("json_meta @> '{\"premium\": true}'")
    .or_having_raw("tsvector @@ to_tsquery('urgent')")

    # ── ORDER BY ──
    .order_by_asc("plan")
    .order_by_desc("score")

    # ── LIMIT / OFFSET ──
    .limit(50)
    .offset(10)

    # ── UNION + UNION ALL ──
    .union(
        db.select("archived_users")
        .columns(["id", "name", "email", "age", "archived_at", "score"])
        .where_greater_than("score", 500)
    )
    .union_all(
        db.select("legacy_users")
        .columns(["id", "name", "email", "age", "created_at", "score"])
        .where_equals("migrated", False)
    )
)
print(f"\n{'-' * 70}")
print(f"GENERATED SQL:")
print(bigQuery.to_sql())
print(f"{'-' * 70}\n")

# ──────────────────────────────────────────────

# 10. DROP TABLE examples using the fluent builder
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
