from mpi4py import MPI
import json
import sys
import numpy as np
import time
import collections as col
import digraph as pg
from searching import depth_first_search
from find import find

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

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

def update_graph(graph, path):
  # print "{0}: (0, s) -> {1}".format(rank, graph.edge_weight(("0", "s")))
  
  # if rank == 0:
    # print "Performing update..."
    # print "path: {0}".format(path)
  
  flow = min(e_c for (u, v, e_c) in path)
  # if rank == 0:
  #   print "f: {0}".format(flow)
  # print "flow={0}".format(flow)

  for edge in path:
    u, v, e_c = edge
    forward_edge = (u, v)
    back_edge = (v, u)
    
    forward_weight = graph.edge_weight(forward_edge) - flow

    if forward_weight > 0:
      graph.set_edge_weight(forward_edge, forward_weight)
    elif forward_weight == 0:
      if graph.has_edge(forward_edge):
        graph.del_edge(forward_edge)
    else:
      if rank == 0:
        print "Fatal error: negative edge weight on edge {0}".format(forward_edge)
        sys.exit(-1)
    
    if graph.has_edge(back_edge):
      back_weight = graph.edge_weight(back_edge) + flow
      graph.set_edge_weight(back_edge, back_weight)
    else:
      graph.add_edge(back_edge, wt=flow)

def check_path(graph, path):
  flow = min(e_c for (u, v, e_c) in path)
  for edge in path:
    u, v, e_c = edge
    if not graph.has_edge((u, v)):
      return False
    
    residue = graph.edge_weight((u, v)) - flow
    
    # if graph.edge_weight((u, v)) != e_c:
    #   print "DIFFFFFF :("
    
    if residue < 0:
      return False

  return True

def has_cycle(path):
  path_so_far = []
  
  for edge in path:
    u, v, e_c = edge
    sources = [u for u, v, e_c in path_so_far]
    if v in sources:
      return True
    path_so_far.append(edge)
    
  return False

def find_path(graph, source):
  # temporarily remove edge from source to "s" to prevent cycles
  # temp_edge = (source, "s")
  # has_edge = graph.has_edge(temp_edge)
  # 
  # if has_edge:
  #   wt = graph.edge_weight(temp_edge)
  #   graph.del_edge(temp_edge)
    
  filt = find("t")
  st, po, _ = depth_first_search(graph, source, filter=filt)
  
  # if has_edge:
  #   graph.add_edge(temp_edge, wt=wt)
  
  if "t" not in st or not graph.has_edge(("s", source)):
    return None
  else:
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

def find_max_flow(original_graph, graph):  
  max_flow = 0
  for edge in original_graph.edges():
    src, sink = edge
    if sink == "t":
      cap = original_graph.edge_weight(edge)
      if graph.has_edge(edge):
        new_cap = graph.edge_weight(edge)
      else:
        new_cap = 0
      flow = cap - new_cap
      max_flow += flow
  return max_flow

def copy_graph(graph):
  new_graph = pg.digraph()
  new_graph.add_nodes(graph.nodes())
  for edge in graph.edges():
    new_graph.add_edge(edge, wt=graph.edge_weight(edge))
  return new_graph

def slave():
  status = MPI.Status()
  graph, updates, node = None, None, None
  
  while True:
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
    
    if "node" in data:
      node = data["node"]
      path = find_path(graph, node)
      comm.send((rank, node, path), dest=0)    
  
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
      
    if converge_count == 0:
      st, _, _ = depth_first_search(graph, "s")
      if "t" not in st:
        break
      else:
        converge_count = 2 * len(s_neighbors)
                  
    new_node = s_neighbors[n % len(s_neighbors)]
    comm.send({"node" : new_node, "updates" : updates[slave_id]}, dest=slave_id)
    waiting_to_send.append(slave_id)
    
    # reset updates
    updates[slave_id] = []
    n += 1
  
  for p in waiting_to_send:
    slave_id, node, path = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    
  for p in xrange(1, size):
    comm.send({"die": 0}, dest=p)

  max_flow = find_max_flow(original_graph, graph)
  
  return max_flow

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python serial.py infile"
    sys.exit(-1)
  
  infile = sys.argv[1]
  
  if rank == 0:
    start_time = MPI.Wtime()
    max_flow = master(infile)
    end_time = MPI.Wtime()
    print "max flow = {0}".format(max_flow)
    print "Time: %f secs" % (end_time - start_time)
  else:
    slave()