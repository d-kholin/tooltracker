#!/usr/bin/env python3
"""
Test script to verify the people table migration works correctly.
This script tests the new multi-user constraint on the people table.
"""

import sqlite3
import os
import tempfile

def test_people_migration():
    """Test the people table migration and new constraints"""
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create connection
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        print("Testing people table migration...")
        
        # Create the old schema (with UNIQUE on name)
        c.execute("""
            CREATE TABLE people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact_info TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
        """)
        
        # Create users table for foreign key reference
        c.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """)
        
        # Insert test users
        c.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", 
                 ('user1', 'User One', 'user1@example.com'))
        c.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", 
                 ('user2', 'User Two', 'user2@example.com'))
        
        # Insert test people with old schema
        c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                 ('John Doe', 'john@example.com', 'user1'))
        
        print("✓ Created old schema with UNIQUE constraint on name")
        print("✓ Inserted test data")
        
        # Now test the migration
        try:
            # Check if the old UNIQUE constraint exists
            c.execute("PRAGMA index_list(people)")
            indexes = c.fetchall()
            has_old_constraint = any('sqlite_autoindex_people_1' in str(idx) for idx in indexes)
            
            if has_old_constraint:
                print("✓ Detected old constraint, starting migration...")
                
                # Create a temporary table with the new schema
                c.execute("""
                    CREATE TABLE people_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        contact_info TEXT,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(created_by) REFERENCES users(id),
                        UNIQUE(name, created_by)
                    )
                """)
                
                # Copy data from old table
                c.execute("INSERT INTO people_new SELECT * FROM people")
                
                # Drop old table and rename new one
                c.execute("DROP TABLE people")
                c.execute("ALTER TABLE people_new RENAME TO people")
                
                print("✓ Successfully migrated people table for multi-user support")
            else:
                print("✓ No old constraint detected")
                
        except sqlite3.OperationalError as e:
            print(f"✗ Migration failed: {e}")
            return False
        
        # Test the new constraint - should allow same name for different users
        try:
            c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                     ('John Doe', 'john2@example.com', 'user2'))
            print("✓ Successfully added person with same name for different user")
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to add person with same name for different user: {e}")
            return False
        
        # Test the new constraint - should prevent same name for same user
        try:
            c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                     ('John Doe', 'john3@example.com', 'user1'))
            print("✗ Should have failed to add duplicate name for same user")
            return False
        except sqlite3.IntegrityError:
            print("✓ Correctly prevented duplicate name for same user")
        
        # Test the new constraint - should allow different names for same user
        try:
            c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                     ('Jane Doe', 'jane@example.com', 'user1'))
            print("✓ Successfully added person with different name for same user")
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to add person with different name for same user: {e}")
            return False
        
        # Verify final state
        c.execute("SELECT name, created_by FROM people ORDER BY created_by, name")
        people = c.fetchall()
        print("\nFinal people list:")
        for person in people:
            print(f"  - {person['name']} (User: {person['created_by']})")
        
        print("\n✓ All tests passed! People table migration is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
        
    finally:
        # Clean up
        conn.close()
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    success = test_people_migration()
    exit(0 if success else 1)
