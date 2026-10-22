import sqlite3
import os
import tempfile
from typing import List, Dict, Any, Optional

def get_default_db_path() -> str:
    """
    Determines optimal SQLite path. Prefers local project directory,
    falling back to temp directory if filesystem locks are restricted (e.g. 9p/NFS).
    """
    if os.environ.get("RETAIL_DB_PATH"):
        return os.environ["RETAIL_DB_PATH"]
    
    preferred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "retail.db")
    try:
        test_conn = sqlite3.connect(preferred_path)
        test_conn.cursor().execute("CREATE TABLE IF NOT EXISTS _fs_test (x INT);")
        test_conn.commit()
        test_conn.cursor().execute("DROP TABLE _fs_test;")
        test_conn.commit()
        test_conn.close()
        return os.path.abspath(preferred_path)
    except Exception:
        return os.path.join(tempfile.gettempdir(), "retail.db")

DB_PATH = get_default_db_path()

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with dict row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Creates database tables if they do not exist and seeds initial sample products."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                unit TEXT NOT NULL DEFAULT 'unit',
                min_stock_alert INTEGER NOT NULL DEFAULT 5
            );
        """)
        
        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE SET NULL
            );
        """)
        
        # Chat logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_phone TEXT,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                intent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Seed initial retail items if products table is empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM products;")
        count = cursor.fetchone()["cnt"]
        if count == 0:
            sample_products = [
                ("Rice 1kg", "Grains & Staples", 60.0, 50, "kg", 10),
                ("Milk 500ml", "Dairy", 30.0, 35, "packet", 8),
                ("Sugar 1kg", "Grains & Staples", 45.0, 40, "kg", 10),
                ("Wheat Flour 1kg", "Grains & Staples", 55.0, 30, "kg", 10),
                ("Tea Powder 250g", "Beverages", 120.0, 25, "pack", 5),
                ("Cooking Oil 1L", "Oils & Ghee", 145.0, 20, "liter", 5),
            ]
            cursor.executemany("""
                INSERT INTO products (name, category, price, stock_quantity, unit, min_stock_alert)
                VALUES (?, ?, ?, ?, ?, ?);
            """, sample_products)
        conn.commit()

def get_all_products() -> List[Dict[str, Any]]:
    """Retrieves all products from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a product by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_product_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a product matching name (case-insensitive substring or exact match)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # First try exact match (case-insensitive)
        cursor.execute("SELECT * FROM products WHERE LOWER(name) = LOWER(?);", (name.strip(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # Next try substring match
        cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?);", (f"%{name.strip()}%",))
        row = cursor.fetchone()
        return dict(row) if row else None

def upsert_product(
    name: str,
    category: Optional[str] = "General",
    price: float = 0.0,
    stock_quantity: int = 0,
    unit: str = "unit",
    min_stock_alert: int = 5,
    product_id: Optional[int] = None
) -> Dict[str, Any]:
    """Inserts a new product or updates an existing product."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if product_id:
            cursor.execute("""
                UPDATE products
                SET name = ?, category = ?, price = ?, stock_quantity = ?, unit = ?, min_stock_alert = ?
                WHERE id = ?;
            """, (name.strip(), category, price, stock_quantity, unit, min_stock_alert, product_id))
            target_id = product_id
        else:
            # Check if exists by name
            cursor.execute("SELECT id FROM products WHERE LOWER(name) = LOWER(?);", (name.strip(),))
            existing = cursor.fetchone()
            if existing:
                target_id = existing["id"]
                cursor.execute("""
                    UPDATE products
                    SET category = COALESCE(?, category),
                        price = ?,
                        stock_quantity = ?,
                        unit = COALESCE(?, unit),
                        min_stock_alert = COALESCE(?, min_stock_alert)
                    WHERE id = ?;
                """, (category, price, stock_quantity, unit, min_stock_alert, target_id))
            else:
                cursor.execute("""
                    INSERT INTO products (name, category, price, stock_quantity, unit, min_stock_alert)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (name.strip(), category, price, stock_quantity, unit, min_stock_alert))
                target_id = cursor.lastrowid
        conn.commit()
        return get_product_by_id(target_id) # type: ignore

def update_stock(product_id: int, qty_change: int) -> Optional[Dict[str, Any]]:
    """Updates product stock quantity by qty_change (positive for restock, negative for sale)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity FROM products WHERE id = ?;", (product_id,))
        row = cursor.fetchone()
        if not row:
            return None
        new_quantity = row["stock_quantity"] + qty_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock. Available: {row['stock_quantity']}, Requested change: {qty_change}")
        
        cursor.execute("UPDATE products SET stock_quantity = ? WHERE id = ?;", (new_quantity, product_id))
        conn.commit()
        return get_product_by_id(product_id)

def record_sale(
    product_name: str,
    quantity: int,
    total_amount: float,
    product_id: Optional[int] = None
) -> Dict[str, Any]:
    """Records a sale and decrements stock if the product exists."""
    with get_connection() as conn:
        cursor = conn.cursor()
        matched_id = product_id
        if not matched_id:
            matched_prod = get_product_by_name(product_name)
            if matched_prod:
                matched_id = matched_prod["id"]
                product_name = matched_prod["name"]
        
        # Decrement stock if item found in catalog
        if matched_id:
            update_stock(matched_id, -quantity)
        
        cursor.execute("""
            INSERT INTO sales (product_id, product_name, quantity, total_amount)
            VALUES (?, ?, ?, ?);
        """, (matched_id, product_name, quantity, total_amount))
        sale_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM sales WHERE id = ?;", (sale_id,))
        return dict(cursor.fetchone())

def get_sales_history() -> List[Dict[str, Any]]:
    """Retrieves all sales records ordered by timestamp descending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales ORDER BY timestamp DESC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def log_chat(
    customer_phone: Optional[str],
    message: str,
    response: str,
    intent: Optional[str] = None
) -> Dict[str, Any]:
    """Logs customer conversations and the assistant reply."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_logs (customer_phone, message, response, intent)
            VALUES (?, ?, ?, ?);
        """, (customer_phone, message, response, intent))
        log_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM chat_logs WHERE id = ?;", (log_id,))
        return dict(cursor.fetchone())
