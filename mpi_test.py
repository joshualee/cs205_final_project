from mpi4py import MPI
import numpy as np
import time
import collections as col
import digraph as pg
from searching import depth_first_search
from find import find

if __name__ == '__main__':
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()
  
  root_graph = None
  
  if rank == 0:
    root_graph = pg.digraph()
    root_graph.add_nodes(["s", "t"])
    root_graph.add_edge(("s", "t"))
    root_graph = {}
    root_graph[1] = 2
  
  graph = comm.bcast(root_graph, root=0)
  
  print "{0}: {1}".format(rank, graph)