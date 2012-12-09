import json
import sys
import random 

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 3:
    print "usage: python graph_generator.py n outfile"
  
  num_nodes = int(sys.argv[1])
  outfile_path = sys.argv[2]
  nodes = ["s", "t"]
  for i in range(num_nodes-2):
    nodes.append(str(i))
    print "Appending " + str(i)

  graph = {}

  for u in nodes:
    graph[u] = []
    print "inserting " + str(u)
    for v in nodes:
      if u != v and u != "t":
        prob_edge = random.random()
        if prob_edge > 0.5:
          random_weight = random.randint(1, 10)
          graph[u].append([v, random_weight])

  outfile = open(outfile_path, "w")
  for key in graph:
    outfile.write(json.dumps(key) + "\t" + json.dumps(graph[key]) + "\n")

  outfile.close()
