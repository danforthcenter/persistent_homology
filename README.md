# Persistent homology

A collection of scripts for persistent homology analysis.

## Requirements

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), then create a new environment:

```bash
conda create -n persistent-homology python=3.7 dionysus numpy scipy dask-jobqueue
```

## Installation

`git clone https://github.com/danforthcenter/persistent_homology.git`

## Analysis

Diagram files should be stored in their own directory. An example setup might look like:

```
  - diagrams
    - diagram0001.txt
    - diagram0002.txt
    ...
    - diagram0100.txt
```

A workflow script will import the diagrams into [Dionysus](https://mrzv.org/software/dionysus2/) and calculate
all combinations of pairwise distances. The workflow script uses Dask to run the calculation jobs in the
HTCondor cluster and aggregates the results into an output matrix file.

```
usage: wf.persistence-diagram-pairwise-distance.py [-h] -d DIR -o OUTFILE
                                                   [-m METHOD]
                                                   [-q WASSERSTEIN_Q]

Calculates pairwise distances between persistence diagrams.

optional arguments:
  -h, --help                     show this help message and exit
  -d DIR, --dir DIR              Directory containing persistance diagrams.
  -o OUTFILE, --outfile OUTFILE  The output matrix filename.
  -m METHOD, --method METHOD     Distance method (bottlebeck or wasserstein
  -q WASSERSTEIN_Q, --wasserstein_q WASSERSTEIN_Q
                                 Wasserstein q parameter (ignored by bottleneck distance)
```

To run the workflow:

* Log into `stargate` with a persistent session
  * Option 1: log in using [mosh](https://mosh.org/).
  * Option 2: run `screen` after logging in.
  * Option 3: run `tmux` after logging in.
* Activate the conda environment: `conda activate persistent-homology`
* Run the workflow

### Examples

#### Bottleneck distance
```bash
wf.persistence-diagram-pairwise-distance.py -d ./diagrams -o bdist.txt
```

#### Wasserstein distance

```bash
wf.persistence-diagram-pairwise-distance.py -d ./diagrams -o 2-wdist.txt -m wasserstein
```

#### Wasserstein distance with a modified q parameter

```bash
wf.persistence-diagram-pairwise-distance.py -d ./diagrams -o 1-wdist.txt -m wasserstein -q 1
```
