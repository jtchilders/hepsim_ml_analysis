#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,random
logger = logging.getLogger(__name__)
os.environ['KERAS_BACKEND'] = 'tensorflow'
import keras


def load_file(filename):
   if os.path.exists(filename):
      npfile = numpy.load(filename)
      image_list = npfile['arr_0']
      return image_list
   return []


def FileGenerator(filelist,batchsize = 20):
   
   images = []

   while True:
      for filename in filelist:
         

         image_list = load_file(filename)
         nimgs,r,eta,phi = image_list.shape

         for i in range(nimgs):
            image = image_list[i,...]

            images.append(image)

            if len(images) == batchsize:
               yield images
               images = []

      
   
   

def main():
   ''' simple starter program that can be copied for use when starting a new script. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-g','--input-glob',dest='input_glob',help='A glob, e.g. "/path/to/*myfiles*.npz", to the input files to loop over.')
   parser.add_option('-t','--test-size',dest='test_size',help='Size of the test dataset as a fraction of all data globbed.',default=0.2,type='int')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input_glob',
                     'test_size',
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   # get list of input files
   filelist = sorted(glob.glob(options.input_glob))

   logger.info('found %s files to process',len(filelist))
   
   # calculate how many to use for training
   num_test_files = int(options.test_size*len(filelist))
   num_train_files = len(filelist) - num_test_files
   
   # get num_train_files worth of random numbers between 0 and len(filelist)
   training_filelist_index = random.sample(range(len(filelist)),num_train_files)
   training_filelist = []
   # use the indices to populate a filelist for training
   for i in training_filelist_index:
      training_filelist.append(filelist[i])

   logger.info('%s training files (%s unique)',len(training_filelist),len(set(training_filelist)))
   
   for events in FileGenerator(filelist):
      logger.info(' %s events ',len(events))



if __name__ == "__main__":
   main()
