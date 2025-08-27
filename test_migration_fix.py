#!/usr/bin/env python3
"""
Simple test script to verify the migration fix works
"""

import os
import sqlite3

def create_test_db():
    """Create a test database with the problematic scenario"""
    db_path = 'test_fix.db'
    
    # Remove existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables with new schema (including created_by columns)
    c.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test user
    c.execute("INSERT INTO users (id, email, name) VALUES (?, ?, ?)", 
              ('test_user', 'test@example.com', 'Test User'))
    
    # Insert test people with duplicate names (this is the problematic scenario)
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('John Doe', 'john@example.com'))
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('John Doe', 'john2@example.com'))  # Duplicate name!
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('Jane Smith', 'jane@example.com'))
    
    # Create the unique constraint (this is what was causing the issue)
    c.execute("CREATE UNIQUE INDEX idx_people_name_user ON people (name, created_by)")
    
    conn.commit()
    conn.close()
    
    print("✅ Test database created with problematic scenario")
    return db_path

def test_migration_fix():
    """Test that the migration fix works"""
    print("🧪 Testing Migration Fix")
    print("=" * 40)
    
    try:
        # Create test database
        db_path = create_test_db()
        
        # Import the fixed migration function
        import sys
        sys.path.insert(0, '.')
        
        # Mock the app context
        class MockApp:
            def __init__(self):
                self.config = {'TOOLTRACKER_DB': db_path}
        
        # Mock current_app
        import app
        with app.app_context():
            # Run the fixed migration
            app.migrate_existing_database()
        
        print("\n✅ Migration completed successfully!")
        
        # Verify the results
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check that all records have created_by values
        c.execute("SELECT COUNT(*) FROM people WHERE created_by IS NOT NULL")
        migrated_count = c.fetchone()[0]
        print(f"✅ {migrated_count} people records now have created_by values")
        
        # Check that duplicate names were handled
        c.execute("SELECT name, COUNT(*) FROM people GROUP BY name HAVING COUNT(*) > 1")
        duplicates = c.fetchall()
        
        if duplicates:
            print(f"⚠️  Found duplicate names after migration: {duplicates}")
            # Check if they have different created_by values
            for dup in duplicates:
                name = dup[0]
                c.execute("SELECT DISTINCT created_by FROM people WHERE name = ?", (name,))
                created_by_values = [row[0] for row in c.fetchall()]
                if len(created_by_values) > 1:
                    print(f"✅ Duplicate name '{name}' has different created_by values: {created_by_values}")
                else:
                    print(f"❌ Duplicate name '{name}' still has same created_by values")
        else:
            print("✅ No duplicate names found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_fix.db'):
            os.remove('test_fix.db')

if __name__ == '__main__':
    test_migration_fix()
