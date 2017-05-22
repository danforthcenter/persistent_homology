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
script to create HTCondor DAG and job cluster files for batches (default = 100) 
of `bottleneck-distance` jobs for all pairwise combinations of diagram
files. The output also includes an HTCondor DAG workflow that can be
used to run all job batches automatically.

`bottleneck-distance-parallel.py --dir ./diagrams --jobname analysis1 --outdir ./condor --numjobs 100`

Submit the bottleneck-distance jobs to the HTCondor queue.

`condor_submit_dag -notification complete analysis1.dag`

Check on your jobs using `condor_q`.

The DAG workflow will run an instance of `run-bottleneck-distance.py` 
for each batch, in parallel. Once all `run-bottleneck-distance.py` jobs
are complete, DAG will run a single 
`bottleneck-distance-condor-cleanup.py` job to pool all the batch 
results together into a single output. Finally, DAG will run a single
`create-matrix.py` job to read the combined results file and output the
final distance matrix.
