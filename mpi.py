"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usage: mpirun -n 4 python mpi.py <input_file>
input: <input_file> is file path to graph in adjacency list format
output: max flow of input graph

Our MPI Implementation of the Max-Flow algorithm based on Ford-Fulkerson
"""

# Library imports
import sys
sys.path.append('./library/pg')
from mpi4py import MPI
import json
import time
import collections as col
import digraph as pg
from searching import depth_first_search
from find import find

# MPI Setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

"""
extract_key_value returns the key and value from a json encoded line
"""
def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

"""
create_graph converts a graph file in adjacency list format to a 
python-graph directed graph. 
"""
def create_graph(infile_name):
  infile = open(infile_name, "r")
  g = pg.digraph()
  for line in infile:
    u, edges = extract_key_value(line)
    if not g.has_node(str(u)):
      g.add_node(str(u))
    for v, e_c in edges:
      if not g.has_node(str(v)):
        g.add_node(str(v))
      g.add_edge((str(u),str(v)), wt=e_c)
  return g


"""
update_graph updates the edge weights in graph with
the new flow from path
"""
def update_graph(graph, path):
  flow = min(e_c for (u, v, e_c) in path)

  for edge in path:
    u, v, e_c = edge
    forward_edge = (u, v)
    back_edge = (v, u)
    
    # handle forward edge
    forward_weight = graph.edge_weight(forward_edge) - flow
    if forward_weight > 0:
      graph.set_edge_weight(forward_edge, forward_weight)
    elif forward_weight == 0:
      if graph.has_edge(forward_edge):
        graph.del_edge(forward_edge)
    else: # should never happen!
      if rank == 0:
        print "Fatal error: negative edge weight on edge {0}".format(forward_edge)
        sys.exit(-1)
    
    # update back edge as well
    if graph.has_edge(back_edge):
      back_weight = graph.edge_weight(back_edge) + flow
      graph.set_edge_weight(back_edge, back_weight)
    else:
      graph.add_edge(back_edge, wt=flow)

"""
check_path returns true if path is a valid path in
graph (i.e. doesn't violate edge capacities) and
false otherwise
"""
def check_path(graph, path):
  flow = min(e_c for (u, v, e_c) in path)
  for edge in path:
    u, v, e_c = edge
    if not graph.has_edge((u, v)):
      return False
    residue = graph.edge_weight((u, v)) - flow
    if residue < 0:
      return False
  return True

"""
has_cycle returns true if path has a cycle
and false otherwise
"""
def has_cycle(path):
  path_so_far = []  
  for edge in path:
    u, v, e_c = edge
    sources = [u for u, v, e_c in path_so_far]
    if v in sources:
      return True
    path_so_far.append(edge)
  return False

"""
find_path returns a path from node 'source' to 't'
returns None if no path exists
Note: Some path may have a cycle, which is allowed in our implementation 
"""
def find_path(graph, source):
  filt = find("t")
  st, po, _ = depth_first_search(graph, source, filter=filt)
  
  # no path from s -> source -> t exists
  if "t" not in st or not graph.has_edge(("s", source)):
    return None
  else: # construct path from st (spanning tree)
    path = []
    sink = "t"
    while sink != source:
      src = st[sink]
      new_edge = (src, sink, graph.edge_weight((src, sink)))
      path.insert(0, new_edge)
      sink = src
    source_edge = ("s", source, graph.edge_weight(("s", source)))
    path.insert(0, source_edge)
    return path

"""
find_max_flow returns the flow sent across original_graph
using graph as the reference for the residual network
"""
def find_max_flow(original_graph, graph):  
  max_flow = 0
  for edge in original_graph.edges():
    src, sink = edge
    
    # sum flow sent across sink edges to find max-flow
    if sink == "t":
      cap = original_graph.edge_weight(edge)
      if graph.has_edge(edge):
        new_cap = graph.edge_weight(edge)
      else:
        new_cap = 0
      flow = cap - new_cap
      max_flow += flow
      
  return max_flow


"""
copy_graph returns a python-graph copy of graph
"""
def copy_graph(graph):
  new_graph = pg.digraph()
  new_graph.add_nodes(graph.nodes())
  for edge in graph.edges():
    new_graph.add_edge(edge, wt=graph.edge_weight(edge))
  return new_graph

"""
slave is the logic for slave nodes
"""
def slave():
  status = MPI.Status()
  graph, updates, node = None, None, None
  
  while True:
    # receive command from master
    data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
    
    # kill command
    if "die" in data:
      return
    
    # original graph
    if "graph" in data:
      graph = data["graph"]
    
    # graph updates
    if "updates" in data:
      updates = data["updates"]
      for path in updates:
        update_graph(graph, path)
    
    # find new path from 's' -> 'node' -> 't'
    if "node" in data:
      node = data["node"]
      path = find_path(graph, node)
      comm.send((rank, node, path), dest=0)    

"""
master is the logic for master node
"""
def master(infile):
  status = MPI.Status() 
  
  # distribute original graph
  graph = create_graph(infile)
  for i in xrange(1, size):
    comm.send({"graph" : graph}, dest=i)
  
  # create copy of graph
  original_graph = copy_graph(graph)
  
  # initialization
  s_neighbors = graph.neighbors("s")
  waiting_to_send = []
  converge_count = 2 * len(s_neighbors)
  updates = {}
  for i in xrange(1, size):
    updates[i] = []
  
  # no path from s to t
  if len(s_neighbors) == 0:
    for p in xrange(1, size):
      comm.send({"die": 0}, dest=p)
    return 0
  
  # seed jobs
  n = 0
  for i in xrange(1, size):
    node = s_neighbors[n % len(s_neighbors)]
    comm.send({"node" : node}, dest=i)
    waiting_to_send.append(i)
    n += 1
  
  while True:
    # process slave results
    slave_id, node, path = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    waiting_to_send.remove(slave_id)
    
    # process path returns from slave
    if path == None:
      converge_count -= 1
    else:
      if check_path(graph, path):
        update_graph(graph, path)
        
        # set updates for distribution to slaves
        for i in xrange(1, size):
          updates[i].append(path) 
          
        # reset converge count
        converge_count = 2 * len(s_neighbors)
    
    # check for convergence
    if converge_count == 0 or len(s_neighbors) == 0:
      break
    
    # send new job to slave
    new_node = s_neighbors[n % len(s_neighbors)]
    comm.send({"node" : new_node, "updates" : updates[slave_id]}, dest=slave_id)
    waiting_to_send.append(slave_id)
    n += 1

    # reset updates
    updates[slave_id] = []
  
  # kill slave nodes
  for p in waiting_to_send:
    slave_id, node, path = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
  for p in xrange(1, size):
    comm.send({"die": 0}, dest=p)
  
  # find max flow based on residual graph
  max_flow = find_max_flow(original_graph, graph)
  
  return max_flow

def run(infile):
  if rank == 0:
    start_time = MPI.Wtime()
    max_flow = master(infile)
    end_time = MPI.Wtime()
    return max_flow, end_time - start_time
  else:
    slave()
    return None, None

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python serial.py infile"
    sys.exit(-1)
  
  infile = sys.argv[1]
  
  max_flow, time = run(infile)
  if rank == 0:
    print "max flow = {0}".format(max_flow)
    print "time: {0} secs".format(time)
    print max_flow