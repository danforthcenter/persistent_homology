#!/usr/bin/env python

import os
import re
import argparse
import mimetypes
import itertools
import dionysus
import scipy.special
import numpy as np
from dask_jobqueue import HTCondorCluster
from dask.distributed import Client, progress


def options():
    """Parse command line options.

    Args:

    Returns:
        argparse object.
    """

    parser = argparse.ArgumentParser(description="Calculates pairwise distances between persistence diagrams.")
    parser.add_argument("-d", "--dir", help="Directory containing persistance diagrams.", required=True)
    parser.add_argument("-o", "--outfile", help="The output matrix filename.", required=True)
    parser.add_argument("-m", "--method", help="Distance method (bottlebeck or wasserstein", default="bottleneck")
    parser.add_argument("-q", "--wasserstein_q", help="Wasserstein q parameter (ignored by bottleneck distance)",
                        default=2, type=int)
    args = parser.parse_args()

    # Valid distance metrics
    valid_methods = ["bottleneck", "wasserstein"]
    if args.method.lower() not in valid_methods:
        raise RuntimeError(f"The method {args.method} is not valid. Only bottleneck and wasserstein are supported.")

    return args


def read_diagram(file):
    # Initialize empty list of birth/death pairs
    dgm_pts = []
    with open(file, "r") as fh:
        # Loop over each birth/death pair of the persistence diagram
        for line in fh:
            # Remove newline characters
            line.rstrip("\n")
            # Split birth and death values by a space
            birth, death = line.split(" ")
            # Append the birth and death values as a tuple to the diagram list
            dgm_pts.append((float(birth), float(death)))
    # Create a persistence diagram
    dgm = dionysus.Diagram(dgm_pts)
    return dgm


def distance(diagram1, diagram2, method, q):
    """Calculate distance between two diagrams.
    Inputs:
    diagram1 - Dictionary of the name and path of a diagram.
    diagram2 - Dictionary of the name and path of a diagram.
    method   - "bottleneck" or "wasserstein" distance metric.
    q        - Wasserstein q parameter (ignored by bottleneck-distance).

    :param diagram1: dict
    :param diagram2: dict
    :param method: str
    :param q: int
    """
    # Import diagrams as Dionysus Diagram objects
    dgm1 = read_diagram(file=diagram1["path"])
    dgm2 = read_diagram(file=diagram2["path"])
    # Calculate distance metric
    if method.lower() == "bottleneck":
        dist = dionysus.bottleneck_distance(dgm1, dgm2)
    elif method.lower() == "wasserstein":
        dist = dionysus.wasserstein_distance(dgm1, dgm2, q)
    return diagram1["id"], diagram2["id"], dist


def main():
    # Parse flags
    args = options()

    # Configure HTCondor cluster
    cluster = HTCondorCluster(
        cores=1,
        memory="1GB",
        disk="1GB",
        local_directory="$_CONDOR_SCRATCH_DIR",
        job_name="dionysus"
    )

    # Collect diagram filenames
    diagrams = []

    # Regular expression pattern
    pat = re.compile("diagram0*")

    # Walk through the input directory and find the diagram files (all text files)
    diagram_n = 0
    for (dirpath, dirnames, filenames) in os.walk(args.dir):
        for filename in filenames:
            # Is the file a text file?
            if 'text/plain' in mimetypes.guess_type(filename):
                diagram_n += 1
                # Extract diagram ID
                dgm_id = os.path.splitext(filename)[0]
                dgm_id = re.sub(pat, "", dgm_id)
                dgm_id = int(dgm_id)
                # Create a dictionary to store the diagram name and path
                diagram = {
                    "id": dgm_id,
                    "path": os.path.join(os.path.abspath(dirpath), filename)
                }
                # Append the diagram to the list of diagrams
                diagrams.append(diagram)

    # Get all pairwise combinations of diagrams
    pairs = itertools.combinations(diagrams, 2)
    total_pairs = scipy.special.comb(diagram_n, 2, exact=True, repetition=False)

    # Configure number of workers
    max_workers = 200
    if total_pairs < max_workers:
        max_workers = total_pairs
    cluster.scale(jobs=max_workers)
    client = Client(cluster)

    # List of job futures
    processed = []
    for pair in pairs:
        # Submit each job
        inputs = {"diagram1": pair[0], "diagram2": pair[1], "method": args.method, "q": args.wasserstein_q}
        processed.append(client.submit(distance, **inputs))
    # Watch jobs and print progress bar
    progress(processed)
    results = client.gather(processed)

    # Create an empty numpy matrix with dimensions equal to the maximum diagram value
    matrix = np.zeros((diagram_n, diagram_n))

    for dgm1, dgm2, dist in results:
        # Store the distance number as a float at the numeric location of each diagram
        matrix[dgm1 - 1][dgm2 - 1] = dist

    # Save the numpy distance matrix
    np.savetxt(args.outfile, matrix, fmt="%.2f", delimiter=",")
    print("\n")


if __name__ == '__main__':
    main()
