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
        IOError: if the file diagram1 does not exist.
        IOError: if the file diagram2 does not exist.
    """

    parser = argparse.ArgumentParser(description="Run bottleneck-distance in parallel using HTCondor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--exe", help="Fully-qualified path to the bottleneck-distance executable.", required=True)
    parser.add_argument("--diagram1", help="Filename of the first diagram file.", required=True)
    parser.add_argument("--diagram2", help="Filename of the second diagram file.", required=True)
    args = parser.parse_args()

    # If the input file diagram1 does not exist, stop
    if not os.path.exists(args.diagram1):
        raise IOError("File does not exist: {0}".format(args.diagram1))

    # If the input file diagram2 does not exist, stop
    if not os.path.exists(args.diagram2):
        raise IOError("File does not exist: {0}".format(args.diagram2))

    return args


def main():
    # Parse flags
    args = options()

    output = subprocess.check_output([args.exe, args.diagram1, args.diagram2])
    output = output.rstrip("\n")
    label, distance = output.split(" ")
    print('\t'.join(map(str, [args.diagram1, args.diagram2, distance])))


if __name__ == '__main__':
    main()
