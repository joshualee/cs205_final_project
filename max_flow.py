"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usage: called from driver
input: infile to MapReduce 
output: outfile of MapReduce 

max_flow.py contains the Mapper and Reducer for the Max-Flow 
MapReduce jobs. 
"""

# Library imports
from mrjob.job import MRJob
from mrjob.protocol import JSONProtocol
import sys
import json

# Project imports
import accumulator as acc

"""
Constant defining maximum number of source 
excess paths that can be accepted by accumulator
"""
MAX_PATHS = 10 

""" MAPPER HELPER FUNCTIONS """

"""
edge_forms_cycle checks to make sure that adding an edge
to a path does not create a cycle
"""
def edge_forms_cycle(new_edge, path):
  v = new_edge[0]
  for edge in path:
    u = edge[0]
    if u == v:
      return True
  return False

"""
update_edge updates the flow of an edge in augmented_edges
and adds it to a list of saturated edges if its flow is 
greater than or equal to its capacity
"""
def update_edge(edge, augmented_edges, saturated_edges):
  e_v, e_id, e_f, e_c = edge[0], edge[1], edge[2], edge[3]
  if e_id in augmented_edges:
    a_f = augmented_edges[e_id]
    e_f = e_f + a_f
    edge[2] = e_f

    if (e_f >= e_c and saturated_edges.count(e_id) == 0):
      saturated_edges.append(e_id)
 
"""
MapReduce class
"""
class MRFlow(MRJob):
  INPUT_PROTOCOL = JSONProtocol
  OUTPUT_PROTOCOL = JSONProtocol
  
  def __init__(self, *args, **kwargs):
    super(MRFlow, self).__init__(*args, **kwargs)

  def mapper(self, u, node_info):
    saturated_edges = [] 
    
    # dictionary containing edges that were augumented from previous
    # MapReduce job
    augmented_edges = node_info.pop()
    
    # update edges in S_u, T_u, and E_u with augmented_edges
    S_u, T_u, E_u = node_info
        
    # updates E_u, S_u, and T_u based on the augmented_edges
    # and addes saturated edges to saturated_edges
    for edge in E_u:
      update_edge(edge, augmented_edges, saturated_edges)
    for path in S_u:
      for edge in path:
        update_edge(edge, augmented_edges, saturated_edges)
    for path in T_u:
      for edge in path:
        update_edge(edge, augmented_edges, saturated_edges)

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
          yield ("t", [[augmenting_path], [], []])
    
    # reseed S's neighbors
    if u == "s":
      for e_v, e_id, e_f, e_c in E_u:
        new_path = [[e_v, e_id, e_f, e_c]]
        yield (e_v, [[new_path],[],[]])
    
    # extends source excess paths
    if len(S_u) != 0:
      for edge in E_u:
        e_v, e_f, e_c = edge[0], edge[2], edge[3]
        if e_f < e_c:
          for source_path in S_u:
            if not edge_forms_cycle(edge, source_path):
              new_path = source_path[:]
              new_path.append(edge)
              yield(e_v, [[new_path], [], []])
    
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
    self.increment_counter("move", "source", len(S_u))

    if (u == "t"):
      yield "A_p", A_p.edges

    yield (u, [S_u, T_u, E_u])

  def steps(self):
    return [self.mr(self.mapper, self.reducer)]

if __name__ == '__main__':
  MRFlow.run()
