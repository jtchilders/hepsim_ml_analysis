#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,json,ROOT
from pyLCIO import IOIMPL
logger = logging.getLogger(__name__)

numpy.seterr(all = 'raise')

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

r_nbins = 50
r_max = 4700
r_delta = float(r_max)/float(r_nbins)

eta_nbins = 50
eta_max = numpy.pi
eta_delta = float(eta_max)/float(eta_nbins)


phi_nbins = 100
phi_max = 2*numpy.pi
phi_delta = float(phi_max)/float(phi_nbins)

max_r = -99999
min_r = 99999

max_theta = -11
min_theta = 11

max_phi = -11
min_phi = 11

def get_spherical( (x,y,z) ):
   global max_r,min_r,max_theta,min_theta,max_phi,min_phi
   try:
      r = numpy.sqrt( x*x + y*y + z*z )
      if r > max_r: max_r = r
      if r < min_r: min_r = r
      theta = numpy.arctan2(y,x)
      if theta > max_theta: max_theta = theta
      if theta < min_theta: min_theta = theta
      phi = numpy.arccos(z/r)
      if phi > max_phi: max_phi = phi
      if phi < min_phi: min_phi = phi
      eta = -1.*numpy.log(numpy.tan(phi/2.))
   except:
      logger.error(' failed to convert x,y,z = %s,%s,%s ',x,y,z)
      raise
   return (r,eta,theta)

def get_spherical_bin( (x,y,z) ):
   
   (r,eta,phi) = get_spherical( (x,y,z) )

   r_bin =  int(r/r_delta)
   eta_bin = int(eta/eta_delta)
   phi_bin = int(phi/phi_delta)
   
   return (r_bin,eta_bin,phi_bin)



def main():
   global max_r,min_r,max_theta,min_theta,max_phi,min_phi
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
   position = []
   for filename in filelist:
      logger.info('file: %s',filename)

      # open file
      reader.open(filename)

      for event in reader:
         event_counter += 1
         logger.info('event %08i',event_counter)
         logger.info('event.getCollectionNames()= ')
         for name in event.getCollectionNames():
            logger.info('   %s',name)

         embarcoll = event.getCollection('EcalBarrelHits')
         logger.info('%s EM_BARREL entries',len(embarcoll))

         # embar contains: ['_IMPL::AccessChecked__checkAccess', '_IMPL::AccessChecked__setReadOnly', '__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__', '__dict__', '__dispatch__', '__div__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__mul__', '__ne__', '__new__', '__nonzero__', '__radd__', '__rdiv__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__rsub__', '__scope__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__weakref__', '_get_smart_ptr', '_lcrtrel::LCRTRelations__cleaners', '_lcrtrel::LCRTRelations__nextID', 'clone', 'getCellID0', 'getCellID1', 'getEnergy', 'getEnergyError', 'getLorentzVec', 'getPosition', 'getPositionVec', 'getRawHit', 'getTime', 'getType', 'id', 'setCellID0', 'setCellID1', 'setEnergy', 'setEnergyError', 'setPosition', 'setPositionVec', 'setRawHit', 'setTime', 'setType', 'simpleUID']

         for embar in embarcoll:
            pos = [embar.getPositionVec()[0],embar.getPositionVec()[1],embar.getPositionVec()[2]]
            r,eta,phi = get_spherical( pos )
            pos.append(r)
            pos.append(eta)
            pos.append(phi)
            position.append(pos)


         emeccoll = event.getCollection('EcalEndcapHits')
         logger.info('%s EM_ENDCAP entries',len(emeccoll))

         for emec in emeccoll:
            pos = [emec.getPositionVec()[0],emec.getPositionVec()[1],emec.getPositionVec()[2]]
            r,eta,phi = get_spherical( pos )
            pos.append(r)
            pos.append(eta)
            pos.append(phi)
            position.append(pos)

         hadbarcoll = event.getCollection('HcalBarrelHits')
         logger.info('%s HAD_BARREL entries',len(hadbarcoll))

         for hadbar in hadbarcoll:
            pos = [hadbar.getPositionVec()[0],hadbar.getPositionVec()[1],hadbar.getPositionVec()[2]]
            r,eta,phi = get_spherical( pos )
            pos.append(r)
            pos.append(eta)
            pos.append(phi)
            position.append(pos)

         hadeccoll = event.getCollection('HcalEndcapHits')
         logger.info('%s HAD_ENDCAP entries',len(hadeccoll))

         for hadec in hadeccoll:
            pos = [hadec.getPositionVec()[0],hadec.getPositionVec()[1],hadec.getPositionVec()[2]]
            r,eta,phi = get_spherical( pos )
            pos.append(r)
            pos.append(eta)
            pos.append(phi) 
            position.append(pos)
         
         
      # close file
      reader.close()

   json.dump(sorted(position),open('calorimeter_position.json','w'))

   logger.info('len(position): %s',len(position))
   # without endcaps = 35832, with endcaps = 93062

   x = [];y=[];z=[]
   r = [];eta=[];phi=[]
   for p in position:
      x.append(p[0])
      y.append(p[1])
      z.append(p[2])
      r.append(p[3])
      eta.append(p[4])
      phi.append(p[5])

   x = sorted(list(set(x)))
   y = sorted(list(set(y)))
   z = sorted(list(set(z)))
   r = sorted(list(set(r)))
   eta = sorted(list(set(eta)))
   phi = sorted(list(set(phi)))

   logger.info('len(x):   %s x[0]:   %s x[-1]:   %s',len(x),x[0],x[-1])
   logger.info('len(y):   %s y[0]:   %s y[-1]:   %s',len(y),y[0],y[-1])
   logger.info('len(z):   %s z[0]:   %s z[-1]:   %s',len(z),z[0],z[-1])
   logger.info('len(r):   %s r[0]:   %s r[-1]:   %s',len(r),r[0],r[-1])
   logger.info('len(eta): %s eta[0]: %s eta[-1]: %s',len(eta),eta[0],eta[-1])
   logger.info('len(phi): %s phi[0]: %s phi[-1]: %s',len(phi),phi[0],phi[-1])

   logger.info(' r = %s - %s',min_r,max_r)
   logger.info(' theta = %s - %s',min_theta,max_theta)
   logger.info(' phi = %s - %s',min_phi,max_phi)
'''
without endcaps
2017-08-31 16:43:19,157 INFO:__main__:len(x): 4847 x[0]: -3570.0 x[-1]: 3465.0
2017-08-31 16:43:19,157 INFO:__main__:len(y): 4833 y[0]: -3430.0 y[-1]: 3570.0
2017-08-31 16:43:19,157 INFO:__main__:len(z): 200 z[0]: -4700.0 z[-1]: 4700.0
with endcaps
2017-08-31 18:25:10,376 INFO:__main__:len(x): 4905 x[0]: -3570.0 x[-1]: 3465.0
2017-08-31 18:25:10,376 INFO:__main__:len(y): 4891 y[0]: -3430.0 y[-1]: 3570.0
2017-08-31 18:25:10,376 INFO:__main__:len(z): 336 z[0]: -4700.0 z[-1]: 4700.0
'''

if __name__ == "__main__":
   main()
