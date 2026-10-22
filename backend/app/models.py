from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProductCreate(BaseModel):
    name: str = Field(..., example="Sugar 1kg")
    category: Optional[str] = Field(default="General", example="Grains & Staples")
    price: float = Field(..., gt=0, example=45.0)
    stock_quantity: int = Field(default=0, ge=0, example=25)
    unit: Optional[str] = Field(default="unit", example="kg")
    min_stock_alert: Optional[int] = Field(default=5, ge=0, example=5)

class ProductResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    price: float
    stock_quantity: int
    unit: str
    min_stock_alert: int

class ChatMessageRequest(BaseModel):
    customer_phone: Optional[str] = Field(default=None, example="+919876543210")
    message: str = Field(..., example="Do you have Rice 1kg in stock and what is the price?")

class ChatMessageResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    items_detected: Optional[List[Dict[str, Any]]] = []
    action_taken: Optional[str] = None

class ReceiptParseRequest(BaseModel):
    receipt_text: str = Field(..., example="Rice 1kg - 20 qty @ 55\nSugar 1kg - 15 qty @ 42")
    auto_update_inventory: Optional[bool] = Field(default=False, example=True)

class ParsedReceiptItem(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total: float

class ReceiptParseResponse(BaseModel):
    parsed_items: List[ParsedReceiptItem]
    total_amount: float
    inventory_updated: bool
    message: str

class SaleCreate(BaseModel):
    product_id: Optional[int] = Field(default=None, example=1)
    product_name: Optional[str] = Field(default=None, example="Rice 1kg")
    quantity: int = Field(default=1, gt=0, example=2)
    total_amount: Optional[float] = Field(default=None, example=120.0)

class SaleResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: str
    quantity: int
    total_amount: float
    timestamp: Optional[str] = None

class SalesSummaryResponse(BaseModel):
    sales: List[SaleResponse]
    total_revenue: float
    total_sales_count: int
