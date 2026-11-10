-- Example domain: a small registry of work items.
CREATE TABLE items (
  id          BIGSERIAL PRIMARY KEY,
  item_key    TEXT NOT NULL UNIQUE,
  title       TEXT NOT NULL,
  owner       TEXT,                                  -- NULL = nobody owns it (a gap to surface)
  priority    TEXT NOT NULL DEFAULT 'unknown' CHECK (priority IN ('high','medium','low','unknown')),
  status      TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','done','archived')),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
