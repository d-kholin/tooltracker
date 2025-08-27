#!/usr/bin/env python3
"""
Migration script to add new fields to the tools table.
Run this script to add brand, model_number, and serial_number columns to existing databases.
"""

import sqlite3
import os
import sys

def get_db_path():
    """Get the database path from environment or use default"""
    db_path = os.environ.get('TOOLTRACKER_DB', 'tooltracker.db')
    return db_path

def migrate_tools_table(db_path):
    """Migrate existing tools table to include new fields"""
    try:
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            print("Please make sure you're running this script from the correct directory")
            return False
        
        print(f"🔧 Migrating database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check if new columns already exist
        c.execute("PRAGMA table_info(tools)")
        columns = [col[1] for col in c.fetchall()]
        
        print(f"Current columns: {', '.join(columns)}")
        
        migrations_applied = []
        
        # Add brand column if it doesn't exist
        if 'brand' not in columns:
            try:
                c.execute("ALTER TABLE tools ADD COLUMN brand TEXT")
                migrations_applied.append("brand")
                print("✓ Added brand column to tools table")
            except sqlite3.OperationalError as e:
                print(f"❌ Error adding brand column: {e}")
        
        # Add model_number column if it doesn't exist
        if 'model_number' not in columns:
            try:
                c.execute("ALTER TABLE tools ADD COLUMN model_number TEXT")
                migrations_applied.append("model_number")
                print("✓ Added model_number column to tools table")
            except sqlite3.OperationalError as e:
                print(f"❌ Error adding model_number column: {e}")
        
        # Add serial_number column if it doesn't exist
        if 'serial_number' not in columns:
            try:
                c.execute("ALTER TABLE tools ADD COLUMN serial_number TEXT")
                migrations_applied.append("serial_number")
                print("✓ Added serial_number column to tools table")
            except sqlite3.OperationalError as e:
                print(f"❌ Error adding serial_number column: {e}")
        
        if migrations_applied:
            conn.commit()
            print(f"✅ Migration completed successfully!")
            print(f"Added columns: {', '.join(migrations_applied)}")
            print("\nYou can now use the new fields in the Tool Tracker application.")
        else:
            print("✅ No migration needed - all columns already exist")
            
        conn.close()
        return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🛠️  Tool Tracker Database Migration")
    print("=" * 40)
    
    db_path = get_db_path()
    
    # Confirm before proceeding
    print(f"This will add new columns to your tools table in: {db_path}")
    response = input("Do you want to continue? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        return
    
    # Create backup
    backup_path = f"{db_path}.backup"
    try:
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"📋 Created backup: {backup_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
        response = input("Continue without backup? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Migration cancelled.")
            return
    
    # Run migration
    success = migrate_tools_table(db_path)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        if os.path.exists(backup_path):
            print(f"💾 Backup saved as: {backup_path}")
        print("\nYou can now restart your Tool Tracker application to use the new fields.")
    else:
        print("\n❌ Migration failed!")
        if os.path.exists(backup_path):
            print(f"💾 Your original database is backed up as: {backup_path}")
        print("Please check the error messages above and try again.")

if __name__ == '__main__':
    main()
