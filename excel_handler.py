"""
Excel file handling operations for expense splitter application.
"""

import pandas as pd
import os
from typing import List, Dict, Any


class ExcelHandler:
    """Handles Excel file operations for expense data."""

    def __init__(self):
        self.required_columns = ["Description", "Paid By", "Amount", "Shared With"]

    def read_expense_data(self, file_path: str) -> pd.DataFrame:
        """
        Read expense data from Excel file.

        Args:
            file_path (str): Path to the Excel file

        Returns:
            pd.DataFrame: DataFrame containing expense data

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
            Exception: For other Excel reading errors
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")

            # Read Excel file
            df = pd.read_excel(file_path)

            # Validate columns
            self._validate_columns(df)

            # Clean and validate data
            df = self._clean_data(df)

            print(f"Successfully loaded {len(df)} expense records from {file_path}")
            return df

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error reading Excel file {file_path}: {str(e)}")

    def _validate_columns(self, df: pd.DataFrame):
        """
        Validate that all required columns are present.

        Args:
            df (pd.DataFrame): DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate expense data.

        Args:
            df (pd.DataFrame): Raw DataFrame

        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Make a copy to avoid modifying original
        df_clean = df.copy()

        # Remove rows with missing essential data
        df_clean = df_clean.dropna(subset=["Description", "Paid By", "Amount"])

        # Convert Amount to numeric, handling any string representations
        df_clean["Amount"] = pd.to_numeric(df_clean["Amount"], errors='coerce')

        # Remove rows with invalid amounts
        df_clean = df_clean.dropna(subset=["Amount"])
        df_clean = df_clean[df_clean["Amount"] > 0]

        # Clean string fields
        df_clean["Description"] = df_clean["Description"].astype(str).str.strip()
        df_clean["Paid By"] = df_clean["Paid By"].astype(str).str.strip()

        # Handle Shared With column - fill NaN with "All"
        df_clean["Shared With"] = df_clean["Shared With"].fillna("All")
        df_clean["Shared With"] = df_clean["Shared With"].astype(str).str.strip()

        return df_clean

    def save_settlement_data(self, detailed_settlements: List[Dict[str, Any]],
                           simplified_settlements: List[Dict[str, Any]],
                           output_path: str, verbose: bool = False):
        """
        Save settlement data to Excel file with multiple sheets.

        Args:
            detailed_settlements (List[Dict]): Detailed settlement records
            simplified_settlements (List[Dict]): Simplified settlement records
            output_path (str): Path for output Excel file
            verbose (bool): Whether to print verbose output
        """
    def save_settlement_data(self, detailed_settlements: List[Dict[str, Any]],
                           simplified_settlements: List[Dict[str, Any]],
                           output_path: str, verbose: bool = False):
        """
        Save settlement data to Excel file with multiple sheets.

        Args:
            detailed_settlements (List[Dict]): Detailed settlement records
            simplified_settlements (List[Dict]): Simplified settlement records
            output_path (str): Path for output Excel file
            verbose (bool): Whether to print verbose output
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Save detailed settlements
                if detailed_settlements:
                    detailed_df = pd.DataFrame(detailed_settlements)
                    detailed_df.to_excel(writer, sheet_name='Detailed_Settlements', index=False)

                # Save simplified settlements
                if simplified_settlements:
                    simplified_df = pd.DataFrame(simplified_settlements)
                    simplified_df.to_excel(writer, sheet_name='Simple_Settlements', index=False)

                # If no settlements, create empty sheets with headers
                if not detailed_settlements:
                    empty_detailed = pd.DataFrame(columns=['From', 'To', 'Amount'])
                    empty_detailed.to_excel(writer, sheet_name='Detailed_Settlements', index=False)

                if not simplified_settlements:
                    empty_simplified = pd.DataFrame(columns=['Person', 'Pays_To', 'Amount', 'Net_Balance'])
                    empty_simplified.to_excel(writer, sheet_name='Simple_Settlements', index=False)

            if verbose:
                print(f"Settlement data saved to: {output_path}")
                print(f"- Detailed settlements: {len(detailed_settlements) if detailed_settlements else 0}")
                print(f"- Simplified settlements: {len([s for s in simplified_settlements if s['Pays_To'] != 'Nobody']) if simplified_settlements else 0} people need to pay")
            else:
                if not detailed_settlements and not simplified_settlements:
                    print("No settlements needed - everyone is even!")
                else:
                    print(f"Settlement results saved to '{output_path}' with 2 sheets:")
                    print(f"  📋 Detailed_Settlements: All individual transactions")
                    print(f"  ✨ Simple_Settlements: Optimized payments (fewer transactions)")

        except Exception as e:
            raise Exception(f"Error saving settlement data to {output_path}: {str(e)}")

    def display_data_summary(self, df: pd.DataFrame, people: List[str]):
        """
        Display a summary of the loaded expense data.

        Args:
            df (pd.DataFrame): Expense data
            people (List[str]): List of people involved
        """
        print("\n" + "="*50)
        print("EXPENSE DATA SUMMARY")
        print("="*50)
        print(f"Total expenses: {len(df)}")
        print(f"Total amount: ${df['Amount'].sum():.2f}")
        print(f"People involved: {', '.join(people)}")

        print("\nExpenses by payer:")
        payer_summary = df.groupby("Paid By")["Amount"].agg(['count', 'sum']).round(2)
        payer_summary.columns = ['Number of Expenses', 'Total Amount']
        print(payer_summary)
        print("="*50 + "\n")


def read_expenses(file_path: str) -> pd.DataFrame:
    """Convenience function to read expense data."""
    handler = ExcelHandler()
    return handler.read_expense_data(file_path)


def save_settlements(detailed_settlements: List[Dict[str, Any]],
                   simplified_settlements: List[Dict[str, Any]],
                   output_path: str, verbose: bool = False):
    """Convenience function to save settlement data."""
    handler = ExcelHandler()
    handler.save_settlement_data(detailed_settlements, simplified_settlements, output_path, verbose)


if __name__ == "__main__":
    # Test the Excel handler
    try:
        handler = ExcelHandler()
        # This will fail if no test file exists, which is expected
        df = handler.read_expense_data("test_expenses.xlsx")
        print("Test successful!")
    except FileNotFoundError:
        print("Test file not found - this is expected for testing.")
    except Exception as e:
        print(f"Test error: {e}")