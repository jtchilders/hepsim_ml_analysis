import numpy

# this is all taken from the Rivet/./Tools/ParticleIdUtils.hh

nj=1
nq3=2
nq2=3
nq1=4
nl=5
nr=6
n=7
n8=8
n9=9
n10=10
location = [nj,nq3,nq2,nq1,nl,nr,n,n8,n9,n10]

def _digit(loc,pid):
   #  PID digits (base 10) are: n nr nl nq1 nq2 nq3 nj (cf. Location)
   if loc not in location: return -1
   numerator = int(10.0**(loc-1))
   x=  int(numpy.fabs(pid)/numerator) % 10
   return x

def _extraBits(pid):
   return int(numpy.fabs(pid)/10000000)

# @brief Return the first two digits if this is a "fundamental" particle
# @note ID = 100 is a special case (internal generator ID's are 81-100)
def  _fundamentalID(pid):
   if _extraBits(pid) > 0: return 0
   if _digit(nq2,pid) == 0 and _digit(nq1,pid) == 0:
     return int(numpy.fabs(pid)) % 10000
   elif numpy.fabs(pid) <= 100:
     return int(numpy.fabs(pid))
   else:
     return 0


# Check to see if this is a valid meson
def isMeson(pid):
   if _extraBits(pid) > 0: return False
   aid = numpy.fabs(pid)
   if aid == 130 or aid == 310 or aid == 210: return True; #< special cases for kaons
   if aid <= 100: return False
   if _digit(nq1,pid) != 0: return False
   if _digit(nq2,pid) == 0: return False
   if _digit(nq3,pid) == 0: return False
   if _digit(nq2,pid) < _digit(nq3,pid): return False
   # EvtGen uses some odd numbers
   # @todo Remove special-casing for EvtGen
   if aid == 150 or aid == 350 or aid == 510 or aid == 530: return True
   # Pomeron, Reggeon, etc.
   if isReggeon(pid): return False #//true; //< WTF?
   # Check for illegal antiparticles
   if _digit(nj,pid) > 0 and _digit(nq3,pid) > 0 and _digit(nq2,pid) > 0 and _digit(nq1,pid) == 0:
     return  not (_digit(nq3,pid) == _digit(nq2,pid) and pid < 0)
   
   return False


def isBaryon(pid):
   if _extraBits(pid) > 0: return False
   if numpy.fabs(pid) <= 100: return False
   if _fundamentalID(pid) <= 100 and _fundamentalID(pid) > 0: return False
   if numpy.fabs(pid) == 2110 or numpy.fabs(pid) == 2210: return True
   if _digit(nj,pid) == 0: return False
   if _digit(nq1,pid) == 0 or _digit(nq2,pid) == 0 or _digit(nq3,pid) == 0: return False
   return True

# Check to see if this is a valid pentaquark
def isPentaquark(pid):
   # a pentaquark is of the form 9abcdej,
   # where j is the spin and a, b, c, d, and e are quarks
   if _extraBits(pid) > 0: return False
   if _digit(n,pid) != 9:  return False
   if _digit(nr,pid) == 9 or _digit(nr,pid) == 0:  return False
   if _digit(nj,pid) == 9 or _digit(nl,pid) == 0:  return False
   if _digit(nq1,pid) == 0:  return False
   if _digit(nq2,pid) == 0:  return False
   if _digit(nq3,pid) == 0:  return False
   if _digit(nj,pid) == 0:  return False
   # check ordering
   if _digit(nq2,pid) > _digit(nq1,pid):  return False
   if _digit(nq1,pid) > _digit(nl,pid):  return False
   if _digit(nl,pid) > _digit(nr,pid):  return False
   return True
    
# Is this a valid hadron ID?
def isHadron(pid):
   if _extraBits(pid) > 0: return False
   if isMeson(pid): return True
   if isBaryon(pid): return True
   if isPentaquark(pid): return True
   return False

# Return the first two digits if this is a "fundamental" particle
# ID = 100 is a special case (internal generator ID's are 81-100)
def _fundamentalID(pid):
   if _extraBits(pid) > 0: return 0
   if _digit(nq2,pid) == 0 and _digit(nq1,pid) == 0:
      return abs(pid) % 10000;
   elif numpy.fabs(pid) <= 100:  return numpy.fabs(pid)
   else: return 0
   
# Parton content functions
def  _hasQ(pid,q):
   if numpy.fabs(pid) == q: return True #< trivial case!
   if _extraBits(pid) > 0: return False
   if _fundamentalID(pid) > 0: return False
   x =  _digit(nq3,pid) == q or _digit(nq2,pid) == q or _digit(nq1,pid) == q
   return x
    

# Does this particle contain a down quark?
def hasDown(pid): return _hasQ(pid, 1)
# Does this particle contain an up quark?
def hasUp(pid): return _hasQ(pid, 2)
# Does this particle contain a strange quark?
def hasStrange(pid): return _hasQ(pid, 3)
# Does this particle contain a charm quark?
def hasCharm(pid): return _hasQ(pid, 4)
# Does this particle contain a bottom quark?
def hasBottom(pid): return _hasQ(pid, 5)
# Does this particle contain a top quark?
def hasTop(pid): return _hasQ(pid, 6)

