PRAGMA foreign_keys=off;

-- Create the OrderStatusHistory table with the correct schema
CREATE TABLE IF NOT EXISTS "orders_orderstatushistory" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(20) NOT NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL,
    created_by_id INTEGER NULL REFERENCES auth_user (id),
    checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
);

-- Create necessary indices
CREATE INDEX IF NOT EXISTS orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id);
CREATE INDEX IF NOT EXISTS orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id);

PRAGMA foreign_keys=on;