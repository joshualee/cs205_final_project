import sys
import subprocess as sp

if __name__ == '__main__':
  # sp.call(["mpirun", "-n", "2", "python", "mpi.py", "easy_2.txt"])
  mpi_installed = True
  try:
    sp.call(["mpirun", "-V"])
  except OSError:
    mpi_install = False
    print "MPI not installed"
    
    
    
