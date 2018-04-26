import cdms2 as cdms
import vcs, os
import MV2
import cdutil, sys, string
import EzTemplate
import numpy as np
import genutil
import json
import cdutil

vars = ['pac_50S30S','pac_10N30N', 'atl_30N50N','atl_10N30N', 'ind_50S30S','ind_30S10S']

var = 'pac_50S30S'
#var = 'pac_10N30N'
#var = 'atl_30N50N'
#var = 'atl_10N30N'
#var = 'ind_50S30S'
#var = 'ind_30S10S'
#obs = ['UCSD','Hosoda-MOAA-PGV','IPRC']

lst = os.popen('ls data_regional/*Hosoda-MOAA-PGV*.nc').readlines()
lst = os.popen('ls data_regional/*.nc').readlines()

vmin = -.4
vmax = .4

  ## EzTemplate ---
#M = EzTemplate.Multi(template=my_template, rows=2,columns=2, x=canvas)

  # Legend colorbar ---
#M.legend.thickness = 0.4 # Thickness of legend color bar
#M.legend.direction = 'horizontal'

v = vcs.init()

isofill = vcs.createisofill("minmax")
isofill.levels = vcs.mkscale(-3,3)

pathout = '/work/gleckler1/www/thetaoClimMetrics/plots_domain_AC_fcn_depth/'


for var in vars:

 for l in lst:
  f = cdms.open(l)
  tmp = l.split('/')[1]
  mod = tmp.split('.nc')[0]

  d = f(var)
  t = d.getAxis(0)
  levs = d.getAxis(1)
  levs.axis = 'Z' # need to set this for obs extration to work
  d.setAxis(1,levs)  
  d = d(level=(0,150))
  levsn = d.getAxis(1)

  dn = d.filled()
  dn = np.swapaxes(dn,1,0)
  d1 = cdms.createVariable(dn)
  d1.setAxis(0,levsn)
  d1.setAxis(1,t)
  print d1.shape

  d0 = MV2.average(d1,axis=1)
  dmasked, d0 = genutil.grower(d1,d0)

  d1 = MV2.subtract(d1,d0)
  d1.id = var + ': ' + mod
  v.plot(d1[::-1,:],isofill,bg = 0)

  w = sys.stdin.readline()
  v.png(pathout + var + '_' + mod) 
  print 'done with ' + var + '_' + mod
#  w = sys.stdin.readline()
  v.clear()







