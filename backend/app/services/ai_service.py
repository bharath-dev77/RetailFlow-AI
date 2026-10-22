import re
from typing import Dict, Any, Optional, List
from app import database

def extract_quantities_and_items(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identifies products and quantities mentioned in the customer text."""
    detected = []
    text_lower = text.lower()
    
    for product in catalog:
        p_name = product["name"].lower()
        # Extract base keywords (e.g. 'rice', 'milk', 'sugar')
        base_words = [w for w in re.split(r'\s+', p_name) if not re.match(r'^\d+(kg|g|l|ml)$', w)]
        
        # Check if full name or base keywords match
        matches = False
        if p_name in text_lower:
            matches = True
        elif any(len(w) > 3 and w in text_lower for w in base_words):
            matches = True
            
        if matches:
            # Check for quantity pattern before or after the product mention
            qty_match = re.search(r'(\d+)\s*(?:packet|packets|pkt|pkts|kg|liter|liters|l|box|boxes|qty|count|units)?\s*(?:of\s+)?' + re.escape(base_words[0]), text_lower)
            if not qty_match:
                qty_match = re.search(re.escape(base_words[0]) + r'.*?(\d+)', text_lower)
            
            quantity = int(qty_match.group(1)) if qty_match else 1
            detected.append({
                "product_id": product["id"],
                "name": product["name"],
                "available_stock": product["stock_quantity"],
                "unit": product["unit"],
                "price": product["price"],
                "requested_quantity": quantity
            })
    return detected

def handle_customer_message(message: str, customer_phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Intelligently classifies retail customer intents and constructs responses.
    Zero external paid dependency fallback, extensible with LLMs.
    """
    msg = message.strip()
    msg_lower = msg.lower()
    catalog = database.get_all_products()
    
    # 1. Greetings
    if re.search(r'^(hi|hello|hey|namaste|vanakkam|good\s+(morning|afternoon|evening))\b', msg_lower):
        reply = (
            "Hello! Welcome to our retail store. "
            "You can ask me about available items, check current prices, check store timings, or place an order for quick pickup. "
            "How can I assist you today?"
        )
        return {
            "reply": reply,
            "intent": "greeting",
            "items_detected": [],
            "action_taken": "greet_user"
        }
    
    # 2. Store timings & location
    if any(k in msg_lower for k in ["timing", "timings", "open", "close", "hours", "where are you", "location", "address"]):
        reply = (
            "We are open every day from 7:30 AM to 10:00 PM. "
            "We are located at Main Bazaar Street. Home delivery is available for orders above ₹300!"
        )
        return {
            "reply": reply,
            "intent": "store_info",
            "items_detected": [],
            "action_taken": "provide_store_info"
        }
    
    # 3. Product Inquiries / Orders
    detected_items = extract_quantities_and_items(msg, catalog)
    
    # Order Intent
    is_order = any(w in msg_lower for w in ["order", "book", "buy", "send", "deliver", "want", "need", "pack"])
    
    if detected_items:
        if is_order:
            order_lines = []
            total_cost = 0.0
            for item in detected_items:
                req_qty = item["requested_quantity"]
                cost = req_qty * item["price"]
                total_cost += cost
                if item["available_stock"] >= req_qty:
                    order_lines.append(f"• {item['name']}: {req_qty} {item['unit']} @ ₹{item['price']} = ₹{cost:.2f}")
                else:
                    order_lines.append(f"• {item['name']}: Only {item['available_stock']} {item['unit']} in stock (Requested: {req_qty})")
            
            summary_str = "\n".join(order_lines)
            reply = (
                f"We have noted your order request:\n{summary_str}\n"
                f"Estimated Total: ₹{total_cost:.2f}.\n"
                f"Your order is reserved and ready for pickup/delivery. Thank you for shopping with us!"
            )
            return {
                "reply": reply,
                "intent": "order_placement",
                "items_detected": detected_items,
                "action_taken": "order_reserved"
            }
        else:
            # Stock & Price Check
            info_lines = []
            for item in detected_items:
                stock_status = f"{item['available_stock']} {item['unit']} in stock" if item['available_stock'] > 0 else "Out of stock"
                info_lines.append(f"• {item['name']}: ₹{item['price']:.2f} per {item['unit']} ({stock_status})")
            
            reply = "Here is the current availability and pricing for your query:\n" + "\n".join(info_lines)
            return {
                "reply": reply,
                "intent": "price_and_stock_inquiry",
                "items_detected": detected_items,
                "action_taken": "provide_catalog_details"
            }
            
    # 4. Catalog overview / General items list
    if any(k in msg_lower for k in ["list", "catalog", "items", "products", "what do you have", "what do you sell"]):
        top_items = catalog[:5]
        item_names = ", ".join([p["name"] for p in top_items])
        reply = (
            f"We stock daily essentials including {item_names}, and more. "
            "Feel free to ask for any specific item's price or availability!"
        )
        return {
            "reply": reply,
            "intent": "catalog_overview",
            "items_detected": [],
            "action_taken": "provide_general_catalog"
        }
        
    # 5. Default Fallback
    reply = (
        "I'm your local store assistant. You can check stock, prices, or place an order by typing something like: "
        "'Do you have Rice 1kg?' or 'Order 2 packets of Milk 500ml'."
    )
    return {
        "reply": reply,
        "intent": "general_inquiry",
        "items_detected": [],
        "action_taken": "fallback_guidance"
    }
