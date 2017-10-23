import numpy,os,json,random,logging
logger = logging.getLogger(__name__)
from keras.utils import Sequence


class FileSequencer(Sequence):
   """
    Every `Sequence` must implements the `__getitem__` and the `__len__` methods.
    If you want to modify your dataset between epochs you may implement `on_epoch_end`.
    The method `__getitem__` should return a complete batch.
    # Notes
    `Sequence` are a safer way to do multiprocessing. This structure guarantees that the network will only train once
     on each sample per epoch which is not the case with generators.
    # Examples
    ```python
        from skimage.io import imread
        from skimage.transform import resize
        import numpy as np
        # Here, `x_set` is list of path to the images
        # and `y_set` are the associated classes.
        class CIFAR10Sequence(Sequence):
            def __init__(self, x_set, y_set, batch_size):
                self.x, self.y = x_set, y_set
                self.batch_size = batch_size
            def __len__(self):
                return len(self.x) // self.batch_size
            def __getitem__(self, idx):
                batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
                batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
                return np.array([
                    resize(imread(file_name), (200, 200))
                       for file_name in batch_x]), np.array(batch_y)
    ```
   """

   def __init__(self,filelist,batch_size=20,evt_per_file=10):
      self.filelist        = filelist
      self.get_truth_list()
      self.evt_per_file    = evt_per_file
      self.batch_size      = batch_size
      self.nevts           = len(filelist)*self.evt_per_file
      self.nbatches        = int(self.nevts*1./self.batch_size)
      
      logger.debug(' n npz files:  %s',len(self.filelist))
      logger.debug(' n json files: %s',len(self.truthlist))
      logger.debug(' evt per file: %s',self.evt_per_file)
      logger.debug(' batch size:   %s',self.batch_size)
      logger.debug(' nevts:        %s',self.nevts)
      logger.debug(' n batches:    %s',self.nbatches)
   
   def get_truth_list(self):
      self.truthlist = []
      for filename in self.filelist:
         self.truthlist.append(filename.replace('.npz','.btagged.json'))

   def __getitem__(self, index):
      """Gets batch at position `index`.
      # Arguments
         index: position of the batch in the Sequence.
      # Returns
         A batch
      """

      file_index,event_index = self.get_start_index(index)
      #end_file_index,end_event_index = self.get_end_index(start_file_index,start_event_index)
      
      logger.debug('index: %-10s file_index: %-10s event_index: %-10s',index,file_index,event_index)

      images = []
      classes = []
      
      # loop until we have enough images
      while len(images) < self.batch_size:
         logger.debug(' n images: %-10s file_index: %-10s event_index: %-20s',len(images),file_index,event_index)
         # open file
         image_list = numpy.load(self.filelist[file_index])['arr_0']
         class_list = json.load(open(self.truthlist[file_index]))
         
         
         while event_index < self.evt_per_file:
            images.append(image_list[event_index,...])
            classes.append(class_list[event_index])
            event_index += 1
         
         event_index = 0
         file_index += 1
      
      logger.debug(' n images: %-10s n classes: %-10s',len(images),len(classes))

      # convert to numpy array
      np_images = numpy.array(images)
      # have to add a channel index even though it is only 1 dimension in our case
      old_shape = np_images.shape
      new_shape = list(old_shape)
      new_shape.append(1)
      new_np_images = np_images.reshape(tuple(new_shape))
      
      logger.debug(' images: old shape: %s   new_shape %s',old_shape,new_np_images.shape)

      # convert to numpy array
      np_classes = numpy.array(classes)
      # have to add a channel index even though it is only 1 dimension in our case
      old_shape = np_classes.shape
      new_shape = list(old_shape)
      new_shape.append(1)
      new_np_classes = np_classes.reshape(tuple(new_shape))

      logger.debug(' classes: old shape: %s   new_shape %s',old_shape,new_np_classes.shape)
      
      return new_np_images,new_np_classes
   
   def get_start_index(self,batch_index):
      
      event_index = batch_index*self.batch_size
      file_index = int(event_index / self.evt_per_file)
      return file_index, ( event_index - file_index * self.evt_per_file )
     
   def __len__(self):
      """Number of batch in the Sequence.
      # Returns
          The number of batches in the Sequence.
      """
      return self.nbatches

   def on_epoch_end(self):
      """Method called at the end of every epoch.
      """
      
      # shuffle the images
      c = list(zip(self.filelist, self.truthlist))
      random.shuffle(c)
      self.filelist,self.truthlist = zip(*c)

def FileGenerator(filelist,batchsize = 20):
   ''' Takes a list of files and serves events in batches '''   
   images = []

   # loops forever
   while True:
      # looping over all the files constitutes one epoch
      for filename in filelist:
         
         # load file
         image_list = load_file(filename)
         # get shape
         nimgs,r,eta,phi = image_list.shape
         
         # loop over each image
         for i in range(nimgs):
            # extract image from array
            image = image_list[i,...]
            # reshape image to add fake channel since keras is expecting one
            image = image.reshape((r,eta,phi,1))
            # add to output list
            images.append(image)
            # if the number of images in the output list
            # is equal to the batch size, return the list
            if len(images) == batchsize:
               yield images
               # reset list
               images = []

      # if we have cycled over the files
      # just skip the remaining images that do not constitute
      # a full batch size to avoid mixing epochs
      images = []

def load_file(filename):
   ''' loads the numpy compressed file  and returns the stored array '''
   if os.path.exists(filename):
      npfile = numpy.load(filename)
      image_list = npfile['arr_0']
      return image_list
   return []


