#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,json
from pyLCIO import IOIMPL
logger = logging.getLogger(__name__)

''' list of collections:
BeamCalHits
CalorimeterHitRelations
EM_BARREL
EM_ENDCAP
EcalBarrelHits
EcalEndcapHits
HAD_BARREL
HAD_ENDCAP
HcalBarrelHits
HcalEndcapHits
HelicalTrackHitRelations
HelicalTrackHits
HelicalTrackMCRelations
LumiCalHits
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

def get_bin( (x,y,z) ):
   
   xbin = int(( x + x_offset ) / x_delta) - 1
   ybin = int(( y + y_offset ) / y_delta) - 1
   zbin = int(( z + z_offset ) / z_delta) - 1

   return xbin,ybin,zbin

def main():
   ''' simple starter program that can be copied for use when starting a new script. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input-glob',dest='input_glob',help='input glob to grab input filenames, can use wildcards but enclose in quotes like this: "/path/to/file*.txt"')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input_glob',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)

   filelist = glob.glob(options.input_glob)
   reader = IOIMPL.LCFactory.getInstance().createLCReader()
   event_counter = 0
   logger.info('processing %s files',len(filelist))
   for filename in filelist:
      logger.info('file: %s',filename)

      # open file
      reader.open(filename)

      # loop over the events
      max = [0,0,0]
      channel_positions = []
      for event in reader:
         event_counter += 1
         logger.info('event %08i',event_counter)

         # get MC particle collection
         #mcparticles = event.getCollection('MCParticle')

         # loop over particles
         #for entry in mcparticles:
            #if numpy.fabs(entry.getPDG()) == 5:
               #logger.info('particle id: %5s status: %05d energy: %7.2d',entry.getPDG(),entry.getGeneratorStatus(),entry.getEnergy())

         # loop over tracking detector collections
         #event_track_hits = 
         
         vxdhits = event.getCollection('VXD_TrackerHits')
         logger.info('%s VXD track hits',len(vxdhits))
         for vxdhit in vxdhits:

            for i in range(3):
               pos = numpy.fabs(vxdhit.getPositionVec()[i])
               if pos > max[i]:
                  max[i] = pos

            channel_position = [vxdhit.getPositionVec()[0],vxdhit.getPositionVec()[1],vxdhit.getPositionVec()[2]]
            if channel_position not in channel_positions:
               channel_positions.append(channel_position)
         tkrhits = event.getCollection('TKR_TrackerHits')
         logger.info('%s TKR track hits',len(tkrhits))
         for tkrhit in tkrhits:
            
            for i in range(3):
               pos = numpy.fabs(tkrhit.getPositionVec()[i])
               if pos > max[i]:
                  max[i] = pos

            channel_position = [vxdhit.getPositionVec()[0],vxdhit.getPositionVec()[1],vxdhit.getPositionVec()[2]]
            if channel_position not in channel_positions:
               channel_positions.append(channel_position)
         


      print max

      #json.dump(sorted(channel_positions),open('channel_positions.json','w'))






      # close file
      reader.close()


if __name__ == "__main__":
   main()
