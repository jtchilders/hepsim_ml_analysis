#!/usr/bin/env python
import os,sys,optparse,logging,glob,numpy,json,ROOT,time,fastjet
from pyLCIO import IOIMPL
reader = IOIMPL.LCFactory.getInstance().createLCReader()
import id_tools
ROOT.gROOT.SetBatch()

def clean_jets(jets):

   main_list = []

   for jetA in jets:
      main_list.append(jetA)
   
   imax = len(main_list)
   i = 0
   while i < imax:
      jetA = main_list[i]
      
      j = i+1
      while j < imax:
         jetB = main_list[j]

         dr = numpy.sqrt( (jetA.eta()-jetB.eta())**2 + (jetA.phi()*jetB.phi())**2  )

         if dr < 0.2:
            del main_list[j]
            imax -= 1

         j += 1
      i += 1

   return main_list


def angle(px,py,pz,qx,qy,qz):
   
   p_dot_q = px*qx + py*qy + pz*qz
   p = numpy.sqrt( px*px + py*py + pz*pz )
   q = numpy.sqrt( qx*qx + qy*qy + qz*qz )

   cosTheta = p_dot_q / (p*q)

   return numpy.arccos(cosTheta)

def print_daughters(particle,string):
   if  particle.getEnergy() > 25. and particle.getGeneratorStatus() == 3:
      for daught in particle.getDaughters():
         mom = daught.getMomentumVec()
         print string % (daught.getPDG(),daught.getGeneratorStatus(),
                       daught.getParents().size(),daught.getDaughters().size(),daught.getEnergy(),
                       mom[0],mom[1],mom[2],daught)
         print_daughters(daught,' ' + string)

print sys.argv
reader.open(sys.argv[1])

#can = ROOT.TCanvas('can','can',0,0,800,600)

hist = ROOT.TH3D('hist','hist',100,-5000,5000,100,-5000,5000,100,-8000,8000)

#first = True
first_event = True
counter = 0
for event in reader:
   
   if first_event:
      print dir(event)
      print 'Collections: '
      for name in event.getCollectionNames():
         print '    ',name

   ### TRUTH PARTICLES

   mcp = event.getCollection('MCParticle')
   first = True
   particles = []
   for particle in mcp:
      mom = particle.getMomentumVec()
      e = particle.getEnergy()
      pid = particle.getPDG()
      pstat = particle.getGeneratorStatus()

      begin = numpy.array(particle.getVertexVec())
      end = numpy.array(particle.getEndpointVec())
      distance = numpy.linalg.norm(end-begin)
      #print pid,distance,e

      if first_event and first:
         print dir(particle)
         first = False
         
      if id_tools.hasBottom(pid):
         print '<< id: %10d E: %10.2f dist: %10.2f stat: %5d isB: %5d - %s %s %s %s %s %s %s %s' % (pid,e,distance,pstat,id_tools.hasBottom(pid),
                  particle.isCreatedInSimulation(),particle.isBackscatter(),particle.vertexIsNotEndpointOfParent(),
                  particle.isDecayedInTracker(),particle.isDecayedInCalorimeter(),particle.hasLeftDetector(),
                  particle.isStopped(),particle.isOverlay())


      if distance > 1:
         jet = fastjet.PseudoJet(mom[0],mom[1],mom[2],e)
         jet.set_user_index(pid)
         particles.append(jet)
        
   
   jet_def = fastjet.JetDefinition(fastjet.antikt_algorithm,0.4)

   cs = fastjet.ClusterSequence(particles,jet_def)
   jets = fastjet.sorted_by_pt(cs.inclusive_jets())
   if first_event: print dir(jets)
   
   print '<',len(jets)
   jets = clean_jets(jets)
   print '>',len(jets)
   
   first = True
   jet_num=0
   for jet in jets:
      if first_event and first:
         print dir(jet)
         first = False

      if jet_num > 20: break
      jet_num += 1
      constituents = fastjet.sorted_by_pt(jet.constituents())
      print '  jet pt: %10.2f  eta: %10.2f phi: %10.2f' % (jet.pt(),jet.eta(),jet.phi())
      for con in constituents:
         
         if id_tools.hasBottom(con.user_index()):
            a = angle(jet.px(),jet.py(),jet.pz(),con.px(),con.py(),con.pz())
            print '   id: ',con.user_index(),' pt: ',con.pt(), ' angle: ',a
   

   embar = event.getCollection('EcalBarrelHits')
   HT = 0.
   
   gembar = ROOT.TGraph2D()
   gembar.SetName('gembar')
   gembar.SetMarkerStyle(20)
   gembar.SetMarkerSize(0.2)
   gembar.SetMarkerColor(ROOT.kRed)
   #gembar.SetHistogram(hist)
   point_counter = 1
   first = True
   for channel in embar:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEnergy()

      HT += energy

      
      if energy > 0.1:
         gembar.SetPoint(point_counter,x,y,z)
         point_counter += 1
   
   counter += point_counter
   
   emec = event.getCollection('EcalEndcapHits')
   gemec = ROOT.TGraph2D()
   gemec.SetName('gemec')
   gemec.SetMarkerStyle(20)
   gemec.SetMarkerSize(0.2)
   gemec.SetMarkerColor(ROOT.kGreen)
   point_counter = 1
   first = True
   for channel in emec:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEnergy()
      
      HT += energy
      

      if energy > 0.1:
         gemec.SetPoint(point_counter,x,y,z)
         point_counter += 1
   
   counter += point_counter
   

   hadbar = event.getCollection('HcalBarrelHits')
   ghadbar = ROOT.TGraph2D()
   ghadbar.SetName('ghadbar')
   ghadbar.SetMarkerStyle(20)
   ghadbar.SetMarkerSize(0.2)
   ghadbar.SetMarkerColor(ROOT.kBlue)
   point_counter = 1
   first = True
   for channel in hadbar:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEnergy()
      
      HT += energy
      

      if energy > 0.1:
         ghadbar.SetPoint(point_counter,x,y,z)
         point_counter += 1

   counter += point_counter
   

   hadec = event.getCollection('HcalEndcapHits')
   ghadec = ROOT.TGraph2D()
   ghadec.SetName('ghadec')
   ghadec.SetMarkerStyle(20)
   ghadec.SetMarkerSize(0.2)
   ghadec.SetMarkerColor(ROOT.kCyan)
   point_counter = 1
   first = True
   for channel in hadec:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEnergy()
      
      HT += energy
      

      if energy > 0.1:
         ghadec.SetPoint(point_counter,x,y,z)
         point_counter += 1

   counter += point_counter
   

   vxdhits = event.getCollection('VXD_TrackerHits')
   gvxd = ROOT.TGraph2D()
   gvxd.SetName('gvxd')
   gvxd.SetMarkerStyle(20)
   gvxd.SetMarkerSize(0.2)
   gvxd.SetMarkerColor(ROOT.kOrange)
   point_counter = 1
   first = True
   for channel in vxdhits:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEDep()
      
      HT += energy
      

      if energy > 0.1:
         gvxd.SetPoint(point_counter,x,y,z)
         point_counter += 1

   counter += point_counter
   



   tkrhits = event.getCollection('TKR_TrackerHits')
   gtkr = ROOT.TGraph2D()
   gtkr.SetName('gtkr')
   gtkr.SetMarkerStyle(20)
   gtkr.SetMarkerSize(0.2)
   gtkr.SetMarkerColor(ROOT.kYellow)
   point_counter = 1
   first = True
   for channel in tkrhits:
      if point_counter == 1 and first_event and first:
         print dir(channel)
         first = False
      
      x,y,z = channel.getPositionVec()[0],channel.getPositionVec()[1],channel.getPositionVec()[2]
      energy = channel.getEDep()
      
      HT += energy
      

      if energy > 0.1:
         gtkr.SetPoint(point_counter,x,y,z)
         point_counter += 1

   counter += point_counter
   
   print counter
   print energy

   first_event = False

   #hist.Draw()
   #gembar.Draw('p same')
   #gemec.Draw('p same')
   #ghadbar.Draw('p same')
   #ghadec.Draw('p same')
   #gvxd.Draw('p same')
   #gtkr.Draw('p same')
   #can.Update()
   #raw_input('...')

