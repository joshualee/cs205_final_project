MAX_PATHS = 10 # k

def reducer(self, u, values):
  # initialize new Accumulators
  A_p, A_s, A_t = {}, {}, {}
  
  S_m, T_m, S_u, T_u, E_u = []
  
  for S_v, T_v, E_v in values:
    # master vertex
    if len(E_v) != 0:
      S_m = S_v
      T_m = T_v
      E_u = E_v
    
    # merge and filter S_v
    for se in S_v:
      if u == "t":
        accept, A_p = acccept(A_p, se)
      elif len(S_u) < MAX_PATHS:
        accept, A_s = accept(A_s, se)
        if accept:
          S_u.append(se)
    for te in T_v:
      if len(T_u) < MAX_PATHS:
        accept, A_t = accept(A_t, te)
        if accept:
          T_u.append(te)

    if (len(S_m) == 0 and len(S_u) > 0):
      print "source_move"
    
    if (len(T_m) == 0 and len(T_u) > 0):
      print "sink_move"
    
    if (u == "t"):
      yield "A_p", A_p
      for edge, flow in A_p.iteritems():
        e_id = edge[1]
        #TODO: write out e_id, flow
    
    yield (u, [S_u, T_u, E_u, A_p])
    
      
        
          
  
def accept(Accumulator, augmenting_path):
  valid_path = True
  new_min_flow = 1000000
  
  # check each edge will not exceed capacity
  # also calculate amount of flow we can push through path
  for edge in augmenting_path:
    e_v, e_id, e_f, e_c = edge
    
    if e_id in Accumulator:
      accumulated_flow = Accumulator[e_id]
    else:
      accumulated_flow = 0
    
    test_flow = e_c - (accumulated_flow + e_f)
    
    if (e_c < 0):
      valid_path = False
    else:
      if (test_flow < new_min_flow):
        new_min_flow = test_flow
  
  # update Accumulator
  if valid_path:
    for edge in augmenting_path:
      e_v, e_id, e_f, e_c = edge
      if e_id in Accumulator:
        Accumulator[e_id] += new_min_flow
      else:
        Accumulator[e_id] = new_min_flow
    return true, Accumulator
  else:
    return false, Accumulator
