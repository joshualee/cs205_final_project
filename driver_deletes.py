def graph_file_to_dict(graph_file):
  graph = open(graph_file, "r")
  d = {}
  for line in graph:
    u, edges = extract_key_value(line)
    d[str(u)] = edges
  return d
  
  
  
def insert_back_edges(g):
  for u in g.nodes():
    for v in g.neighbors(u):
      if not g.has_edge((v, u)):
        g.add_edge((v, u), wt=0)
        
def diff(l1, l2):
  diff_list = []
  for e1 in l1:
    if e1 not in l2:
      diff_list.append(e1)
  return diff_list
  
def validate_edge(edge):
  e_v, e_id, e_f, e_c = edge
  if e_c < 0:
    print "cannot have negative edge capacity"
    sys.exit(-1)
    
    
Max flow deletes:
    # extends sink excess paths
    # if len(T_u) != 0:
    #   for edge in E_u:
    #     e_v, e_f, e_c = edge[0], edge[2], edge[3]
    #     if -e_f < e_c:
    #       for sink_path in T_u:
    #         if not edge_forms_cycle(edge, sink_path):
    #           new_path = sink_path[:]
    #           new_path.insert(0, edge)
    #           sys.stderr.write("extended sink path: " + str(new_path))
    #           yield(e_v, [[], [new_path], []])
    #           break
    