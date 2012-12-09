from mrjob.job import MRJob
from mrjob.protocol import JSONProtocol

import accumulator as acc
import sys
import json

# MAPPER HELPER FUNCTIONS
MAX_PATHS = 10 # k

def edge_forms_cycle(new_edge, path):
  sys.stderr.write("path: " + str(path) + "\n")
  v = new_edge[0]
  for edge in path:
    u = edge[0]
    if u == v:
      print "edge forms cycle " + str(u)  + ","  + str(v)
      return True
  return False

def update_edge(edge, augmented_edges, saturated_edges):
  # sys.stderr.write("edge type: " + str(type(edge)) + "\t" + "edge: " + str(edge) + "\n")
  e_v, e_id, e_f, e_c = edge[0], edge[1], edge[2], edge[3]
  if e_id in augmented_edges:
    a_f = augmented_edges[e_id]
    e_f = e_f + a_f
    edge[2] = e_f

    if (e_f >= e_c and saturated_edges.count(e_id) == 0):
      saturated_edges.append(e_id)
      
class MRFlow(MRJob):
  INPUT_PROTOCOL = JSONProtocol
  OUTPUT_PROTOCOL = JSONProtocol
  
  def __init__(self, *args, **kwargs):
    super(MRFlow, self).__init__(*args, **kwargs)

  def mapper(self, u, node_info):
    saturated_edges = []
                
    augmented_edges = node_info.pop()
    # first = node_info.pop()
    # if first == 1:
    #   inf = open("edges.txt", "r")
    #   augmented_edges = json.loads(inf.readline())
    # else:
    #   augmented_edges = {}
    
    sys.stderr.write(str(type(augmented_edges)))
    
    # update edges in S_u, T_u, and E_u with augmented_edges
    S_u, T_u, E_u = node_info
    
    sys.stderr.write("(M) " + str(u) + ": S_u: " + str(S_u) + "\t" + "T_u: " + str(T_u) + "\t" + "E_u: " + str(E_u) + "\n")
    
    for edge in E_u:
      update_edge(edge, augmented_edges, saturated_edges)
    for path in S_u:
      for edge in path:
        update_edge(edge, augmented_edges, saturated_edges)
    for path in T_u:
      for edge in path:
        update_edge(edge, augmented_edges, saturated_edges)

    # for e_v, e_id, e_f, e_c in E_u:
    #   if (e_f >= e_c and e_id not in saturated_edges):
    #     saturated_edges.append(e_f)
    # for path in S_u:
    #   for e_v, e_id, e_f, e_c in path:
    #     if (e_f >= e_c and e_id not in saturated_edges):
    #       saturated_edges.append(e_f)
    # for path in T_u:
    #   for e_v, e_id, e_f, e_c in path:
    #     if (e_f >= e_c and e_id not in saturated_edges):
    #       saturated_edges.append(e_f)
    
    # remove saturated excess paths
    for e_id in saturated_edges:    
      for path in S_u:
        if path.count(e_id) > 0:
          S_u.remove(path)
    
      for path in T_u:
        if path.count(e_id) > 0:
          T_u.remove(path)
    
    # attempt to combine source and sink excess paths
    accumulator = acc.Accumulator()
    
    for source_path in S_u:
      for sink_path in T_u:
        augmenting_path = source_path + sink_path
        if accumulator.accept(augmenting_path):
          sys.stderr.write("accepted aug. path: " + str(augmenting_path) + "\n")
          yield ("t", [[augmenting_path], [], []])
        else:
          sys.stderr.write("rejected aug. path: " + str(augmenting_path) + "\n")          
    
    # reseed S's neighbors
    if u == "s":
      for e_v, e_id, e_f, e_c in E_u:
        new_path = [[e_v, e_id, e_f, e_c]]
        yield (e_v, [[new_path],[],[]])
    
    # extends source excess paths
    if len(S_u) != 0:
      sys.stderr.write("len S_u = " + str(len(S_u)) + "\n")
      sys.stderr.write("S_u = " + str(S_u) + "\n")
      for edge in E_u:
        e_v, e_f, e_c = edge[0], edge[2], edge[3]
        if e_f < e_c:
          for source_path in S_u:
            if not edge_forms_cycle(edge, source_path):
              new_path = source_path[:]
              new_path.append(edge)
              sys.stderr.write("D source_path = " + str(new_path) + "\n")
              sys.stderr.write("extended source path: " + str(new_path) + "\n")
              yield(e_v, [[new_path], [], []])
              # break
            else:
              sys.stderr.write("CYCLE\n")
              sys.stderr.write("path: " + str(source_path))
              sys.stderr.write("\nedge: " + str(edge))
    
    # extends sink excess paths
    # if len(T_u) != 0:
    #   for edge in E_u:
    #     e_v, e_f, e_c = edge[0], edge[2], edge[3]
    #     if -e_f < e_c:
    #       for sink_path in T_u:
    #         if not edge_forms_cycle(edge, sink_path):
    #           new_path = sink_path[:]
    #           new_path.insert(0, edge)
    #           sys.stderr.write("extended sink path: " + str(new_path))
    #           yield(e_v, [[], [new_path], []])
    #           break
    
    yield(u, [S_u, T_u, E_u])
    
  def reducer(self, u, values):
      
    # initialize new Accumulators
    A_p, A_s, A_t = acc.Accumulator(), acc.Accumulator(), acc.Accumulator()
     
    S_m, T_m, S_u, T_u, E_u = [], [], [], [], []
     
    for S_v, T_v, E_v in values:
      # master vertex
      if len(E_v) != 0:
        S_m = S_v
        T_m = T_v
        E_u = E_v
    
      # merge and filter S_v
      for se in S_v:
        if u == "t":
          A_p.accept(se)
        elif len(S_u) < MAX_PATHS:
          if A_s.accept(se):
            S_u.append(se)
      for te in T_v:
        if len(T_u) < MAX_PATHS:
          if A_t.accept(te):
            T_u.append(te)
    
    # initalize counter
    self.increment_counter("move", "source", 0)
    self.increment_counter("move", "source", 0)
    self.increment_counter("move", "sink", 0)
    
    # if (len(S_m) == 0 and len(S_u) > 0):
    #   self.increment_counter("move", "source", 1)
      
    self.increment_counter("move", "source", len(S_u))
    
    if (len(T_m) == 0 and len(T_u) > 0):
      self.increment_counter("move", "sink", 1) 
    
    if (u == "t"):
      yield "A_p", A_p.edges

    sys.stderr.write("(R) " + str(u) + ": S_u: " + str(S_u) + "\t" + "T_u: " + str(T_u) + "\t" + "E_u: " + str(E_u) + "\n")

    yield (u, [S_u, T_u, E_u])

  def steps(self):
    return [self.mr(self.mapper, self.reducer)]

if __name__ == '__main__':
  MRFlow.run()
