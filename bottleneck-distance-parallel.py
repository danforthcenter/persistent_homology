#!/usr/bin/env python

import argparse
import os
from math import ceil


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
    parser.add_argument("-j", "--jobname", help='HTCondor job name. This will be the prefix of multiple output files',
                        required=True)
    parser.add_argument("-o", "--outdir", help="Output directory. Directory will be created if it does not exist.",
                        default=".")
    parser.add_argument("-n", "--numjobs", help="The number of jobs per batch.", default=1000, type=int)
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

    # Job list
    jobs = []

    # Create a job for all diagram file pairs (combinations)
    # For each diagram file
    for i in range(0, len(diagrams)):
        # Create a job with all the remaining diagram files
        for j in range(i + 1, len(diagrams)):
            jobs.append("arguments = " + diagrams[i] + " " + diagrams[j])

    # Create DAGman file
    dagman = open(args.jobname + '.dag', 'w')

    # Job counter
    job = 0

    # Number of batches
    batches = int(ceil(len(jobs) / args.numjobs))

    for batch in range(0, batches):
        # Create job batch file
        fname = args.jobname + ".batch." + str(batch) + ".condor"
        jobfile = open(fname, "w")

        # Initialize jobfile with basic condor configuration
        init_jobfile(jobfile, args.outdir, args.exe, args.group)

        for j in range(job, job + args.numjobs):
            if j == len(jobs):
                break
            jobfile.write("output = $(output_dir)/$(Cluster).$(Process)." + str(j) + ".bottleneck-distance.out\n")
            jobfile.write(jobs[j] + "\n")
            jobfile.write("queue\n\n")
        job += args.numjobs
        jobfile.close()

        # Add job batch file to the DAGman file
        dagman.write("JOB batch" + str(batch) + " " + fname + "\n")

    # Add jobs in serial workflow
    for i in range(0, batches - 1):
        dagman.write("PARENT batch" + str(i) + " CHILD batch" + str(i + 1) + "\n")
    dagman.close()


def init_jobfile(jobfile, outdir, exe, group=None):
    jobfile.write("universe = vanilla\n")
    jobfile.write("request_cpus = 1\n")
    jobfile.write("output_dir = " + outdir + "\n")
    if group:
        # If CONDOR_GROUP was defined, define the job accounting group
        jobfile.write("accounting_group = " + group + '\n')
    jobfile.write("executable = " + exe + '\n')
    jobfile.write("log = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.log\n")
    jobfile.write("error = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.error\n")
    jobfile.write("\n")


if __name__ == '__main__':
    main()
