#!/usr/bin/env python
from __future__ import division
import os,sys,optparse,logging,glob,numpy,json
import multiprocessing

from pyLCIO import IOIMPL
logger = logging.getLogger(__name__)

''' list of collections:
BeamCalHits
CalorimeterHitRelations
EM_BARREL
EM_ENDCAP
HAD_BARREL
HAD_ENDCAP
HelicalTrackHitRelations
HelicalTrackHits
HelicalTrackMCRelations
LumiCalHits
MCInfo
MCParticle
MUON_BARREL
MUON_ENDCAP
MuonBarrelHits
MuonEndcapHits
PandoraPFOCollection
ReconClusters
SiTrackerBarrelHits
SiTrackerEndcapHits
SiTrackerForwardHits
SiVertexBarrelHits
SiVertexEndcapHits
StateAtECal
StateAtEnd
StateAtStart
TKR_RawTrackerHits
TKR_TrackerHits
Tracks
VXD_RawTrackerHits
VXD_TrackerHits


   dx    = 0.0025
   xmax  = 1231.7740
   nx    = 12520
   n_xpix = 492710

   dy    = 0.0045
   ymax  = 1232.4274
   ny    = 12696
   n_ypix = 273873

   dz    = 0.0057
   zmax  = 2325.9992
   nz    = 5516
   n_zpix = 408071


x_delta = 100
x_offset = 3570
n_xbins = x_offset*2/x_delta
y_delta = 100
y_offset = 3570
n_ybins = y_offset*2/y_delta
z_delta = 100
z_offset = 4700
n_zbins = z_offset*2/z_delta
'''

x_delta = 2
x_offset = 166
n_xbins = x_offset*2/x_delta
y_delta = 2
y_offset = 166
n_ybins = y_offset*2/y_delta
z_delta = 10
z_offset = 1190
n_zbins = z_offset*2/z_delta

def get_cartesian_bin( (x,y,z) ):
   
   xbin = int(( x + x_offset ) / x_delta) - 1
   ybin = int(( y + y_offset ) / y_delta) - 1
   zbin = int(( z + z_offset ) / z_delta) - 1

   return xbin,ybin,zbin

r_nbins = 90
r_max = 9000
r_min = 0
r_delta = float(r_max - r_min)/float(r_nbins)

eta_nbins = 100
eta_max = 5
eta_min = -5
eta_delta = float(eta_max - eta_min)/float(eta_nbins)


phi_nbins = 64
phi_max = numpy.pi
phi_min = -numpy.pi
phi_delta = float(phi_max - phi_min)/float(phi_nbins)


def get_spherical( (x,y,z) ):
   try:
      r = numpy.sqrt( x*x + y*y + z*z )
      theta = numpy.arctan2(y,x) # we typically call this phi in HEP
      phi = numpy.arccos(z/r)
      eta = -1.*numpy.log(numpy.tan(phi/2.))
   except:
      logger.error(' failed to convert x,y,z = %s,%s,%s ',x,y,z)
      raise
   return (r,eta,theta)

def get_spherical_bin( (x,y,z) ):
   
   (r,eta,phi) = get_spherical( (x,y,z) )

   r_bin   = int( ( r   - r_min   ) / r_delta   )
   eta_bin = int( ( eta - eta_min ) / eta_delta )
   phi_bin = int( ( phi - phi_min ) / phi_delta )
   
   return (r_bin,eta_bin,phi_bin)


def main():
   ''' Convert HepSim simulation output to compressed numpy for ML. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(process)d:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-g','--input-glob',dest='input_glob',help='input glob to grab input filenames, can use wildcards but enclose in quotes like this: "/path/to/*_digi.slcio". This can also be a comma separated list of file names.')
   parser.add_option('-n','--nprocs',dest='nprocs',help='number of parallel processes to use',type='int',default=1)
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input_glob',
                     'nprocs',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)

   # get file list
   if options.input_glob.find(',') >= 0:
      filelist = sorted(options.input_glob.split(','))
   else:
      filelist = sorted(glob.glob(options.input_glob))


   logger.info('processing %s files',len(filelist))

   logger.info('image size = %s',(r_nbins*eta_nbins*phi_nbins))

   logger.info('processes = %s',options.nprocs)

   pool = multiprocessing.Pool(processes=options.nprocs)


   for i, _ in enumerate(pool.imap_unordered(convert_events_in_file,filelist), 1):
      logger.info('percent done: %05.2f%%',i*100./len(filelist))
   logger.info('done')



def convert_events_in_file(filename):

   # init reader of data files
   reader = IOIMPL.LCFactory.getInstance().createLCReader()
   # keep event count
   event_counter = 0



   logger.info('file: %s',filename)

   image_list = []

   try:

      # open file
      reader.open(filename)

      for event in reader:
         event_counter += 1
         logger.info('event %08i',event_counter)

         image = numpy.zeros((r_nbins,eta_nbins,phi_nbins))


         vxdhits = event.getCollection('VXD_TrackerHits')
         logger.debug('%s VXD track hits',len(vxdhits))
         for vxdhit in vxdhits:
            (rbin,etabin,phibin) = get_spherical_bin(vxdhit.getPositionVec())
            image[rbin,etabin,phibin] += vxdhit.getEDep()

         tkrhits = event.getCollection('TKR_TrackerHits')
         logger.debug('%s TKR track hits',len(tkrhits))
         for tkrhit in tkrhits:
            (rbin,etabin,phibin) = get_spherical_bin(tkrhit.getPositionVec())
            image[rbin,etabin,phibin] += tkrhit.getEDep()

         embarcoll = event.getCollection('EcalBarrelHits')
         logger.debug('%s EM_BARREL entries',len(embarcoll))

         for embar in embarcoll:
            (rbin,etabin,phibin) = get_spherical_bin(embar.getPositionVec())
            image[rbin,etabin,phibin] += embar.getEnergy()

         emeccoll = event.getCollection('EcalEndcapHits')
         logger.debug('%s EM_ENDCAP entries',len(emeccoll))

         for emec in emeccoll:
            (rbin,etabin,phibin) = get_spherical_bin(emec.getPositionVec())
            image[rbin,etabin,phibin] += emec.getEnergy()

         hadbarcoll = event.getCollection('HcalBarrelHits')
         logger.debug('%s HAD_BARREL entries',len(hadbarcoll))

         for hadbar in hadbarcoll:
            (rbin,etabin,phibin) = get_spherical_bin(hadbar.getPositionVec())
            image[rbin,etabin,phibin] += hadbar.getEnergy()

         hadeccoll = event.getCollection('HcalEndcapHits')
         logger.debug('%s HAD_ENDCAP entries',len(hadeccoll))

         for hadec in hadeccoll:
            (rbin,etabin,phibin) = get_spherical_bin(hadec.getPositionVec())
            image[rbin,etabin,phibin] += hadec.getEnergy()

         image_list.append(image)


      # close file
      reader.close()

      # save images
      image_list = numpy.array(image_list)
      numpy.savez_compressed(filename.replace('.slcio',''),image_list)
   except:
      logger.exception('received exception while processing file "%s" will try to continue',filename)
      if len(image_list) > 0:
         # save any images already processed
         image_list = numpy.array(image_list)
         numpy.savez_compressed(filename.replace('.slcio',''),image_list)
         

   logger.info('events processed: %s',event_counter)

   


if __name__ == "__main__":
   main()
