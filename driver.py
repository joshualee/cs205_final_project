from mrjob.job import MRJob
import json
import sys
import subprocess
import max_flow
import numpy as np
import matplotlib.image as img
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import depth_first_search

def merge_edge_flow(master, new):
  for edge, flow in new.iteritems():
    if flow == 0:
      print "zero flow for edge: " + str(edge)
    if edge in master:
      master[edge] += flow
    else:
      master[edge] = flow

def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

def validate_edge(edge):
  e_v, e_id, e_f, e_c = edge
  if e_c < 0:
    print "cannot have negative edge capacity"
    # sys.exit(-1)

def convert_graph(original_file, new_file):
  original_input = open(original_file, "r")
  out_file = open(new_file, "w")

  e_id = 0
  s_neighbors = {}
  new_graph = {}
  
  for line in original_input:
    vertex_id, edges = extract_key_value(line)
    
    E_u = []
    S_u = []
    T_u = []
    
    for e_v, e_c in edges:
      new_edge = [e_v, str(e_id), 0, e_c]
      validate_edge(new_edge)
      E_u.append(new_edge)
      e_id += 1
      
      # assumes verticies in neighbor list are unique
      if vertex_id == "s":
        s_neighbors[e_v] = new_edge
      if e_v == "t":
        T_u.append([new_edge])
      
    new_graph[vertex_id] = [S_u, T_u, E_u]
  
  for vertex_id, edge in s_neighbors.iteritems():
    new_graph[vertex_id][0] = [[edge]]
    
  if "s" not in new_graph or "t" not in new_graph:
    print "need to provide source and sink verticies"
    # sys.exit(-1)
  
  for vertex_id, vertex_info in new_graph.iteritems():
    vertex_info.append({})
    new_line = json.dumps(vertex_id) + "\t" + json.dumps(vertex_info) + "\n"
    out_file.write(new_line)

def augment_graph(original_graph_path, augmented_edges):
  min_cut = 0
  
  e_id = 0
  augmented_graph_dict = {}
  for line in open(original_graph_path, "r"):
   u, edges = extract_key_value(line)
   for edge in edges:
     if str(e_id) in augmented_edges:
       original_capacity = edge[1]
       new_capacity = original_capacity - augmented_edges[str(e_id)]
       edge[1] = new_capacity
       if new_capacity == 0:
         min_cut += original_capacity
       elif new_capacity < 0:
         print "Fatal error: negative capacity in augmented graph"
         sys.exit(-1)
     e_id += 1
   augmented_graph_dict[u] = edges

  # create augmented graph
  augmented_graph = digraph()
  augmented_graph.add_nodes(augmented_graph_dict.keys())
  for u, edges in augmented_graph_dict.iteritems():
   for edge in edges:
     e_v, e_c = edge
     # remove saturated edges
     if e_c > 0:
       augmented_graph.add_edge((u, e_v))

  return min_cut, augmented_graph

def run(in_graph_file):
  mr_file_name = "tmp/mr_max_flow.txt"
  convert_graph(in_graph_file, mr_file_name)
  
  counter = 0
  augmented_edges = {}
  converged = False
  while(not converged):
   infile = open(mr_file_name, "r")

   mr_job = max_flow.MRFlow()
   mr_job.stdin = infile

   with mr_job.make_runner() as runner:

     # perform iteration of map reduce
     runner.run()
     # process map reduce output
     out_buffer = []
     for line in runner.stream_output():
       print str(counter) + ": " + line
       key, value = extract_key_value(line)

       if key == "A_p":
         A_p = value
         merge_edge_flow(augmented_edges, A_p)
       else:
         out_buffer.append(line)

     # write map reduce output to file for next iteration
     outfile = open(mr_file_name, "w")
     for line in out_buffer:
       key, value = extract_key_value(line)
       value.append(A_p)
       new_line = json.dumps(key) + "\t" + json.dumps(value) + "\n"
       outfile.write(new_line)

     # check for convergence
     move_counts = runner.counters()[0]["move"]
     print "source moves: " + str(move_counts["source"])
     print "sink moves: " + str(move_counts["sink"])
     if move_counts["source"] == 0: # or move_counts["sink"] == 0:
       converged = True

   infile.close()    
   outfile.close()
   counter += 1

  print "augmented edges: " + str(augmented_edges)
  print "counter=" + str(counter)
  
  # augment graph based on max flow
  min_cut, augmented_graph = augment_graph(in_graph_file, augmented_edges)
  # find cut
  spanning_tree, preordering, postordering = depth_first_search(augmented_graph, "s")
  
  print "min cut", min_cut
  print "nodes in S", preordering
  
  return min_cut, preordering

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: python driver.py infile"
    sys.exit(-1)
  
  in_graph_file = sys.argv[1]
  run(in_graph_file)