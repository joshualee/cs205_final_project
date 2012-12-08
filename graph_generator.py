import json
import sys
import random 

if __name__ == '__main__':
  num_nodes = int(sys.argv[1])

  nodes = ["s", "t"]
  for i in range(num_nodes-2):
    nodes.append(str(i))
    print "Appending " + str(i)

  graph = {}
  
  for u in nodes:
    graph[u] = []
    print "inserting " + str(u)
    for v in nodes:

      if u != v:
        prob_edge = random.random()
        if prob_edge > 0.5:
          random_weight = random.randint(1, 10)
          graph[u].append([v, random_weight])
  
  outfile_name = "graphs/generated_graphs/generated_graph_" + str(num_nodes)

  print str(graph)
  outfile = open(outfile_name, "w")      
  for key in graph:

    outfile.write(json.dumps(key) + "\t" + json.dumps(graph[key]) + "\n")


  outfile.close()
