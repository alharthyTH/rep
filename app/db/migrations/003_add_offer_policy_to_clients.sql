-- Migration: Add offer_policy to clients table
-- Description: Adds a safety guardrail for AI's generosity.

ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS offer_policy TEXT DEFAULT 'NEVER offer free items, refunds, or discounts. Just apologize and ask to DM.';