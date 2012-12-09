import sys
import json

class Edge(object):
    def __init__(self, u, v, w):
        self.source = u
        self.sink = v
        self.capacity = w
    def __repr__(self):
        return "%s->%s:%s" % (self.source, self.sink, self.capacity)
 
class FlowNetwork(object):
    def __init__(self):
        self.adj = {}
        self.flow = {}
 
    def add_vertex(self, vertex):
        self.adj[vertex] = []
 
    def get_edges(self, v):
        return self.adj[v]
 
    def add_edge(self, u, v, w=0):
        if u == v:
            raise ValueError("u == v")
        edge = Edge(u,v,w)
        redge = Edge(v,u,0)
        edge.redge = redge
        redge.redge = edge
        self.adj[u].append(edge)
        self.adj[v].append(redge)
        self.flow[edge] = 0
        self.flow[redge] = 0
        
    def edgeinpath(self,edge, path):
      print "looking for edge in path"
      for (pedge, presidual) in path:
        if pedge == edge or pedge == edge.redge:
          return True
      return False
 
    def find_path(self, source, sink, path):
        if source == sink:
            return path
        find_path_iter = 0 
        for edge in self.get_edges(source):
            find_path_iter += 1
            residual = edge.capacity - self.flow[edge]
            if residual > 0 and not self.edgeinpath(edge, path):
                result = self.find_path( edge.sink, sink, path + [(edge,residual)] )
                if result != None:
                    return result
 
    def max_flow(self, source, sink):
        path = self.find_path(source, sink, [])
        while path != None:
            flow = min(res for edge,res in path)
            for edge,res in path:
                self.flow[edge] += flow
                self.flow[edge.redge] -= flow
            path = self.find_path(source, sink, [])
        return sum(self.flow[edge] for edge in self.get_edges(source))
 
 
#if __name__ == "__main __":
infile = open(sys.argv[1], "r")

vertices = []
edges = {}

g=FlowNetwork()

for line in infile:
    split_line = line.split("\t")
    v, n = json.loads(split_line[0]), json.loads(split_line[1])
    vertices.append(v)
    
    for edge in n:
        e_v, e_c = edge
        edge_id = str(v) + "," + str(e_v)
        edges[edge_id] = e_c  
        
map(g.add_vertex, vertices)

for key in edges:
    u, v = key.split(",")
    g.add_edge(u, v, edges[key])
    
print g.max_flow('s','t')
