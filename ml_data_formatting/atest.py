#!/usr/bin/env python
import json,numpy,ROOT

points = json.load(open('channel_positions.json'))

'''
x=[]
y=[]
z=[]
for i in xrange(len(points)):
   p = points[i]
   x.append(p[0])
   y.append(p[1])
   z.append(p[2])

x = sorted(list(set(x)))
y = sorted(list(set(y)))
z = sorted(list(set(z)))

print x[0],x[-1]
print y[0],y[-1]
print z[0],z[-1]
   
print min_dr
# min_dr = 0.02

x_min x_max
-164.301514611 162.863655954
y_min y_max
-163.107632355 164.353153046
z_min z_max
-1180.98903051 1180.98903051


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

bins = numpy.zeros((n_xbins,n_ybins,n_zbins))
print bins.shape, bins.shape[0]*bins.shape[1]*bins.shape[2]
print len(points)

for point in points:
   x,y,z = get_bin(point)
   bins[x,y,z] += 1
   #print bins[x,y,z]

bincontent = ROOT.TH1I('bincontent','',100,0,100)

for bin in bins.flatten():
   bincontent.Fill(bin)

can = ROOT.TCanvas('can','can',0,0,800,600)
bincontent.Draw()
raw_input('...')




#print bins





