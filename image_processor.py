import json
import sys
import subprocess
import numpy as np
import matplotlib.image as img

def rgb_to_grayscale(image):
  height, width, channels = image.shape
  new_image = np.zeros((height,width))
  for i in xrange(height):
    for j in xrange(width):
      r = np.int32(image[i,j,0])
      g = np.int32(image[i,j,1])
      b = np.int32(image[i,j,2])
      print r, g, b
      new_image[i,j] = np.int32((r+g+b)/3)
  return new_image

def get_edge(i, j, i_p, j_p, height, width, image):
  if i_p < 0 or i_p >= height or j_p < 0 or j_p >= width:
    return None
  else:
    id_p = str(i_p * width + j_p)
    # return [id_p, int(abs(image[i,j]-image[i_p,j_p]))]
    return [id_p, 10]

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: python image_processor.py infile"
    sys.exit(-1)
  
  image_file = sys.argv[1]
  original_image = img.imread(image_file)
  image = rgb_to_grayscale(original_image)
  height, width = image.shape
  print type(width)
  print (height, width)
  print 13357
  print "i", 13357 / width
  print "j", 13357 % width
  
  # img.imsave(image_file + "_grayscale", image, cmap='gray', vmin=0, vmax=1)
  img.imsave("grayscale.png", image, cmap="gray")
  
  # vertex_id -> edgese
  graph = {}
  counter = 0
  for i in xrange(height):
    for j in xrange(width):
      my_id = str(i * width + j)
      edges = []
      
      top_left = get_edge(i, j, i-1, j-1, height, width, image)
      top = get_edge(i, j, i-1, j, height, width, image)
      top_right = get_edge(i, j, i-1, j+1, height, width, image)
      left = get_edge(i, j, i, j-1, height, width, image)
      right = get_edge(i, j, i, j+1, height, width, image)
      bottom_left = get_edge(i, j, i+1, j-1, height, width, image)
      bottom = get_edge(i, j, i+1, j, height, width, image)
      bottom_right = get_edge(i, j, i+1, j+1, height, width, image)
      
      edges.append(top_left)
      edges.append(top)
      edges.append(top_right)
      edges.append(left)
      edges.append(right)
      edges.append(bottom_left)
      edges.append(bottom)
      edges.append(bottom_right)
      
      lst = range(len(edges))
      lst.reverse()
      for k in lst:
        if edges[k] == None:
          edges.pop(k)
      
      graph[my_id] = edges
      counter +=1
  
  print counter
  # super source and super sink
  source_edges = []
  for i in xrange(height):
    for j in xrange(width):
      v_id = str(i * width + j)
      # source_edges.append([v_id, image[i, j]])
      # graph[v_id].append(["t", 255 - image[i, j]])
      source_edges.append([v_id, 15])
      graph[v_id].append(["t", 15])
      
  graph["s"] = source_edges
  graph["t"] = []
  
  outfile = open("graphs/graph_image.txt", "w")
  for u, edges in graph.iteritems():
    outfile.write(json.dumps(u) + "\t" + json.dumps(edges) + "\n")