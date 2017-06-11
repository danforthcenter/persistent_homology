#!/bin/bash

# Diagram files are provided as arguments
DIAGRAM1=$1
DIAGRAM2=$2
# Run bottleneck-distance and capture the numeric distance
DISTANCE="$(./bottleneck-distance ${DIAGRAM1} ${DIAGRAM2} | awk '{print $2}')"
# Print out the diagram file names and distance
echo -e "$DIAGRAM1\t$DIAGRAM2\t$DISTANCE"
