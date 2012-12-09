import sys
import json
import time

class Max_Flow(object):
  def __init__(self, adj, flow):
    self.adj = adj
    self.flow = flow
    self.previous_calls = []

  def find_path(self, source, sink, path):
    if source == sink:
      return path
  
    for neighbor, edge_id, r_id, capacity in self.adj[source]:
      # print "Neigh " + str(neighbor) + "  Edge ID " + str(edge_id)
      # print "Path " + str(path)
      residual = capacity - self.flow[edge_id]
      # print "Residual on edge " + str(edge_id) + " = " + str(residual)
      new_edge = [neighbor, edge_id, r_id, residual]
      
      if_count = 0 
      if residual > 0 and new_edge not in path:
        #print "\t" + str(path)
        if len(path) > 1:
          print "{0}: path start: {1} path end: {2}".format(if_count, path[0], path[-11:])
          print "\n"
        # print "creating new edge " + str(new_edge)
        
        new_path = path[:]
        new_path.append(new_edge)
        print "precall: {0}".format(new_edge)
        new_call = (neighbor, sink, new_path)
        print "previous calls: {0}".format(self.previous_calls)
        if new_call not in self.previous_calls:
          self.previous_calls.append(new_call)
          result = self.find_path(neighbor, sink, new_path)
        else:
          result = None
        print "postcall: {0}".format(new_edge)

        if result != None:
          return result

        if_count += 1

  def max_flow(self, source, sink):
    iter = 0 
    print "first path"
    path = self.find_path(source, sink, [])
    print "done first path"
    while path != None:
      print "looking for path " + str(iter)
      iter += 1
      flow = min(residual for [e_v, e_id, r_id, residual] in path)
      # print "Min flow " + str(flow)
      # print "path in max_flow" + str(path)
      print "PATH LENGTH " + str(len(path))
      path_iter = 0 
      for e_v, e_id, r_id, e_c in path:
        print "looking in path " + str(path_iter)
        path_iter += 1
      
        #print "Adding flow to edge " + str(e_id)
        #print "Subtracting flow from edge " + str(r_id) + "\n"
        self.flow[e_id] += flow
        self.flow[r_id] -= flow 

      print "calling find path"
      self.previous_calls = []
      path = self.find_path(source, sink, [])
      print "NEW CALL"
      time.sleep(.5)

    max_flow = 0 
    for e_v, e_id, r_id, e_c in self.adj[source]:
      #print "e_v : " + str(e_v) + "   flow : " + str(self.flow[e_id]) + "   eid : " + str(e_id)
      max_flow += self.flow[e_id]

    return max_flow

def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

def create_graph(infile_name):
  infile = open(infile_name, "r")

  adj = {} 
  flow = {}
  edges = {}

  e_id_counter = 0
  
  for line in infile:
    vertex_id, edges = extract_key_value(line)
        
    for e_v, e_c in edges:
      e_id = 0
      r_id = 0

      new_edge = [e_v, str(vertex_id) + "," + str(e_v), str(e_v) + "," + str(vertex_id), e_c]

      if vertex_id in adj:
        adj[vertex_id].append(new_edge)
      else:
        adj[vertex_id] = [new_edge]

      flow[str(vertex_id) + "," + str(e_v)] = 0 
      flow[str(e_v) + "," + str(vertex_id)] = 0 
  
  # print "Adjacency Matrix"
  # for key in adj:
  #  print str(key) + "\t" + str(adj[key]) + "\n"

  return adj, flow
        
if __name__ == '__main__':

  sys.setrecursionlimit(2000)

  file_name = sys.argv[1]
  infile = "../graphs/generated_graphs/" + file_name

  adj, flow = create_graph(infile)
  max_flow = Max_Flow(adj, flow)

  x = max_flow.max_flow("s", "t")
  print "X " + str(x)
