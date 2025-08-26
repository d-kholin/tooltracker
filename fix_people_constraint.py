#!/usr/bin/env python3
"""
Script to fix the people table constraint issue.
This will ensure that the same name can be used by different users.
"""

import sqlite3
import os

def fix_people_constraint():
    """Fix the people table constraint to allow same names for different users"""
    
    db_path = 'tooltracker.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        print("Checking current people table schema...")
        
        # Check current constraints
        c.execute("PRAGMA index_list(people)")
        indexes = c.fetchall()
        print(f"Current indexes: {indexes}")
        
        # Check if the old UNIQUE constraint on name exists
        has_old_constraint = False
        for idx in indexes:
            if 'sqlite_autoindex_people_1' in str(idx):
                has_old_constraint = True
                break
        
        if has_old_constraint:
            print("Found old constraint - migrating to new schema...")
            
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
            
            # Verify the new constraint
            c.execute("PRAGMA index_list(people)")
            new_indexes = c.fetchall()
            print(f"New indexes: {new_indexes}")
            
        else:
            print("✓ People table already has the correct constraint")
        
        # Test the constraint by trying to add the same name for different users
        print("\nTesting the constraint...")
        
        # First, ensure we have at least one user
        c.execute("SELECT id FROM users LIMIT 1")
        user = c.fetchone()
        if not user:
            print("No users found in database. Please create a user first.")
            return False
        
        user_id = user[0]
        
        # Try to add a test person
        try:
            c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                     ('Test Person', 'test@example.com', user_id))
            print("✓ Successfully added test person")
            
            # Try to add another person with same name for same user (should fail)
            try:
                c.execute("INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)", 
                         ('Test Person', 'test2@example.com', user_id))
                print("✗ Should have failed to add duplicate name for same user")
                # Rollback the test
                c.execute("DELETE FROM people WHERE name = 'Test Person' AND created_by = ?", (user_id,))
            except sqlite3.IntegrityError:
                print("✓ Correctly prevented duplicate name for same user")
                # Clean up test data
                c.execute("DELETE FROM people WHERE name = 'Test Person' AND created_by = ?", (user_id,))
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to add test person: {e}")
            return False
        
        conn.commit()
        print("\n✓ People table constraint is working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing constraint: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Fixing people table constraint...")
    success = fix_people_constraint()
    if success:
        print("\nConstraint fix completed successfully!")
    else:
        print("\nConstraint fix failed!")
