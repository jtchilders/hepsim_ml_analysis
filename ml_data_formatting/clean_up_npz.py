#!/usr/bin/env python
import os,sys,optparse,logging,numpy
logger = logging.getLogger(__name__)

def main():
   ''' simple starter program that can be copied for use when starting a new script. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='This script will loop over npz files and remove them if they do not have enough events inside')
   parser.add_option('-i','--input',dest='input',help='Directory to loop over ')
   parser.add_option('-n','--nevts',dest='nevts',help='number of events required to keep files',default=10,type='int')
   parser.add_option('-o','--output',dest='output',help='file in which to store the names of files to remove',default='files_to_remove.txt')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                     'nevts',
                     'output',
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)

   outfile = open(options.output,'w')
   
   for root,dir,filenames in os.walk(options.input):
      for filename in filenames:
         if filename.endswith('.npz'):
            try:
               size,a,b,c = numpy.load(os.path.join(root,filename))['arr_0'].shape
               if size < options.nevts:
                  outfile.write(filename + '\n')
            except:
               logger.exception('exception received while reading file: %s',filename)
               outfile.write(filename + '\n')



if __name__ == "__main__":
   main()
