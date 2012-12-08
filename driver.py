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
  
def dict_graph_to_python_graph(d):
  g = digraph()
  g.add_nodes(d.keys())
  for u, edges in d.iteritems():
    for edge in edges:
      e_v, e_c = edge
      g.add_edge((u, e_v), wt=e_c)
  return g

def augment_graph(graph, augmented_edges):
  # copy graph
  g = digraph()
  g.add_nodes(graph.nodes())
  for edge in graph.edges():
    g.add_edge(edge, wt=graph.edge_weight(edge))
  
  # update edge weights based on augmentation
  for u in g.nodes():
    for v in g.neighbors(u):
      e_id = "{0},{1}".format(u, v)
      if e_id in augmented_edges:
        flow = augmented_edges[e_id]
        
        # update forward edge
        f_e = (u, v)
        residue = g.edge_weight(f_e) - flow
        g.set_edge_weight(f_e, residue)
        if residue < 0:
          print "Fatal error: negative edge residue"
          sys.exit(-1)
        
        # update back edge
        r_id = "{0},{1}".format(v, u)
        b_e = (v, u) 
        if g.has_edge(b_e):
          new_weight = g.edge_weight(b_e) + flow
          g.set_edge_weight(b_e, new_weight)
        else:
          g.add_edge(b_e, wt=flow)
  
  # remove edges with zero capacity
  for edge in g.edges():
    if g.edge_weight(edge) == 0:
      g.del_edge(edge)
  
  # for u, edges in graph.iteritems():
  #   for edge in edges:
  #     e_v, e_c = edge
  #     e_id = str(u) + "," + str(e_v)
  #     if e_id in augmented_edges:
  #       new_capacity = e_c - augmented_edges[e_id]
  #       if new_capacity > 0:
  #         augmented_graph.add_edge((u, e_v))
  #       elif new_capacity < 0:
  #         print "Fatal error: negative capacity in augmented graph"
  #         sys.exit(-1)

  return g

# 
# def find_min_cut(graph, cut):
#   
#   for edge in edges

def find_min_cut(graph, cut_nodes):
  min_cut = 0
  for edge in graph.edges():
    u, v = edge
    if u in cut_nodes and v not in cut_nodes:
      min_cut += graph.edge_weight(edge)
  return min_cut
  # 
  # min_cut = 0
  # for u, edges in graph.iteritems():
  #   for edge in edges:
  #     e_v, e_c = edge
  #     e_id = str(u) + "," + str(e_v)
  #     if e_id in augmented_edges:
  #       new_c = e_c - augmented_edges[e_id]
  #       if new_c == 0 and u in cut and e_v not in cut:
  #         min_cut += e_c
  # return min_cut
  
def find_min_cut_serial(graph):  
  flow, cut = maximum_flow(graph, "s", "t")
  
  serial_cut = []
  for u, i in cut.iteritems():
    if i == 0:
      serial_cut.append(str(u))
  
  min_cut = cut_value(graph, flow, cut)
  return int(min_cut), serial_cut

def diff(l1, l2):
  diff_list = []
  for e1 in l1:
    if e1 not in l2:
      diff_list.append(e1)
  return diff_list

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
  
  while converge_count != 0:
   infile = open(mr_file_name, "r")

   mr_job = max_flow.MRFlow()
   mr_job.stdin = infile

   with mr_job.make_runner() as runner:
     print "iteration {0}...".format(counter)
     
     # perform iteration of map reduce
     runner.run()
     # process map reduce output
     out_buffer = []
     for line in runner.stream_output():
       # print str(counter) + ": " + line
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
     print move_counts
     if move_counts["source"] == previous_count:
      converge_count -= 1
     else:
       converge_count = 5
     previous_count = move_counts["source"]

   infile.close()    
   outfile.close()
   counter += 1
  
  print "augmented_edges", augmented_edges
  # augment graph based on max flow
  original_graph = dict_graph_to_python_graph(original_graph_dict)
  augmented_graph = augment_graph(original_graph, augmented_edges)
  
  # find cut
  spanning_tree, preordering, postordering = depth_first_search(augmented_graph, "s")
  min_cut = find_min_cut(original_graph, preordering)
  min_cut_serial, serial_cut = find_min_cut_serial(original_graph)
  
  serial_cut = sorted(serial_cut)
  parallel_cut = sorted([str(i) for i in preordering])
  S_P = diff(serial_cut, parallel_cut)
  P_S = diff(parallel_cut, serial_cut)
  
  print "Min Cut: \n\t parallel: {0} \n\t serial: {1}".format(min_cut, min_cut_serial)
  
  print "Parallel cut (P): {0}".format(parallel_cut)
  print "Serial cut (S):   {0}".format(serial_cut)
  print "S - P: {0}".format(S_P)
  print "P - S: {0}".format(P_S)
  
  alternative_flow_t = 0
  alternative_flow_s = 0
  for key in augmented_edges:
    #print str(key)                                                                                     
    src, sink = key.split(",")
    if src == "s":
      alternative_flow_s += augmented_edges[key]
    if sink == "t":
      alternative_flow_t += augmented_edges[key]

  print "S-T Flow Calculation:"
  print "\ts: {0} \n \tt: {1}".format(alternative_flow_s, alternative_flow_t)
  
  alternative_flow = 0
  for key in augmented_edges:
    #print str(key)
    src, sink = key.split(",")
    if sink == "t": 
      alternative_flow += augmented_edges[key]

  print "Alternative Flow Calculation : " + str(alternative_flow)

  return min_cut, preordering

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: python driver.py infile"
    sys.exit(-1)
  
  in_graph_file = sys.argv[1]
  run(in_graph_file)
