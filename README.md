# Expense Splitter

A modular Python application for splitting expenses between people, similar to Splitwise.

## Project Structure

```
expense-splitter/
├── main.py              # Main application entry point
├── args_parser.py       # Command line argument handling
├── excel_handler.py     # Excel file operations
├── expense_logic.py     # Core expense splitting logic
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Features

- ✅ Read expense data from Excel files
- ✅ Support for multiple people and flexible expense sharing
- ✅ Automatic debt netting (A owes B $10, B owes A $6 → A owes B $4)
- ✅ Command line interface with argument validation
- ✅ Detailed settlement reports
- ✅ Export results to Excel
- ✅ Verbose mode for detailed output

## Installation

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python main.py --file expenses.xlsx --people Alice Bob Charlie David
```

### Short Form
```bash
python main.py -f expenses.xlsx -p Alice Bob Charlie David
```

### With Custom Output and Verbose Mode
```bash
python main.py -f expenses.xlsx -p Alice Bob Charlie David -o my_settlements.xlsx --verbose
```

### Get Help
```bash
python main.py --help
```

## Excel File Format

Your input Excel file should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| **Description** | What the expense was for | "Pizza dinner", "Gas for trip" |
| **Paid By** | Who paid for it | "Alice" |
| **Amount** | How much it cost | 25.50 |
| **Shared With** | Who should split it | "All" or "Alice, Bob" |

### Example Excel Data:
| Description | Paid By | Amount | Shared With |
|-------------|---------|---------|-------------|
| Pizza dinner | Alice | 40 | All |
| Gas for trip | Bob | 60 | Bob, Alice |
| Coffee | Charlie | 15 | All |
| Movie tickets | Alice | 24 | Alice, David |

## Command Line Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--file` | `-f` | ✅ | Path to Excel file with expense data |
| `--people` | `-p` | ✅ | Names of people (space-separated) |
| `--output` | `-o` | ❌ | Output file path (default: settlements.xlsx) |
| `--verbose` | `-v` | ❌ | Enable detailed output |

## Module Descriptions

### `main.py`
The main application entry point that orchestrates all other modules. Handles:
- Overall application flow
- Error handling and user feedback
- Environment validation

### `args_parser.py`
Handles command line argument parsing and validation. Features:
- Argument validation and cleaning
- Help text generation
- Duplicate name removal

### `excel_handler.py`
Manages all Excel file operations. Includes:
- Reading expense data with validation
- Data cleaning and error handling
- Saving settlement results
- Data summary generation

### `expense_logic.py`
Contains the core expense splitting algorithm. Provides:
- Expense parsing and validation
- Balance calculation with debt netting
- Settlement optimization
- Summary reporting

## Example Output

```
📊 Loading expense data...
Successfully loaded 15 expense records from expenses.xlsx

🔄 Calculating settlements...

==================================================
SETTLEMENT SUMMARY
==================================================
Total settlements needed: 3

💰 Charlie → Alice: $45.25
💰 David → Bob: $32.50
💰 Charlie → Bob: $12.75

------------------------------
INDIVIDUAL BALANCES
------------------------------
✅ Alice: Net +$23.50 (gets back $45.25, pays $21.75)
✅ Bob: Net +$21.75 (gets back $45.25, pays $23.50)
💸 Charlie: Net -$58.00 (gets back $0.00, pays $58.00)
💸 David: Net -32.50 (gets back $0.00, pays $32.50)
==================================================

💾 Saving settlement data...
Settlement results saved to 'settlements.xlsx'
✅ Processing completed successfully!
```

## Error Handling

The application handles various error scenarios:
- Missing or invalid Excel files
- Missing required columns
- Invalid expense amounts
- Unknown people in expense data
- File permission issues

## Testing Individual Modules

Each module can be tested independently:

```bash
# Test argument parser
python args_parser.py -f test.xlsx -p Alice Bob

# Test Excel handler (needs a test file)
python excel_handler.py

# Test expense logic
python expense_logic.py
```

## Contributing

The modular design makes it easy to extend:
- Add new input formats by extending `excel_handler.py`
- Add new argument types in `args_parser.py`  
- Modify splitting logic in `expense_logic.py`
- Add new output formats or features in `main.py`