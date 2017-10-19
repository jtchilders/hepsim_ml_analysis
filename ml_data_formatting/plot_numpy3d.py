#!/usr/bin/env python
import os,sys,optparse,logging,numpy,ROOT
logger = logging.getLogger(__name__)

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

def convert_coord(r,eta,phi):
   
   # what we call phi is really theta in spherical coods.
   theta = phi
   # covert eta back to phi
   phi =  2.*numpy.arctan(numpy.e**(-eta))
   
   # convert to cartesian
   x = r*numpy.cos(theta)*numpy.sin(phi)
   y = r*numpy.sin(theta)*numpy.sin(phi)
   z = r*numpy.cos(phi)
   
   return x,y,z

def convert_bin(r_bin,eta_bin,phi_bin):
   
   r   = ( float(r_bin)   * r_delta   ) + r_min
   eta = ( float(eta_bin) * eta_delta ) + eta_min
   phi = ( float(phi_bin) * phi_delta ) + phi_min
   
   return r,eta,phi




def main():
   ''' simple program to plot a 3D detector image using ROOT. '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   ROOT.gStyle.SetOptStat(0)
   
   event_images = numpy.load(options.input)['arr_0']
   
   can = ROOT.TCanvas('can','can',0,0,800,600)

   for image in event_images:
      plot(image,can)
      raw_input('...')
   
   
def plot(image,can):

   #hist = ROOT.TH3F('hist3d',';x;y;z',100,0,8000,100,0,8000,100,0,8000)
   hist = ROOT.TH1F('hist',';energy deposit',100,0,10)

   for r_bin in xrange(r_nbins):
      for eta_bin in xrange(eta_nbins):
         for phi_bin in xrange(phi_nbins):
            #r,eta,phi = convert_bin(r_bin,eta_bin,phi_bin)

            #x,y,z = convert_coord(r,eta,phi)

            hist.Fill(image[r_bin,eta_bin,phi_bin])

   
   can.cd()
   hist.Draw()
   can.Update()

   
   


if __name__ == "__main__":
   main()
