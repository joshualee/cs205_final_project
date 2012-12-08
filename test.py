import driver

if __name__ == '__main__':
  for i in [10, 100, 500, 1000]:
    graph_name = "graphs/generated_graphs/generated_graph_" + str(i)
    
    graph = driver.graph_file_to_dict(graph_name)
    min_cut_parallel, _ = driver.run(graph_name)
    min_cut_serial = driver.find_min_cut_serial(graph)
    
    print "%d: %d, %d" % (i, min_cut_parallel, min_cut_serial)
    assert(min_cut_parallel == min_cut_serial)
    
    
    
    