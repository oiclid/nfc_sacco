"""
Database Manager - Handles all database operations
==================================================
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import hashlib


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        return self.conn.execute(query, params)
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.conn.rollback()
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        """
        user = self.fetchone(query, (username, password_hash))
        
        if user:
            # Update last login
            self.execute(
                "UPDATE users SET last_login = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user['user_id'])
            )
            self.commit()
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    # ========================================================================
    # MEMBERS
    # ========================================================================
    
    def get_all_members(self, active_only: bool = True) -> List[Dict]:
        """Get all members"""
        query = "SELECT * FROM members"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY member_id"
        return self.fetchall(query)
    
    def get_member(self, member_id: str) -> Optional[Dict]:
        """Get member by ID"""
        return self.fetchone("SELECT * FROM members WHERE member_id = ?", (member_id,))
    
    def search_members(self, search_term: str) -> List[Dict]:
        """Search members by name or ID - searches first, middle, last names"""
        query = """
            SELECT * FROM members 
            WHERE (
                member_id LIKE ? 
                OR first_name LIKE ? 
                OR middle_name LIKE ?
                OR last_name LIKE ?
                OR (first_name || ' ' || COALESCE(middle_name, '') || ' ' || last_name) LIKE ?
            )
            ORDER BY member_id
        """
        term = f"%{search_term}%"
        # Search across: member_id, first_name, middle_name, last_name, and full name combined
        return self.fetchall(query, (term, term, term, term, term))
    
    def add_member(self, member_data: Dict, created_by: str) -> str:
        """Add new member"""
        # Get next member ID
        next_num = self.get_next_member_number()
        member_id = f"NFC{next_num:04d}"
        
        query = """
            INSERT INTO members (
                member_id, station_id, registration_number,
                first_name, middle_name, last_name, gender,
                date_of_birth, date_joined, address, phone_number, email,
                employee_id, grade_level,
                nok1_name, nok1_relationship, nok1_address, nok1_phone,
                nok2_name, nok2_relationship, nok2_address, nok2_phone,
                created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.execute(query, (
            member_id, member_data['station_id'], member_id,
            member_data['first_name'], member_data.get('middle_name'),
            member_data['last_name'], member_data['gender'],
            member_data.get('date_of_birth'), member_data['date_joined'],
            member_data.get('address'), member_data.get('phone_number'),
            member_data.get('email'), member_data.get('employee_id'),
            member_data.get('grade_level'),
            member_data.get('nok1_name'), member_data.get('nok1_relationship'),
            member_data.get('nok1_address'), member_data.get('nok1_phone'),
            member_data.get('nok2_name'), member_data.get('nok2_relationship'),
            member_data.get('nok2_address'), member_data.get('nok2_phone'),
            created_by
        ))
        
        # Update next member number
        self.update_setting('next_member_number', str(next_num + 1))
        
        self.commit()
        return member_id
    
    def update_member(self, member_id: str, member_data: Dict, modified_by: str):
        """Update member"""
        query = """
            UPDATE members SET
                station_id = ?, first_name = ?, middle_name = ?, last_name = ?,
                gender = ?, date_of_birth = ?, address = ?, phone_number = ?,
                email = ?, employee_id = ?, grade_level = ?,
                nok1_name = ?, nok1_relationship = ?, nok1_address = ?, nok1_phone = ?,
                nok2_name = ?, nok2_relationship = ?, nok2_address = ?, nok2_phone = ?,
                modified_by = ?
            WHERE member_id = ?
        """
        
        self.execute(query, (
            member_data['station_id'], member_data['first_name'],
            member_data.get('middle_name'), member_data['last_name'],
            member_data['gender'], member_data.get('date_of_birth'),
            member_data.get('address'), member_data.get('phone_number'),
            member_data.get('email'), member_data.get('employee_id'),
            member_data.get('grade_level'),
            member_data.get('nok1_name'), member_data.get('nok1_relationship'),
            member_data.get('nok1_address'), member_data.get('nok1_phone'),
            member_data.get('nok2_name'), member_data.get('nok2_relationship'),
            member_data.get('nok2_address'), member_data.get('nok2_phone'),
            modified_by, member_id
        ))
        self.commit()
    
    def get_member_summary(self, member_id: Optional[str] = None) -> List[Dict]:
        """Get member account summary"""
        query = "SELECT * FROM vw_member_summary"
        if member_id:
            query += " WHERE member_id = ?"
            return self.fetchall(query, (member_id,))
        return self.fetchall(query)
    
    # ========================================================================
    # STATIONS
    # ========================================================================
    
    def get_all_stations(self, enabled_only: bool = True) -> List[Dict]:
        """Get all stations"""
        query = "SELECT * FROM stations"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY station_id"
        return self.fetchall(query)
    
    def add_station(self, city: str) -> str:
        """Add new station"""
        # Get next station ID
        next_num = int(self.get_setting('next_station_number'))
        station_id = f"{next_num:02d}"
        station_name = f"NFC - {city}"
        
        query = """
            INSERT INTO stations (station_id, station_name, address, city, enabled)
            VALUES (?, ?, ?, ?, 1)
        """
        self.execute(query, (station_id, station_name, city, city))
        
        # Update next station number
        self.update_setting('next_station_number', str(next_num + 1))
        
        self.commit()
        return station_id
    
    # ========================================================================
    # SAVINGS
    # ========================================================================
    
    def get_savings_types(self) -> List[Dict]:
        """Get all savings types"""
        return self.fetchall("SELECT * FROM savings_types WHERE is_active = 1")
    
    def get_member_savings_accounts(self, member_id: str) -> List[Dict]:
        """Get member's savings accounts"""
        query = """
            SELECT sa.*, st.type_name, st.type_code, st.interest_rate
            FROM savings_accounts sa
            JOIN savings_types st ON sa.savings_type_id = st.savings_type_id
            WHERE sa.member_id = ? AND sa.is_active = 1
        """
        return self.fetchall(query, (member_id,))
    
    def create_savings_account(self, member_id: str, savings_type_id: int) -> int:
        """Create savings account for member"""
        # Get type code
        stype = self.fetchone(
            "SELECT type_code FROM savings_types WHERE savings_type_id = ?",
            (savings_type_id,)
        )
        
        account_number = f"{member_id}-{stype['type_code'][:4].upper()}"
        
        query = """
            INSERT INTO savings_accounts (member_id, savings_type_id, account_number)
            VALUES (?, ?, ?)
        """
        cursor = self.execute(query, (member_id, savings_type_id, account_number))
        self.commit()
        return cursor.lastrowid
    
    def deposit_to_savings(self, account_id: int, amount: float, 
                          transaction_data: Dict, created_by: str):
        """Deposit to savings account"""
        # Update account balance
        query = """
            UPDATE savings_accounts 
            SET current_balance = current_balance + ?,
                total_deposits = total_deposits + ?
            WHERE account_id = ?
        """
        self.execute(query, (amount, amount, account_id))
        
        # Record transaction
        account = self.fetchone(
            "SELECT member_id FROM savings_accounts WHERE account_id = ?",
            (account_id,)
        )
        
        self.record_transaction(
            member_id=account['member_id'],
            transaction_type="Savings Deposit",
            account_type="Savings",
            account_id=str(account_id),
            amount=amount,
            is_credit=True,
            transaction_data=transaction_data,
            created_by=created_by
        )
        
        self.commit()
    
    def withdraw_from_savings(self, account_id: int, amount: float,
                             transaction_data: Dict, created_by: str):
        """Withdraw from savings account"""
        # Check balance
        account = self.fetchone(
            "SELECT current_balance, member_id FROM savings_accounts WHERE account_id = ?",
            (account_id,)
        )
        
        if account['current_balance'] < amount:
            raise ValueError("Insufficient balance")
        
        # Update account balance
        query = """
            UPDATE savings_accounts 
            SET current_balance = current_balance - ?,
                total_withdrawals = total_withdrawals + ?
            WHERE account_id = ?
        """
        self.execute(query, (amount, amount, account_id))
        
        # Record transaction
        self.record_transaction(
            member_id=account['member_id'],
            transaction_type="Savings Withdrawal",
            account_type="Savings",
            account_id=str(account_id),
            amount=amount,
            is_credit=False,
            transaction_data=transaction_data,
            created_by=created_by
        )
        
        self.commit()
    
    # ========================================================================
    # LOANS
    # ========================================================================
    
    def get_loan_types(self) -> List[Dict]:
        """Get all loan types"""
        return self.fetchall("SELECT * FROM loan_types WHERE is_active = 1")
    
    def get_member_loans(self, member_id: str, active_only: bool = True) -> List[Dict]:
        """Get member's loans"""
        query = """
            SELECT l.*, lt.type_name, lt.type_code
            FROM loans l
            JOIN loan_types lt ON l.loan_type_id = lt.loan_type_id
            WHERE l.member_id = ?
        """
        if active_only:
            query += " AND l.status = 'Active'"
        query += " ORDER BY l.created_date DESC"
        return self.fetchall(query, (member_id,))
    
    def disburse_loan(self, loan_data: Dict, created_by: str) -> int:
        """Disburse a new loan"""
        member_id = loan_data['member_id']
        
        # Calculate loan details
        principal = loan_data['principal_amount']
        interest_rate = loan_data['interest_rate']
        duration = loan_data['duration_months']
        
        interest_amount = principal * (interest_rate / 100)
        total_amount = principal + interest_amount
        monthly_installment = total_amount / duration
        
        # Generate loan number
        loan_number = f"L-{member_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create loan
        query = """
            INSERT INTO loans (
                member_id, station_id, loan_type_id, loan_number,
                principal_amount, interest_rate, interest_amount, total_amount,
                monthly_installment, duration_months, balance_outstanding,
                disbursement_date, start_date, end_date,
                cheque_number, bank_name, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
        """
        
        cursor = self.execute(query, (
            member_id, loan_data['station_id'], loan_data['loan_type_id'],
            loan_number, principal, interest_rate, interest_amount, total_amount,
            monthly_installment, duration, total_amount,
            loan_data.get('disbursement_date', datetime.now().date().isoformat()),
            loan_data['start_date'], loan_data['end_date'],
            loan_data.get('cheque_number'), loan_data.get('bank_name'),
            created_by
        ))
        
        loan_id = cursor.lastrowid
        
        # Record transaction
        self.record_transaction(
            member_id=member_id,
            transaction_type="Loan Disbursement",
            account_type="Loan",
            account_id=str(loan_id),
            amount=principal,
            is_credit=True,
            transaction_data={
                'description': f"Loan Disbursement - {loan_number}",
                'cheque_number': loan_data.get('cheque_number'),
                'payment_method': loan_data.get('payment_method', 'Cheque')
            },
            created_by=created_by
        )
        
        self.commit()
        return loan_id
    
    def record_loan_repayment(self, loan_id: int, amount: float,
                             payment_data: Dict, created_by: str):
        """Record loan repayment"""
        # Get loan details
        loan = self.fetchone(
            "SELECT * FROM loans WHERE loan_id = ?",
            (loan_id,)
        )
        
        if not loan:
            raise ValueError("Loan not found")
        
        balance_before = loan['balance_outstanding']
        balance_after = max(0, balance_before - amount)
        
        # Record repayment
        query = """
            INSERT INTO loan_repayments (
                loan_id, member_id, payment_date,
                expected_amount, actual_amount, balance_before, balance_after,
                payment_method, cheque_number, receipt_number, notes,
                created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.execute(query, (
            loan_id, loan['member_id'], payment_data.get('payment_date', datetime.now().date().isoformat()),
            loan['monthly_installment'], amount, balance_before, balance_after,
            payment_data.get('payment_method'), payment_data.get('cheque_number'),
            payment_data.get('receipt_number'), payment_data.get('notes'),
            created_by
        ))
        
        # Update loan
        new_amount_paid = loan['amount_paid'] + amount
        new_status = 'Completed' if balance_after <= 0 else 'Active'
        
        self.execute("""
            UPDATE loans 
            SET amount_paid = ?, balance_outstanding = ?, status = ?
            WHERE loan_id = ?
        """, (new_amount_paid, balance_after, new_status, loan_id))
        
        # Record transaction
        self.record_transaction(
            member_id=loan['member_id'],
            transaction_type="Loan Repayment",
            account_type="Loan",
            account_id=str(loan_id),
            amount=amount,
            is_credit=False,
            transaction_data=payment_data,
            created_by=created_by
        )
        
        self.commit()
    
    # ========================================================================
    # TRANSACTIONS
    # ========================================================================
    
    def record_transaction(self, member_id: str, transaction_type: str,
                          account_type: str, account_id: str, amount: float,
                          is_credit: bool, transaction_data: Dict, created_by: str):
        """Record a transaction"""
        # Get station from member
        member = self.get_member(member_id)
        
        query = """
            INSERT INTO transactions (
                transaction_date, member_id, station_id,
                transaction_type, account_type, account_id,
                description, amount, is_credit,
                payment_method, cheque_number, receipt_number,
                created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.execute(query, (
            transaction_data.get('transaction_date', datetime.now().date().isoformat()),
            member_id, member['station_id'],
            transaction_type, account_type, account_id,
            transaction_data.get('description', ''),
            amount, 1 if is_credit else 0,
            transaction_data.get('payment_method'),
            transaction_data.get('cheque_number'),
            transaction_data.get('receipt_number'),
            created_by
        ))
    
    def get_transactions(self, member_id: Optional[str] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> List[Dict]:
        """Get transactions"""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if member_id:
            query += " AND member_id = ?"
            params.append(member_id)
        
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY transaction_date DESC, transaction_id DESC"
        
        return self.fetchall(query, tuple(params))
    
    # ========================================================================
    # SYSTEM SETTINGS
    # ========================================================================
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get system setting"""
        result = self.fetchone(
            "SELECT setting_value FROM system_settings WHERE setting_key = ?",
            (key,)
        )
        return result['setting_value'] if result else None
    
    def update_setting(self, key: str, value: str, modified_by: Optional[str] = None):
        """Update system setting"""
        self.execute("""
            UPDATE system_settings 
            SET setting_value = ?, modified_by = ?
            WHERE setting_key = ?
        """, (value, modified_by, key))
        self.commit()
    
    def get_next_member_number(self) -> int:
        """Get next member number"""
        return int(self.get_setting('next_member_number'))
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
