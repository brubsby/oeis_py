# script to update composite work amounts to help with quitting long ecm jobs

import argparse
from modules import oeis_factor_db, factor, expression

# Initialize the ArgumentParser object
parser = argparse.ArgumentParser(description="My Script")

# Add arguments
parser.add_argument("-e", "--expression", type=str, required=False, help="Enter a string expression.")
parser.add_argument("-w", "--work", type=float, required=False, help="Enter a decimal number for work.")

# Parse the arguments
args = parser.parse_args()

expr = args.expression
if not expr:
    expr = input("Please enter a string expression: ")
composite = expression.evaluate(expr)
print(f"Composite Expression: {expr}")
print(f"Composite Value:      {composite}")
remaining_composites = factor.factordb_get_remaining_composites(composite)
print(f"Remaining Composites:  {remaining_composites}")
db = oeis_factor_db.OEISFactorDB()
print(f"Current Work:         {db.get_work(remaining_composites[0])}")

work = args.work
if not work:
    work = float(input("Please enter a decimal number for work: "))
print(f"Target Work:          {work}")
db.update_work(remaining_composites[0], work)
print(f"Updated Work:         {db.get_work(remaining_composites[0])}")
