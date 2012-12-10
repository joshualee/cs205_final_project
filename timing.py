import driver
import sys
import serial
import driver
import subprocess as sp

if __name__ == '__main__':
  args = sys.argv
  if len(args) != 2:
    print "usage: python timing.py"
  
  mpi_installed = True
  try:
    sp.call(["mpirun", "-V"])
  except OSError:
    mpi_install = False
    print "MPI not installed"
  
  # for num_nodes in [2, 10, 25, 50, 100, 150, 200, 250, 350, 500]:
  for num_nodes in [2, 10, 25, 50, 100, 150, 200]:
    in_path = "graphs/timings/graph_{0}".format(num_nodes)
    
    print "Running library max flow on {0}...".format(in_path)
    graph = driver.file_to_graph(in_path)
    library_max_flow, _ = driver.find_min_cut_serial(graph)
    
    print "Running serial max flow on {0}...".format(in_path)
    serial_max_flow = serial.run(in_path)
    
    print "Running map/reduce max flow on {0}...".format(in_path)
    mr_max_flow, _ = driver.run(in_path)   
    
    if mpi_installed:
      print "Running MPI max flow on {0}...".format(in_path)
      mpi_output = sp.check_output(["mpirun", "-n", "4", "python", "mpi.py", in_path])
      mpi_max_flow = int(mpi_output.split("\n")[-2])
    
    assert (library_max_flow == serial_max_flow)
    assert(library_max_flow == mr_max_flow)
    
    if mpi_installed:
      assert(library_max_flow == mpi_max_flow)
    
    print "Success! All implementations have max_flow={0} for n={1}".format(library_max_flow, num_nodes)
    
    
    
