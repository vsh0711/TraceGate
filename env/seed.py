"""Build the store database. The data is fixed, so every trial starts from the same state."""
import sqlite3

SCHEMA = """
CREATE TABLE customers (customer_id TEXT PRIMARY KEY, name TEXT, email TEXT, zip_code TEXT);
CREATE TABLE products (product_id TEXT PRIMARY KEY, name TEXT, price REAL, final_sale INTEGER);
CREATE TABLE orders (order_id TEXT PRIMARY KEY, customer_id TEXT, status TEXT,
  placed_at TEXT, delivered_at TEXT, address TEXT, total REAL);
CREATE TABLE order_items (order_id TEXT, product_id TEXT, quantity INTEGER);
CREATE TABLE refunds (refund_id TEXT PRIMARY KEY, order_id TEXT, amount REAL, created_at TEXT);
"""

CUSTOMERS = [
    ("C1", "Alice Nguyen", "alice.nguyen@example.com", "94107"),
    ("C2", "Ben Carter", "ben.carter@example.com", "10001"),
    ("C3", "Chloe Diaz", "chloe.diaz@example.com", "60601"),
    ("C4", "Dev Patel", "dev.patel@example.com", "73301"),
    ("C5", "Elena Rossi", "elena.rossi@example.com", "98101"),
    ("C6", "Farid Khan", "farid.khan@example.com", "30301"),
    ("C7", "Grace Liu", "grace.liu@example.com", "02108"),
    ("C8", "Hugo Martin", "hugo.martin@example.com", "80202"),
    ("C9", "Ivy Brooks", "ivy.brooks@example.com", "33101"),
    ("C10", "Jon Weber", "jon.weber@example.com", "55401"),
]

PRODUCTS = [
    ("P1", "Wireless Mouse", 25.00, 0),
    ("P2", "Mechanical Keyboard", 80.00, 0),
    ("P3", "USB-C Hub", 45.00, 0),
    ("P4", "Laptop Stand", 35.00, 0),
    ("P5", "Webcam HD", 60.00, 0),
    ("P6", "Noise Headphones", 120.00, 0),
    ("P7", "Phone Case", 15.00, 0),
    ("P8", "Clearance Cable Pack", 10.00, 1),
    ("P9", "Clearance Desk Lamp", 30.00, 1),
    ("P10", "Monitor 27in", 220.00, 0),
]

# order_id, customer, status, placed_at, delivered_at, items [(product, qty)]
ORDERS = [
    ("O1001", "C1", "delivered", "2026-09-15", "2026-09-20", [("P1", 1), ("P7", 1)]),
    ("O1002", "C1", "processing", "2026-09-29", None, [("P6", 1)]),
    ("O1003", "C1", "delivered", "2026-07-10", "2026-07-15", [("P3", 1)]),
    ("O1004", "C2", "shipped", "2026-09-27", None, [("P2", 1)]),
    ("O1005", "C2", "delivered", "2026-09-20", "2026-09-25", [("P5", 1)]),
    ("O1006", "C2", "processing", "2026-09-30", None, [("P4", 2)]),
    ("O1007", "C3", "delivered", "2026-09-05", "2026-09-10", [("P10", 1)]),
    ("O1008", "C3", "delivered", "2026-09-13", "2026-09-18", [("P8", 2)]),
    ("O1009", "C3", "processing", "2026-09-30", None, [("P1", 2), ("P3", 1)]),
    ("O1010", "C4", "delivered", "2026-08-15", "2026-08-20", [("P2", 1)]),
    ("O1011", "C4", "shipped", "2026-09-26", None, [("P6", 1)]),
    ("O1012", "C4", "cancelled", "2026-09-20", None, [("P7", 1)]),
    ("O1013", "C5", "delivered", "2026-09-23", "2026-09-28", [("P6", 1)]),
    ("O1014", "C5", "processing", "2026-09-29", None, [("P2", 1), ("P1", 1)]),
    ("O1015", "C5", "delivered", "2026-09-01", "2026-09-05", [("P9", 1)]),
    ("O1016", "C6", "processing", "2026-09-30", None, [("P10", 1)]),
    ("O1017", "C6", "delivered", "2026-09-10", "2026-09-15", [("P5", 1), ("P4", 1)]),
    ("O1018", "C6", "shipped", "2026-09-28", None, [("P3", 1)]),
    ("O1019", "C7", "delivered", "2026-09-17", "2026-09-22", [("P2", 2)]),
    ("O1020", "C7", "processing", "2026-09-30", None, [("P7", 3)]),
    ("O1021", "C7", "delivered", "2026-07-27", "2026-08-01", [("P1", 1)]),
    ("O1022", "C8", "delivered", "2026-09-07", "2026-09-12", [("P6", 1), ("P7", 1)]),
    ("O1023", "C8", "processing", "2026-09-29", None, [("P4", 1)]),
    ("O1024", "C8", "shipped", "2026-09-27", None, [("P1", 2)]),
    ("O1025", "C9", "delivered", "2026-09-22", "2026-09-27", [("P3", 2)]),
    ("O1026", "C9", "processing", "2026-09-30", None, [("P5", 1)]),
    ("O1027", "C9", "delivered", "2026-08-27", "2026-09-01", [("P7", 1)]),
    ("O1028", "C10", "delivered", "2026-09-25", "2026-09-30", [("P10", 1)]),
    ("O1029", "C10", "processing", "2026-09-30", None, [("P2", 1), ("P4", 1)]),
    ("O1030", "C10", "shipped", "2026-09-28", None, [("P5", 1)]),
]

# refund_id, order, amount, created_at (refunds that exist before any trial starts)
REFUNDS = [("R1", "O1022", 135.00, "2026-09-20")]


def address_for(order_id: str, customer_id: str) -> str:
    n = int(order_id[1:]) % 97 + 10
    return f"{n} Market Street, Unit {customer_id[1:]}"


def build_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO customers VALUES (?,?,?,?)", CUSTOMERS)
    db.executemany("INSERT INTO products VALUES (?,?,?,?)", PRODUCTS)
    price = {p[0]: p[2] for p in PRODUCTS}
    for oid, cid, status, placed, delivered, items in ORDERS:
        total = round(sum(price[p] * q for p, q in items), 2)
        db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?)",
                   (oid, cid, status, placed, delivered, address_for(oid, cid), total))
        db.executemany("INSERT INTO order_items VALUES (?,?,?)", [(oid, p, q) for p, q in items])
    db.executemany("INSERT INTO refunds VALUES (?,?,?,?)", REFUNDS)
    db.commit()
    return db


def snapshot(db: sqlite3.Connection) -> dict:
    """The part of the database that agents can change."""
    orders = {r["order_id"]: {"status": r["status"], "address": r["address"]}
              for r in db.execute("SELECT * FROM orders")}
    refunds = sorted((r["order_id"], round(r["amount"], 2)) for r in db.execute("SELECT * FROM refunds"))
    return {"orders": orders, "refunds": refunds}


def diff(before: dict, after: dict) -> dict:
    """Changes between two snapshots, in the same format as a task's `expected` field."""
    orders = {}
    for oid, new in after["orders"].items():
        old = before["orders"][oid]
        ch = {k: v for k, v in new.items() if old[k] != v}
        if ch:
            orders[oid] = ch
    old_refunds = list(before["refunds"])
    new_refunds = []
    for r in after["refunds"]:
        if r in old_refunds:
            old_refunds.remove(r)
        else:
            new_refunds.append(list(r))
    return {"orders": orders, "refunds": sorted(new_refunds)}
