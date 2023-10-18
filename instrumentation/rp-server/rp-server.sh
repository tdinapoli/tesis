#!/bin/bash

# Define your specific identifier
IDENTIFIER="rp-server"

# Check if a process with the specific identifier is running
if pgrep -f "$IDENTIFIER" > /dev/null; then
  # If the process is running, kill it
  pkill -f "$IDENTIFIER"
  echo "Killed $IDENTIFIER"
fi

# Start the Python script with the identifier
python3 __init__.py "$IDENTIFIER" &

echo "Started $IDENTIFIER"
