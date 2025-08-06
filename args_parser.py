"""
Command line argument parser for expense splitter application.
"""

import argparse
import sys


class ArgumentParser:
    """Handles command line argument parsing for expense splitting."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self):
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='Split expenses between people',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py -f expenses.xlsx -p Alice Bob Charlie
  python main.py --file data.xlsx --people John Jane --output results.xlsx
            """
        )

        parser.add_argument(
            '--file', '-f',
            required=True,
            help='Path to Excel file with expense data'
        )

        parser.add_argument(
            '--people', '-p',
            required=True,
            nargs='+',
            help='Names of people involved (space-separated)'
        )

        parser.add_argument(
            '--output', '-o',
            default='settlements.xlsx',
            help='Output file path (default: settlements.xlsx)'
        )

        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )

        return parser

    def parse_args(self, args=None):
        """Parse command line arguments and return parsed args."""
        try:
            parsed_args = self.parser.parse_args(args)
            self._validate_args(parsed_args)
            return parsed_args
        except SystemExit:
            # Re-raise SystemExit to maintain argparse behavior
            raise
        except Exception as e:
            print(f"Error parsing arguments: {e}")
            sys.exit(1)

    def _validate_args(self, args):
        """Validate parsed arguments."""
        # Check if people list is not empty
        if not args.people:
            raise ValueError("At least one person must be specified")

        # Remove duplicates while preserving order
        seen = set()
        unique_people = []
        for person in args.people:
            if person not in seen:
                seen.add(person)
                unique_people.append(person)
        args.people = unique_people

        # Validate file extensions
        if not args.file.lower().endswith(('.xlsx', '.xls')):
            print("Warning: Input file should be an Excel file (.xlsx or .xls)")

        if not args.output.lower().endswith(('.xlsx', '.xls')):
            print("Warning: Output file should be an Excel file (.xlsx or .xls)")


def get_arguments():
    """Convenience function to get parsed arguments."""
    parser = ArgumentParser()
    return parser.parse_args()


if __name__ == "__main__":
    # Test the argument parser
    args = get_arguments()
    print(f"File: {args.file}")
    print(f"People: {args.people}")
    print(f"Output: {args.output}")
    print(f"Verbose: {args.verbose}")