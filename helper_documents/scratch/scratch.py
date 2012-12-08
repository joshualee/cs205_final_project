# del_indices = []  
# for i in len(S_u):
#   path = S_u[i]
#   if path.count(e_id) > 0:
#     del_indices.append(i)
#   
# while len(del_indices > 0):
#   index = del_indices.pop()
#   S_u.remove(index)

# // line 4 for sink 
# del_indices = []
# for i in xrange(0, T_u.range):
#     e_id = T_u[i] 
# if e_id in SaturatedPaths:
#     del_indices.append(i)
# 
#     while len(del_indices > 0):
#         index = del_indices.pop()
# T_u.remove(index)