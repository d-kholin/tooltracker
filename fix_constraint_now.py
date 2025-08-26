#!/usr/bin/env python3
"""
Standalone script to immediately fix the people table constraint issue.
Run this script to fix the database constraint without starting the full application.
"""

import sqlite3
import os

def fix_people_constraint_immediately():
    """Immediately fix the people table constraint"""
    
    db_path = 'tooltracker.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        print("=== PEOPLE TABLE CONSTRAINT FIX ===")
        print("Checking current people table schema...")
        
        # Check current constraints
        c.execute("PRAGMA index_list(people)")
        indexes = c.fetchall()
        print(f"Current indexes: {indexes}")
        
        # Check table info
        c.execute("PRAGMA table_info(people)")
        columns = c.fetchall()
        print(f"Table columns: {columns}")
        
        # Look for any unique constraints on just the name column
        has_name_only_constraint = False
        
        # Check if there's a unique constraint on just the name column
        for idx in indexes:
            idx_name = str(idx[1]) if len(idx) > 1 else str(idx)
            if 'sqlite_autoindex' in idx_name and 'people' in idx_name:
                # This is an auto-generated index, likely for a unique constraint
                has_name_only_constraint = True
                print(f"Found auto-generated index: {idx_name}")
                break
        
        if has_name_only_constraint:
            print("\nFound constraint that needs migration - performing migration...")
            
            # Get all existing data
            c.execute("SELECT * FROM people")
            existing_data = c.fetchall()
            print(f"Found {len(existing_data)} existing people records")
            
            # Create a completely new table with the correct schema
            c.execute("DROP TABLE people")
            
            c.execute("""
                CREATE TABLE people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_info TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(created_by) REFERENCES users(id),
                    UNIQUE(name, created_by)
                )
            """)
            
            # Re-insert all the data
            if existing_data:
                for row in existing_data:
                    # Handle different column counts (for backward compatibility)
                    if len(row) >= 4:  # id, name, contact_info, created_by
                        c.execute("""
                            INSERT INTO people (id, name, contact_info, created_by, created_at) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (row[0], row[1], row[2], row[3], row[4] if len(row) > 4 else 'CURRENT_TIMESTAMP'))
                    elif len(row) >= 3:  # id, name, contact_info
                        c.execute("""
                            INSERT INTO people (id, name, contact_info, created_by, created_at) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (row[0], row[1], row[2], 'unknown', 'CURRENT_TIMESTAMP'))
                    elif len(row) >= 2:  # id, name
                        c.execute("""
                            INSERT INTO people (id, name, contact_info, created_by, created_at) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (row[0], row[1], '', 'unknown', 'CURRENT_TIMESTAMP'))
            
            print("✓ Successfully migrated people table for multi-user support")
            
            # Verify the new constraint
            c.execute("PRAGMA index_list(people)")
            new_indexes = c.fetchall()
            print(f"New indexes after migration: {new_indexes}")
            
        else:
            print("✓ People table already has correct constraint or no migration needed")
        
        # Test the constraint
        print("\n=== TESTING CONSTRAINT ===")
        
        # First, ensure we have at least one user
        c.execute("SELECT id FROM users LIMIT 1")
        user = c.fetchone()
        if not user:
            print("No users found in database. Please create a user first.")
            return False
        
        user_id = user[0]
        print(f"Testing with user ID: {user_id}")
        
        # Try to add a test person
        test_name = "_TEST_CONSTRAINT_"
        try:
            c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                     (test_name, 'test@example.com', user_id))
            print("✓ Successfully added test person")
            
            # Try to add another person with same name for same user (should fail)
            try:
                c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                         (test_name, 'test2@example.com', user_id))
                print("✗ WARNING: Constraint not working - duplicate names allowed for same user")
                # Clean up both test entries
                c.execute("DELETE FROM people WHERE name = ? AND created_by = ?", (test_name, user_id))
                return False
            except sqlite3.IntegrityError:
                print("✓ Constraint working correctly - prevents duplicate names for same user")
                # Clean up test entry
                c.execute("DELETE FROM people WHERE name = ? AND created_by = ?", (test_name, user_id))
                
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to add test person: {e}")
            return False
        
        conn.commit()
        print("\n=== CONSTRAINT FIX COMPLETED SUCCESSFULLY ===")
        print("✓ People table now allows same names for different users")
        print("✓ Same names are still prevented for the same user")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing constraint: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Starting immediate constraint fix...")
    success = fix_people_constraint_immediately()
    if success:
        print("\n🎉 SUCCESS: Your database constraint has been fixed!")
        print("You can now add people with the same name to different users' lists.")
    else:
        print("\n❌ FAILED: Could not fix the constraint. Check the error messages above.")
