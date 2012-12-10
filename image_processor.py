"""
CS205 Final Project -- Joshua Lee and Mona Huang
TF: Verena Kaynig-Fittkau
Project: Parallel Max-Flow Min-Cut 

usage: python image_processor.py <infile> <outfile>
input: reads .png or .jpg image located at <infile>
output: writes graph in adjacency list format to <outfile>

Converts image located at <infile> into a graph in adjacency list format and
writes the output to <outfile>. This is a helper module used by segment.py.

The edge weights given by the functions:
  - source_weight
  - sink_weight
  - edge_weight
are extremely important for our image segmentation algorithm. 
"""

import json
import sys
import subprocess
import numpy as np
import matplotlib.image as img

"""
Returns greyscale version of image
"""
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
        
      new_image[i,j] = np.int32((r+g+b)/3)
      
  return new_image

"""
Returns the weight between source "s" and pixel (i, j)
In image segmentation, this is the probabiity of placing 
pixel (i, j) in the same cut as "s".
Here we use simple model of pixel intensity.
"""
def source_weight(i, j, image):
  return image[i, j]

"""
Returns the weight between pixel (i, j) and sink "t"
In image segmentation, this is the probabiity of placing 
pixel (i, j) in the same cut as "t".
Here we use simple model of inverted pixel intensity.
"""
def sink_weight(i, j, image):
  return 255 - image[i, j]
  
"""
Returns the weight between pixels (i, j) and (i_p, j_p).
In image segmentation, this is interpreted as the penalty of placing
pixel (i, j) and (i_p, j_p) in different cuts.
Here we use simple model of the absolute difference in pixel intensity.
"""
def edge_weight(i, j, i_p, j_p, image):
  return 255 - int(abs(image[i,j] - image[i_p, j_p]))

"""
Returns the edge with appropriate weight between
pixel (i, j) and (i_p, j_p)
"""
def get_edge(i, j, i_p, j_p, height, width, image):
  if i_p < 0 or i_p >= height or j_p < 0 or j_p >= width:
    return None
  else:
    id_p = str(i_p * width + j_p)
    return [id_p, edge_weight(i, j, i_p, j_p, image)]

def convert(image_file, outfile):
  original_image = img.imread(image_file)
  image = rgb_to_grayscale(original_image)
  height, width = image.shape
  print "Converting image ({0}x{1}) to graph...".format(width, height)
  img.imsave("tmp/grayscale.png", image, cmap="gray")
  
  graph = {} # graph has structure vertex_id -> edges
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
  
  # super source and super sink
  source_edges = []
  for i in xrange(height):
    for j in xrange(width):
      v_id = str(i * width + j)
      source_edges.append([v_id, source_weight(i, j, image)])
      graph[v_id].append(["t", sink_weight(i, j, image)])
  graph["s"] = source_edges
  graph["t"] = []
  
  # write the outfile
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