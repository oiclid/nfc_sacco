# NFC Cooperative Management System

A comprehensive Windows desktop application for managing cooperative society operations including savings, loans, dividends, and financial reporting.

## 📋 Features

### Savings Management
- **Fixed Savings (Premium)** - Regular monthly savings with configurable interest
- **Target Savings (Special)** - Goal-based savings accounts
- **Fixed Deposits** - Term deposit accounts
- **Investment Shares** - Share capital management

All savings types support:
- Configurable monthly interest rates
- Toggle-able automatic interest calculation
- Individual account tracking

### Loans Management
7 loan types with different rates and terms:
- **Major Loan** (10%, 24 months)
- **Car Loan** (15%, 36 months)
- **Electronics Loan** (10%, 18 months)
- **Land Loan** (10%, 24 months)
- **Essential Commodities** (10%, 12 months)
- **Education Loan** (10%, 6 months)
- **Emergency Loan** (5%, 4 months)

Features:
- Flexible repayment tracking (allow overpayment/underpayment)
- Automatic interest calculation (flat rate)
- Loan disbursement and repayment history

### Dividends & Benefits
- Special savings dividends
- Fixed deposit dividends
- **Withdrawal benefits** 
  - Retirement withdrawals (+10% benefit by default)
  - Non-retirement withdrawals (-5% charge by default)
- **Death benefit management**
  - Configurable per-member charge (default ₦5,000)
  - Automatic charging of all active members
  - Benefit accrual to deceased member's account
  - Permanent account closure
- Default charges

### Reports
- Cashbook
- Monthly repayments/disbursements/revenue
- Bank statements & reconciliation
- Bank mandate & charges
- Accounts ledger
- Income & Expenditure statement
- Statement of Financial Position
- Audit reports
- Custom member statements with breakdown

### User Management
Multi-user support with role-based access:
- **Admin** - Full system access
- **Cashier** - Transaction processing only
- **Accountant** - Transactions + Reports
- **Auditor** - Read-only reports

Security features:
- Secure password hashing (SHA-256, upgradeable to bcrypt)
- Audit trail for all operations
- Session management

## 🚀 Installation

### Prerequisites
- **Windows 10/11** (64-bit)
- **Python 3.10 or higher**

### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, **CHECK "Add Python to PATH"** ✓
3. Verify installation:
   ```cmd
   python --version
   ```
   Should show: Python 3.10.x or higher

### Step 2: Setup Project
1. Extract the project folder to your desired location
   Example: `C:\NFC-Cooperative`

2. Open Command Prompt in the project folder:
   - Navigate to the folder in File Explorer
   - Type `cmd` in the address bar and press Enter

3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   
   This will install:
   - PyQt6 (GUI framework)
   - bcrypt (password security)
   - reportlab (PDF generation)
   - openpyxl (Excel generation)
   - And other utilities

### Step 3: Migrate Your Data

**IMPORTANT**: Your existing `database.sld` file should already be in the `data/` folder.

Run the migration:
```cmd
python migrations/migrate.py
```

The migration will:
1. Create a new database: `data/nfc_cooperative.db`
2. Migrate all your data:
   - ✓ 3 stations
   - ✓ 327 members
   - ✓ All savings account balances
   - ✓ 8,486+ loan records
   - ✓ User accounts
3. Generate a detailed report: `migrations/migration_report.txt`

**Review the migration report** after completion to ensure all data was migrated successfully.

### Step 4: Run the Application
```cmd
python main.py
```

**Note**: The full application GUI will be provided in the next phase. For now, you have:
- ✓ Complete database schema
- ✓ Data migration completed
- ✓ All backend infrastructure ready

## 📁 Project Structure

```
nfc-cooperative-system/
│
├── data/
│   ├── database.sld              # Your original database (READONLY)
│   ├── nfc_cooperative.db        # New SQLite database (after migration)
│   └── backups/                  # Automatic database backups (future)
│
├── migrations/
│   ├── schema.sql                # Complete database schema
│   ├── migrate.py                # Migration script
│   └── migration_report.txt      # Migration log (created after migration)
│
├── src/
│   ├── database/                 # Database operations (future)
│   ├── utils/                    # Utility functions (future)
│   ├── gui/                      # GUI components (future)
│   └── reports/                  # Report generation (future)
│
├── config/
│   ├── settings.py               # Application settings (future)
│   └── constants.py              # Constants (future)
│
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── main.py                       # Application entry point (future)
```

## 🔧 Configuration

### System Settings (Configurable after migration)

The following settings can be adjusted in the `system_settings` table:

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `interest_auto_calculate` | Enabled | Auto-calculate monthly interest |
| `death_benefit_enabled` | Enabled | Enable death benefit charges |
| `death_benefit_amount` | ₦5,000.00 | Amount per member for death benefit |
| `retirement_benefit_percentage` | 10.00% | Benefit for retirement withdrawals |
| `non_retirement_charge_percentage` | 5.00% | Charge for non-retirement withdrawals |
| `next_member_number` | 330 | Next member registration number |
| `next_station_number` | 4 | Next station number |

To modify settings after migration:
```sql
-- Example: Change death benefit amount to ₦10,000
UPDATE system_settings 
SET setting_value = '10000.00' 
WHERE setting_key = 'death_benefit_amount';
```

## 📊 Database Schema

### Key Tables

**Stations**
- Manages branch/location information
- Auto-generates IDs: 01, 02, ..., 99, 100
- Format: `NFC - City Name`

**Members**
- Registration number format: `NFCxxxx` (e.g., NFC0001, NFC0999, NFC1000)
- Split into First/Middle/Last names
- Includes next of kin information
- Tracks active/deceased status

**Savings Types** (4 default types)
1. PREMIUM - Fixed Savings (2% monthly)
2. TARGET - Target Savings (3% monthly)
3. FIXED_DEPOSIT - Fixed Deposits (4% monthly)
4. SHARES - Investment Shares (5% monthly)

**Loan Types** (7 default types)
1. MAJOR - Major Loan (10%, 24 months)
2. CAR - Car Loan (15%, 36 months)
3. ELECTRONICS - Electronics (10%, 18 months)
4. LAND - Land Loan (10%, 24 months)
5. ESSENTIALS - Essential Commodities (10%, 12 months)
6. EDUCATION - Education Loan (10%, 6 months)
7. EMERGENCY - Emergency Loan (5%, 4 months)

**Additional Tables**
- `savings_accounts` - Individual savings accounts
- `loans` - Loan records with full amortization
- `loan_repayments` - Track each repayment
- `transactions` - General ledger
- `dividends` - Dividend payments
- `death_benefits` & `death_benefit_charges` - Death benefit tracking
- `withdrawal_benefits` - Withdrawal benefit tracking
- `bank_transactions` - Bank reconciliation
- `users` - User accounts & authentication
- `audit_log` - Full audit trail

### Views

**vw_member_summary** - Complete member account overview
- Registration number & name
- Total savings by type
- Total loans outstanding
- Net balance (savings - loans)

## 🔐 Security Features

### Password Security
- All passwords are hashed (SHA-256 currently, bcrypt in production)
- Original passwords from old database will still work
- Never stored in plain text

### Access Control
- Role-based permissions
- Four user roles with granular permissions
- Audit trail for all changes

### Data Protection
- Foreign key constraints enforce data integrity
- Automatic backup system (future)
- Transaction rollback on errors

## 📝 Migration Details

### What Gets Migrated

✅ **Stations** (3 records)
- All station information
- Enable/disable status preserved

✅ **Members** (327 records)
- Member IDs preserved (NFC0001 - NFC0329)
- Names split properly
- Gender converted to single field
- Next of kin data cleaned

✅ **Savings Accounts** (created from ledger)
- Premium savings (B account → PREMIUM)
- Special savings (G account → TARGET)
- Share capital (A account → SHARES)
- Balances calculated from ledger

✅ **Loans** (8,486+ records)
- All active and completed loans
- Interest recalculated properly
- Payment history preserved
- Defaulted to MAJOR loan type

✅ **Users** (3 accounts)
- Usernames preserved
- Passwords hashed but original passwords work
- Permissions mapped to new system

### Data Improvements

**From:**
- Names in single field: "JAMES LAWAL GEORGE"
- Gender as two booleans: Male=1, Female=0
- NULL values as commas: ","

**To:**
- First: "JAMES", Middle: "LAWAL", Last: "GEORGE"
- Gender: "Male" or "Female"
- Proper NULL handling

**Added:**
- Primary keys on all tables
- Foreign key relationships
- Indexes for performance
- Audit timestamps

## 🆘 Troubleshooting

### Migration Issues

**Problem**: "Error: Old database not found"
**Solution**: Ensure `database.sld` is in the `data/` folder

**Problem**: "Some members skipped during migration"
**Solution**: Check `migration_report.txt` for details. Likely data quality issues (missing names, invalid IDs, etc.)

**Problem**: "Database already exists"
**Solution**: The script will ask if you want to overwrite. Type `yes` to continue.

### Installation Issues

**Problem**: "ModuleNotFoundError: No module named 'PyQt6'"
**Solution**: Run `pip install -r requirements.txt`

**Problem**: "pip is not recognized"
**Solution**: Python wasn't added to PATH. Reinstall Python and CHECK "Add Python to PATH"

**Problem**: "Permission denied"
**Solution**: Run Command Prompt as Administrator

### Database Issues

**Problem**: "Database is locked"
**Solution**: Close any programs accessing the database (including DB browsers)

**Problem**: "Incorrect password"
**Solution**: Passwords are case-sensitive. Try your original password from the old system.

## 📞 Support

For issues or questions:
1. Check `migrations/migration_report.txt` for migration details
2. Review the error messages carefully
3. Contact your system administrator

## 🔄 Next Steps

After successful migration:

1. ✅ **Verify Data**
   - Check member counts
   - Verify savings balances
   - Review loan records

2. ⏳ **Wait for Full Application** (Coming next)
   - Complete GUI interface
   - Transaction processing
   - Report generation
   - User management

3. ⏳ **Training** (After app completion)
   - User training sessions
   - Administrator guide
   - Best practices

## 📜 Version History

**Version 1.8.0** - February 2026
- Initial database schema design
- Data migration from old system
- Core table structure
- Default loan and savings types

---

**License**: Internal use - Nigerian Film Corporation  
**Created by**: oïclid
**Last Updated**: February 3, 2026

---

## 🎯 Quick Start Guide

1. Install Python 3.10+
2. Extract project folder
3. Open Command Prompt in project folder
4. Run: `pip install -r requirements.txt`
5. Run: `python migrations/migrate.py`
6. Review: `migrations/migration_report.txt`
7. Wait for full application (coming soon!)

**Your data is safe!** The original `database.sld` remains unchanged.

