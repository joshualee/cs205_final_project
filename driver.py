"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usuage: python driver.py <infile>
input: infile that holds graph 
output: integer representing max-flow of input graph 

driver.py manages the iterations of MapReduce used to calculate
the maximum flow of a graph from a specified infile. See README 
for acceptable graph format. 
"""

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

# Project imports
import max_flow

"""
merge_edge_flow merges the edges in a new path into the existing 
set of augmented edges 
"""
def merge_edge_flow(master, new):
  for edge, flow in new.iteritems():
    if flow == 0:
      print "zero flow for edge: " + str(edge)
    if edge in master:
      master[edge] += flow
    else:
      master[edge] = flow

"""
extract_key_value returns the key and value from a json encoded line
"""
def extract_key_value(line):
  split_line = line.split("\t")
  key = json.loads(split_line[0])
  value = json.loads(split_line[1])
  return key, value

"""
file_to_graph converts a graph representation from a file to a 
directed graph. 
"""
def file_to_graph(graph_file_path):
  graph_file = open(graph_file_path, "r")
  g = digraph()
  for line in graph_file:
    u, edges = extract_key_value(line)
    if not g.has_node(u):
      g.add_node(u)
    for edge in edges:
      v, e_c = edge
      if not g.has_node(v):
        g.add_node(v)
      g.add_edge((u, v), wt=e_c)
  return g
  
"""
dict_to_graph_file converts a dictionary representation of a graph 
to an acceptable form to be written to an outfile. To learn more 
about the file representation of the graph, see README.
"""
def dict_to_graph_file(d, outfile_path):
  outfile = open(outfile_path, "w")
  for vertex_id, vertex_info in d.iteritems():
    vertex_info.append({})
    new_line = json.dumps(vertex_id) + "\t" + json.dumps(vertex_info) + "\n"
    outfile.write(new_line)
  outfile.close()

"""
mr_graph_convert converts a digraph containing nodes and their edges into 
a dictionary representation of the graph that has keys representing nodes 
and values [S_u, T_u, E_u]. S_u, T_u, E_u are defined in README. 
"""
def mr_graph_convert(g):
  s_neighbors = {}
  new_graph = {}
  back_edges = {}
  
  for u in g.nodes():
    E_u = []
    S_u = []
    T_u = []
    
    for v in g.neighbors(u):
      e_c = g.edge_weight((u, v))
      new_edge = [v, "{0},{1}".format(u,v), 0, e_c]
      E_u.append(new_edge)
      
      # assumes verticies in neighbor list are unique
      if u == "s":
        s_neighbors[v] = new_edge
      if v == "t":
        T_u.append([new_edge])

    new_graph[u] = [S_u, T_u, E_u]

  for u, edge in s_neighbors.iteritems():
    new_graph[u][0] = [[edge]]

  if "s" not in new_graph or "t" not in new_graph:
    print "need to provide source and sink verticies"
    sys.exit(-1)

  return new_graph
  
  
""" 
dict_graph_to_python_graph converts a dictionary representation of a graph 
into a directed graph using the python library. 
"""
def dict_graph_to_python_graph(d):
  g = digraph()
  g.add_nodes(d.keys())
  for u, edges in d.iteritems():
    for edge in edges:
      e_v, e_c = edge
      g.add_edge((u, e_v), wt=e_c)
  return g
  
  
"""
augment_graph updates a graph based on a set of augmented_edges that 
contains edges and the flow that can be pushed across the edge
"""
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
  
  # remove edges with zero or less capacity
  for edge in g.edges():
    if g.edge_weight(edge) == 0:
      g.del_edge(edge)

  return g
  
"""
find_max_flow finds the maximum flow in a graph given the corresponding
edges on one side of the cut of the graph. 
"""
def find_max_flow(graph, s_side_cut_nodes):
  min_cut = 0
  for edge in graph.edges():
    u, v = edge
    
    # edges that have nodes on different sides of the cut
    # contribute to the maximum flow
    if u in s_side_cut_nodes and v not in s_side_cut_nodes:
      min_cut += graph.edge_weight(edge)
  return min_cut
  
"""
find_min_cut_serial finds the maximum flow and minimum cut edges 
of a graph in serial 
"""
def find_min_cut_serial(graph):  
  flow, cut = maximum_flow(graph, "s", "t")
  
  serial_cut = []
  for u, i in cut.iteritems():
    if i == 0:
      serial_cut.append(str(u))
  
  # finds corresponding max_flow value from 
  # cut using library function cut_value 
  max_flow = cut_value(graph, flow, cut)
  return int(max_flow), serial_cut

"""
fun accepts a file representation of a graph and finds the maximum 
flow of the graph through multiple iterations of MapReduce. For more
information on the MapReduce process, see max_flow.py. run updates 
the graph based on edges augmented from each iteration of MapReduce
and checks for convergence of the max-flow algorithm when no augmented
paths are added after a MapReduce job. 
"""
def run(in_graph_file):
  # converts a graph in an acceptable form into a representation 
  # that is usable in MapReduce
  mr_file_name = "mr_max_flow.txt"
  original_graph = file_to_graph(in_graph_file)
  mr_graph = mr_graph_convert(original_graph)
  dict_to_graph_file(mr_graph, mr_file_name)
  
  augmented_edges = {}
  
  # counters to keep track of convergence of MapReduce jobs
  converge_count = 5
  previous_count = -1
  
  while converge_count != 0:
   infile = open(mr_file_name, "r")

   # uncomment to run on emr
   # mr_job = max_flow.MRFlow(args=['-r', 'emr'])
   
   mr_job = max_flow.MRFlow()
   mr_job.stdin = infile

   with mr_job.make_runner() as runner:
     # perform iteration of MapReduce
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
  
  # augment graph based on max flow
  # original_graph = dict_graph_to_python_graph(original_graph_dict)
  augmented_graph = augment_graph(original_graph, augmented_edges)
  
  # find cut
  spanning_tree, preordering, postordering = depth_first_search(augmented_graph, "s")
  min_cut = find_max_flow(original_graph, preordering)
  min_cut_serial, serial_cut = find_min_cut_serial(original_graph)

  print "Min Cut: \n\t parallel: {0} \n\t serial: {1}".format(min_cut, min_cut_serial)
  return min_cut, preordering

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: python driver.py <infile>"
    sys.exit(-1)
  
  in_graph_file = sys.argv[1]
  run(in_graph_file)
