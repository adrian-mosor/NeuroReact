import re
from collections import defaultdict
import sys

# Check for correct usage
if len(sys.argv) != 2:
    print("Usage: python script.py <input_file>")
    sys.exit(1)

# Get input file from command-line argument
input_file = sys.argv[1]

# Dictionary to store red click counts per sequence
red_clicks = defaultdict(int)

# Read the file and count red clicks
with open(input_file, "r") as file:
    for line in file:
        match = re.match(r"Sequence (\d+) - Iteration \d+: .*\(Clicked Red: (True|False)\)", line)
        if match:
            sequence = f"Sequence {match.group(1)}"
            clicked_red = match.group(2) == "True"
            if clicked_red:
                red_clicks[sequence] += 1

# Display results
for sequence, count in sorted(red_clicks.items()):
    print(f"{sequence}: {count} times Red was clicked")
