#!/usr/bin/env python

import argparse
import os
import subprocess


def options():
    """Parse command line options.

    Args:

    Returns:
        argparse object.
    Raises:
        IOError: if dir does not exist.
        IOError: if the program bottleneck-distance does not exist.
    """

    parser = argparse.ArgumentParser(description="Run bottleneck-distance in parallel using HTCondor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b", "--batchfile", help="Bottleneck-distance job batch file.", required=True)
    args = parser.parse_args()

    # If the input file of bottleneck-distance jobs does not exist, stop
    if not os.path.exists(args.batchfile):
        raise IOError("File does not exist: {0}".format(args.batchfile))

    # If the program bottleneck-distance cannot be found in PATH, stop
    args.exe = os.popen("which bottleneck-distance").read().strip()
    if len(args.exe) == 0:
        raise IOError("The executable bottleneck-distance could not be found")

    return args


def main():
    # Parse flags
    args = options()

    # Open batch file
    batch = open(args.batchfile, 'r')
    for job in batch:
        job = job.rstrip("\n")
        exe, diagram1, diagram2 = job.split(" ")
        output = subprocess.check_output([exe, diagram1, diagram2])
        output = output.rstrip("\n")
        label, distance = output.split(" ")
        print('\t'.join(map(str, [diagram1, diagram2, distance])))


if __name__ == '__main__':
    main()