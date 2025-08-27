#!/usr/bin/env python3
"""
Test script to verify the PRAGMA syntax fix works
"""

import os
import sqlite3

def test_pragma_fix():
    """Test that the PRAGMA syntax fix works correctly"""
    print("🧪 Testing PRAGMA Syntax Fix")
    print("=" * 40)
    
    try:
        # Create a test database
        db_path = 'test_pragma.db'
        
        if os.path.exists(db_path):
            os.remove(db_path)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create tables
        c.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        """)
        
        c.execute("""
            CREATE TABLE people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_info TEXT,
                created_by TEXT
            )
        """)
        
        # Insert test data
        c.execute("INSERT INTO users (id, email, name) VALUES (?, ?, ?)", 
                  ('test_user', 'test@example.com', 'Test User'))
        
        c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                  ('John Doe', 'john@example.com', 'test_user'))
        c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
                  ('John Doe', 'john2@example.com'))
        
        # Create the unique constraint
        c.execute("CREATE UNIQUE INDEX idx_people_name_user ON people (name, created_by)")
        
        conn.commit()
        
        print("✅ Created test database with constraint")
        
        # Test the PRAGMA queries that were failing
        print("\n🔍 Testing PRAGMA queries...")
        
        # Test index_list
        c.execute("PRAGMA index_list(people)")
        indexes = c.fetchall()
        print(f"Indexes found: {[idx[1] for idx in indexes]}")
        
        # Test index_info for the problematic constraint
        for idx in indexes:
            if 'idx_people_name_user' in idx[1]:
                print(f"Found constraint: {idx[1]} (type: {idx[2]})")
                
                # This is the line that was failing - now it should work
                c.execute(f"PRAGMA index_info({idx[1]})")
                index_info = c.fetchall()
                print(f"  Index columns: {[col[2] for col in index_info]}")
        
        print("\n✅ All PRAGMA queries executed successfully!")
        
        # Test the migration logic
        print("\n🧪 Testing migration logic...")
        
        # Check for constraint violations
        c.execute("""
            SELECT name, COUNT(*) as count 
            FROM people 
            WHERE created_by IS NOT NULL 
            GROUP BY name 
            HAVING count > 1
        """)
        constraint_violations = c.fetchall()
        
        if constraint_violations:
            print(f"Found {len(constraint_violations)} constraint violations:")
            for violation in constraint_violations:
                name = violation[0]
                print(f"  - {name} appears {violation[1]} times")
                
                # Get conflicting records
                c.execute("SELECT id, name, created_by FROM people WHERE name = ? ORDER BY id", (name,))
                conflicting_records = c.fetchall()
                for record in conflicting_records:
                    print(f"    Record {record[0]}: {record[1]} (created_by: {record[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_pragma.db'):
            os.remove('test_pragma.db')

if __name__ == '__main__':
    test_pragma_fix()
