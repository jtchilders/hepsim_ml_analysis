#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,json,ROOT
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

'''

x_delta = 100
x_offset = 3570
n_xbins = x_offset*2/x_delta
y_delta = 100
y_offset = 3570
n_ybins = y_offset*2/y_delta
z_delta = 100
z_offset = 4700
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

   # get file list
   filelist = glob.glob(options.input_glob)
   # init reader of data files
   reader = IOIMPL.LCFactory.getInstance().createLCReader()
   # keep event count
   event_counter = 0

   can = ROOT.TCanvas('can','can',300,0,800,600)

   energy = ROOT.TH1D('energy',';energy (units=?)',10000,1e-6,1e-1)

   logger.info('image size = %s',(n_xbins*n_ybins*n_zbins))

   logger.info('processing %s files',len(filelist))
   for filename in filelist:
      logger.info('file: %s',filename)

      # open file
      reader.open(filename)

      for event in reader:
         event_counter += 1
         logger.info('event %08i',event_counter)

         vxdhits = event.getCollection('VXD_TrackerHits')
         for vxdhit in vxdhits:
            energy.Fill(vxdhit.getEDep())

         tkrhits = event.getCollection('TKR_TrackerHits')
         for tkrhit in tkrhits:
            energy.Fill(tkrhit.getEDep())

         embarcoll = event.getCollection('EcalBarrelHits')
         for embar in embarcoll:
            energy.Fill(embar.getEnergy()/0.0184)

         emeccoll = event.getCollection('EcalEndcapHits')
         for emec in emeccoll:
            energy.Fill(emec.getEnergy()/0.0184)

         hadbarcoll = event.getCollection('HcalBarrelHits')
         for hadbar in hadbarcoll:
            energy.Fill(hadbar.getEnergy()/0.031)

         hadeccoll = event.getCollection('HcalEndcapHits')
         for hadec in hadeccoll:
            energy.Fill(hadec.getEnergy()/0.031)

         #logger.info('done iterating over bincontent')
         #bincontent.Draw()
         #can.Update()

         #raw_input('...')

      # close file
      reader.close()

      energy.Draw()
      can.Update()
      raw_input('...')




if __name__ == "__main__":
   main()
