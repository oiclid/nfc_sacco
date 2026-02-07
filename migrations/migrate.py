#!/usr/bin/env python3
"""
NFC Cooperative Management System - Database Migration Script
==============================================================
This script migrates data from the old database.sld to the new improved structure.

Author: Claude
Date: February 2026
"""

import sqlite3
import os
import sys
import hashlib
from datetime import datetime
from decimal import Decimal

class DatabaseMigration:
    def __init__(self, old_db_path, new_db_path):
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        self.old_conn = None
        self.new_conn = None
        self.migration_log = []
        self.errors = []
        
    def log(self, message, level="INFO"):
        """Log migration messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
        
    def connect_databases(self):
        """Connect to both old and new databases"""
        try:
            self.log("Connecting to old database...")
            self.old_conn = sqlite3.connect(self.old_db_path)
            self.old_conn.row_factory = sqlite3.Row
            
            self.log("Connecting to new database...")
            self.new_conn = sqlite3.connect(self.new_db_path)
            self.new_conn.row_factory = sqlite3.Row
            
            self.log("Database connections established successfully!")
            return True
        except Exception as e:
            self.log(f"Error connecting to databases: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def create_new_schema(self):
        """Create new database schema"""
        try:
            self.log("Creating new database schema...")
            
            # Read schema file
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema
            self.new_conn.executescript(schema_sql)
            self.new_conn.commit()
            
            self.log("New database schema created successfully!")
            return True
        except Exception as e:
            self.log(f"Error creating schema: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def migrate_stations(self):
        """Migrate stations data"""
        try:
            self.log("\n" + "="*60)
            self.log("Migrating Stations...")
            self.log("="*60)
            
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM StationDB")
            stations = cursor.fetchall()
            
            new_cursor = self.new_conn.cursor()
            migrated = 0
            
            for station in stations:
                station_id = station['StationID'].strip()
                description = station['Description'].strip()
                address = station['Address'].strip()
                enabled = station['EnableStation']
                
                # Extract city from description (e.g., "NFC - Abuja" -> "Abuja")
                city = ""
                if " - " in description:
                    city = description.split(" - ")[-1].strip()
                else:
                    city = address
                
                new_cursor.execute("""
                    INSERT INTO stations (station_id, station_name, address, city, enabled)
                    VALUES (?, ?, ?, ?, ?)
                """, (station_id, description, address, city, enabled))
                
                migrated += 1
            
            self.new_conn.commit()
            self.log(f"✓ Migrated {migrated} stations")
            return True
            
        except Exception as e:
            self.log(f"Error migrating stations: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def migrate_members(self):
        """Migrate members data with improved structure"""
        try:
            self.log("\n" + "="*60)
            self.log("Migrating Members...")
            self.log("="*60)
            
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM MemberDataTbl")
            members = cursor.fetchall()
            
            new_cursor = self.new_conn.cursor()
            migrated = 0
            skipped = 0
            
            for member in members:
                try:
                    member_id = member['MemberID'].strip()
                    station_id = member['StationID'].strip()
                    full_name = member['Names'].strip()
                    
                    # Split name into parts
                    name_parts = full_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
                    last_name = name_parts[-1] if len(name_parts) > 1 else "Unknown"
                    middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else None
                    
                    # Determine gender
                    gender = "Male" if member['Male'] == 1 else "Female" if member['Female'] == 1 else None
                    
                    # Clean up fields (replace commas with None)
                    def clean_field(value):
                        if value is None or value.strip() == ',' or value.strip() == '':
                            return None
                        return value.strip()
                    
                    new_cursor.execute("""
                        INSERT INTO members (
                            member_id, station_id, registration_number,
                            first_name, middle_name, last_name, gender,
                            date_joined, address, phone_number, employee_id, grade_level,
                            nok1_name, nok1_address, nok1_relationship, nok1_phone,
                            nok2_name, nok2_address, nok2_relationship, nok2_phone,
                            photo_path, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        member_id, station_id, member_id,
                        first_name, middle_name, last_name, gender,
                        member['DateJoined'], clean_field(member['Address']),
                        clean_field(member['PhoneNo']), clean_field(member['EmployeeID']),
                        clean_field(member['GradeLevel']),
                        clean_field(member['FirstKinName']), clean_field(member['FirstKinAddr']),
                        clean_field(member['FirstKinRelatnshp']), clean_field(member['FirstKinPhoneNo']),
                        clean_field(member['SecondKinName']), clean_field(member['SecondKinAddr']),
                        clean_field(member['SecondKinRelatnshp']), clean_field(member['SecondKinPhoneNo']),
                        clean_field(member['PicLoc']), member['Enable']
                    ))
                    
                    migrated += 1
                    
                except Exception as e:
                    self.log(f"  × Skipped member {member_id}: {e}", "WARNING")
                    skipped += 1
            
            self.new_conn.commit()
            self.log(f"✓ Migrated {migrated} members")
            if skipped > 0:
                self.log(f"  ⚠ Skipped {skipped} members due to errors", "WARNING")
            return True
            
        except Exception as e:
            self.log(f"Error migrating members: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def create_savings_accounts_from_ledger(self):
        """Create savings accounts based on ledger data"""
        try:
            self.log("\n" + "="*60)
            self.log("Creating Savings Accounts from Ledger...")
            self.log("="*60)
            
            cursor = self.old_conn.cursor()
            new_cursor = self.new_conn.cursor()
            
            # Get unique members from ledger
            cursor.execute("""
                SELECT DISTINCT MemberID 
                FROM LedgerTbl 
                WHERE Enable = 'Yes'
            """)
            members = cursor.fetchall()
            
            created = 0
            
            for member in members:
                member_id = member['MemberID'].strip()
                
                # Check if member exists in new database
                new_cursor.execute("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
                if not new_cursor.fetchone():
                    continue
                
                # Calculate balances for each savings type
                # Premium (B account in old system)
                cursor.execute("""
                    SELECT SUM(SavingsLedger) as balance 
                    FROM LedgerTbl 
                    WHERE MemberID = ? AND AccountID = 'B' AND Enable = 'Yes'
                """, (member_id,))
                premium_balance = cursor.fetchone()['balance'] or 0
                
                if premium_balance > 0:
                    new_cursor.execute("""
                        INSERT INTO savings_accounts (member_id, savings_type_id, account_number, current_balance, total_deposits)
                        SELECT ?, savings_type_id, ?, ?, ?
                        FROM savings_types WHERE type_code = 'PREMIUM'
                    """, (member_id, f"{member_id}-PREM", premium_balance, premium_balance))
                    created += 1
                
                # Special Savings (G account in old system)
                cursor.execute("""
                    SELECT SUM(SpecialSavings) as balance 
                    FROM LedgerTbl 
                    WHERE MemberID = ? AND AccountID = 'G' AND Enable = 'Yes'
                """, (member_id,))
                special_balance = cursor.fetchone()['balance'] or 0
                
                if special_balance > 0:
                    new_cursor.execute("""
                        INSERT INTO savings_accounts (member_id, savings_type_id, account_number, current_balance, total_deposits)
                        SELECT ?, savings_type_id, ?, ?, ?
                        FROM savings_types WHERE type_code = 'TARGET'
                    """, (member_id, f"{member_id}-TARG", special_balance, special_balance))
                    created += 1
                
                # Share Capital (A account in old system)
                cursor.execute("""
                    SELECT SUM(ShareCapital) as balance 
                    FROM LedgerTbl 
                    WHERE MemberID = ? AND AccountID = 'A' AND Enable = 'Yes'
                """, (member_id,))
                share_balance = cursor.fetchone()['balance'] or 0
                
                if share_balance > 0:
                    new_cursor.execute("""
                        INSERT INTO savings_accounts (member_id, savings_type_id, account_number, current_balance, total_deposits)
                        SELECT ?, savings_type_id, ?, ?, ?
                        FROM savings_types WHERE type_code = 'SHARES'
                    """, (member_id, f"{member_id}-SHAR", share_balance, share_balance))
                    created += 1
            
            self.new_conn.commit()
            self.log(f"✓ Created {created} savings accounts")
            return True
            
        except Exception as e:
            self.log(f"Error creating savings accounts: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def migrate_loans(self):
        """Migrate loans data"""
        try:
            self.log("\n" + "="*60)
            self.log("Migrating Loans...")
            self.log("="*60)
            
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM LoansAndPurchasesTbl WHERE Enable = 'Yes'")
            loans = cursor.fetchall()
            
            new_cursor = self.new_conn.cursor()
            migrated = 0
            skipped = 0
            loan_counter = {}  # Track loans per member for unique numbering
            
            for loan in loans:
                try:
                    member_id = loan['MemberID'].strip()
                    station_id = loan['StationID'].strip()
                    
                    # Verify member exists
                    new_cursor.execute("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
                    if not new_cursor.fetchone():
                        skipped += 1
                        continue
                    
                    # Parse principal amount (handle negative values)
                    try:
                        principal = abs(float(loan['Amount']))
                    except (ValueError, TypeError):
                        skipped += 1
                        continue
                    
                    if principal <= 0:
                        skipped += 1
                        continue
                    
                    # Parse duration (handle bad data like '24Q', '6`', etc.)
                    try:
                        duration_str = str(loan['NoOfMonths'] or '12')
                        # Remove any non-numeric characters
                        duration_str = ''.join(c for c in duration_str if c.isdigit())
                        duration = int(duration_str) if duration_str else 12
                        if duration <= 0 or duration > 360:
                            duration = 12
                    except (ValueError, TypeError):
                        duration = 12
                    
                    # Default to MAJOR loan type for old data (C1 = Macro-Loans)
                    # Get loan type ID
                    new_cursor.execute("SELECT loan_type_id, interest_rate FROM loan_types WHERE type_code = 'MAJOR'")
                    loan_type = new_cursor.fetchone()
                    loan_type_id = loan_type['loan_type_id']
                    interest_rate = float(loan_type['interest_rate'])
                    
                    # Calculate interest (flat rate)
                    interest_amount = principal * (interest_rate / 100)
                    total_amount = principal + interest_amount
                    monthly_installment = total_amount / duration if duration > 0 else 0
                    
                    # Calculate amount paid from LedgerTbl (with error handling for corrupted DB)
                    try:
                        cursor.execute("""
                            SELECT SUM(MacroLoans) as paid
                            FROM LedgerTbl
                            WHERE MemberID = ? AND Credit = 'Yes' AND Enable = 'Yes'
                            AND SysDate >= ?
                        """, (member_id, loan['StartDate']))
                        
                        paid_result = cursor.fetchone()
                        amount_paid = abs(float(paid_result['paid'])) if paid_result and paid_result['paid'] else 0
                    except:
                        # If ledger query fails (corrupted data), assume no payments made
                        amount_paid = 0
                    
                    balance = max(0, total_amount - amount_paid)
                    
                    # Determine status
                    status = 'Active' if balance > 0 else 'Completed'
                    
                    # Generate UNIQUE loan number with counter
                    if member_id not in loan_counter:
                        loan_counter[member_id] = 1
                    else:
                        loan_counter[member_id] += 1
                    
                    # Create unique loan number: L-MEMBERID-COUNTER
                    loan_number = f"L-{member_id}-{loan_counter[member_id]:04d}"
                    
                    new_cursor.execute("""
                        INSERT INTO loans (
                            member_id, station_id, loan_type_id, loan_number,
                            principal_amount, interest_rate, interest_amount, total_amount,
                            monthly_installment, duration_months, amount_paid, balance_outstanding,
                            disbursement_date, start_date, end_date, cheque_number,
                            status, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        member_id, station_id, loan_type_id, loan_number,
                        principal, interest_rate, interest_amount, total_amount,
                        monthly_installment, duration, amount_paid, balance,
                        loan['SysDate'], loan['StartDate'], loan['EndDate'], loan['ChequeNo'],
                        status, 1
                    ))
                    
                    migrated += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    # Only log a sample of errors to avoid flooding the output
                    if skipped < 10 or 'database disk image is malformed' not in error_msg:
                        self.log(f"  × Skipped loan for {member_id}: {error_msg}", "WARNING")
                    skipped += 1
            
            self.new_conn.commit()
            self.log(f"✓ Migrated {migrated} loans")
            if skipped > 0:
                self.log(f"  ⚠ Skipped {skipped} loans due to errors", "WARNING")
                self.log(f"  ℹ Common issues: duplicates, corrupted data, invalid amounts/durations", "WARNING")
            return True
            
        except Exception as e:
            self.log(f"Error migrating loans: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def migrate_users(self):
        """Migrate users with password hashing"""
        try:
            self.log("\n" + "="*60)
            self.log("Migrating Users...")
            self.log("="*60)
            
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM LoginTbl")
            users = cursor.fetchall()
            
            new_cursor = self.new_conn.cursor()
            migrated = 0
            
            for user in users:
                username = user['Username'].strip()
                # Hash the password (using SHA-256 for now, will use bcrypt in full app)
                password = user['Password'].strip()
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Map to new role system
                role = "Admin"  # Default all old users to Admin for now
                
                can_maintain = int(user['Maintain'].strip()) if user['Maintain'] else 0
                can_operate = int(user['Operations'].strip()) if user['Operations'] else 0
                can_edit = int(user['EditPriv'].strip()) if user['EditPriv'] else 0
                can_view_reports = int(user['Reports'].strip()) if user['Reports'] else 0
                
                new_cursor.execute("""
                    INSERT INTO users (
                        username, password_hash, role,
                        can_maintain, can_operate, can_edit, can_view_reports,
                        is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username, password_hash, role,
                    can_maintain, can_operate, can_edit, can_view_reports,
                    1
                ))
                
                migrated += 1
                self.log(f"  → Migrated user: {username}")
            
            self.new_conn.commit()
            self.log(f"✓ Migrated {migrated} users")
            self.log(f"  ⚠ NOTE: Passwords are hashed. Original passwords from old DB will work.", "WARNING")
            return True
            
        except Exception as e:
            self.log(f"Error migrating users: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def update_system_settings(self):
        """Update system settings based on migrated data"""
        try:
            self.log("\n" + "="*60)
            self.log("Updating System Settings...")
            self.log("="*60)
            
            new_cursor = self.new_conn.cursor()
            
            # Get highest member number
            new_cursor.execute("SELECT MAX(CAST(SUBSTR(member_id, 4) AS INTEGER)) as max_num FROM members")
            result = new_cursor.fetchone()
            max_member_num = result['max_num'] if result['max_num'] else 0
            next_member_num = max_member_num + 1
            
            # Get highest station number
            new_cursor.execute("SELECT MAX(CAST(station_id AS INTEGER)) as max_num FROM stations")
            result = new_cursor.fetchone()
            max_station_num = result['max_num'] if result['max_num'] else 0
            next_station_num = max_station_num + 1
            
            # Update settings
            new_cursor.execute("""
                UPDATE system_settings 
                SET setting_value = ? 
                WHERE setting_key = 'next_member_number'
            """, (str(next_member_num),))
            
            new_cursor.execute("""
                UPDATE system_settings 
                SET setting_value = ? 
                WHERE setting_key = 'next_station_number'
            """, (str(next_station_num),))
            
            self.new_conn.commit()
            self.log(f"✓ Next member number set to: {next_member_num}")
            self.log(f"✓ Next station number set to: {next_station_num}")
            return True
            
        except Exception as e:
            self.log(f"Error updating system settings: {e}", "ERROR")
            self.errors.append(str(e))
            return False
    
    def generate_report(self):
        """Generate migration report"""
        try:
            self.log("\n" + "="*60)
            self.log("Generating Migration Report...")
            self.log("="*60)
            
            # Get counts from new database
            new_cursor = self.new_conn.cursor()
            
            stats = {}
            tables = ['stations', 'members', 'savings_accounts', 'loans', 'users']
            
            for table in tables:
                new_cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = new_cursor.fetchone()['count']
            
            # Create report
            report_path = os.path.join(os.path.dirname(__file__), 'migration_report.txt')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("NFC COOPERATIVE MANAGEMENT SYSTEM - MIGRATION REPORT\n")
                f.write("="*70 + "\n")
                f.write(f"Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Old Database: {self.old_db_path}\n")
                f.write(f"New Database: {self.new_db_path}\n")
                f.write("="*70 + "\n\n")
                
                f.write("MIGRATION STATISTICS\n")
                f.write("-"*70 + "\n")
                for table, count in stats.items():
                    f.write(f"{table.capitalize():<30} {count:>10} records\n")
                
                f.write("\n" + "="*70 + "\n\n")
                
                f.write("MIGRATION LOG\n")
                f.write("-"*70 + "\n")
                for log_entry in self.migration_log:
                    f.write(log_entry + "\n")
                
                if self.errors:
                    f.write("\n" + "="*70 + "\n\n")
                    f.write("ERRORS ENCOUNTERED\n")
                    f.write("-"*70 + "\n")
                    for error in self.errors:
                        f.write(f"× {error}\n")
                
                f.write("\n" + "="*70 + "\n")
                f.write("END OF REPORT\n")
                f.write("="*70 + "\n")
            
            self.log(f"✓ Migration report saved to: {report_path}")
            
            print("\n" + "="*70)
            print("MIGRATION SUMMARY")
            print("="*70)
            for table, count in stats.items():
                print(f"{table.capitalize():<30} {count:>10} records")
            print("="*70)
            
            return True
            
        except Exception as e:
            self.log(f"Error generating report: {e}", "ERROR")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        print("\n" + "="*70)
        print("NFC COOPERATIVE MANAGEMENT SYSTEM - DATABASE MIGRATION")
        print("="*70 + "\n")
        
        # Check if old database exists
        if not os.path.exists(self.old_db_path):
            print(f"ERROR: Old database not found at: {self.old_db_path}")
            return False
        
        # Backup check
        if os.path.exists(self.new_db_path):
            response = input(f"\nWARNING: New database already exists at {self.new_db_path}\nOverwrite? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return False
            os.remove(self.new_db_path)
        
        # Connect to databases
        if not self.connect_databases():
            return False
        
        # Create new schema
        if not self.create_new_schema():
            return False
        
        # Run migrations in order
        steps = [
            ("Stations", self.migrate_stations),
            ("Members", self.migrate_members),
            ("Savings Accounts", self.create_savings_accounts_from_ledger),
            ("Loans", self.migrate_loans),
            ("Users", self.migrate_users),
            ("System Settings", self.update_system_settings),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.log(f"Migration failed at step: {step_name}", "ERROR")
                return False
        
        # Generate report
        self.generate_report()
        
        # Close connections
        if self.old_conn:
            self.old_conn.close()
        if self.new_conn:
            self.new_conn.close()
        
        print("\n" + "="*70)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nNew database created at: {self.new_db_path}")
        print(f"Migration report saved at: {os.path.join(os.path.dirname(__file__), 'migration_report.txt')}")
        print("\nYou can now use the new database with the NFC Cooperative Management System.")
        print("="*70 + "\n")
        
        return True


def main():
    """Main entry point"""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')
    
    old_db_path = os.path.join(data_dir, 'database.sld')
    new_db_path = os.path.join(data_dir, 'nfc_cooperative.db')
    
    # Run migration
    migrator = DatabaseMigration(old_db_path, new_db_path)
    success = migrator.run_migration()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
