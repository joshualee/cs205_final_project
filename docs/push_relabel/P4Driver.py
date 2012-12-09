from mrjob.job import MRJob
import sys
import subprocess
import P4

if __name__ == '__main__':
    file_name = "shortest_path_graph.txt"
    subprocess.call(["cp", "graph.txt", file_name])
    
    converged = False
    while(not converged):
        infile = open(file_name, "r")

        mr_job = P4.MRGraph()
        mr_job.stdin = infile

        with mr_job.make_runner() as runner:
            runner.run()

            outfile = open(file_name, "w")
            for line in runner.stream_output():
                outfile.write(line)

            counts = runner.counters()[0]
            if counts['graph']['update'] == 0:
                converged = True
        
        infile.close()
        outfile.close()
            
            
