import sys
import json
import time
import collections as col
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.filters.find import find

class Max_Flow(object):
  def __init__(self, graph):
    self.flow = col.defaultdict(int)
    self.graph = graph

    self.original_graph = digraph()
    self.original_graph.add_nodes(self.graph.nodes())
    for edge in self.graph.edges():
      self.original_graph.add_edge(edge, wt=self.graph.edge_weight(edge))

  def find_path(self):
    filt = find("t")
    st, _, _ = depth_first_search(self.graph, "s", filter=filt)
    if "t" not in st:
      return None
    else:
      path = []
      sink = "t"
      while sink != "s":
        src = st[sink]
        new_edge = (src, sink, self.graph.edge_weight((src, sink)))
        path.insert(0, new_edge)
        sink = src
      return path

  def max_flow(self):
    path = self.find_path()
    while path != None:
      flow = min(curr_cap for (u, v, curr_cap) in path)
    
      print "Path : " + str(path)
      for u, v, curr_cap in path:
        new_weight = curr_cap - flow
        if new_weight > 0:
          self.graph.set_edge_weight((u, v), new_weight)
          if (self.graph.has_edge((v, u))):
            curr_weight = self.graph.edge_weight((v, u))
            self.graph.set_edge_weight((v, u), curr_weight + flow)
          else:
            self.graph.add_edge((v, u), wt=flow)
        elif new_weight == 0:
          if self.graph.has_edge((u,v)):
            self.graph.del_edge((u,v))
      path = self.find_path()
    
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
    
def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

def create_graph(infile_name):
  infile = open(infile_name, "r")
  
  g = digraph()
  
  for line in infile:
    u, edges = extract_key_value(line)
    if not g.has_node(u):
      g.add_node(u)
    for v, e_c in edges:
      if not g.has_node(v):
        g.add_node(v)
      g.add_edge((u,v), wt=e_c)
  
  return g

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python serial.py infile"
    sys.exit(-1)
  
  infile = "../graphs/generated_graphs/" + sys.argv[1]

  graph = create_graph(infile)
  max_flow = Max_Flow(graph)

  x = max_flow.max_flow()
  print "max_flow : " + str(x)
