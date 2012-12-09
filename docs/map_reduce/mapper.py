Su -> source excess paths
Tu -> sink excess paths
Eu -> list of edges connecting u to neighbors 
eid -> edge id
ef -> flow amount
ec -> capacity of edge


# Assumes no self edge
def edgeFormsCycle(new_edge, path):
  new_destination = new_edge[0]

  for edge in path:
    vertex = edge[0]
    if vertex == new_destination:
      return True
  
  return False

def updateEdge(edge, AugmentedEdges, SaturatedEdges):
  e_v, e_id, e_f, e_c = edge
  if e_id in AugmentedEdges:
    a_v, a_id, a_f, a_c = AugumentedEdges[e_id]
    e_f = e_f + a_f
    edge[2] = e_f
    
    if (e_f >= e_c and SaturatedEdges.count(e_id) == 0):
      SaturatedEdges.append(e_id)


def mapper(self, u, nodeInfo):
  SaturatedEdges = []

  AugmentedEdges = nodeInfo.pop() # AugmentedEdges is a dictionary
    
  for i in len(nodeInfo):
    S_u, T_u, E_u = nodeInfo[i]
    
    for edge in E_u:
      updateEdge(edge, AugmentedEdges, SaturatedEdges)
    for edge in S_u:
      updateEdge(edge, AugmentedEdges, SaturatedEdges)
    for edge in T_u:
      updateEdge(edge, AugmentedEdges, SaturatedEdges)
    
  # line 4
  for e_id in SaturatedEdges:    
    for path in S_u:
      if path.count(e_id) > 0:
        S_u.remove(path)
        
    for path in T_u:
      if path.count(e_id) > 0:
        T_u.remove(path)

  # stores e_id, e_f
  accumulator = Accumulator()

  for source_path in S_u:
    for sink_path in T_u:
      augmenting_path = source_path + sink_path
      if accumulator.accept(augmenting_path):
        yield ("t", [[augmenting_path], [], []])

  if len(S_u) != 0:
    for edge in E_u:
      e_v, e_id, e_f, e_c = edge
      if e_f < e_c:
        for source_path in S_u:
          if not edgeFormsCycle(edge, source_path):
            yield(e_v, [[source_path[:].append(edge)], [], []])
            break

  if len(T_u) != 0:
    for edge in E_u:
      e_v, e_id, e_f, e_c = edge
      if -e_f < e_c:
        for sink_path in T_u:
          if not edgeFormsCycle(edge, sink_path):
            yield(e_v, [[], [sink_path[:].prepend(edge)], []])
            break
  
  yield(u, [S_u, T_u, E_u])