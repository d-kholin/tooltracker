#!/usr/bin/env python3
"""
Test script to verify the constraint violation fix
"""

import os
import sqlite3

def create_problematic_db():
    """Create a database with the exact problematic scenario from the logs"""
    db_path = 'test_constraint.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
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
    
    # Insert test user (using the ID from the logs)
    c.execute("INSERT INTO users (id, email, name) VALUES (?, ?, ?)", 
              ('02d7ee3bf13d2890199ce9294e15bed882f9962557869f1e6657babb2cee01b2', 
               'test@example.com', 'Test User'))
    
    # Insert test people - this creates the problematic scenario
    c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
              ('John Doe', 'john@example.com', '02d7ee3bf13d2890199ce9294e15bed882f9962557869f1e6657babb2cee01b2'))
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('John Doe', 'john2@example.com'))  # This will cause the constraint violation
    
    # Create the unique constraint
    c.execute("CREATE UNIQUE INDEX idx_people_name_user ON people (name, created_by)")
    
    conn.commit()
    conn.close()
    
    print("✅ Created test database with problematic scenario")
    return db_path

def test_fix():
    """Test the constraint violation fix"""
    print("🧪 Testing Constraint Violation Fix")
    print("=" * 50)
    
    try:
        # Create test database
        db_path = create_problematic_db()
        
        # Import and run the fixed migration
        import sys
        sys.path.insert(0, '.')
        
        # Mock the app context
        import app
        
        # Set the database path
        app.app.config['TOOLTRACKER_DB'] = db_path
        
        # Run the migration
        with app.app.app_context():
            app.migrate_existing_database()
        
        print("\n✅ Migration completed successfully!")
        
        # Verify the results
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check final state
        c.execute("SELECT name, created_by FROM people ORDER BY name")
        final_state = c.fetchall()
        
        print("\n📊 Final database state:")
        for row in final_state:
            print(f"  - {row[0]} (created_by: {row[1]})")
        
        # Verify no constraint violations
        c.execute("SELECT name, COUNT(*) FROM people GROUP BY name HAVING COUNT(*) > 1")
        duplicates = c.fetchall()
        
        if duplicates:
            print(f"\n⚠️  Still have duplicates: {duplicates}")
            return False
        else:
            print("\n✅ No duplicate names found - constraint satisfied!")
            return True
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_constraint.db'):
            os.remove('test_constraint.db')

if __name__ == '__main__':
    test_fix()
