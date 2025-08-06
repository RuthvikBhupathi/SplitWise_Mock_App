"""
Main application entry point for expense splitter.
"""

import sys
import os
from typing import Optional

# Import our custom modules
from args_parser import get_arguments
from excel_handler import ExcelHandler
from expense_logic import ExpenseSplitter


def main():
    """Main application function."""
    try:
        # Parse command line arguments
        args = get_arguments()

        if args.verbose:
            print(f"Processing expenses for: {', '.join(args.people)}")
            print(f"Reading from: {args.file}")
            print(f"Output will be saved to: {args.output}")
            print("-" * 50)

        # Initialize handlers
        excel_handler = ExcelHandler()
        expense_splitter = ExpenseSplitter(args.people)

        # Read expense data
        print("📊 Loading expense data...")
        expense_data = excel_handler.read_expense_data(args.file)

        # Display data summary if verbose
        if args.verbose:
            excel_handler.display_data_summary(expense_data, args.people)

        # Process expenses and calculate settlements
        print("🔄 Calculating settlements...")
        detailed_settlements, simplified_settlements, summary = expense_splitter.process_expenses(expense_data)

        # Display results
        expense_splitter.print_settlement_summary(detailed_settlements, summary)

        # Display simplified settlements
        print("\n" + "="*50)
        print("SIMPLIFIED SETTLEMENT (Optimized)")
        print("="*50)
        if simplified_settlements:
            for person_data in simplified_settlements:
                person = person_data['Person']
                pays_to = person_data['Pays_To']
                amount = person_data['Amount']

                if pays_to == "Nobody":
                    print(f"✅ {person} pays $0.00")
                else:
                    print(f"💳 {person} pays {pays_to} {amount}")
        else:
            print("🎉 Everyone is even! No payments needed.")
        print("="*50 + "\n")

        # Save results
        print("💾 Saving settlement data...")
        excel_handler.save_settlement_data(detailed_settlements, simplified_settlements, args.output, args.verbose)

        print("✅ Processing completed successfully!")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        return 1

    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        return 1

    except ValueError as e:
        print(f"❌ Data error: {e}")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


def validate_environment():
    """Validate that all required modules are available."""
    required_modules = ['pandas', 'openpyxl']  # openpyxl needed for Excel support
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nInstall with: pip install " + " ".join(missing_modules))
        return False

    return True


if __name__ == "__main__":
    # Validate environment first
    if not validate_environment():
        sys.exit(1)

    # Run main application
    exit_code = main()
    sys.exit(exit_code)