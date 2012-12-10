# Parallel Max-Flow Min-Cut

We implemented two parallel versions of the Max-Flow Min-Cut algorithm: one in MapReduce and one in MPI. Both implementations are based off the [Ford Fulkerson algorithm](http://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm). We use the MapReduce version to perform binary image segmentation (separating background from foreground). We also did a serial implementation to give us a baseline for timing.

## Project Information 

Team: Joshua Lee and Mona Huang

Teaching Fellow: Verena Kaynig-Fittkau

Class: CS205, Harvard University, Fall 2012

## Basic Usage

Binary Image Segmentation. Relabels foreground as black and background as white using our map reduce min cut algorithm:

	python segment.py <input_image_path> <output_image_path>

Map Reduce Max-Flow:

	python driver.py <in_file_path>

MPI Max-Flow:

	mpirun -n 4 python mpi.py <in_file_path>

Serial Max-Flow:
	
	python serial.py <in_file_path>

* <input_image_path> is a path to .jpg or .png
* <in_file_path> is graph in adjacency list format (see "graph file format" section for example)
* You can find test graphs in the graphs directory.

File Summary
See header comments in each file for more in-depth description.

MAP REDUCE
`driver.py`
Driver for map-reduce max-flow algorithm. Handles graph conversation, and 

`max_flow.py`
MRJob class used for parallel max flow

`accumulator.py`
Accumulator class used by our MRJob class. Responsible for ensuring 

MPI
mpi.py

IMAGE SEGMENTATION
image_processor.py

segment.py

TESTING

timing.py

test.py

serial.py
our max flow serial implementation

DIRECTORIES

graphs/
directory for sample input graphs for max flow

images/
directory for sample input images for segmentation

tmp/
directory for temporary files used by segment.py and driver.py (e.g. intermediate mapreduce input/output)

scripts/
directory for helper scripts e.g. test graph generation

docs/
directory helper documents e.g. papers describing max flow min cut algorithm

library/
directory for external libraries

Internal Libraries
These packages came preinstalled on the CS205 VirtualBox and are readily available on Resonance Nodes.

mpi4py (http://mpi4py.scipy.org/)
mrjob (http://packages.python.org/mrjob/)
numpy

External Libraries
We have placed these dependencies in our project's library directory. Our project imports these local files, so you should not get any import errors.

python-graph (http://code.google.com/p/python-graph/)

If you do run into import errors from python-graph, you may have to run the following install command from our project root directory. You will need sudo permissions.

<from project root>
cd library/python-graph/core/
sudo python setup.py install