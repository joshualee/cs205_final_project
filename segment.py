# Library
import sys
import numpy as np
import matplotlib.image as img

# Our Project
import driver
import image_processor as ip

if __name__ == '__main__':
  args = sys.argv
  
  if len(args) != 3:
    print "usage: python segment.py input_image output_image"
    sys.exit(-1)
  
  input_image = args[1]
  output_image = args[2]
  
  original_image = img.imread(input_image)
  height, width, channels = original_image.shape
  print "Processing image (%dx%d)..." % (width, height)
  
  image_as_graph_path = "tmp/image_graph.txt"
  ip.convert(input_image, image_as_graph_path)
  
  max_flow, cut = driver.run(image_as_graph_path)

  # gererate and output segmented image
  segmented_image = np.zeros((height, width))
  for i in xrange(height):
    for j in xrange(width):
      my_id = str(i * width + j)
      # my_id is reachable from s 
      if my_id in cut:
        segmented_image[i,j] = 255
      # my_id is not reachable from s
      else:
        segmented_image[i,j] = 0
  
  img.imsave("output/{0}".format(output_image), segmented_image, cmap="gray")