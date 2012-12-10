# Parallel Max-Flow Min-Cut

We implemented two parallel versions of the Max-Flow Min-Cut algorithm: one in MapReduce and one in MPI. Both implementations are based off the [Ford Fulkerson algorithm](http://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm). We use the MapReduce version to perform binary image segmentation (separating background from foreground). We also did a serial implementation to give us a baseline for timing.

## Project Information 

**Team:** Joshua Lee and Mona Huang

**Teaching Fellow:** Verena Kaynig-Fittkau

**Class:** CS205, Harvard University, Fall 2012

## Basic Usage

All dependencies are located locally inside the project directory. There should not be any required steps for setup. If you run into issues, see the *dependencies* section below.

Binary Image Segmentation. Relabels foreground as black and background as white using our map reduce min cut algorithm (outputs binary image):

	python segment.py <input_image_path> <output_image_path>

Map Reduce Max-Flow (returns max-flow):

	python driver.py <in_file_path>

MPI Max-Flow (returns max-flow):

	mpirun -n 4 python mpi.py <in_file_path>

Serial Max-Flow (returns max-flow):
	
	python serial.py <in_file_path>

* See header comments in files for more in-depth description.
* `input_image_path` is a path to .jpg or .png
* `in_file_path` is graph in adjacency list format (see "graph file format" section for example)
* You can find test graphs in the graphs directory.

## Files Summary
See header comments in files for more in-depth description.

### MapReduce
`driver.py` is the driver for our MapReduce max-flow implementation. It handles file to graph conversation, reading/writing intermediate output between MapReduce iterations, and calculating the max flow and cut of the residual graph.

`max_flow.py` is the MRJob class used by `driver.py`

`accumulator.py` is a helper class used by `max_flow.py`. It is responsible for ensuring we accept only valid paths that do not violate any capacity constraints.

### MPI
`mpi.py` is our MPI max-flow implementation

### Image Segmentation
`segment.py` segments foreground and background of input image using MapReduce max-flow implementation.

`image_processor.py` is a helper file used by `segment.py` to convert an image into a graph file in adjacency list format.

### Testing/Timing

`serial.py` is our max-flow serial implementation

`test.py` uses a python-graph library to implement the max-flow algorithm. Used for testing. 

`timing.py` runs the serial, MapReduce, and MPI max-flow implementations on various graphs. Serves as a testing and timing module.

### Directories

`graphs/` directory for sample input graphs for max flow

`images/` directory for sample input images for segmentation

`tmp/` directory for temporary files used by segment.py and driver.py (e.g. intermediate mapreduce input/output)

`scripts/` directory for helper scripts e.g. test graph generation

`docs/` directory helper documents e.g. papers describing max flow min cut algorithm

`library/` directory for external libraries

## Dependencies

### Internal Libraries
These packages came preinstalled on the CS205 VirtualBox and are readily available on Resonance Nodes.

* [mpi4py](http://mpi4py.scipy.org/)
* [mrjob](http://packages.python.org/mrjob/)

### External Libraries
We have placed these dependencies in our project's library directory. Our project imports these local files, so you should not get any import errors.

* [python-graph](http://code.google.com/p/python-graph/)

If you do run into import errors from python-graph, you may have to run the following install command from our project root directory. You will need sudo permissions:

	cd project_root
	cd library/python-graph/core/
	sudo python setup.py install

## Graph File Format

### Format

	"vertex_id" \t [["neighbor_id_1", edge_capacity_1], ["neighbor_id_2", edge_capacity_2], ...]
	
Note these (key, value) pairs must be tab separated or our JSON reader won't work.

### Example

	"s"	[["1", 2], ["2", 2]]
	"0"	[["s", 7], ["t", 4], ["1", 3], ["2", 1]]
	"1"	[["s", 6], ["t", 2]]
	"2"	[["s", 10], ["0", 8], ["1", 2]]
	"t"	[]