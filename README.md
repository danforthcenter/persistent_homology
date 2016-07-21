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
script to create an HTCondor job cluster file that will queue 
`bottleneck-distance` jobs for all pairwise combinations of diagram
files.

`bottleneck-distance-parallel.py --dir ./diagrams --jobfile bd.condor.jobs --outdir ./condor`

Submit the bottleneck-distance jobs to the HTCondor queue.

`condor_submit bd.condor.jobs`

Check on your jobs using `condor_q`. Your jobs will share a common 
cluster ID and a separate process ID per job (e.g. 987.1, 987.2, etc.). 
When the jobs are done, the analysis1 will look like:

```
- analysis1
  - bd.condor.jobs
  - condor
    - 987.1.bottleneck-distance.error
    - 987.1.bottleneck-distance.log
    - 987.1.bottleneck-distance.out
    ...
    - 987.100.bottleneck-distance.error
    - 987.100.bottleneck-distance.log
    - 987.100.bottleneck-distance.out
  - diagrams
    - diagram0001.txt
    - diagram0002.txt
    ...
    - diagram0100.txt
```

To create a combined distance matrix, run the `create-matrix.py` script.

`create-matrix.py --diagrams ./diagrams --condor ./condor --matrix analysis1.matrix.csv`
