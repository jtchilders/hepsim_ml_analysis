#!/usr/bin/env python
from __future__ import division
import os,sys,optparse,logging,glob,numpy,json,time,fastjet,subprocess
import multiprocessing as mp
from pyLCIO import IOIMPL
reader = IOIMPL.LCFactory.getInstance().createLCReader()
import id_tools
logger = logging.getLogger(__name__)

def main():
   ''' program to create a list of events with bjets '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-f','--file-list',dest='filelist',help='Pass a filename to a file which contains a list of files to process. One file per line.')
   parser.add_option('-j','--drjet',dest='drjet',help='The radius of anti-kt jets used.',default=0.4,type='int')
   parser.add_option('-o','--output-file',dest='output_file',help='file to save b-tagging information',default='btagged_jets.txt')
   parser.add_option('-n','--nprocs',dest='nprocs',help='number of pool processes to run',default=4,type='int')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'filelist',
                     'drjet',
                     'output_file',
                     'nprocs'
                  ]

   for man in manditory_args:
      if man not in options.__dict__ or options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   


   # set global jet definition
   global jet_def
   jet_def = fastjet.JetDefinition(fastjet.antikt_algorithm,options.drjet)
   global drjet
   drjet = options.drjet
   
      
   nfiles = get_number_of_files(options.filelist)
   logger.info('processing %s files',nfiles)
   
   pool = mp.Pool(processes=options.nprocs)

   returned = pool.imap_unordered(process_file,file_generator(options.filelist))
   
   output = ''
   for ret in returned:
      output += ret

   
   # open output file
   outfile = open(options.output_file,'w')
   outfile.write(output)

   

'''
   # loop over each file
   for filename in file_generator(options.filelist):
      
      if file_count % one_percent == 0:
         logger.info(' %10d of %10d files processed',file_count,nfiles)
      file_count += 1
      
      start = time.time()
      output = process_file(filename,jet_def,options.drjet)
      logger.info('total: %s',time.time() - start)
'''

def file_generator(filename):
   infile = open(filename)
   for line in infile:
      f =  line.strip()
      #logger.info('file: %s',f)
      yield f
   #logger.info('done')
   

def process_file(filename):
   global jet_def,drjet
   # open file
   #logger.info('filename: %s',filename)
   reader.open(filename.strip())

   output = ''

   # loop over events
   file_event_counter = 0
   for event in reader:
      # get truth particles
      mcps = event.getCollection('MCParticle')
      
      # build list of particles to include in jet finding
      jet_particles = get_jet_particles(mcps)
      
      # run fastjet
      cluster = fastjet.ClusterSequence(jet_particles,jet_def)
      jets = fastjet.sorted_by_pt(cluster.inclusive_jets())
      
      # remove jets that overlap
      jets = id_tools.jet_overlap_removal(jets,drjet/2.)

      # loop over jets and identify those that are b-jet candidates
      for jet in jets:
         cons = fastjet.sorted_by_pt(jet.constituents())
         
         bjet_tag = False
         # loop over constituents and find b-hadrons
         for con in cons:
            if id_tools.hasBottom(con.user_index()):
               bjet_tag = True
               break

         # if this is a b-jet write output to file
         if bjet_tag:
            output += '%s %10d %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f\n' % (filename,file_event_counter,jet.px(),jet.py(),jet.pz(),jet.eta(),jet.phi(),jet.e(),jet.m())
      
      file_event_counter += 1

            
   # close file
   reader.close()

   return output
      
      
def get_number_of_files(filename):
   
   p = subprocess.Popen('wc -l ' + filename,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   out,err = p.communicate()

   return int(out.split()[0])

def get_particle_travel_distance_numpy(p):
   begin = numpy.array(p.getVertexVec())
   end   = numpy.array(p.getEndpointVec())
   return numpy.linalg.norm(end - begin)

def get_particle_travel_distance(p):
   bx,by,bz = p.getVertexVec()
   ex,ey,ez = p.getEndpointVec()
   if bx < 0.001 and by < 0.001 and bz < 0.001 and ex < 0.001 and ey < 0.001 and ez < 0.001: return 0.
   return numpy.sqrt( (bx-ex)*(bx-ex) + (by-ey)*(by-ey) + (bz-ez)*(bz-ez) )

def get_jet_particles(mcparticles):
   # build list of particles to include in jet finding
   jet_particles = []
   for mcp in mcparticles:
      pstat = mcp.getGeneratorStatus()
      # only include particles with status 2 or 1
      if pstat == 3: continue
      pid   = mcp.getPDG()
      dist  = get_particle_travel_distance(mcp)
      # only include particles that travel more than 1 mm
      if dist < 1: continue
      mom   = mcp.getMomentumVec()
      e     = mcp.getEnergy()
      
      jet = fastjet.PseudoJet(mom[0],mom[1],mom[2],e)
      jet.set_user_index(pid)
      jet_particles.append(jet)
   return jet_particles


if __name__ == "__main__":
   main()
