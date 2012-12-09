"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usuage: python max_flow_serial.py <infile>
input: infile that holds graph
output: integer representing max-flow of input graph 

max_flow_serial.py calculates in serial the maximum flow of a graph from a 
specified infile. See README for acceptable graph format. 
"""

import sys
sys.path.append('./library/pg')

import json
import time
import collections as col
import digraph as pg
from searching import depth_first_search
from find import find

class Max_Flow(object):
  def __init__(self, graph):
    self.flow = col.defaultdict(int)
    self.graph = graph

    self.original_graph = pg.digraph()
    self.original_graph.add_nodes(self.graph.nodes())
    for edge in self.graph.edges():
      self.original_graph.add_edge(edge, wt=self.graph.edge_weight(edge))

  """ 
  find_path uses depth first search to find a path from source s
  to a sink t. If no path is found, None is returned
  """
  def find_path(self):
    filt = find("t")
    st, _, _ = depth_first_search(self.graph, "s", filter=filt)
    if "t" not in st:
      return None
    else:
      path = []
      sink = "t"
      
      # build up path from spanning tree returned from dfs 
      while sink != "s":
        src = st[sink]
        new_edge = (src, sink, self.graph.edge_weight((src, sink)))
        path.insert(0, new_edge)
        sink = src
      return path
      
  """
  max_flow continues to increment the flow as long as an augmenting
  path can be found.
  """
  def max_flow(self):
    path = self.find_path()
    while path != None:
      flow = min(curr_cap for (u, v, curr_cap) in path)
    
      # updates all edges and backedges in path with residual capacity 
      # and deletes the edge if no capacity remains 
      for u, v, curr_cap in path:
        new_weight = curr_cap - flow
        if new_weight > 0:
          self.graph.set_edge_weight((u, v), new_weight)
        elif new_weight == 0:
          if self.graph.has_edge((u,v)):
            self.graph.del_edge((u,v))
        if (self.graph.has_edge((v, u))):
          curr_weight = self.graph.edge_weight((v, u))
          self.graph.set_edge_weight((v, u), curr_weight + flow)
        else:
          self.graph.add_edge((v, u), wt=flow)
      path = self.find_path()
    
    # calculates the final max_flow by comparing the residual 
    # capacity of edges out of "s" in  the final graph with their 
    # original capacities 
    s_neighbors = self.original_graph.neighbors("s")
    max_flow = 0
    for v in s_neighbors:      
      edge = ("s", v)
      original_capacity = self.original_graph.edge_weight(edge)
      if self.graph.has_edge(edge):
        new_capacity = self.graph.edge_weight(edge)
      else:
        new_capacity = 0
      
      flow = original_capacity - new_capacity
      max_flow += flow
    return max_flow
    
"""
extract_key_value returns the key and value from a json encoded line
"""
def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value
  
  
"""
create_graph generates a directed graph from a file containing an 
adjacency list representation of a graph
"""
def create_graph(infile_name):
  infile = open(infile_name, "r")
  
  g = pg.digraph()
  
  # extracts the nodes and edges encoded in each line and 
  # inserts them into the graph g 
  for line in infile:
    u, edges = extract_key_value(line)
    if not g.has_node(u):
      g.add_node(u)
    for v, e_c in edges:
      if not g.has_node(v):
        g.add_node(v)
      g.add_edge((u,v), wt=e_c)
  
  infile.close()
  return g

def run(infile):
  graph = create_graph(infile)
  max_flow = Max_Flow(graph)
  x = max_flow.max_flow()
  return x

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python max_flow_serial.py infile"
    sys.exit(-1)
  
  infile = sys.argv[1]
  max_flow = run(infile)
  print "max flow = {0}".format(max_flow)
