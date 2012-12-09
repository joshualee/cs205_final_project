"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usuage: python test.py <infile>
input: infile containing graph 
output: max flow of input graph

test.py runs the input graph through a library-defined max-flow 
algorithm. test.py is used to validate our own serial and parallel 
implementations against a working implementation. 
"""

import driver
import sys

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python test.py infile"
  
  infile = args[1]
  graph = driver.file_to_graph(infile)
  
  # find_min_cut_serial in driver utilizes the 
  # library function 
  min_cut_serial, min_cut_nodes_serial = driver.find_min_cut_serial(graph)
    
  print "min cut: %d" % (min_cut_serial)
    
    
    
    
