MAX_PATHS = 10 # k

def reducer(self, u, values):
  # initialize new Accumulators
  A_p, A_s, A_t = Accumulator(), Accumulator(), Accumulator()
  
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
        A_p.acccept(se)
      elif len(S_u) < MAX_PATHS:
        if A_s.accept(se):
          S_u.append(se)
    for te in T_v:
      if len(T_u) < MAX_PATHS:
        if A_t.accept(te):
          T_u.append(te)

    # initalize counter
    self.increment_counter("move", "source", 0) 
    self.increment_counter("move", "sink", 0) 
    
    if (len(S_m) == 0 and len(S_u) > 0):
      self.increment_counter("move", "source", 1) 
    
    if (len(T_m) == 0 and len(T_u) > 0):
      self.increment_counter("move", "sink", 1) 
    
    if (u == "t"):
      yield "A_p", A_p
          
      # for edge, flow in A_p.iteritems():
      #   e_id = edge[1]
      #   #TODO: write out e_id, flow
    
    yield (u, [S_u, T_u, E_u, A_p])
