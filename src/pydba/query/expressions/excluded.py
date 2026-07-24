from __future__ import annotations


class Excluded:
    """Marker for EXCLUDED.column in PostgreSQL ON CONFLICT DO UPDATE SET.

    Pass this as a value in ``on_conflict_do_update()`` updates dict::

        db.insert("users").values({...}).on_conflict_do_update(
            ["id"],
            {"name": Excluded()},
        ).execute()

    The dialect detects this marker and generates ``EXCLUDED.\"name\"``.
    """


class Values(Excluded):
    """Marker for VALUES(column) in MySQL ON DUPLICATE KEY UPDATE.

    Pass this as a value in ``on_conflict_do_update()`` updates dict::

        db.insert("users").values({...}).on_conflict_do_update(
            ["id"],
            {"name": Values()},
        ).execute()

    The dialect detects this marker and generates ``VALUES(`name`)``.
    """