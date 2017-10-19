#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,json,time
from pyLCIO import IOIMPL
reader = IOIMPL.LCFactory.getInstance().createLCReader()

'''def iTopCopy(particle):
  parents = particle.getParents()
  while ( iUp > 0 && (*evtPtr)[iUp].mother2() == (*evtPtr)[iUp].mother1()
    && (*evtPtr)[iUp].mother1() > 0) iUp = (*evtPtr)[iUp].mother1();
  return iUp;

int Particle::iBotCopy() const {

  if (evtPtr == 0) return -1;
  int iDn = index();
  while ( iDn > 0 && (*evtPtr)[iDn].daughter2() == (*evtPtr)[iDn].daughter1()
    && (*evtPtr)[iDn].daughter1() > 0) iDn = (*evtPtr)[iDn].daughter1();
  return iDn;

}'''

def add_dot(pt,lvl,parent=None):
   lvl+=1
   out = ''
   if lvl > 3: return out
   for d in pt.getDaughters():
      pid = int(numpy.fabs(pt.getPDG()))
      did = int(numpy.fabs(d.getPDG()))

      if pid == did and d.getParents().size() == 1:
         lvl -= 1
         if parent is not None:
            add_dot(d,lvl,parent)
         else:
            add_dot(d,lvl,pt)
         lvl += 1
      else:
         if parent is not None:
            out+=  (' '*lvl) + 'p%s_%s -> p%s_%s;\n' % (parent,id(parent),did,id(d))
            out+=add_dot(d,lvl)
         else:
            out+=  (' '*lvl) + 'p%s_%s -> p%s_%s;\n' % (pid,id(pt),did,id(d))
            out+=add_dot(d,lvl)
   lvl-=1
   return out

def print_daughters(particle,string):
   if  particle.getEnergy() > 25. and particle.getGeneratorStatus() == 3:
      for daught in particle.getDaughters():
         mom = daught.getMomentumVec()
         print string % (daught.getPDG(),daught.getGeneratorStatus(),
                       daught.getParents().size(),daught.getDaughters().size(),daught.getEnergy(),
                       mom[0],mom[1],mom[2],daught)
         print_daughters(daught,' ' + string)

class Particle:
   def __init__(self):
      self.parents = []
      self.daughters = []

print sys.argv
reader.open(sys.argv[1])

for event in reader:
   
   script = 'strict digraph test{\n'

   ### TRUTH PARTICLES

   

   mcp = event.getCollection('MCParticle')
   particle_counter = 0
   for particle in mcp:
      
      particle_level = 0
      
      pid = particle.getPDG()
      pstat = particle.getGeneratorStatus()
      parents = particle.getParents()
      daughters = particle.getDaughters()
      energy = particle.getEnergy()


      s = "%10d(%5.0f) -> " % (pid,particle.getEnergy())
      

      if pstat != 3 or energy < 100: continue
      
      for d in daughters:
         if d.getGeneratorStatus() != 3 or d.getEnergy() < 100: continue
         script +=  'p%s_%s -> p%s_%s;\n' % (int(numpy.fabs(pid)),id(particle),int(numpy.fabs(d.getPDG())),id(d))
         s += "%10d(%5.0f) " % (d.getPDG(),d.getEnergy())

      for p in parents:
         script += 'p%s_%s -> p%s_%s;\n' % (int(numpy.fabs(p.getPDG())),id(p),int(numpy.fabs(pid)),id(particle))

      #print s
      #script += add_dot(particle,particle_level);

      particle_counter += 1
      if particle_counter > 400: break
   
   script += '}\n'

   #new_script = ''
   #for line in script.split('\n'):
   #   if '->' in line:
         
   
   open('test.txt','w').write(script)

   sys.exit(0)

