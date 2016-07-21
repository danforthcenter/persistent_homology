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

    parser = argparse.ArgumentParser(description="Run bottleneck-distance in parallel using HTCondor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--dir", help="Input directory containing diagram files.", required=True)
    parser.add_argument("-j", "--jobfile", help='HTCondor job file.', required=True)
    parser.add_argument("-o", "--outdir", help="Output directory. Directory will be created if it does not exist.",
                        default=".")
    args = parser.parse_args()

    # If the input directory of diagram files does not exist, stop
    if not os.path.exists(args.dir):
        raise IOError("Directory does not exist: {0}".format(args.dir))

    # If the program bottleneck-distance cannot be found in PATH, stop
    args.exe = os.popen("which bottleneck-distance").read().strip()
    if len(args.exe) == 0:
        raise IOError("The executable bottleneck-distance could not be found")

    # Convert the output directory to an absolute path
    args.outdir = os.path.abspath(args.outdir)

    # If the output directory does not exist, make it
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    # Get the value of the CONDOR_GROUP environmental variable, if defined
    args.group = os.getenv('CONDOR_GROUP')

    return args


def main():
    # Parse flags
    args = options()

    # Collect diagram filenames
    diagrams = []

    # Walk through the input directory and find the diagram files (all *.txt files)
    for (dirpath, dirnames, filenames) in os.walk(args.dir):
        for filename in filenames:
            # Is the file a *.txt file?
            if filename[-3:] == 'txt':
                diagrams.append(os.path.join(os.path.abspath(dirpath), filename))

    # Create HTCondor job file
    condor = open(args.jobfile, 'w')
    condor.write("universe = vanilla\n")
    condor.write("request_cpus = 1\n")
    condor.write("output_dir = " + args.outdir + "\n")
    if args.group:
        # If CONDOR_GROUP was defined, define the job accounting group
        condor.write("accounting_group = " + args.group + '\n')
    condor.write("executable = " + args.exe + '\n')
    condor.write("log = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.log\n")
    condor.write("output = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.out\n")
    condor.write("error = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.error\n")
    condor.write("\n")

    # Create a job for all diagram file pairs (combinations)
    # For each diagram file
    for i in range(0, len(diagrams)):
        # Create a job with all the remaining diagram files
        for j in range(i + 1, len(diagrams)):
            condor.write("arguments = " + diagrams[i] + " " + diagrams[j] + "\n")
            condor.write("queue\n\n")


if __name__ == '__main__':
    main()
