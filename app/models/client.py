from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ClientBase(BaseModel):
    phone_number: str = Field(..., description="The client's WhatsApp number.")
    google_location_id: str = Field(..., description="The ID of their shop in Google Maps.")
    business_name: str
    language_preference: str = Field(default="ar-om", description="Omani Arabic by default.")
    offer_policy: str = Field(
        default="NEVER offer free items, refunds, or discounts. Just apologize and ask to DM.",
        description="Business-specific policy for AI offers."
    )

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
