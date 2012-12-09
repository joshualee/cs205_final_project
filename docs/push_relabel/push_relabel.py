from mrjob.job import MRJob
from mrjob.protocol import JSONProtocol
import sys
import json

class MRPushRebal(MRJob):
    INPUT_PROTOCOL = JSONProtocol
    OUTPUT_PROTOCOL = JSONProtocol

    def mapper(self, v, neighbors):
        yield v, ("graph", neighbors)
        
        d_v, e_v = neighbors.pop(0)
        
        if d_v > 0 and v != "s" and v != "t":
          for w, c_v_w, e_w, d_w in neighbors:
            if d_v > d_w and c_v_w > 0:
              delta = min(e_v, c_v_w)
              yield v, ("new_e", e_v - delta) # e_v = e_v - delta
              yield v, ("new_e", e_v - delta) # e_v = e_v - delta
            else:
              relabel
        
        
        for destination, distance in neighbors:
            yield destination, ("distance", current_distance + distance)

    def reducer(self, node, typed_values):
        min_distance = 999
        neighbors = []

        for typed, typed_value in typed_values:
            if typed == "graph":
                neighbors = typed_value
            elif typed == "distance":
                min_distance = min(min_distance, typed_value)
            else:
                raise Exception("Unknown value type")

        self.increment_counter("graph", "update", 0) # initalize counter

        current_distance = neighbors[0]
        if (min_distance < current_distance):
            neighbors[0] = min_distance
            self.increment_counter("graph", "update", 1)
        yield node, neighbors

    def steps(self):
        return [self.mr(self.mapper, self.reducer)]

if __name__ == '__main__':
    MRGraph.run()
