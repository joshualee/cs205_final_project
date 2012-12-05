from mrjob.job import MRJob
from mrjob.protocol import JSONProtocol

import accumulator as acc
import sys
import json

class MRFlow(MRJob):
    INPUT_PROTOCOL = JSONProtocol
    OUTPUT_PROTOCOL = JSONProtocol
    
    MAX_PATHS = 10 # k
    
    def __init__(self, *args, **kwargs):
        super(MRFlow, self).__init__(*args, **kwargs)
    
    # MAPPER HELPER FUNCTIONS
    def edge_forms_cycle(new_edge, path):
      new_destination = new_edge[0]
      for edge in path:
        vertex = edge[0]
        if vertex == new_destination:
          return True
      return False

    def update_edge(edge, augmented_edges, saturated_edges):
      e_v, e_id, e_f, e_c = edge
      if e_id in augmented_edges:
        a_v, a_id, a_f, a_c = augmented_edges[e_id]
        e_f = e_f + a_f
        edge[2] = e_f

        if (e_f >= e_c and saturated_edges.count(e_id) == 0):
          saturated_edges.append(e_id)

    def mapper(self, u, node_info):
      saturated_edges = []

      augmented_edges = node_info.pop()

      # update edges in S_u, T_u, and E_u with augmented_edges
      sys.stderr.write("TESTSTESTESTSTS")
      S_u, T_u, E_u = node_info

      for edge in E_u:
        update_edge(edge, augmented_edges, saturated_edges)
      for edge in S_u:
        update_edge(edge, augmented_edges, saturated_edges)
      for edge in T_u:
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

      # extends source excess paths
      if len(S_u) != 0:
        for e_v, _, e_f, e_c in E_u:
          if e_f < e_c:
            for source_path in S_u:
              if not edge_forms_cycle(edge, source_path):
                yield(e_v, [[source_path[:].append(edge)], [], []])
                break

      # extends sink excess paths
      if len(T_u) != 0:
        for e_v, _, e_f, e_c in E_u:
          if -e_f < e_c:
            for sink_path in T_u:
              if not edge_forms_cycle(edge, sink_path):
                yield(e_v, [[], [sink_path[:].prepend(edge)], []])
                break

      yield(u, [S_u, T_u, E_u])

      def reducer(self, u, values):
        # initialize new Accumulators
        A_p, A_s, A_t = acc.Accumulator(), acc.Accumulator(), acc.Accumulator()

        S_m, T_m, S_u, T_u, E_u = []

        for S_v, T_v, E_v in values:
          # master vertex
          if len(E_v) != 0:
            S_m = S_v
            T_m = T_v
            E_u = E_v

          # merge and filter S_v
          for se in S_v:
            if u == "t":
              A_p.acccept(se)
            elif len(S_u) < MAX_PATHS:
              if A_s.accept(se):
                S_u.append(se)
          for te in T_v:
            if len(T_u) < MAX_PATHS:
              if A_t.accept(te):
                T_u.append(te)

          # initalize counter
          self.increment_counter("move", "source", 0) 
          self.increment_counter("move", "sink", 0) 

          if (len(S_m) == 0 and len(S_u) > 0):
            self.increment_counter("move", "source", 1) 

          if (len(T_m) == 0 and len(T_u) > 0):
            self.increment_counter("move", "sink", 1) 

          if (u == "t"):
            yield "A_p", A_p

            # for edge, flow in A_p.iteritems():
            #   e_id = edge[1]
            #   #TODO: write out e_id, flow

          yield (u, [S_u, T_u, E_u, A_p])

    def steps(self):
        return [self.mr(self.mapper, self.reducer)]

if __name__ == '__main__':
    MRFlow.run()
