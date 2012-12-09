from mpi4py import MPI
import json
import sys
import numpy as np
import time
import collections as col
import digraph as pg
from searching import depth_first_search
from find import find

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
    if not g.has_node(u):
      g.add_node(u)
    for v, e_c in edges:
      if not g.has_node(v):
        g.add_node(v)
      g.add_edge((u,v), wt=e_c)
  return g

def update_graph(graph, path):
  flow = min(e_c for (e, v, e_c) in path)
  for edge in path:
    u, v, e_c = edge
    new_weight = e_c - flow
    if new_weight > 0:
      forward_edge = (u, v)
      back_edge = (v, u)
      
      graph.set_edge_weight(forward_edge, new_weight)
      if graph.has_edge(back_edge):
        back_weight = graph.edge_weight(back_edge) + flow
        graph.set_edge_weight(back_edge, back_weight)
      else:
        graph.add_edge(back_edge, wt=flow)
    elif new_weight == 0:
      if graph.has_edge(forward_edge):
        graph.del_edge(forward_edge)

def check_path(graph, path):
  print path
  flow = min(e_c for (e, v, e_c) in path)
  for edge in path:
    u, v, e_c = edge
    if not graph.has_edge((u, v)):
      return False
    
    residue = graph.edge_weight((u, v)) - flow
    if residue < 0:
      return False
  
  return True
    
def find_path(graph, source):
  filt = find("t")
  st, _, _ = depth_first_search(graph, source, filter=filt)
  if "t" not in st:
    return None
  else:
    path = []
    sink = "t"
    while sink != source:
      print "sink={0}".format(sink)
      print "st={0}".format(st)
      src = st[sink]
      new_edge = (src, sink, graph.edge_weight((src, sink)))
      path.insert(0, new_edge)
      sink = src
    return path

def find_max_flow(original_graph, graph):
  max_flow = 0
  s_neighbors = original_graph.neighbors("s")
  for v in s_neighbors:      
    edge = ("s", v)
    original_capacity = original_graph.edge_weight(edge)
    if graph.has_edge(edge):
      new_capacity = graph.edge_weight(edge)
    else:
      new_capacity = 0
    
    flow = original_capacity - new_capacity
    max_flow += flow
    
  return max_flow

def copy_graph(graph):
  new_graph = pg.digraph()
  new_graph.add_nodes(graph.nodes())
  for edge in graph.edges():
    new_graph.add_edge(edge, wt=graph.edge_weight(edge))
  return new_graph

def slave(comm):
  rank = comm.Get_rank()
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
  
def master(comm, infile):
  size = comm.Get_size()
  status = MPI.Status() 
  
  # distribute original graph
  graph = create_graph(infile)
  for i in xrange(1, size):
    comm.send({"graph" : graph}, dest=i)
  
  # create copy of graph
  original_graph = copy_graph(graph)
  
  s_neighbors = graph.neighbors("s")
  print "original s_neighbors: {0}".format(s_neighbors)
  n_count = len(s_neighbors)
  
  # seed jobs
  n = 0
  
  for i in xrange(1, size):
    node = s_neighbors[n % n_count]
    comm.send({"node" : node}, dest=i)
    n += 1
  
  updates = {}
  for i in xrange(1, size):
    updates[i] = []
  
  active = s_neighbors[:]
  active_p = [i for i in xrange(1, size)]
  while len(s_neighbors) != 0:
    # process slave results
    slave_id, node, path = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    active_p.remove(slave_id)
    if path != None:
    #   # deactivate dead nodes
    #   if node in active:
    #     active.remove(node)
    # else:
    #   # reactivate live nodes
    #   if node not in active:
    #     active.insert(node)
    #   
      v, _, _ = path[0]
      if graph.has_edge(("s", v)):
        s_edge = ("s", v, graph.edge_weight(("s", v)))
        path.insert(0, s_edge)
      
        if check_path(graph, path):
          update_graph(graph, path)
          for i in xrange(1, size):
            updates[i].append(path)
    
    if len(s_neighbors) == 0:
      break
    # send slave new job with node and any updates to graph
    print "n={0}, n_count={1}, s_neighbors={2}, mod={3}".format(n, n_count, s_neighbors, n % n_count)
    new_node = s_neighbors[n % len(s_neighbors)]
    comm.send({"node" : new_node, "update" : updates[slave_id]}, dest=slave_id)
    active_p.append(slave_id)
    # reset updates
    updates[slave_id] = []
    n += 1
  
  # for p in xrange(1, size):
  for p in active_p:
    slave_id, path = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    comm.send({"die": 0}, dest=slave_id)


  print "og: {0}".format(original_graph)
  for edge in graph.edges():
    print "edge: {0}, w={1}".format(edge, graph.edge_weight(edge))
  max_flow = find_max_flow(original_graph, graph)
  
  return max_flow

if __name__ == '__main__':
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()
  
  args = sys.argv
  if len(args) != 2:
    print "usage: python serial.py infile"
    sys.exit(-1)
  
  infile = sys.argv[1]
  
  if rank == 0:
    start_time = MPI.Wtime()
    max_flow = master(comm, infile)
    end_time = MPI.Wtime()
    print "max flow = {0}".format(max_flow)
    print "Time: %f secs" % (end_time - start_time)
  else:
    slave(comm)