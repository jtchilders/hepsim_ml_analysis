import os,sys,optparse,logging,glob,numpy,json,time
from pyLCIO import IOIMPL
reader = IOIMPL.LCFactory.getInstance().createLCReader()
reader.open('pythia8_zprimebb_digi/tev14_pythia8_zbbar_m125_10_skip00190_digi.slcio')
event = reader.readNextEvent()
pts = event.getCollection('MCParticle')

