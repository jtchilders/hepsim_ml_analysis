#!/usr/bin/env python
import os,sys,optparse,logging,glob,copy,stat
logger = logging.getLogger(__name__)

# slic -x -i output/tev14_pythia8_zbbar_m3000_8_truth.slcio  -g geom/sifcch7.lcdd
#      -m geom/config/defaultILCCrossingAngle.mac  -o output/tev14_pythia8_zbbar_m3000_8.slcio  -r 5000

def main():
   ''' simple starter program that can be copied for use when starting a new script. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-g','--glob-input',dest='glob_input',help='a glob to catch all the input files')
   parser.add_option('-f','--files-per-node',dest='files_per_node',help='the number of files to process per node',type='int')
   parser.add_option('-n','--nodes-per-job',dest='nodes_per_job',help='the number of nodes in a single batch job',type='int')
   parser.add_option('-p','--processes-per-node',dest='processes_per_node',help='the number of processes per node',type='int',default=68)
   options,args = parser.parse_args()


   manditory_args = [
                     'glob_input',
                     'files_per_node',
                     'nodes_per_job',
                     'processes_per_node'
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)

   filelist = sorted(glob.glob(options.glob_input))

   logger.info(' %s files to process ',len(filelist))

   logger.info(' will require %s jobs',len(filelist)*1./options.files_per_node/options.nodes_per_job)


   # this is a script that will be created dynamically that runs <processes_per_node> 
   # convert_corescript_filename scripts on a single node with different files
   convert_nodelevel_cmd = 'srun -N 1 -n 1 --ntasks-per-node=1 --cpu_bind=verbose,none --cpus-per-task=272 -o %%j_node%04d.stdout -e %%j_node%04d.stderr ./lcio2np.py -g %s -n %s & \n'
   # this is the job submission script that launches all the nodescripts
   convert_jobscript_filename  = 'convert_scripts/convert_job%04d.sh'
   
   # this is the start of the content for the job script
   convert_jobscript_start = '''#!/bin/bash -l
#SBATCH -N {nodes}
#SBATCH -p normal
#SBATCH -C knl,quad,cache
#SBATCH -t 1:00:00
#SBATCH -L SCRATCH
#SBATCH --image=docker:argonneeic/fpadsim:v1.4

echo [$SECONDS] starting conversion jobs

source /global/cscratch1/sd/parton/mlworkspace/hepsim/setup.sh

'''

   # this is the job script
   jobscript = convert_jobscript_start
   
   for i in xrange(0,len(filelist),options.files_per_node):
      input_files = filelist[i:i+options.files_per_node]
      node_num = i / options.files_per_node
      logger.info(' %s %s ',i,node_num)
      # only include so many nodes in a job
      if (node_num+1) % options.nodes_per_job == 0:
         # calculate node number starting from 1 and use in filename
         filename = convert_jobscript_filename % ((node_num+1)/options.nodes_per_job)
         logger.info('filename %s',filename)
         # add wait to the end of the script 
         jobscript += 'wait\n'
         # write script
         write_script(filename,jobscript.format(nodes=options.nodes_per_job))

         # restart nodescript
         jobscript = convert_jobscript_start
      
      jobscript += convert_nodelevel_cmd % (node_num,node_num,','.join(input_files),options.processes_per_node)

   node_num = len(filelist)/options.files_per_node
   # calculate node number starting from 1 and use in filename
   filename = convert_jobscript_filename %  ( (node_num+1) / options.nodes_per_job + 1 )
   logger.info('filename %s',filename)
   # add wait to the end of the script 
   jobscript += 'wait\n'
   # write script
   write_script(filename,jobscript.format(nodes=options.nodes_per_job))


def write_script(filename,script):
   open(filename,'w').write(script)
   make_exe(filename)

def make_exe(file):
   os.chmod(file,os.stat(file).st_mode | stat.S_IEXEC)

if __name__ == "__main__":
   main()
