# Persistent homology

A collection of scripts for persistent homology analysis.

## Requirements

* [Python 2.7.x](https://www.python.org/)
* [NumPy 1.7.x](http://www.numpy.org/)
* [Argparse 1.4.x](https://pypi.python.org/pypi/argparse)
* bottleneck-distance from [Dionysus](http://www.mrzv.org/software/dionysus/index.html)
* [HTCondor 8.x](https://research.cs.wisc.edu/htcondor/)

## Installation

`git clone https://github.com/danforthcenter/persistent_homology.git`

## Analysis

Diagram files should be stored in their own directory and must each have
a .txt extension. An example setup might look like:

```
- analysis1
  - diagrams
    - diagram0001.txt
    - diagram0002.txt
    ...
    - diagram0100.txt
```

In the analysis1 directory, run the `bottleneck-distance-parallel.py` 
script to create HTCondor job cluster files for batches (default = 1000) 
of `bottleneck-distance` jobs for all pairwise combinations of diagram
files. The output also includes an HTCondor DAG workflow that can be
used to run all job batches automatically.

`bottleneck-distance-parallel.py --dir ./diagrams --jobname analysis1 --outdir ./condor`

Submit the bottleneck-distance jobs to the HTCondor queue.

`condor_submit_dag -notification complete analysis1.dag`

Check on your jobs using `condor_q`. When the jobs are done, the 
analysis1 directory will look like:

```
- analysis1
  - bd.condor.jobs
  - condor
    - 987.1.bottleneck-distance.error
    - 987.1.bottleneck-distance.log
    - 987.1.0.bottleneck-distance.out
    ...
    - 987.100.bottleneck-distance.error
    - 987.100.bottleneck-distance.log
    - 987.100.99.bottleneck-distance.out
  - diagrams
    - diagram0001.txt
    - diagram0002.txt
    ...
    - diagram0100.txt
```

The third number in the .out files is the overall unique job ID.
To create a combined distance matrix, run the `create-matrix.py` script.

`create-matrix.py --diagrams ./diagrams --condor ./condor --matrix analysis1.matrix.csv`
