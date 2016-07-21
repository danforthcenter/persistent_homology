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
        IOError: if dir diagrams does not exist.
        IOError: if dir condor does not exist.
    """

    parser = argparse.ArgumentParser(description="Create a matrix from bottleneck-distance output.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--diagrams", help="Input directory containing diagram files.", required=True)
    parser.add_argument("-c", "--condor", help='Input directory containing HTCondor output files.', required=True)
    parser.add_argument("-m", "--matrix", help="Output matrix file.", required=True)
    args = parser.parse_args()

    # If the input directory of diagram files does not exist, stop
    if not os.path.exists(args.diagrams):
        raise IOError("Directory does not exist: {0}".format(args.diagrams))

    # If the input directory of HTCondor files does not exist, stop
    if not os.path.exists(args.condor):
        raise IOError("Directory does not exist: {0}".format(args.condor))

    return args


def main():
    # Parse flags
    args = options()

    # Collect diagram filenames
    diagrams = []
    files = {}

    # Walk through the input directory and find the diagram files (all *.txt files)
    for (dirpath, dirnames, filenames) in os.walk(args.diagrams):
        for i, filename in enumerate(filenames):
            # Is the file a *.txt file?
            if filename[-3:] == 'txt':
                diagrams.append(filename)
                files[filename] = i

    # Number the jobs for all diagram file pairs (combinations)
    jobs = []
    # For each diagram file
    for i in range(0, len(diagrams)):
        # Create a job with all the remaining diagram files
        for j in range(i + 1, len(diagrams)):
            jobs.append([diagrams[i], diagrams[j]])

    # Retrieve the distances from the condor output files
    for (dirpath, dirnames, filenames) in os.walk(args.condor):
        for filename in filenames:
            # Is the file an HTCondor stdout file?
            if filename[-3:] == 'out':
                # Get the process ID from the filename
                cluster, process, label, extension = filename.split(".")
                # Open the file and get the distance
                result = open(os.path.join(dirpath, filename), 'r')
                distance = result.readline().strip()
                distance = distance.replace("Distance: ", "")

                # Convert process into a job index
                process = int(process)
                jobs[process].append(distance)

    # Create HTCondor job file
    matrix = np.zeros((len(diagrams), len(diagrams)))
    for job in jobs:
        i = files[job[0]]
        j = files[job[1]]
        d = job[2]
        print(' '.join(map(str, [i, j])))
        matrix[i][j] = float(d)

    np.savetxt(args.matrix, matrix, fmt="%.1e", delimiter=",")


if __name__ == '__main__':
    main()
