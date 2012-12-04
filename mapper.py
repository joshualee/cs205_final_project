Su -> source excess paths
Tu -> sink excess paths
Eu -> list of edges connecting u to neighbors 
eid -> edge id
ef -> flow amount
ec -> capacity of edge



def mapper(self, node, nodeInfo):
    SaturatedPaths = []

    AugmentedEdges = nodeInfo.pop()
    for S_u, T_u, E_u in nodeInfo:
        if (round-1) in AugumentedEdges:
            e_v, e_id, e_f, e_c = E_u
    if e_id in AugmentedEdges[round-1]:
        a_v, a_id, a_f, a_c = AugumentedEdges[round-1][e_id]
        e_f = e_f + a_f // how to replace
        if (e_f  >= e_c)
    
        // line 4 for source 
        del_indices = []
        for i in xrange(0, S_u.range):
            e_id = S_u[i] 
if e_id in SaturatedPaths:
    del_indices.append(i)

    while len(del_indices > 0):
        index = del_indices.pop()
S_u.remove(index)

// line 4 for sink 
del_indices = []
for i in xrange(0, T_u.range):
    e_id = T_u[i] 
if e_id in SaturatedPaths:
    del_indices.append(i)

    while len(del_indices > 0):
        index = del_indices.pop()
T_u.remove(index)

// stores e_id, e_f
Accumulator = []


**HAVE S_U BE DICTIONARY WITH E_ID AS KEY" to easily match up with T_u
for e_id in S_u:
if e_id in T_u:
accept, Accumulator = accept(Accumulator, e_id)
if accept == true:
emit(something on line 8)

 



def accept(Accumulator, a_id, a_f):
if a_id in Accumulator:
flow, cap = Accumulator[a_id]
if flow + a_f < cap: 
Accumulator[a_id] = flow + a_f, cap
return true, Accumulator
return false, AccumulatorSaturatedPaths[e_id] = true
