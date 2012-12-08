import sys
import json

class Max_Flow(object):
  def __init__(self, adj, flow):
    self.adj = adj
    self.flow = flow

  def find_path(self, source, sink, path):
    if source == sink:
      return path
  
    for neighbor, edge_id, r_id, capacity in self.adj[source]:
      # print "Path " + str(path)
      residual = capacity - self.flow[edge_id]
 
      if residual > 0 and path.count([neighbor, edge_id, r_id, residual]) == 0:

        new_edge = [neighbor, edge_id, r_id, residual]
        # print "creating new edge " + str(new_edge)
        path.append(new_edge)
        result = self.find_path(neighbor, sink, path)

        if result != None:
          return result
    
  def max_flow(self, source, sink):
    path = self.find_path(source, sink, [])
 
    while path != None:
      flow = min(residual for [e_v, e_id, r_id, residual] in path)
      for _, e_id, r_id, _ in path:
        self.flow[e_id] += flow
        self.flow[r_id] -= flow 
        path = self.find_path(source, sink, [])

    return sum(self.flow[e_id] for e_v, e_id, r_id, e_c in self.adj[source])


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

      if e_v in adj:
        for v, eid, rid, ec in adj[e_v]:
          if v == vertex_id:
            e_id = rid
            r_id = eid
      else:
        e_id = e_id_counter
        r_id = e_id_counter + 1
        e_id_counter += 2
        
      new_edge = [e_v, str(e_id), str(r_id), e_c]

      if vertex_id in adj:
        adj[vertex_id].append(new_edge)
      else:
        adj[vertex_id] = [new_edge]

      flow[str(e_id)] = 0 
      flow[str(r_id)] = 0 

  return adj, flow
        
if __name__ == '__main__':
  infile = "../graphs/test_graph_simple.txt"

  adj, flow = create_graph(infile)
  max_flow = Max_Flow(adj, flow)

  x = max_flow.max_flow("s", "t")
  print "X " + str(x)
