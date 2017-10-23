#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,random
logger = logging.getLogger(__name__)

def main():
   ''' simple starter program that can be copied for use when starting a new script. '''
   logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(process)d:%(thread)d:%(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-f','--input-filelist',dest='input_filelist',help='A file containing the names of the input compressed numpy image files, one per line.')
   parser.add_option('-t','--test-size',dest='test_size',help='Size of the test dataset as a fraction of all data globbed.',default=0.2,type='int')
   parser.add_option('-r','--randomize',dest='randomize',help='randomize which files are used for training and testing.',default=False,action='store_true')
   parser.add_option('-w','--workers',dest='workers',help='option passed to keras fitter for number of workers to use in training',default=8,type='int')
   parser.add_option('-o','--output',dest='output',help='output filename for the model',default='output_model.keras.h5')
   parser.add_option('-e','--epochs',dest='epochs',help='number of epochs to train',default=10,type='int')
   parser.add_option('-b','--batch-size',dest='batch_size',help='size of each batch of iimages processed per training step.',default=20,type='int')
   parser.add_option('--theano',dest='theano',help='switch from default keras backend of Tensorflow to Theano.',default=False,action='store_true')
   parser.add_option('--num-classes',dest='num_classes',help='number of classes to categorize images',default=2,type='int')
   parser.add_option('--events-per-file',dest='events_per_file',help='number of events per input file',default=10,type='int')
  
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input_filelist',
                     'test_size',
                     'randomize',
                     'workers',
                     'output',
                     'epochs',
                     'batch_size',
                     'theano',
                     'num_classes',
                     'events_per_file',
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   os.environ['KERAS_BACKEND'] = 'tensorflow'
   if options.theano:
      os.environ['KERAS_BACKEND'] = 'theano'
   import keras
   global keras
   logger.info('Keras Version: %s',keras.__version__)
   import file_gen
   global file_gen
   if options.theano:
      import theano as backend
   else:
      import tensorflow as backend
   logger.info('backend version: %s',backend.__version__)
   

   # get list of input files
   filelist = sorted(get_file_list(options.input_filelist))

   logger.info('found %s files to process',len(filelist))

   # get image shape
   image_shape = get_image_shape(filelist[0])
   logger.info('image shape: %s',image_shape)
   
   # calculate how many to use for training
   num_test_files = int(options.test_size*len(filelist))
   num_train_files = len(filelist) - num_test_files
   
   # get num_train_files worth of random numbers between 0 and len(filelist)
   if options.randomize:
      training_filelist_index = random.sample(range(len(filelist)),num_train_files)
   else:
      training_filelist_index = range(num_train_files)
      
   training_filelist = []
   testing_filelist = []
   # use the indices to populate a filelist for training
   for i in xrange(len(filelist)):
      if i in training_filelist_index:
         training_filelist.append(filelist[i])
      else:
         testing_filelist.append(filelist[i])

   logger.info('%s training files (%s unique)',len(training_filelist),len(set(training_filelist)))
   
   #for events in FileGenerator(filelist):
   #   logger.info(' %s events ',len(events))
   
   # get the model
   model = create_model(image_shape,options.num_classes)
   
   # create an optimizer
   opt = keras.optimizers.rmsprop(lr=0.0001,decay=1e-6)

   # train
   model.compile(loss='categorical_crossentropy',
                 optimizer=opt,
                 metrics=['accuracy'])
   
   train_gen   = file_gen.FileSequencer(training_filelist,options.num_classes,options.batch_size,options.events_per_file)
   test_gen    = file_gen.FileSequencer(testing_filelist,options.num_classes,options.batch_size,options.events_per_file)

   train_steps_per_epoch = ( len(training_filelist) * options.events_per_file ) // options.batch_size
   test_steps_per_epoch  = ( len(testing_filelist)  * options.events_per_file ) // options.batch_size

   model.fit_generator(train_gen,
                       steps_per_epoch    =  train_steps_per_epoch,
                       validation_data    =  test_gen,
                       validation_steps   =  test_steps_per_epoch,
                       workers            =  options.workers,
                       epochs             =  options.epochs,
                      )
   
   model.save(options.output)
   test_gen = file_gen.FileSequencer(testing_filelist,options.batch_size,options.events_per_file)
   steps    = ( len(testing_filelist) * options.events_per_file ) // options.batch_size
   scores   = model.evaluate_generator(test_gen,steps,workers=options.workers)
   logger.info('Test loss: %10.2f', scores[0])
   logger.info('Test accuracy: %10.2f', scores[1])


def create_model(image_shape,num_classes = 2):
   logger.debug('image_shape: %s num_classes: %s',image_shape,num_classes)
   model = keras.models.Sequential()
   add_cifar10_layer(model,image_shape)
   add_cifar10_layer(model,filters=64)

   model.add(keras.layers.Flatten())
   model.add(keras.layers.Dense(100000))
   model.add(keras.layers.Activation('relu'))
   model.add(keras.layers.Dropout(0.5))
   model.add(keras.layers.Dense(num_classes))
   model.add(keras.layers.Activation('softmax'))

   return model

def add_cifar10_layer(model,
                      image_shape=None,
                      filters = 32,
                      kernel_size= (5,5,5),
                      padding='same',
                      activation_function = 'relu',
                      pool_size = (2,2,2),
                      dropout = 0.25,
                      ):
   
   if image_shape is not None:
      model.add(keras.layers.Conv3D(filters, kernel_size, padding=padding,input_shape=image_shape))
   else:
      model.add(keras.layers.Conv3D(filters, kernel_size, padding=padding))

   model.add(keras.layers.Activation(activation_function))
   model.add(keras.layers.Conv3D(filters, kernel_size))
   model.add(keras.layers.Activation(activation_function))
   model.add(keras.layers.MaxPooling3D(pool_size=pool_size))
   model.add(keras.layers.Dropout(dropout))

   


def get_image_shape(filename):
   image_list = file_gen.load_file(filename)
   a,b,c,d = image_list.shape
   return (b,c,d,1)

def get_file_list(filename):
   filelist = []
   for line in open(filename):
      filelist.append(line.strip())
   return filelist


if __name__ == "__main__":
   main()
