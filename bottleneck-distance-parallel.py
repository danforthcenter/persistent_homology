#!/usr/bin/env python

import argparse
import os
import sys
from math import ceil


def options():
    """Parse command line options.

    Args:

    Returns:
        argparse object.
    Raises:
        IOError: if dir does not exist.
        IOError: if the program bottleneck-distance does not exist.
        IOError: if the program run-bottleneck-distance.py does not exist.
        IOError: if the program bottleneck-distance-condor-cleanup.py does not exist.
        IOError: if the program create-matrix.py does not exist.
    """

    parser = argparse.ArgumentParser(description="Create bottleneck-distance jobs for HTCondor",
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
        raise IOError("The executable bottleneck-distance could not be found.")

    # Convert the output directory to an absolute path
    args.outdir = os.path.abspath(args.outdir)

    # If the output directory does not exist, make it
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    # Find the script run-bottleneck-distance.py or stop
    repo_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    run_script = os.path.join(repo_dir, 'run-bottleneck-distance.py')
    if not os.path.exists(run_script):
        raise IOError("The program run-bottleneck-distance.py could not be found.")
    else:
        args.script = run_script

    # Find the script bottleneck-distance-condor-cleanup.py or stop
    clean_script = os.path.join(repo_dir, 'bottleneck-distance-condor-cleanup.py')
    if not os.path.exists(clean_script):
        raise IOError("The program bottleneck-distance-condor-cleanup.py could not be found.")
    else:
        args.clean = clean_script

    # Find the script create-matrix.py or stop
    matrix_script = os.path.join(repo_dir, 'create-matrix.py')
    if not os.path.exists(matrix_script):
        raise IOError("The program create-matrix.py could not be found.")
    else:
        args.matrix = matrix_script

    # Get the value of the CONDOR_GROUP environmental variable, if defined
    args.group = os.getenv('CONDOR_GROUP')

    return args


def main():
    # Parse flags
    args = options()

    # Create cleanup script condor job file
    cleanfile = args.jobname + ".cleanup.condor"
    clean = open(cleanfile, "w")
    cleanargs = "--dir " + args.outdir + " --outfile " + args.jobname + ".bottleneck-distance.results.txt"
    create_jobfile(clean, args.outdir, args.clean, cleanargs, args.group)
    clean.close()

    # Create matrix script condor job file
    matrixfile = args.jobname + ".matrix.condor"
    matrix = open(matrixfile, "w")
    matrixargs = "--file " + args.jobname + ".bottleneck-distance.results.txt " + \
                 "--matrix " + args.jobname + ".matrix.csv"
    create_jobfile(matrix, args.outdir, args.matrix, matrixargs, args.group)
    matrix.close()

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
            jobs.append(args.exe + " " + diagrams[i] + " " + diagrams[j])

    # Create DAGman file
    dagman = open(args.jobname + '.dag', 'w')
    dagman.write("JOB clean " + cleanfile + "\n")
    dagman.write("JOB matrix " + matrixfile + "\n")

    # Job counter
    job = 0

    # Number of batches
    batches = int(ceil(len(jobs) / float(args.numjobs)))

    for batch in range(0, batches):
        # Create job batch file
        bname = args.jobname + ".batch." + str(batch) + ".txt"
        batchfile = open(bname, "w")

        # Create condor job file
        fname = args.jobname + ".batch." + str(batch) + ".condor"
        jobfile = open(fname, "w")

        jobargs = "--batchfile " + bname

        # Initialize jobfile with basic condor configuration
        create_jobfile(jobfile, args.outdir, args.script, jobargs, args.group)

        jobfile.close()

        for j in range(job, job + args.numjobs):
            if j == len(jobs):
                break
            batchfile.write(jobs[j] + "\n")
        job += args.numjobs

        # Add job batch file to the DAGman file
        dagman.write("JOB batch" + str(batch) + " " + fname + "\n")

    # Add jobs in serial workflow
    for i in range(0, batches):
        dagman.write("PARENT batch" + str(i) + " CHILD clean\n")
    dagman.write("PARENT clean CHILD matrix\n")
    dagman.close()


def create_jobfile(jobfile, outdir, exe, arguments, group=None):
    jobfile.write("universe = vanilla\n")
    jobfile.write("getenv = true\n")
    jobfile.write("request_cpus = 1\n")
    jobfile.write("output_dir = " + outdir + "\n")
    if group:
        # If CONDOR_GROUP was defined, define the job accounting group
        jobfile.write("accounting_group = " + group + '\n')
    jobfile.write("executable = " + exe + '\n')
    jobfile.write("arguments = " + arguments + '\n')
    jobfile.write("log = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.log\n")
    jobfile.write("error = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.error\n")
    jobfile.write("output = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.out\n")
    jobfile.write("queue\n")


if __name__ == '__main__':
    main()
