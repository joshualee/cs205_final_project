# Library imports
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.minmax import maximum_flow, cut_value
from mrjob.job import MRJob
import json
import sys
import subprocess
import numpy as np
import matplotlib.image as img

# Our Project
import max_flow

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
    sys.exit(-1)

def graph_file_to_dict(graph_file):
  graph = open(graph_file, "r")
  d = {}
  for line in graph:
    u, edges = extract_key_value(line)
    d[u] = edges
  return d

def dict_to_graph_file(d, outfile_path):
  outfile = open(outfile_path, "w")
  for vertex_id, vertex_info in d.iteritems():
    vertex_info.append({})
    # vertex_info.append(0)
    new_line = json.dumps(vertex_id) + "\t" + json.dumps(vertex_info) + "\n"
    outfile.write(new_line)
  outfile.close()

def mr_graph_convert(d):
  s_neighbors = {}
  new_graph = {}
  
  for vertex_id, edges in d.iteritems():
    E_u = []
    S_u = []
    T_u = []

    for e_v, e_c in edges:
      new_edge = [e_v, str(vertex_id) + "," + str(e_v), 0, e_c]
      validate_edge(new_edge)
      E_u.append(new_edge)

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
    sys.exit(-1)
  
  return new_graph

def augment_graph(graph, augmented_edges):
  augmented_graph = digraph()
  augmented_graph.add_nodes(graph.keys())
  
  for u, edges in graph.iteritems():
    for edge in edges:
      e_v, e_c = edge
      e_id = str(u) + "," + str(e_v)
      if e_id in augmented_edges:
        new_capacity = e_c - augmented_edges[e_id]
        if new_capacity > 0:
          augmented_graph.add_edge((u, e_v))
        elif new_capacity < 0:
          print "Fatal error: negative capacity in augmented graph"
          sys.exit(-1)

  return augmented_graph

def find_min_cut(graph, augmented_edges, cut):
  min_cut = 0
  for u, edges in graph.iteritems():
    for edge in edges:
      e_v, e_c = edge
      e_id = str(u) + "," + str(e_v)
      if e_id in augmented_edges:
        new_c = e_c - augmented_edges[e_id]
        if new_c == 0 and u in cut and e_v not in cut:
          min_cut += e_c
  return min_cut
  
def find_min_cut_serial(graph_dict):
  graph = digraph()
  graph.add_nodes(graph_dict.keys())
  for u, edges in graph_dict.iteritems():
    for e_v, e_c in edges:
      graph.add_edge((u, e_v), wt = e_c)
  
  flow, cut = maximum_flow(graph, "s", "t")
  print "serial cut", cut
  min_cut = cut_value(graph, flow, cut)
  return int(min_cut)

def run(in_graph_file):
  mr_file_name = "tmp/mr_max_flow.txt"

  original_graph_dict = graph_file_to_dict(in_graph_file)
  mr_graph = mr_graph_convert(original_graph_dict)
  dict_to_graph_file(mr_graph, mr_file_name)
  
  edge_file = open("edges.txt", "w")
  edge_file.write("")
  
  counter = 0
  augmented_edges = {}
  
  converge_count = 5
  previous_count = -1
  
  converged = False
  while converge_count != 0:
  # while(not converged):
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
       # value.append(1)
       new_line = json.dumps(key) + "\t" + json.dumps(value) + "\n"
       outfile.write(new_line)

     # check for convergence
     move_counts = runner.counters()[0]["move"]
     print "counts", move_counts
     # if move_counts["source"] == 0: # or move_counts["sink"] == 0:
     #   converged = True
     if move_counts["source"] == previous_count:
       converge_count -= 1
     else:
       converge_count = 5
     previous_count = move_counts["source"]

   infile.close()    
   outfile.close()
   counter += 1
  
  # augment graph based on max flow
  augmented_graph = augment_graph(original_graph_dict, augmented_edges)
  
  # find cut
  spanning_tree, preordering, postordering = depth_first_search(augmented_graph, "s")
  min_cut = find_min_cut(original_graph_dict, augmented_edges, preordering)
  min_cut_serial = find_min_cut_serial(original_graph_dict)
  
  print "min cut", min_cut
  print "min cut serial", min_cut_serial
  print "nodes in S", preordering
  print "augmented_edges", augmented_edges
  
  return min_cut, preordering

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: python driver.py infile"
    sys.exit(-1)
  
  in_graph_file = sys.argv[1]
  run(in_graph_file)