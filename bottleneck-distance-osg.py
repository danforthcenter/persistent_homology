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
        IOError: if the program run-bottleneck-distance.sh does not exist.
    """

    parser = argparse.ArgumentParser(description="Create bottleneck-distance jobs for HTCondor",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--dir", help="Input directory containing diagram files.", required=True)
    parser.add_argument("-j", "--jobname", help='HTCondor job name. This will be the prefix of multiple output files',
                        required=True)
    parser.add_argument("-n", "--numjobs", help="The number of jobs per batch.", default=100, type=int)
    parser.add_argument("-o", "--outdir", help="Output directory. Directory will be created if it does not exist.",
                        default=".")
    parser.add_argument("-p", "--project", help="OSG project name.", required=True)
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
    run_script = os.path.join(repo_dir, 'run-bottleneck-distance.sh')
    if not os.path.exists(run_script):
        raise IOError("The program run-bottleneck-distance.sh could not be found.")
    else:
        args.script = run_script

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
    # File transfer list
    transfers = []

    # Create a job for all diagram file pairs (combinations)
    # For each diagram file
    for i in range(0, len(diagrams)):
        # Create a job with all the remaining diagram files
        for j in range(i + 1, len(diagrams)):
            transfers.append(",".join(map(str, [args.exe, diagrams[i], diagrams[j]])))
            jobs.append(" ".join(map(str, os.path.basename(diagrams[i]), os.path.basename(diagrams[j]))))

    # Create DAGman file
    dagman = open(args.jobname + '.dag', 'w')

    # Job counter
    job_num = 0

    # Number of batches
    batches = int(ceil(len(jobs) / float(args.numjobs)))

    for batch in range(0, batches):
        # Create job batch (cluster) file
        bname = args.jobname + ".batch." + str(batch) + ".condor"
        batchfile = open(bname, "w")
        # Initialize batch condor file
        create_jobfile(batchfile, args.outdir, args.script, "$(job_args)", "$(transfers)", args.project)

        for job in range(job_num, job_num + args.numjobs):
            if job == len(jobs):
                break
            batchfile.write("job_args = " + jobs[job] + "\n")
            batchfile.write("transfers = " + transfers[job] + "\n")
            batchfile.write("queue\n")
        job_num += args.numjobs

        # Add job batch file to the DAGman file
        dagman.write("JOB batch" + str(batch) + " " + bname + "\n")
    dagman.close()


def create_jobfile(jobfile, outdir, exe, arguments, transfers, project):
    jobfile.write("universe = vanilla\n")
    jobfile.write('requirements = (OSGVO_OS_STRING == "RHEL 6" || OSGVO_OS_STRING == "RHEL 7") && Arch == "X86_64"\n')
    jobfile.write("request_cpus = 1\n")
    jobfile.write("request_memory = 1G\n")
    jobfile.write("output_dir = " + outdir + "\n")
    jobfile.write("+ProjectName = " + project + '\n')
    jobfile.write("executable = " + exe + '\n')
    jobfile.write("arguments = " + arguments + '\n')
    jobfile.write("transfer_executable = true\n")
    jobfile.write("should_transfer_files = YES\n")
    jobfile.write("transfer_input_files = " + transfers + "\n")
    jobfile.write("log = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.log\n")
    jobfile.write("error = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.error\n")
    jobfile.write("output = $(output_dir)/$(Cluster).$(Process).bottleneck-distance.out\n")
    # jobfile.write("queue\n")


if __name__ == '__main__':
    main()
