import json
import sys
import subprocess
import numpy as np
import matplotlib.image as img

def rgb_to_grayscale(image):
  height, width, channels = image.shape
  new_image = np.zeros((height,width))  
  convert = (type(image[0,0,0]) == np.float32)
  
  for i in xrange(height):
    for j in xrange(width):
      # convert from float to int
      if convert:
        r = np.int32(image[i,j,0] * 255)
        g = np.int32(image[i,j,1] * 255)
        b = np.int32(image[i,j,2] * 255)
      else:
        r = np.int32(image[i,j,0])
        g = np.int32(image[i,j,1])
        b = np.int32(image[i,j,2])
      print r, g, b
      new_image[i,j] = np.int32((r+g+b)/3)
  return new_image

def source_weight(i, j, image):
  return image[i, j]
    
def sink_weight(i, j, image):
  return 255 - image[i, j]
  
def edge_weight(i, j, i_p, j_p, image):
  return 255 - int(abs(image[i,j] - image[i_p, j_p]))

def get_edge(i, j, i_p, j_p, height, width, image):
  if i_p < 0 or i_p >= height or j_p < 0 or j_p >= width:
    return None
  else:
    id_p = str(i_p * width + j_p)
    # return [id_p, int(abs(image[i,j]-image[i_p,j_p]))]
    return [id_p, edge_weight(i, j, i_p, j_p, image)]

def convert(image_file, outfile):
  original_image = img.imread(image_file)

  image = rgb_to_grayscale(original_image)
  height, width = image.shape
  print "Converting image ({0}x{1}) to graph...".format(width, height)
  
  img.imsave("tmp/grayscale.png", image, cmap="gray")
  
  # vertex_id -> edges
  graph = {}
  counter = 0
  for i in xrange(height):
    for j in xrange(width):
      my_id = str(i * width + j)
      edges = []
      
      # create edge between adjaceny pixels
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
      
      # remove out of range edges
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
      
      source_edges.append([v_id, source_weight(i, j, image)])
      graph[v_id].append(["t", sink_weight(i, j, image)])
      
  graph["s"] = source_edges
  graph["t"] = []
  
  outfile = open(outfile, "w")
  for u, edges in graph.iteritems():
    outfile.write(json.dumps(u) + "\t" + json.dumps(edges) + "\n")

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "usage: python image_processor.py infile outfile"
    sys.exit(-1)
  
  image_file = sys.argv[1]
  outfile = sys.argv[2]
  convert(image_file, outfile)