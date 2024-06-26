#!/usr/bin/env python3
import sys
import csv
import subprocess

# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: {} <action> <jobid_csv_file>".format(sys.argv[0]))
    sys.exit(1)

action = sys.argv[1]
csv_file = sys.argv[2]

# Check if the action is valid
valid_actions = ["suspend", "resume", "cancel"]
if action not in valid_actions:
    print("Invalid action. Allowed actions are: suspend, resume, and cancel.")
    sys.exit(1)

# Check if the file exists
try:
    with open(csv_file, 'r') as f:
        pass
except FileNotFoundError:
    print("File not found:", csv_file)
    sys.exit(1)

# Process the CSV file and execute the float command for each jobid in the last column
jobidlist = []
with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    #next(reader)  # Skip header
    for row in reader:
        jobid = row[-1]  # Last column
        jobidlist.append(jobid)

for jobid in jobidlist:
    # Execute the float command with -f flag included
    subprocess.run(["float", action, "-j", jobid, "-f"])
