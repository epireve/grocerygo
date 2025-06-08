PRAGMA foreign_keys=off;

-- Check if apartment_unit already exists in the address table
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM pragma_table_info('orders_address') WHERE name='apartment_unit'
)
THEN (
    -- Remove duplicate column if it exists
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
    
    -- Copy data from old table, handling potential duplicate columns
    INSERT INTO orders_address_new 
    SELECT 
        id, 
        address_type, 
        full_name, 
        street_address, 
        apartment_unit, -- Use the existing apartment_unit column
        city, 
        state, 
        postal_code, 
        country, 
        phone, 
        is_default, 
        created_at, 
        updated_at, 
        user_id 
    FROM orders_address;
    
    -- Drop old table
    DROP TABLE orders_address;
    
    -- Rename new table
    ALTER TABLE orders_address_new RENAME TO orders_address;
    
    -- Recreate indices
    CREATE INDEX orders_address_user_id ON orders_address (user_id);
)
ELSE (
    SELECT 1
) END;

-- Fix OrderStatusHistory table if it exists
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM sqlite_master WHERE type='table' AND name='orders_orderstatushistory'
)
THEN (
    -- Create a new version of the table with correct columns
    CREATE TABLE orders_orderstatushistory_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status VARCHAR(20) NOT NULL,
        notes TEXT NULL,
        created_at DATETIME NOT NULL,
        created_by_id INTEGER NULL REFERENCES auth_user (id),
        checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
    );
    
    -- Copy data, making sure to use checkout_id correctly
    INSERT INTO orders_orderstatushistory_new (id, status, notes, created_at, created_by_id, checkout_id)
    SELECT 
        id, 
        status, 
        notes, 
        created_at, 
        created_by_id,
        COALESCE(checkout_id, id) -- Use checkout_id if it exists, otherwise fall back to id
    FROM orders_orderstatushistory;
    
    -- Drop old table
    DROP TABLE orders_orderstatushistory;
    
    -- Rename new table
    ALTER TABLE orders_orderstatushistory_new RENAME TO orders_orderstatushistory;
    
    -- Recreate indices
    CREATE INDEX orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id);
    CREATE INDEX orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id);
)
ELSE (
    SELECT 1
) END;

PRAGMA foreign_keys=on;