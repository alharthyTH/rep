-- Migration: Create clients table
-- Description: Stores shop information and client preferences.

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number TEXT UNIQUE NOT NULL,
    google_location_id TEXT NOT NULL,
    business_name TEXT NOT NULL,
    language_preference TEXT NOT NULL DEFAULT 'ar-om',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups by phone number
CREATE INDEX IF NOT EXISTS idx_clients_phone_number ON clients(phone_number);
