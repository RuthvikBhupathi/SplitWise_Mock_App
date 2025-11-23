"""
Core logic for splitting expenses and calculating settlements.
"""

import pandas as pd
from collections import defaultdict
from typing import List, Dict, Any, Tuple


class ExpenseSplitter:
    """Handles the core logic for splitting expenses and calculating settlements."""

    def __init__(self, people: List[str]):
        """
        Initialize the expense splitter.

        Args:
            people (List[str]): List of people involved in expenses
        """
        self.people = people
        self.balances = defaultdict(lambda: defaultdict(float))
        self.final_balances = defaultdict(dict)

    def parse_shared_with(self, shared_with: str) -> List[str]:
        """
        Parse the 'Shared With' field to get list of people.

        Args:
            shared_with (str): Comma-separated names or "All"

        Returns:
            List[str]: List of people who shared the expense
        """
        if not shared_with or shared_with.strip().lower() == "all":
            return self.people.copy()

        # Split by comma and clean up names
        shared_people = [name.strip() for name in shared_with.split(",")]

        # Filter to only include known people
        valid_people = [person for person in shared_people if person in self.people]

        # If no valid people found, default to all
        if not valid_people:
            print(f"Warning: No valid people found in '{shared_with}', defaulting to all people")
            return self.people.copy()

        return valid_people

    def calculate_balances(self, expense_data: pd.DataFrame) -> None:
        """
        Calculate how much each person owes to each other person.

        Args:
            expense_data (pd.DataFrame): DataFrame with expense data
        """
        # Reset balances
        self.balances = defaultdict(lambda: defaultdict(float))

        for _, row in expense_data.iterrows():
            paid_by = row["Paid By"]
            amount = row["Amount"]
            shared_with = self.parse_shared_with(row["Shared With"])

            # Skip if payer is not in our people list
            if paid_by not in self.people:
                print(f"Warning: '{paid_by}' not in people list, skipping expense: {row['Description']}")
                continue

            # Calculate amount each person owes
            amount_per_person = amount / len(shared_with)

            # Add debt for each person who shared the expense (except the payer)
            for person in shared_with:
                if person != paid_by and person in self.people:
                    self.balances[person][paid_by] += amount_per_person

    def net_balances(self) -> None:
        """
        Net off mutual debts to simplify settlements.
        For example, if A owes B $10 and B owes A $6,
        result is A owes B $4.
        """
        self.final_balances = defaultdict(dict)

        for person1 in self.people:
            for person2 in self.people:
                if person1 != person2:
                    # Calculate net amount person1 owes person2
                    amount_1_owes_2 = self.balances[person1][person2]
                    amount_2_owes_1 = self.balances[person2][person1]

                    net_amount = amount_1_owes_2 - amount_2_owes_1

                    if net_amount > 0.01:  # Only record if significant amount
                        self.final_balances[person1][person2] = round(net_amount, 2)

    def get_settlements(self) -> List[Dict[str, Any]]:
        """
        Get the final settlement list.

        Returns:
            List[Dict]: List of settlements with 'From', 'To', and 'Amount' keys
        """
        settlements = []

        for debtor, creditors in self.final_balances.items():
            for creditor, amount in creditors.items():
                settlements.append({
                    "From": debtor,
                    "To": creditor,
                    "Amount": f"${amount:.2f}"
                })

        # Sort settlements by amount (highest first)
        settlements.sort(key=lambda x: float(x["Amount"][1:]), reverse=True)

        return settlements

    def get_simplified_settlements(self) -> List[Dict[str, Any]]:
        """
        Get simplified settlements that minimize the number of transactions.
        Uses a greedy algorithm to reduce the number of payments needed.

        Returns:
            List[Dict]: Simplified settlement list with 'Person', 'Pays_To', 'Amount', 'Net_Balance'
        """
        # Calculate net balance for each person (positive = owed money, negative = owes money)
        net_balances = {}
        for person in self.people:
            owes = sum(self.final_balances[person].values())
            owed = sum(balances.get(person, 0) for balances in self.final_balances.values())
            net_balances[person] = round(owed - owes, 2)

        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = [(person, amount) for person, amount in net_balances.items() if amount > 0.01]
        debtors = [(person, -amount) for person, amount in net_balances.items() if amount < -0.01]

        # Sort by amount (largest first)
        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)

        # Create simplified transactions
        simplified_transactions = []
        creditor_idx = 0
        debtor_idx = 0

        while creditor_idx < len(creditors) and debtor_idx < len(debtors):
            creditor_name, credit_amount = creditors[creditor_idx]
            debtor_name, debt_amount = debtors[debtor_idx]

            # Determine transaction amount
            transaction_amount = min(credit_amount, debt_amount)

            if transaction_amount > 0.01:  # Only record significant amounts
                simplified_transactions.append({
                    "From": debtor_name,
                    "To": creditor_name,
                    "Amount": round(transaction_amount, 2)
                })

            # Update remaining amounts
            creditors[creditor_idx] = (creditor_name, credit_amount - transaction_amount)
            debtors[debtor_idx] = (debtor_name, debt_amount - transaction_amount)

            # Move to next creditor/debtor if current one is settled
            if creditors[creditor_idx][1] < 0.01:
                creditor_idx += 1
            if debtors[debtor_idx][1] < 0.01:
                debtor_idx += 1

        # Create payment summary for each person
        payment_summary = []

        for person in self.people:
            # Find who this person needs to pay and how much
            payments_to_make = [t for t in simplified_transactions if t["From"] == person]

            if payments_to_make:
                # If person makes multiple payments, combine them or show the main one
                if len(payments_to_make) == 1:
                    payment = payments_to_make[0]
                    payment_summary.append({
                        "Person": person,
                        "Pays_To": payment["To"],
                        "Amount": f"${payment['Amount']:.2f}",
                        "Net_Balance": f"-${payment['Amount']:.2f}"
                    })
                else:
                    # Multiple payments - show total and main recipient
                    total_payment = sum(p["Amount"] for p in payments_to_make)
                    main_recipient = max(payments_to_make, key=lambda x: x["Amount"])["To"]
                    payment_summary.append({
                        "Person": person,
                        "Pays_To": f"{main_recipient} (+others)",
                        "Amount": f"${total_payment:.2f}",
                        "Net_Balance": f"-${total_payment:.2f}"
                    })
            else:
                # Person doesn't need to pay anyone
                net_balance = net_balances.get(person, 0)
                if net_balance > 0.01:
                    payment_summary.append({
                        "Person": person,
                        "Pays_To": "Nobody",
                        "Amount": "$0.00",
                        "Net_Balance": f"+${net_balance:.2f}"
                    })
                else:
                    payment_summary.append({
                        "Person": person,
                        "Pays_To": "Nobody",
                        "Amount": "$0.00",
                        "Net_Balance": "$0.00"
                    })

        return payment_summary

    def get_balance_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get a summary of who owes what to whom.

        Returns:
            Dict: Nested dictionary of balances
        """
        summary = {}
        for person in self.people:
            summary[person] = {
                "owes": sum(self.final_balances[person].values()),
                "owed": sum(balances.get(person, 0) for balances in self.final_balances.values())
            }
        return summary

    def get_optimized_transactions(self) -> List[Dict[str, Any]]:
        """
        Compute the optimized list of transactions (debtor → creditor → amount)
        using the same greedy algorithm as get_simplified_settlements, but
        without aggregating by person.
        """
        # Calculate net balance for each person (positive = owed money, negative = owes money)
        net_balances = {}
        for person in self.people:
            owes = sum(self.final_balances[person].values())
            owed = sum(balances.get(person, 0) for balances in self.final_balances.values())
            net_balances[person] = round(owed - owes, 2)

        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = [(person, amount) for person, amount in net_balances.items() if amount > 0.01]
        debtors = [(person, -amount) for person, amount in net_balances.items() if amount < -0.01]

        # Sort by amount (largest first)
        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)

        transactions: List[Dict[str, Any]] = []
        creditor_idx = 0
        debtor_idx = 0

        while creditor_idx < len(creditors) and debtor_idx < len(debtors):
            creditor_name, credit_amount = creditors[creditor_idx]
            debtor_name, debt_amount = debtors[debtor_idx]

            # Determine transaction amount
            transaction_amount = min(credit_amount, debt_amount)

            if transaction_amount > 0.01:  # Only record significant amounts
                transactions.append({
                    "From": debtor_name,
                    "To": creditor_name,
                    "Amount": round(transaction_amount, 2)
                })

            # Update remaining amounts
            creditors[creditor_idx] = (creditor_name, credit_amount - transaction_amount)
            debtors[debtor_idx] = (debtor_name, debt_amount - transaction_amount)

            # Move to next creditor/debtor if current one is settled
            if creditors[creditor_idx][1] < 0.01:
                creditor_idx += 1
            if debtors[debtor_idx][1] < 0.01:
                debtor_idx += 1

        return transactions


    def process_expenses(self, expense_data: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, float]]]:
        """
        Process all expenses and return settlements and summary.

        Args:
            expense_data (pd.DataFrame): DataFrame with expense data

        Returns:
            Tuple: (detailed_settlements, simplified_settlements, balance_summary)
        """
        self.calculate_balances(expense_data)
        self.net_balances()

        detailed_settlements = self.get_settlements()
        simplified_settlements = self.get_simplified_settlements()
        summary = self.get_balance_summary()

        return detailed_settlements, simplified_settlements, summary

    def print_settlement_summary(self, settlements: List[Dict[str, Any]],
                               summary: Dict[str, Dict[str, float]]):
        """
        Print a formatted summary of settlements.

        Args:
            settlements (List[Dict]): List of settlement records
            summary (Dict): Balance summary for each person
        """
        print("\n" + "="*50)
        print("SETTLEMENT SUMMARY")
        print("="*50)

        if not settlements:
            print("🎉 Everyone is even! No settlements needed.")
            return

        print(f"Total settlements needed: {len(settlements)}\n")

        for settlement in settlements:
            print(f"💰 {settlement['From']} → {settlement['To']}: {settlement['Amount']}")

        print("\n" + "-"*30)
        print("INDIVIDUAL BALANCES")
        print("-"*30)

        for person, balance in summary.items():
            owes = balance['owes']
            owed = balance['owed']
            net = owed - owes

            if net > 0.01:
                print(f"✅ {person}: Net +${net:.2f} (gets back ${owed:.2f}, pays ${owes:.2f})")
            elif net < -0.01:
                print(f"💸 {person}: Net ${net:.2f} (gets back ${owed:.2f}, pays ${owes:.2f})")
            else:
                print(f"⚖️  {person}: Even (gets back ${owed:.2f}, pays ${owes:.2f})")

        print("="*50 + "\n")


def split_expenses(expense_data: pd.DataFrame, people: List[str], verbose: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, float]]]:
    """
    Convenience function to split expenses.

    Args:
        expense_data (pd.DataFrame): Expense data
        people (List[str]): List of people
        verbose (bool): Whether to print detailed output

    Returns:
        Tuple: (detailed_settlements, simplified_settlements, summary)
    """
    splitter = ExpenseSplitter(people)
    detailed_settlements, simplified_settlements, summary = splitter.process_expenses(expense_data)

    if verbose:
        splitter.print_settlement_summary(detailed_settlements, summary)

    return detailed_settlements, simplified_settlements, summary


if __name__ == "__main__":
    # Test the expense splitter with sample data
    import pandas as pd

    sample_data = [
        ["Pizza", "Alice", 20, "All"],
        ["Gas", "Bob", 40, "Bob, Alice"],
        ["Coffee", "Charlie", 15, "All"]
    ]

    df = pd.DataFrame(sample_data, columns=["Description", "Paid By", "Amount", "Shared With"])
    people = ["Alice", "Bob", "Charlie"]

    detailed_settlements, simplified_settlements, summary = split_expenses(df, people, verbose=True)
    print("Test completed successfully!")