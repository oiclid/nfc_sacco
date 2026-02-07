-- ============================================================================
-- NFC COOPERATIVE MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- SQLite Database Schema
-- Created: February 2026
-- ============================================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. STATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS stations (
    station_id TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    enabled INTEGER DEFAULT 1,
    created_date TEXT DEFAULT (datetime('now')),
    modified_date TEXT DEFAULT (datetime('now'))
);

-- ============================================================================
-- 2. MEMBERS TABLE (Improved structure)
-- ============================================================================
CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    station_id TEXT NOT NULL,
    registration_number TEXT UNIQUE NOT NULL,  -- Same as member_id for compatibility
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('Male', 'Female')),
    date_of_birth TEXT,
    date_joined TEXT NOT NULL,
    address TEXT,
    phone_number TEXT,
    email TEXT,
    employee_id TEXT,
    grade_level TEXT,
    
    -- Next of Kin 1
    nok1_name TEXT,
    nok1_relationship TEXT,
    nok1_address TEXT,
    nok1_phone TEXT,
    
    -- Next of Kin 2
    nok2_name TEXT,
    nok2_relationship TEXT,
    nok2_address TEXT,
    nok2_phone TEXT,
    
    -- Status
    is_active INTEGER DEFAULT 1,
    is_deceased INTEGER DEFAULT 0,
    deceased_date TEXT,
    photo_path TEXT,
    
    -- Audit fields
    created_date TEXT DEFAULT (datetime('now')),
    modified_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    modified_by TEXT,
    
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ============================================================================
-- 3. SAVINGS TYPES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS savings_types (
    savings_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_code TEXT UNIQUE NOT NULL,
    type_name TEXT NOT NULL,
    description TEXT,
    interest_rate DECIMAL(5,2) DEFAULT 0.00,  -- Monthly interest rate (e.g., 5.00 for 5%)
    interest_enabled INTEGER DEFAULT 1,
    minimum_balance DECIMAL(15,2) DEFAULT 0.00,
    is_active INTEGER DEFAULT 1,
    created_date TEXT DEFAULT (datetime('now'))
);

-- Insert default savings types
INSERT INTO savings_types (type_code, type_name, description, interest_rate) VALUES
('PREMIUM', 'Fixed Savings (Premium)', 'Monthly fixed savings with interest', 2.00),
('TARGET', 'Target Savings (Special)', 'Target-based special savings', 3.00),
('FIXED_DEPOSIT', 'Fixed Deposit (Flexible)', 'Flexible fixed deposit account', 4.00),
('SHARES', 'Investment Shares', 'Share capital investment', 5.00);

-- ============================================================================
-- 4. SAVINGS ACCOUNTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS savings_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    savings_type_id INTEGER NOT NULL,
    account_number TEXT UNIQUE,
    current_balance DECIMAL(15,2) DEFAULT 0.00,
    total_deposits DECIMAL(15,2) DEFAULT 0.00,
    total_withdrawals DECIMAL(15,2) DEFAULT 0.00,
    total_interest_earned DECIMAL(15,2) DEFAULT 0.00,
    monthly_target DECIMAL(15,2) DEFAULT 0.00,  -- For target savings
    date_opened TEXT DEFAULT (datetime('now')),
    is_active INTEGER DEFAULT 1,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (savings_type_id) REFERENCES savings_types(savings_type_id)
);

-- ============================================================================
-- 5. LOAN TYPES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS loan_types (
    loan_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_code TEXT UNIQUE NOT NULL,
    type_name TEXT NOT NULL,
    description TEXT,
    interest_rate DECIMAL(5,2) NOT NULL,  -- Flat rate percentage
    max_duration_months INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_date TEXT DEFAULT (datetime('now'))
);

-- Insert default loan types
INSERT INTO loan_types (type_code, type_name, description, interest_rate, max_duration_months) VALUES
('MAJOR', 'Major Loan', 'Major/Macro loan facility', 10.00, 24),
('CAR', 'Car Loan', 'Vehicle purchase loan', 15.00, 36),
('ELECTRONICS', 'Electronics Loan', 'Electronics purchase loan', 10.00, 18),
('LAND', 'Land Loan', 'Land purchase loan', 10.00, 24),
('ESSENTIALS', 'Essential Commodities', 'Essential commodities loan', 10.00, 12),
('EDUCATION', 'Education Loan', 'Education financing loan', 10.00, 6),
('EMERGENCY', 'Emergency Loan', 'Emergency loan facility', 5.00, 4);

-- ============================================================================
-- 6. LOANS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    station_id TEXT NOT NULL,
    loan_type_id INTEGER NOT NULL,
    loan_number TEXT UNIQUE,
    principal_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    interest_amount DECIMAL(15,2) NOT NULL,  -- Calculated flat interest
    total_amount DECIMAL(15,2) NOT NULL,     -- Principal + Interest
    monthly_installment DECIMAL(15,2) NOT NULL,
    duration_months INTEGER NOT NULL,
    amount_paid DECIMAL(15,2) DEFAULT 0.00,
    balance_outstanding DECIMAL(15,2) NOT NULL,
    
    disbursement_date TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    
    cheque_number TEXT,
    bank_name TEXT,
    
    status TEXT DEFAULT 'Active' CHECK(status IN ('Pending', 'Active', 'Completed', 'Defaulted')),
    is_active INTEGER DEFAULT 1,
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    FOREIGN KEY (loan_type_id) REFERENCES loan_types(loan_type_id)
);

-- ============================================================================
-- 7. LOAN REPAYMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS loan_repayments (
    repayment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    member_id TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    expected_amount DECIMAL(15,2) NOT NULL,
    actual_amount DECIMAL(15,2) NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    payment_method TEXT,  -- Cash, Cheque, Transfer
    cheque_number TEXT,
    receipt_number TEXT,
    notes TEXT,
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- ============================================================================
-- 8. TRANSACTIONS TABLE (General ledger)
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,
    member_id TEXT NOT NULL,
    station_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,  -- Deposit, Withdrawal, Loan Disbursement, Loan Repayment, etc.
    account_type TEXT NOT NULL,      -- Savings, Loan, Shares, etc.
    account_id TEXT,                 -- Reference to specific account
    description TEXT,
    amount DECIMAL(15,2) NOT NULL,
    is_credit INTEGER NOT NULL,      -- 1 for Credit, 0 for Debit
    payment_method TEXT,             -- Cash, Cheque, Transfer
    cheque_number TEXT,
    receipt_number TEXT,
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ============================================================================
-- 9. DIVIDENDS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS dividends (
    dividend_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    dividend_type TEXT NOT NULL,  -- Special Savings, Fixed Deposit, General Dividend
    amount DECIMAL(15,2) NOT NULL,
    dividend_date TEXT NOT NULL,
    financial_year TEXT,
    description TEXT,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Paid', 'Cancelled')),
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- ============================================================================
-- 10. DEATH BENEFITS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS death_benefits (
    benefit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deceased_member_id TEXT NOT NULL,
    deceased_date TEXT NOT NULL,
    total_benefit_amount DECIMAL(15,2) DEFAULT 0.00,
    per_member_charge DECIMAL(15,2) NOT NULL,
    total_members_charged INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Processing' CHECK(status IN ('Processing', 'Completed')),
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (deceased_member_id) REFERENCES members(member_id)
);

-- ============================================================================
-- 11. DEATH BENEFIT CHARGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS death_benefit_charges (
    charge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    benefit_id INTEGER NOT NULL,
    member_id TEXT NOT NULL,           -- Member being charged
    deceased_member_id TEXT NOT NULL,  -- Member who died
    charge_amount DECIMAL(15,2) NOT NULL,
    charge_date TEXT NOT NULL,
    transaction_id INTEGER,
    
    created_date TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (benefit_id) REFERENCES death_benefits(benefit_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (deceased_member_id) REFERENCES members(member_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- ============================================================================
-- 12. WITHDRAWAL BENEFITS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS withdrawal_benefits (
    benefit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    withdrawal_type TEXT NOT NULL,  -- Retirement, Non-Retirement
    withdrawal_date TEXT NOT NULL,
    total_balance DECIMAL(15,2) NOT NULL,
    benefit_percentage DECIMAL(5,2) NOT NULL,
    benefit_amount DECIMAL(15,2) NOT NULL,
    final_amount DECIMAL(15,2) NOT NULL,  -- Balance +/- benefit
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- ============================================================================
-- 13. BANK TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS bank_transactions (
    bank_transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,  -- Deposit, Withdrawal, Transfer
    payee_name TEXT,
    description TEXT,
    amount DECIMAL(15,2) NOT NULL,
    payment_method TEXT,
    cheque_number TEXT,
    bank_name TEXT,
    receipt_number TEXT,
    bank_charges DECIMAL(15,2) DEFAULT 0.00,
    bank_interest DECIMAL(15,2) DEFAULT 0.00,
    is_cleared INTEGER DEFAULT 0,
    details TEXT,
    
    created_date TEXT DEFAULT (datetime('now')),
    created_by TEXT
);

-- ============================================================================
-- 14. SYSTEM SETTINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type TEXT,  -- String, Integer, Decimal, Boolean
    description TEXT,
    is_editable INTEGER DEFAULT 1,
    
    modified_date TEXT DEFAULT (datetime('now')),
    modified_by TEXT
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('interest_auto_calculate', '1', 'Boolean', 'Enable automatic monthly interest calculation'),
('death_benefit_enabled', '1', 'Boolean', 'Enable death benefit charges'),
('death_benefit_amount', '5000.00', 'Decimal', 'Amount charged per member for death benefit'),
('retirement_benefit_percentage', '10.00', 'Decimal', 'Percentage added for retirement withdrawals'),
('non_retirement_charge_percentage', '5.00', 'Decimal', 'Percentage charged for non-retirement withdrawals'),
('next_member_number', '330', 'Integer', 'Next member registration number'),
('next_station_number', '4', 'Integer', 'Next station number'),
('organization_name', 'Nigerian Film Corporation', 'String', 'Organization name'),
('currency_symbol', '₦', 'String', 'Currency symbol'),
('date_format', 'YYYY-MM-DD', 'String', 'Date format for display');

-- ============================================================================
-- 15. USERS TABLE (Authentication)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    role TEXT NOT NULL CHECK(role IN ('Admin', 'Cashier', 'Accountant', 'Auditor')),
    
    -- Permissions
    can_maintain INTEGER DEFAULT 0,     -- Add/Edit members, settings
    can_operate INTEGER DEFAULT 0,      -- Process transactions
    can_edit INTEGER DEFAULT 0,         -- Edit transactions
    can_view_reports INTEGER DEFAULT 0, -- View reports
    
    is_active INTEGER DEFAULT 1,
    last_login TEXT,
    
    created_date TEXT DEFAULT (datetime('now')),
    modified_date TEXT DEFAULT (datetime('now'))
);

-- ============================================================================
-- 16. AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date TEXT DEFAULT (datetime('now')),
    user_id INTEGER,
    username TEXT,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id TEXT,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_members_station ON members(station_id);
CREATE INDEX IF NOT EXISTS idx_members_active ON members(is_active);
CREATE INDEX IF NOT EXISTS idx_savings_member ON savings_accounts(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_transactions_member ON transactions(member_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_repayments_loan ON loan_repayments(loan_id);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- View: Member Account Summary
CREATE VIEW IF NOT EXISTS vw_member_summary AS
SELECT 
    m.member_id,
    m.registration_number,
    m.first_name || ' ' || COALESCE(m.middle_name || ' ', '') || m.last_name AS full_name,
    m.station_id,
    s.station_name,
    m.is_active,
    m.is_deceased,
    
    -- Total Savings
    COALESCE(SUM(CASE WHEN st.type_code = 'PREMIUM' THEN sa.current_balance ELSE 0 END), 0) AS premium_savings,
    COALESCE(SUM(CASE WHEN st.type_code IN ('TARGET', 'FIXED_DEPOSIT') THEN sa.current_balance ELSE 0 END), 0) AS fixed_target_deposits,
    COALESCE(SUM(CASE WHEN st.type_code = 'SHARES' THEN sa.current_balance ELSE 0 END), 0) AS shares_investment,
    COALESCE(SUM(sa.current_balance), 0) AS total_savings,
    
    -- Total Loans
    COALESCE(SUM(l.balance_outstanding), 0) AS total_loans_outstanding,
    
    -- Net Balance
    COALESCE(SUM(sa.current_balance), 0) - COALESCE(SUM(l.balance_outstanding), 0) AS net_balance
    
FROM members m
LEFT JOIN stations s ON m.station_id = s.station_id
LEFT JOIN savings_accounts sa ON m.member_id = sa.member_id AND sa.is_active = 1
LEFT JOIN savings_types st ON sa.savings_type_id = st.savings_type_id
LEFT JOIN loans l ON m.member_id = l.member_id AND l.status = 'Active'
GROUP BY m.member_id, m.registration_number, m.first_name, m.middle_name, m.last_name, m.station_id, s.station_name, m.is_active, m.is_deceased;

-- ============================================================================
-- TRIGGERS for Audit Trail
-- ============================================================================

-- Trigger: Update modified_date on stations
CREATE TRIGGER IF NOT EXISTS trg_stations_update
AFTER UPDATE ON stations
BEGIN
    UPDATE stations SET modified_date = datetime('now') WHERE station_id = NEW.station_id;
END;

-- Trigger: Update modified_date on members
CREATE TRIGGER IF NOT EXISTS trg_members_update
AFTER UPDATE ON members
BEGIN
    UPDATE members SET modified_date = datetime('now') WHERE member_id = NEW.member_id;
END;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
