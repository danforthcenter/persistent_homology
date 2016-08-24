#!/usr/bin/env python

import argparse
import os
import numpy as np


def options():
    """Parse command line options.

    Args:

    Returns:
        argparse object.
    Raises:
        IOError: if file does not exist.
    """

    parser = argparse.ArgumentParser(description="Create a matrix from bottleneck-distance output.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file", help="Combined distance results file.", required=True)
    parser.add_argument("-m", "--matrix", help="Output matrix file.", required=True)
    args = parser.parse_args()

    # If the input directory of diagram files does not exist, stop
    if not os.path.exists(args.file):
        raise IOError("File does not exist: {0}".format(args.file))

    return args


def main():
    # Parse flags
    args = options()

    # Create unique dictionary of diagram names
    diagrams = {}
    # Store distance of diagram pairs in dictionary
    pairs = {}

    # Read through the results file
    results = open(args.file, 'r')
    for result in results:
        # Remove the newline
        result = result.rstrip("\n")
        # Split each result into the names of diagram 1 and 2 and the distance
        diagram1, diagram2, distance = result.split("\t")
        # Get the file names of diagrams 1 and 2
        d1 = os.path.basename(diagram1)
        d2 = os.path.basename(diagram2)

        # Extract the diagram number out of the filenames
        # Remove extension
        d1 = d1[:-4]
        d2 = d2[:-4]

        # Split on the word diagram
        parts1 = d1.split("diagram")
        parts2 = d2.split("diagram")

        # The numbers should be the last element
        n1 = int(parts1[-1])
        n2 = int(parts2[-1])

        # Store the diagram numbers in the dictionary
        diagrams[n1] = 1
        diagrams[n2] = 1
        # Store the distance for each pair
        pairs[str(n1) + ":" + str(n2)] = distance
    results.close()

    # Create a numeric list of all the diagram numbers
    nums = np.array(diagrams.keys())

    # Create an empty numpy matrix with dimensions equal to the maximum diagram value
    # Note that if diagram numbering starts > 1, there will be empty columns and rows at the left side of the matrix
    matrix = np.zeros((np.max(nums), np.max(nums)))

    # Loop over each diagram pair
    for pair in pairs.keys():
        # Split the diagram pair into component diagrams, numeric values
        # Note that the matrix is zero-indexed, so 1 is subtracted from each input diagram number
        d1, d2 = pair.split(":")
        d1 = int(d1) - 1
        d2 = int(d2) - 1
        # Store the distance number as a float at the numeric location of each diagram
        matrix[d1][d2] = float(pairs[pair])

    # Save the numpy distance matrix
    np.savetxt(args.matrix, matrix, fmt="%.2f", delimiter=",")


if __name__ == '__main__':
    main()
