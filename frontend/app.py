import os
import sys
import datetime
import pandas as pd
import streamlit as st

# Setup backend import paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import database
from app.services import ai_service, ocr_service

# Initialize database
database.init_db()

# Page configuration
st.set_page_config(
    page_title="RetailFlow AI - Local Retail Automator",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=400&q=80", use_container_width=True)
    st.title("🏪 RetailFlow AI")
    st.caption("AI-Powered Local Retail Automator for Kirana & Retail Stores")
    st.markdown("---")
    
    st.write("**Store Details:**")
    st.write("📍 **Store:** Krishna Stores & Provisions")
    st.write("🕒 **Hours:** 7:30 AM – 10:00 PM Daily")
    st.write("📞 **Phone:** +91 98765 43210")
    st.markdown("---")
    
    products = database.get_all_products()
    low_stock = [p for p in products if p["stock_quantity"] <= p.get("min_stock_alert", 5)]
    
    st.write("🚨 **System Status**")
    if low_stock:
        st.error(f"{len(low_stock)} items need restocking!")
    else:
        st.success("All stock levels healthy.")
    
    st.caption("100% Free & Open-Source Stack")

# Header
st.markdown("<div class='main-header'>🏪 RetailFlow AI — Local Retail Automator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated WhatsApp customer inquiries, zero-cost invoice digitizer, and smart inventory management.</div>", unsafe_allow_html=True)

# Navigation Tabs
tab_inventory, tab_bot, tab_ocr, tab_pos = st.tabs([
    "📦 Inventory Management",
    "🤖 WhatsApp Customer Bot",
    "🧾 Bill & Receipt Digitizer",
    "📊 POS & Sales Ledger"
])

# -------------------------------------------------------------
# TAB 1: INVENTORY MANAGEMENT
# -------------------------------------------------------------
with tab_inventory:
    st.subheader("Current Store Inventory")
    products = database.get_all_products()
    
    # KPI Row
    col_p1, col_p2, col_p3 = st.columns(3)
    total_val = sum(p["price"] * p["stock_quantity"] for p in products)
    low_stock_count = sum(1 for p in products if p["stock_quantity"] <= p.get("min_stock_alert", 5))
    
    col_p1.metric("Total Unique Products", len(products))
    col_p2.metric("Inventory Valuation", f"₹ {total_val:,.2f}")
    col_p3.metric("Low Stock Alerts", low_stock_count, delta=-low_stock_count if low_stock_count > 0 else 0, delta_color="inverse")
    
    if low_stock_count > 0:
        st.warning(f"⚠️ **Attention Required:** {low_stock_count} item(s) are at or below their reorder threshold!")
    
    # Display table
    df_products = pd.DataFrame(products)
    if not df_products.empty:
        df_display = df_products[["id", "name", "category", "price", "stock_quantity", "unit", "min_stock_alert"]].copy()
        df_display.columns = ["ID", "Product Name", "Category", "Selling Price (₹)", "Current Stock", "Unit", "Alert Level"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No products found in the database. Add your first item below!")
        
    st.markdown("---")
    
    # Quick Stock Adjustment & New Product Form
    col_adj, col_add = st.columns(2)
    
    with col_adj:
        st.markdown("### ⚡ Quick Stock Adjustment")
        if products:
            selected_product_name = st.selectbox(
                "Select Product to Adjust", 
                options=[p["name"] for p in products],
                key="adj_prod"
            )
            selected_prod = next(p for p in products if p["name"] == selected_product_name)
            st.info(f"Current Stock for **{selected_prod['name']}**: `{selected_prod['stock_quantity']} {selected_prod['unit']}`")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("➕ Add 1", key="btn_add_1"):
                    database.update_stock(selected_prod["id"], 1)
                    st.success("Added 1 unit!")
                    st.rerun()
            with col_b2:
                if st.button("➖ Remove 1", key="btn_sub_1"):
                    database.update_stock(selected_prod["id"], -1)
                    st.warning("Removed 1 unit!")
                    st.rerun()
            with col_b3:
                if st.button("📦 Restock +10", key="btn_add_10"):
                    database.update_stock(selected_prod["id"], 10)
                    st.success("Restocked 10 units!")
                    st.rerun()
                    
            with st.form("custom_adjust_form"):
                qty_delta = st.number_input("Custom Delta (+ to add, - to subtract)", value=0, step=1)
                submit_delta = st.form_submit_button("Update Stock")
                if submit_delta and qty_delta != 0:
                    database.update_stock(selected_prod["id"], int(qty_delta))
                    st.success(f"Adjusted stock by {qty_delta}!")
                    st.rerun()

    with col_add:
        st.markdown("### ➕ Add or Restock Product")
        with st.form("new_product_form"):
            new_name = st.text_input("Product Name (e.g. Masoor Dal 500g)")
            new_cat = st.selectbox("Category", ["Grains & Pulses", "Dairy", "Beverages", "Spices & Oils", "Snacks", "Personal Care", "Other"])
            new_price = st.number_input("Selling Price (₹)", min_value=0.0, value=50.0, step=1.0)
            new_qty = st.number_input("Stock Quantity", min_value=0, value=20, step=1)
            new_unit = st.selectbox("Unit", ["pack", "kg", "g", "liter", "ml", "bottle", "piece"])
            new_alert = st.number_input("Min Stock Alert Threshold", min_value=1, value=5, step=1)
            
            submitted = st.form_submit_button("Save to Inventory")
            if submitted:
                if new_name.strip():
                    database.upsert_product(
                        name=new_name.strip(),
                        category=new_cat,
                        price=float(new_price),
                        stock_quantity=int(new_qty),
                        unit=new_unit,
                        min_stock_alert=int(new_alert)
                    )
                    st.success(f"Product '{new_name}' saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid product name.")

# -------------------------------------------------------------
# TAB 2: WHATSAPP CUSTOMER BOT SIMULATOR
# -------------------------------------------------------------
with tab_bot:
    st.subheader("💬 AI WhatsApp Customer Assistant")
    st.write("Simulate real-time customer messages received via WhatsApp or SMS. The AI engine detects customer intent, queries live inventory, and crafts automated replies with zero external API costs.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Welcome to Krishna Stores. How can I help you today? You can ask about product availability, prices, or store timings!"}
        ]
        
    # Quick Test Chips
    st.write("**Try asking:**")
    quick_cols = st.columns(4)
    q1 = quick_cols[0].button("🌾 'Do you have rice?'")
    q2 = quick_cols[1].button("🥛 'What is price of milk?'")
    q3 = quick_cols[2].button("🛍️ 'Order 2 packets of milk'")
    q4 = quick_cols[3].button("🕒 'What are your store hours?'")
    
    test_query = None
    if q1: test_query = "Do you have rice in stock?"
    if q2: test_query = "What is the price of milk?"
    if q3: test_query = "I want to order 2 packets of milk"
    if q4: test_query = "What time does your store open today?"
    
    # Display Chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "metadata" in msg:
                    with st.expander("🔍 Intent & Entities Detected by AI", expanded=False):
                        st.json(msg["metadata"])
                        
    # Input box
    user_input = st.chat_input("Type a customer message...") or test_query
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process message with AI Service
        bot_response = ai_service.handle_customer_message(user_input, "+91 99887 76655")
        reply_text = bot_response.get("reply") or bot_response.get("response_text") or "Thank you for reaching out!"
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": reply_text,
            "metadata": {
                "intent": bot_response.get("intent"),
                "items_detected": bot_response.get("items_detected") or bot_response.get("extracted_items", []),
                "action_taken": bot_response.get("action_taken") or bot_response.get("status")
            }
        })
        st.rerun()

# -------------------------------------------------------------
# TAB 3: RECEIPT & INVOICE DIGITIZER (OCR)
# -------------------------------------------------------------
with tab_ocr:
    st.subheader("🧾 Zero-Cost Bill & Supplier Invoice Digitizer")
    st.write("Scan or paste wholesale vendor invoices to automatically parse line items, prices, and quantities without manual data entry.")
    
    SAMPLE_INVOICES = {
        "Sample 1: Sri Lakshmi Wholesale Provisions": """SRI LAKSHMI WHOLESALE PROVISIONS
Invoice No: INV-2026-881
Date: 14-Sep-2026

Items:
Rice 1kg - 50 qty @ Rs. 52.00
Sugar 1kg - 30 qty @ Rs. 40.00
Wheat Flour 1kg - 25 qty @ Rs. 45.00
Cooking Oil 1L - 20 qty @ Rs. 130.00

Total Items: 125
Grand Total: Rs. 7,525.00""",
        
        "Sample 2: Dairy Fresh Milk & Beverage Supplies": """DAIRY FRESH COOPERATIVE DISTRIBUTORS
Bill: DF-9042
Date: 14/09/2026

Items Supplied:
Milk 500ml x 40 @ 28.00
Tea Powder 250g x 15 @ 75.00

Total: Rs. 2,245.00""",
        
        "Sample 3: Custom Plain Text Format": """Wholesale Mart
Date: 2026-09-14
Rice 1kg, 20, 50.00
Sugar 1kg, 15, 38.00
Tea Powder 250g, 10, 70.00
Total: 2270"""
    }
    
    selected_sample = st.selectbox("Load Sample Invoice or Enter Custom:", list(SAMPLE_INVOICES.keys()) + ["Enter Custom Text"])
    
    if selected_sample == "Enter Custom Text":
        raw_invoice_text = st.text_area("Paste receipt or invoice text here:", height=160)
    else:
        raw_invoice_text = st.text_area("Invoice Text:", value=SAMPLE_INVOICES[selected_sample], height=160)
        
    col_ocr_btn, col_ocr_res = st.columns([1, 2])
    
    with col_ocr_btn:
        auto_update = st.checkbox("Auto-update inventory when processed", value=False)
        process_btn = st.button("⚡ Parse & Digitize Invoice", type="primary")
        
    if process_btn:
        if raw_invoice_text.strip():
            parsed_result = ocr_service.parse_receipt_text(raw_invoice_text, auto_update_inventory=auto_update)
            st.session_state["parsed_ocr"] = parsed_result
            st.success(parsed_result.get("message", "Invoice successfully processed!"))
        else:
            st.error("Please provide invoice text to process.")
            
    if "parsed_ocr" in st.session_state:
        res = st.session_state["parsed_ocr"]
        st.markdown("### 📋 Digitized Line Items")
        
        items = res.get("parsed_items") or res.get("items", [])
        total_val = res.get("total_amount") or res.get("calculated_total", 0.0)
        
        c1, c2 = st.columns(2)
        c1.metric("Items Detected", len(items))
        c2.metric("Calculated Invoice Total", f"₹ {total_val:,.2f}")
        
        if items:
            df_items = pd.DataFrame(items)
            st.dataframe(df_items, use_container_width=True, hide_index=True)
            
            if not res.get("inventory_updated"):
                if st.button("📥 Commit These Items to Store Inventory", key="commit_inv"):
                    for item in items:
                        existing = database.get_product_by_name(item["name"])
                        if existing:
                            database.update_stock(existing["id"], item["quantity"])
                        else:
                            database.upsert_product(
                                name=item["name"],
                                category="Wholesale Restock",
                                price=round(item["unit_price"] * 1.2, 2), # 20% margin default
                                stock_quantity=item["quantity"],
                                unit="pack",
                                min_stock_alert=5
                            )
                    st.success("Stock updated in database successfully!")
                    st.rerun()
        else:
            st.warning("No line items could be parsed. Check the text format.")

# -------------------------------------------------------------
# TAB 4: SALES & POS COUNTER BILLING
# -------------------------------------------------------------
with tab_pos:
    st.subheader("📊 Point of Sale (POS) Counter Billing")
    
    col_pos_left, col_pos_right = st.columns([1, 1])
    
    with col_pos_left:
        st.markdown("### 🛒 New Customer Sale")
        products = database.get_all_products()
        if products:
            with st.form("pos_sale_form"):
                pos_prod_name = st.selectbox("Select Product", [p["name"] for p in products])
                prod_obj = next(p for p in products if p["name"] == pos_prod_name)
                
                st.write(f"Unit Price: **₹ {prod_obj['price']:.2f}** | Available: `{prod_obj['stock_quantity']} {prod_obj['unit']}`")
                pos_qty = st.number_input("Quantity to Sell", min_value=1, max_value=max(1, prod_obj["stock_quantity"]), value=1, step=1)
                pos_customer = st.text_input("Customer Phone / Name (optional)", value="Walk-in Customer")
                pos_payment = st.selectbox("Payment Method", ["Cash", "UPI / QR Code", "Store Credit / Khata"])
                
                total_sale_price = pos_qty * prod_obj["price"]
                st.markdown(f"#### **Total Bill: ₹ {total_sale_price:.2f}**")
                
                bill_submit = st.form_submit_button("💳 Record Sale & Print Bill", type="primary")
                if bill_submit:
                    if prod_obj["stock_quantity"] < pos_qty:
                        st.error("Insufficient stock!")
                    else:
                        database.record_sale(
                            product_name=prod_obj["name"],
                            quantity=int(pos_qty),
                            total_amount=float(total_sale_price),
                            product_id=prod_obj["id"]
                        )
                        st.success(f"Sale recorded: ₹ {total_sale_price:.2f} for {pos_qty} x {prod_obj['name']}")
                        st.rerun()
        else:
            st.info("Please add products in the inventory tab first.")
            
    with col_pos_right:
        st.markdown("### 📈 Recent Sales Ledger")
        sales_records = database.get_sales_history()
        if sales_records:
            total_rev = sum(s["total_amount"] for s in sales_records)
            st.metric("Total Revenue Logged", f"₹ {total_rev:,.2f}", f"{len(sales_records)} sales")
            df_sales = pd.DataFrame(sales_records)
            st.dataframe(df_sales, hide_index=True, use_container_width=True)
        else:
            st.info("No sales transactions recorded yet.")
