import re
from typing import Dict, Any, List
from app import database

def parse_receipt_line(line: str) -> Dict[str, Any] | None:
    """Parses a single line from receipt text into item, quantity, and unit price."""
    cleaned = line.strip()
    if not cleaned or len(cleaned) < 3:
        return None
    
    # Strip leading bullet/index like "1.", "1)", "-"
    cleaned = re.sub(r'^[\d\.\-\*\•\)]+\s*', '', cleaned)
    
    # Pattern 1: Name - Qty @ Price (e.g., "Rice 1kg - 20 qty @ 55" or "Milk 500ml x 10 @ 30")
    m1 = re.search(r'^(.*?)[,\-\|xX]?\s*(?:qty:?|quantity:?)?\s*(\d+)\s*(?:units?|pcs?|packets?|kg|l)?\s*[@xX|,\-]\s*(?:rs\.?|₹)?\s*([\d\.]+)', cleaned, re.IGNORECASE)
    if m1:
        name = m1.group(1).strip(" -|,xX")
        qty = int(m1.group(2))
        price = float(m1.group(3))
        if name:
            return {"name": name, "quantity": qty, "unit_price": price, "total": round(qty * price, 2)}
    
    # Pattern 2: Name followed by 2 numbers (e.g., "Rice 1kg 20 55" or "Milk 500ml, 10, 28")
    m2 = re.search(r'^(.*?)[,\-\|\t]\s*(\d+)\s*[,\-\|\t]\s*([\d\.]+)', cleaned)
    if m2:
        name = m2.group(1).strip()
        qty = int(m2.group(2))
        price = float(m2.group(3))
        if name:
            return {"name": name, "quantity": qty, "unit_price": price, "total": round(qty * price, 2)}
            
    # Pattern 3: Simple Name @ Price (Default qty 1)
    m3 = re.search(r'^(.*?)\s*[@=]\s*(?:rs\.?|₹)?\s*([\d\.]+)', cleaned, re.IGNORECASE)
    if m3:
        name = m3.group(1).strip(" -|,")
        qty = 1
        price = float(m3.group(2))
        if name:
            return {"name": name, "quantity": qty, "unit_price": price, "total": round(qty * price, 2)}

    return None

def parse_receipt_text(receipt_text: str, auto_update_inventory: bool = False) -> Dict[str, Any]:
    """
    Parses OCR invoice/bill text, extracts structured items,
    and optionally syncs stock updates directly to SQLite database.
    """
    lines = receipt_text.strip().split("\n")
    parsed_items: List[Dict[str, Any]] = []
    total_amount = 0.0

    for line in lines:
        parsed = parse_receipt_line(line)
        if parsed:
            parsed_items.append(parsed)
            total_amount += parsed["total"]
            
            if auto_update_inventory:
                # Check if item exists in inventory
                existing = database.get_product_by_name(parsed["name"])
                if existing:
                    # Update stock with new intake
                    database.update_stock(existing["id"], parsed["quantity"])
                else:
                    # Create new product entry
                    database.upsert_product(
                        name=parsed["name"],
                        category="Inventory Intake",
                        price=round(parsed["unit_price"] * 1.15, 2), # retail markup 15%
                        stock_quantity=parsed["quantity"],
                        unit="unit",
                        min_stock_alert=5
                    )

    return {
        "parsed_items": parsed_items,
        "total_amount": round(total_amount, 2),
        "inventory_updated": auto_update_inventory,
        "message": (
            f"Successfully parsed {len(parsed_items)} item(s). "
            + ("Inventory counts updated." if auto_update_inventory else "Inventory not modified.")
        )
    }
