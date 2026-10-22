from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from app import database
from app.models import (
    ProductCreate,
    ProductResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ReceiptParseRequest,
    ReceiptParseResponse,
    SaleCreate,
    SaleResponse,
    SalesSummaryResponse,
)
from app.services import ai_service, ocr_service

app = FastAPI(
    title="AI-Powered Local Retail Automator API",
    description="Backend API powering automated retail inventory, conversational WhatsApp/customer bot, and invoice processing.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard and messaging webhooks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Initialize database and seed sample data on application launch."""
    database.init_db()

@app.get("/", tags=["General"])
def root() -> Dict[str, Any]:
    """App status and API metadata."""
    return {
        "app_name": "AI-Powered Local Retail Automator",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "products": "/api/products",
            "chat": "/api/chat",
            "receipt": "/api/receipt",
            "sales": "/api/sales",
            "docs": "/docs"
        }
    }

@app.get("/health", tags=["General"])
def health_check() -> Dict[str, str]:
    """Health check endpoint to verify server and database status."""
    try:
        # Simple test query to ensure DB is responsive
        database.get_all_products()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity issue: {str(e)}"
        )

@app.get("/api/products", response_model=List[ProductResponse], tags=["Products & Inventory"])
def list_products():
    """Returns list of all available retail products and current inventory levels."""
    try:
        return database.get_all_products()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch products: {str(e)}"
        )

@app.post("/api/products", response_model=ProductResponse, tags=["Products & Inventory"])
def create_or_update_product(product: ProductCreate):
    """Creates a new product or updates an existing one if the name already exists."""
    try:
        saved_product = database.upsert_product(
            name=product.name,
            category=product.category,
            price=product.price,
            stock_quantity=product.stock_quantity,
            unit=product.unit or "unit",
            min_stock_alert=product.min_stock_alert or 5
        )
        return saved_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save product: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatMessageResponse, tags=["AI Assistant"])
def chat_with_assistant(payload: ChatMessageRequest):
    """
    Handles customer inquiry, detects intent, checks inventory,
    logs the interaction, and returns an actionable response.
    """
    try:
        result = ai_service.handle_customer_message(
            message=payload.message,
            customer_phone=payload.customer_phone
        )
        # Log to chat history
        database.log_chat(
            customer_phone=payload.customer_phone,
            message=payload.message,
            response=result["reply"],
            intent=result.get("intent")
        )
        return ChatMessageResponse(
            reply=result["reply"],
            intent=result.get("intent"),
            items_detected=result.get("items_detected", []),
            action_taken=result.get("action_taken")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing error: {str(e)}"
        )

@app.post("/api/receipt", response_model=ReceiptParseResponse, tags=["OCR & Intake"])
def process_receipt(payload: ReceiptParseRequest):
    """
    Parses vendor receipt or bill text into structured line items,
    and optionally auto-updates product stock in the SQLite database.
    """
    try:
        result = ocr_service.parse_receipt_text(
            receipt_text=payload.receipt_text,
            auto_update_inventory=bool(payload.auto_update_inventory)
        )
        return ReceiptParseResponse(
            parsed_items=result["parsed_items"],
            total_amount=result["total_amount"],
            inventory_updated=result["inventory_updated"],
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse receipt: {str(e)}"
        )

@app.get("/api/sales", response_model=SalesSummaryResponse, tags=["Sales & Billing"])
def get_sales():
    """Retrieves all past sales records along with total revenue and order count."""
    try:
        history = database.get_sales_history()
        total_rev = sum(item["total_amount"] for item in history)
        return SalesSummaryResponse(
            sales=history,
            total_revenue=round(total_rev, 2),
            total_sales_count=len(history)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales history: {str(e)}"
        )

@app.post("/api/sales", response_model=SaleResponse, tags=["Sales & Billing"])
def create_sale(sale: SaleCreate):
    """Records a retail sale, auto-calculates total amount if not given, and updates stock."""
    try:
        product_name = sale.product_name
        product_id = sale.product_id
        
        # Resolve product
        matched = None
        if product_id:
            matched = database.get_product_by_id(product_id)
        elif product_name:
            matched = database.get_product_by_name(product_name)
            
        if not matched and not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either product_id or product_name must be provided."
            )
            
        if matched:
            product_id = matched["id"]
            product_name = matched["name"]
            unit_price = matched["price"]
        else:
            unit_price = 0.0
            
        total_amount = sale.total_amount
        if total_amount is None:
            if unit_price > 0:
                total_amount = round(unit_price * sale.quantity, 2)
            else:
                total_amount = 0.0
                
        # Record sale in database (handles stock decrement)
        recorded = database.record_sale(
            product_id=product_id,
            product_name=product_name or "Custom Item",
            quantity=sale.quantity,
            total_amount=total_amount
        )
        return recorded
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record sale: {str(e)}"
        )
