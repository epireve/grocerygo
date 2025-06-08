PRAGMA foreign_keys=off;

-- Fix Address table
CREATE TABLE orders_address_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address_type VARCHAR(10) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    apartment_unit VARCHAR(255) NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NULL,
    is_default BOOL NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    user_id INTEGER NOT NULL REFERENCES auth_user (id)
);

-- Copy data from old table, safely handling potential column differences
INSERT INTO orders_address_new (
    id, address_type, full_name, street_address, apartment_unit,
    city, state, postal_code, country, phone, is_default, created_at, updated_at, user_id
)
SELECT 
    id, address_type, full_name, street_address, 
    COALESCE(apartment_unit, apartment_address), -- Use either one that exists
    city, state, postal_code, country, phone, 
    is_default, created_at, updated_at, user_id 
FROM orders_address;

-- Drop old table
DROP TABLE orders_address;

-- Rename new table
ALTER TABLE orders_address_new RENAME TO orders_address;

-- Recreate indices
CREATE INDEX orders_address_user_id ON orders_address (user_id);

PRAGMA foreign_keys=on;