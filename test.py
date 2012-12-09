import driver
import sys

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python test.py infile"
  
  infile = args[1]
  graph = driver.file_to_graph(infile)
  min_cut_serial, min_cut_nodes_serial = driver.find_min_cut_serial(graph)
    
  print "min cut: %d" % (min_cut_serial)
    
    
    
    
