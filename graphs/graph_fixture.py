# INPUT GRAPH STRUCTURE

vertex_id, neighbors
vertex_id, neighbors
vertex_id, neighbors
...

vertex_id = "u"

neighbors = [directed_edge, ...]

# edge from u to v
directed_edge = ["v", original_capacity]
original_capacity = 10

# example
"1" [["2", 10], ["3", 5]]
"2" [["3", 2], ["4", 1]]
"3" [["2", 3], ["4", 9], ["5", 2]]
"4" [["5", 4]]
"5" [["1", 7], ["4", 6]]


# MAP REDUCE GRAPH STRUCTURE
"s", [S_u, T_u, E_u]

S_u = [path, ...]
T_u = [path, ...]
E_u = [edge, ...]

path = [edge, ...]

edge = (e_v, e_id, e_f, e_c)
e_v = "t"
e_id = "3"
e_f = 0
e_c = 5