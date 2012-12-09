"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

accumulator.py defines the Accumulator class that is used when 
accepting augmented paths in the MapReduce jobs. An Accumulator
will accept a path as long as accepting the edges in the path does
not violate the capacity constraints of the existing edges in the 
Accumulator 
"""

#Library imports
import sys

class Accumulator:
  def __init__(self):
      self.edges = {}
  
  def accept(self, augmenting_path):
    sys.stderr.write(str(augmenting_path))
    valid_path = True
    min_flow = 1000000
    
    # check each edge will not exceed capacity
    # also calculate amount of flow we can push through path
    for edge in augmenting_path:
      e_v, e_id, e_f, e_c = edge

      if e_id in self.edges:
        accumulated_flow = self.edges[e_id]
      else:
        accumulated_flow = 0

      residue = e_c - (accumulated_flow + e_f)

      if (residue <= 0):
        valid_path = False
      else:
        if (residue < min_flow):
          min_flow = residue

    # update Accumlator's edges
    if valid_path:
      for edge in augmenting_path:
        e_v, e_id, e_f, e_c = edge
        r = e_id.split(",")
        e_r = "{0},{1}".format(r[1], r[0])
        
        if e_id in self.edges:
          self.edges[e_id] += min_flow
        else:
          self.edges[e_id] = min_flow
      return True
    else:
      return False