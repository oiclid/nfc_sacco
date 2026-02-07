#!/usr/bin/env python3
"""
Test Script - Verify Database Migration
========================================
This script tests the migration without running it fully.
It verifies the schema and shows what would be migrated.
"""

import sqlite3
import os

def test_database():
    print("="*70)
    print("NFC COOPERATIVE SYSTEM - DATABASE TEST")
    print("="*70 + "\n")
    
    # Paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, 'data')
    old_db = os.path.join(data_dir, 'database.sld')
    
    if not os.path.exists(old_db):
        print("❌ ERROR: database.sld not found in data/ folder")
        print(f"   Expected location: {old_db}")
        print("\nPlease copy your database.sld file to the data/ folder.")
        return False
    
    print("✓ Found database.sld")
    print(f"  Location: {old_db}")
    print(f"  Size: {os.path.getsize(old_db) / (1024*1024):.2f} MB\n")
    
    # Connect and check tables
    try:
        conn = sqlite3.connect(old_db)
        cursor = conn.cursor()
        
        # Get table counts
        print("-"*70)
        print("DATA SUMMARY (Old Database)")
        print("-"*70)
        
        tables = {
            'StationDB': 'Stations',
            'MemberDataTbl': 'Members',
            'LoansAndPurchasesTbl': 'Loans',
            'PayOrWithdrawTbl': 'Transactions',
            'LedgerTbl': 'Ledger Entries',
            'LoginTbl': 'Users'
        }
        
        for table, name in tables.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{name:<30} {count:>10} records")
        
        print("-"*70 + "\n")
        
        # Check for newest member
        cursor.execute("SELECT MAX(MemberID) FROM MemberDataTbl")
        max_member = cursor.fetchone()[0]
        print(f"Latest Member ID: {max_member}")
        
        # Extract number
        member_num = int(max_member[3:])  # Remove 'NFC'
        next_num = member_num + 1
        next_id = f"NFC{next_num:04d}"
        print(f"Next Member ID will be: {next_id}\n")
        
        conn.close()
        
        print("="*70)
        print("✓ DATABASE TEST PASSED")
        print("="*70)
        print("\nYour database is ready for migration!")
        print("\nTo migrate, run:")
        print("  python migrations/migrate.py")
        print("\n" + "="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing database: {e}")
        return False

if __name__ == "__main__":
    test_database()
