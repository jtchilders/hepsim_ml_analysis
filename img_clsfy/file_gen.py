import numpy,os

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


