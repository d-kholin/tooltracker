#!/usr/bin/env python3
"""
Enhanced database migration script that addresses gaps in the current migration
"""

import os
import sqlite3
from datetime import datetime

def enhanced_migrate_database(db_path):
    """
    Enhanced migration that handles all tables and ensures data integrity
    """
    print("🚀 Starting Enhanced Database Migration")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        c = conn.cursor()
        
        # 1. Verify users table exists and has data
        print("\n📋 Step 1: Verifying users table...")
        c.execute("PRAGMA table_info(users)")
        users_table_info = c.fetchall()
        
        if not users_table_info:
            print("❌ Users table doesn't exist - cannot proceed with migration")
            return False
        
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        print(f"✅ Found {user_count} users in the system")
        
        if user_count == 0:
            print("❌ No users found - cannot assign orphaned records")
            return False
        
        # Get default user for orphaned records
        c.execute("SELECT id FROM users ORDER BY created_at LIMIT 1")
        default_user = c.fetchone()
        default_user_id = default_user['id']
        print(f"📌 Using default user: {default_user_id}")
        
        # 2. Migrate tools table
        print("\n🔧 Step 2: Migrating tools table...")
        migrate_tools_table(c, default_user_id)
        
        # 3. Migrate people table
        print("\n👥 Step 3: Migrating people table...")
        migrate_people_table(c, default_user_id)
        
        # 4. Migrate loans table
        print("\n📦 Step 4: Migrating loans table...")
        migrate_loans_table(c, default_user_id)
        
        # 5. Verify foreign key integrity
        print("\n🔍 Step 5: Verifying foreign key integrity...")
        verify_foreign_keys(c)
        
        # 6. Create indexes and constraints
        print("\n📊 Step 6: Creating indexes and constraints...")
        create_indexes_and_constraints(c)
        
        conn.commit()
        print("\n🎉 Enhanced migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def migrate_tools_table(cursor, default_user_id):
    """Migrate tools table to add created_by column"""
    # Check if created_by column exists
    cursor.execute("PRAGMA table_info(tools)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'created_by' not in columns:
        print("  ➕ Adding created_by column to tools table...")
        cursor.execute("ALTER TABLE tools ADD COLUMN created_by TEXT")
    
    # Update orphaned tools
    cursor.execute("SELECT COUNT(*) FROM tools WHERE created_by IS NULL")
    orphaned_count = cursor.fetchone()[0]
    
    if orphaned_count > 0:
        print(f"  🔄 Assigning {orphaned_count} orphaned tools to default user...")
        cursor.execute("UPDATE tools SET created_by = ? WHERE created_by IS NULL", (default_user_id,))
    
    # Verify migration
    cursor.execute("SELECT COUNT(*) FROM tools WHERE created_by IS NOT NULL")
    migrated_count = cursor.fetchone()[0]
    print(f"  ✅ {migrated_count} tools now have created_by values")

def migrate_people_table(cursor, default_user_id):
    """Migrate people table to add created_by column and handle duplicates"""
    # Check if created_by column exists
    cursor.execute("PRAGMA table_info(people)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'created_by' not in columns:
        print("  ➕ Adding created_by column to people table...")
        cursor.execute("ALTER TABLE people ADD COLUMN created_by TEXT")
    
    # Check for duplicate names that would violate constraints
    cursor.execute("""
        SELECT name, COUNT(*) as count 
        FROM people 
        WHERE created_by IS NULL 
        GROUP BY name 
        HAVING count > 1
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"  🔄 Handling {len(duplicates)} duplicate names...")
        
        for dup in duplicates:
            name = dup['name']
            count = dup['count']
            
            # Get all records with this name
            cursor.execute("""
                SELECT id FROM people 
                WHERE name = ? AND created_by IS NULL 
                ORDER BY id
            """, (name,))
            duplicate_records = cursor.fetchall()
            
            # Assign first record to default user, make others unique
            for i, record in enumerate(duplicate_records):
                if i == 0:
                    # First record gets the original name
                    cursor.execute("""
                        UPDATE people 
                        SET created_by = ? 
                        WHERE id = ?
                    """, (default_user_id, record['id']))
                else:
                    # Subsequent records get a unique name
                    unique_name = f"{name}_{i+1}"
                    cursor.execute("""
                        UPDATE people 
                        SET name = ?, created_by = ? 
                        WHERE id = ?
                    """, (unique_name, default_user_id, record['id']))
                    print(f"    📝 Renamed duplicate to: {unique_name}")
    
    # Update remaining orphaned records
    cursor.execute("SELECT COUNT(*) FROM people WHERE created_by IS NULL")
    remaining_count = cursor.fetchone()[0]
    
    if remaining_count > 0:
        print(f"  🔄 Assigning {remaining_count} remaining people to default user...")
        cursor.execute("UPDATE people SET created_by = ? WHERE created_by IS NULL", (default_user_id,))
    
    # Verify migration
    cursor.execute("SELECT COUNT(*) FROM people WHERE created_by IS NOT NULL")
    migrated_count = cursor.fetchone()[0]
    print(f"  ✅ {migrated_count} people now have created_by values")

def migrate_loans_table(cursor, default_user_id):
    """Migrate loans table to add lent_by column"""
    # Check if lent_by column exists
    cursor.execute("PRAGMA table_info(loans)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'lent_by' not in columns:
        print("  ➕ Adding lent_by column to loans table...")
        cursor.execute("ALTER TABLE loans ADD COLUMN lent_by TEXT")
    
    # Update orphaned loans
    cursor.execute("SELECT COUNT(*) FROM loans WHERE lent_by IS NULL")
    orphaned_count = cursor.fetchone()[0]
    
    if orphaned_count > 0:
        print(f"  🔄 Assigning {orphaned_count} orphaned loans to default user...")
        cursor.execute("UPDATE loans SET lent_by = ? WHERE lent_by IS NULL", (default_user_id,))
    
    # Verify migration
    cursor.execute("SELECT COUNT(*) FROM loans WHERE lent_by IS NOT NULL")
    migrated_count = cursor.fetchone()[0]
    print(f"  ✅ {migrated_count} loans now have lent_by values")

def verify_foreign_keys(cursor):
    """Verify that all foreign key references are valid"""
    print("  🔍 Checking foreign key integrity...")
    
    # Check tools.created_by references
    cursor.execute("""
        SELECT COUNT(*) FROM tools t
        LEFT JOIN users u ON t.created_by = u.id
        WHERE t.created_by IS NOT NULL AND u.id IS NULL
    """)
    broken_tools = cursor.fetchone()[0]
    
    # Check people.created_by references
    cursor.execute("""
        SELECT COUNT(*) FROM people p
        LEFT JOIN users u ON p.created_by = u.id
        WHERE p.created_by IS NOT NULL AND u.id IS NULL
    """)
    broken_people = cursor.fetchone()[0]
    
    # Check loans.lent_by references
    cursor.execute("""
        SELECT COUNT(*) FROM loans l
        LEFT JOIN users u ON l.lent_by = u.id
        WHERE l.lent_by IS NOT NULL AND u.id IS NULL
    """)
    broken_loans = cursor.fetchone()[0]
    
    if broken_tools == 0 and broken_people == 0 and broken_loans == 0:
        print("  ✅ All foreign key references are valid")
    else:
        print(f"  ⚠️  Found broken foreign key references:")
        print(f"     - Tools: {broken_tools}")
        print(f"     - People: {broken_people}")
        print(f"     - Loans: {broken_loans}")

def create_indexes_and_constraints(cursor):
    """Create necessary indexes and constraints"""
    print("  📊 Creating indexes and constraints...")
    
    # Create composite unique constraint for people (name + created_by)
    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_people_name_user 
            ON people (name, created_by)
        """)
        print("    ✅ Created composite unique constraint on people (name, created_by)")
    except sqlite3.OperationalError as e:
        print(f"    ⚠️  Could not create people constraint: {e}")
    
    # Create index on tools.created_by for performance
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tools_created_by 
            ON tools (created_by)
        """)
        print("    ✅ Created index on tools.created_by")
    except sqlite3.OperationalError as e:
        print(f"    ⚠️  Could not create tools index: {e}")
    
    # Create index on loans.lent_by for performance
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_loans_lent_by 
            ON loans (lent_by)
        """)
        print("    ✅ Created index on loans.lent_by")
    except sqlite3.OperationalError as e:
        print(f"    ⚠️  Could not create loans index: {e}")

def print_migration_summary(db_path):
    """Print a summary of the database after migration"""
    print("\n📊 Migration Summary")
    print("=" * 30)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        c = conn.cursor()
        
        # Count records in each table
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM tools")
        tool_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM people")
        people_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM loans")
        loan_count = c.fetchone()[0]
        
        print(f"👥 Users: {user_count}")
        print(f"🔧 Tools: {tool_count}")
        print(f"👤 People: {people_count}")
        print(f"📦 Loans: {loan_count}")
        
        # Check column status
        print("\n📋 Column Status:")
        
        for table in ['tools', 'people', 'loans']:
            c.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in c.fetchall()]
            
            if table == 'tools':
                has_created_by = 'created_by' in columns
                print(f"  {table}: created_by {'✅' if has_created_by else '❌'}")
            elif table == 'people':
                has_created_by = 'created_by' in columns
                print(f"  {table}: created_by {'✅' if has_created_by else '❌'}")
            elif table == 'loans':
                has_lent_by = 'lent_by' in columns
                print(f"  {table}: lent_by {'✅' if has_lent_by else '❌'}")
        
    finally:
        conn.close()

if __name__ == '__main__':
    # Test with the default database path
    db_path = 'tooltracker.db'
    
    if os.path.exists(db_path):
        success = enhanced_migrate_database(db_path)
        if success:
            print_migration_summary(db_path)
    else:
        print(f"Database {db_path} not found. Please run the application first to create it.")
