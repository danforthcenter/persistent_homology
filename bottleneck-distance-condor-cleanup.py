#!/usr/bin/env python

import argparse
import os


def options():
    """Parse command line options.

    Args:

    Returns:
        argparse object.
    Raises:
        IOError: if dir does not exist.
        IOError: if the program bottleneck-distance does not exist.
    """

    parser = argparse.ArgumentParser(description="Consolidate the bottleneck-distance outputs from HTCondor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--dir", help="The HTCondor output directory.", required=True)
    parser.add_argument("-o", "--outfile", help="The output filename.", required=True)
    args = parser.parse_args()

    # If the input file of bottleneck-distance jobs does not exist, stop
    if not os.path.exists(args.dir):
        raise IOError("Directory does not exist: {0}".format(args.dir))

    return args


def main():
    # Parse flags
    args = options()

    # Open output file
    out = open(args.outfile, "w")

    # Walk through the input directory and find the condor output files (all *.out files)
    for (dirpath, dirnames, filenames) in os.walk(args.dir):
        for filename in filenames:
            # Is the file a *.out file?
            if filename[-3:] == 'out':
                results = open(filename, 'r')
                out.write(results.read())
                results.close()
    out.close()


if __name__ == '__main__':
    main()