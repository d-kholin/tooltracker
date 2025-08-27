#!/usr/bin/env python3
"""
Test script to verify database migration functionality
"""

import os
import sqlite3
import tempfile
import shutil
from unittest.mock import patch

# Mock the Flask app context
class MockApp:
    def __init__(self):
        self.config = {
            'TOOLTRACKER_DB': 'test_tooltracker.db',
            'UPLOAD_FOLDER': 'test_uploads'
        }
    
    def app_context(self):
        return MockAppContext()

class MockAppContext:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Import the functions we want to test
import sys
sys.path.insert(0, '.')

# Mock the current_app for auth functions
from unittest.mock import patch
import auth
import app

def create_test_database():
    """Create a test database with old schema"""
    db_path = 'test_tooltracker.db'
    
    # Remove existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create old schema (without created_by columns)
    c.execute("""
        CREATE TABLE tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            value REAL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            lent_on TEXT NOT NULL,
            returned_on TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tool_id) REFERENCES tools(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        )
    """)
    
    # Create users table
    c.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    c.execute("INSERT INTO users (id, email, name) VALUES (?, ?, ?)", 
              ('test_user_1', 'user1@test.com', 'Test User 1'))
    c.execute("INSERT INTO users (id, email, name) VALUES (?, ?, ?)", 
              ('test_user_2', 'user2@test.com', 'Test User 2'))
    
    # Insert test tools
    c.execute("INSERT INTO tools (name, description, value) VALUES (?, ?, ?)", 
              ('Hammer', 'Basic hammer', 25.0))
    c.execute("INSERT INTO tools (name, description, value) VALUES (?, ?, ?)", 
              ('Screwdriver', 'Phillips head', 15.0))
    
    # Insert test people (with potential duplicates)
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('John Doe', 'john@test.com'))
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('John Doe', 'john2@test.com'))  # Duplicate name
    c.execute("INSERT INTO people (name, contact_info) VALUES (?, ?)", 
              ('Jane Smith', 'jane@test.com'))
    
    # Insert test loans
    c.execute("INSERT INTO loans (tool_id, person_id, lent_on) VALUES (?, ?, ?)", 
              (1, 1, '2024-01-01'))
    
    conn.commit()
    conn.close()
    
    print("✅ Test database created with old schema")
    return db_path

def verify_migration_results():
    """Verify that the migration worked correctly"""
    db_path = 'test_tooltracker.db'
    
    if not os.path.exists(db_path):
        print("❌ Test database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if created_by columns were added
    c.execute("PRAGMA table_info(tools)")
    tools_columns = [col[1] for col in c.fetchall()]
    
    c.execute("PRAGMA table_info(people)")
    people_columns = [col[1] for col in c.fetchall()]
    
    c.execute("PRAGMA table_info(loans)")
    loans_columns = [col[1] for col in c.fetchall()]
    
    # Check for required columns
    required_tools_columns = ['id', 'name', 'description', 'value', 'image_path', 'created_by', 'created_at']
    required_people_columns = ['id', 'name', 'contact_info', 'created_by', 'created_at']
    required_loans_columns = ['id', 'tool_id', 'person_id', 'lent_on', 'returned_on', 'lent_by', 'created_at']
    
    tools_missing = set(required_tools_columns) - set(tools_columns)
    people_missing = set(required_people_columns) - set(people_columns)
    loans_missing = set(required_loans_columns) - set(loans_columns)
    
    if tools_missing:
        print(f"❌ Tools table missing columns: {tools_missing}")
        return False
    else:
        print("✅ Tools table has all required columns")
    
    if people_missing:
        print(f"❌ People table missing columns: {people_missing}")
        return False
    else:
        print("✅ People table has all required columns")
    
    if loans_missing:
        print(f"❌ Loans table missing columns: {loans_missing}")
        return False
    else:
        print("✅ Loans table has all required columns")
    
    # Check if created_by values were populated
    c.execute("SELECT COUNT(*) FROM tools WHERE created_by IS NOT NULL")
    tools_with_created_by = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM people WHERE created_by IS NOT NULL")
    people_with_created_by = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM loans WHERE lent_by IS NOT NULL")
    loans_with_lent_by = c.fetchone()[0]
    
    print(f"✅ Tools with created_by: {tools_with_created_by}")
    print(f"✅ People with created_by: {people_with_created_by}")
    print(f"✅ Loans with lent_by: {loans_with_created_by}")
    
    # Check if duplicate names were handled
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
    
    # Check if unique constraints were created
    c.execute("PRAGMA index_list(people)")
    indexes = [idx[1] for idx in c.fetchall()]
    
    if 'idx_people_name_user' in indexes:
        print("✅ Composite unique constraint created successfully")
    else:
        print("⚠️  Composite unique constraint not found")
    
    conn.close()
    return True

def test_migration():
    """Test the complete migration process"""
    print("🧪 Testing Database Migration")
    print("=" * 50)
    
    try:
        # Create test database
        db_path = create_test_database()
        
        # Mock the app context and run migration
        with patch('app.current_app', MockApp()):
            # Initialize the database
            app.init_db()
            
            # Run the migration
            app.migrate_existing_database()
        
        print("\n🔍 Verifying Migration Results")
        print("-" * 30)
        
        # Verify the results
        success = verify_migration_results()
        
        if success:
            print("\n🎉 Migration test completed successfully!")
        else:
            print("\n❌ Migration test failed!")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Migration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_tooltracker.db'):
            os.remove('test_tooltracker.db')
        if os.path.exists('test_uploads'):
            shutil.rmtree('test_uploads', ignore_errors=True)

if __name__ == '__main__':
    test_migration()
