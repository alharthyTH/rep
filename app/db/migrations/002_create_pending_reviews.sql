-- Migration: Create pending_reviews table
-- Description: Stores review drafts awaiting client approval.

CREATE TYPE review_status AS ENUM ('pending', 'approved', 'rejected', 'posted');

CREATE TABLE IF NOT EXISTS pending_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    google_review_id TEXT NOT NULL,
    review_text TEXT,
    star_rating INTEGER,
    draft_reply TEXT,
    status review_status DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for lookup during Twilio webhook (by client phone and pending status)
CREATE INDEX IF NOT EXISTS idx_pending_reviews_client_status ON pending_reviews(client_id, status);
