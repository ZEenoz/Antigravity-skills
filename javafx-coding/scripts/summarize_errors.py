#!/usr/bin/env python3
import sys

IMPORTANT = (
    'loadexception', 'location is not set', 'fx:id', 'onaction',
    'controller', 'not on fx application thread', 'nullpointerexception',
    'exception', 'error', 'failed', 'failure', 'caused by',
    'module', 'javafx.fxml', 'cannot find symbol', 'compilation failure'
)

lines = sys.stdin.read().splitlines()
filtered = []
for line in lines:
    lower = line.lower()
    if any(k in lower for k in IMPORTANT):
        filtered.append(line)

for line in filtered[:120]:
    print(line)

if len(filtered) > 120:
    print(f"... truncated {len(filtered) - 120} more important lines")
