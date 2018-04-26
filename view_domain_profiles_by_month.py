import cdms2 as cdms
import vcs, os
import MV2
import cdutil, sys, string
import EzTemplate
import numpy as np
import genutil
import json
import cdutil
import time

vars = ['pac_50S30S','pac_10N30N', 'atl_30N50N','atl_10N30N', 'ind_50S30S','ind_30S10S']

var = 'pac_50S30S_mam'
#var = 'pac_10N30N'
#var = 'atl_30N50N'
#var = 'atl_10N30N_mam'
#var = 'ind_50S30S'
#var = 'ind_30S10S'

var = 'pac_50S30S'
#var = 'atl_30N50N'
var  = 'atl_NH'
#var = 'atl_SH_mam'
#var = 'ind_SH_mam'

lst = os.popen('ls data_regional/*Hosoda-MOAA-PGV*.nc').readlines()
lst = os.popen('ls data_regional/*.nc').readlines()

# VCS background or no
bkg = 0
bkg = 1

# ANNUAL MEAN REMOVED Y or N
am = 'Y'

vmin = -.4
vmax = .4

range_dic = {'atl_10N30N_mam':(-3,3),
             'atl_NH_mam':(-3,3),
             'atl_SH_mam':(-3,3),
             'pac_50S30S_mam':(-3,4),
             'ind_SH_mam':(-3,3),
             'atl_10N30N':(-3,3),
             'atl_NH':(10,25),
             'atl_SH':(10,20),
             'pac_50S30S':(10,20),
             'ind_SH':(-3,3),
  }

xmin = range_dic[var][0]
xmax = range_dic[var][1]


v = vcs.init()

##  THIS APPLIES TO ALL PLOTS root_template = vcs.createtemplate("reduced")
root_template = vcs.createtemplate("reduced")
root_template.blank(["mean", "max", "min", "zvalue", "dataname", "crtime", "ytic2", "xtic2","xname","legend"])

M = EzTemplate.Multi(columns=3,rows=4,template=root_template)

line = vcs.create1d()
#line.datawc_y1 = vmin  #min_vals[tick_sides[n]]
#line.datawc_y2 = vmax   #max_vals[tick_sides[n]]
line.linecolor = 'black'
line.linewidth = 2

line.datawc_x1 = xmin 
line.datawc_x2 = xmax

rangedic = {}
for i in range(xmin,xmax+1):
    rangedic[i] = `i`
 
line.xticlabels1 = rangedic 

plot_title = vcs.createtext()
#plot_title.x = .5
#plot_title.y = .91
plot_title.height = 24
plot_title.halign = "right"   #"center"
plot_title.valign = "top"
plot_title.color="black"
#canvas.plot(plot_title)

pathout = '/work/gleckler1/www/thetaoClimMetrics/plots_domain_profiles/'

months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

#months = ['jan','oct']

for month in months:
 if month == 'jan': m = 0
 if month == 'feb': m = 1
 if month == 'mar': m = 2
 if month == 'apr': m = 3
 if month == 'may': m = 4
 if month == 'jun': m = 5
 if month == 'jul': m = 6
 if month == 'aug': m = 7
 if month == 'sep': m = 8
 if month == 'oct': m = 9 
 if month == 'nov': m = 10 
 if month == 'dec': m = 11 

 plot_title.string = month

 if month == 'jan': pn=M.get(row=0, column=0)
 if month == 'feb': pn=M.get(row=0, column=1)
 if month == 'mar': pn=M.get(row=0, column=2)
 if month == 'apr': pn=M.get(row=1, column=0)
 if month == 'may': pn=M.get(row=1, column=1)
 if month == 'jun': pn=M.get(row=1, column=2)
 if month == 'jul': pn=M.get(row=2, column=0)
 if month == 'aug': pn=M.get(row=2, column=1)
 if month == 'sep': pn=M.get(row=2, column=2)
 if month == 'oct': pn=M.get(row=3, column=0)
 if month == 'nov': pn=M.get(row=3, column=1)
 if month == 'dec': pn=M.get(row=3, column=2)

 pn.legend.priority = 0

 plot_title.x = (pn.data.x1 + pn.data.x2)/2.
 plot_title.y = pn.data.y2 + .02
 v.plot(plot_title,pn,bg=bkg)


 for l in lst:
  f = cdms.open(l)
  tmp = l.split('/')[1]
  mod = tmp.split('.nc')[0]

  bt = time.time()
  d = f(var,time = slice(m,m+1))(squeeze=1)

  if var.find('mam') == -1: d = MV2.subtract(d,273.15) 

### FUTZING HERE to make axis the data, and visa versa.  Also change sign of new coordinate so surface is on top
  t = d.getAxis(0)
  levs = d.getAxis(0)
  levs.axis = 'Z' # need to set this for obs extration to work
  d.setAxis(0,levs)  
  ds = d(level=(150,0))
# print d.getLevel()[:]
# print ds.getLevel()[:]
# w = sys.stdin.readline()
  levsn = ds.getAxis(0)
  for i in range(len(levsn)):
    levsn[i] = -1*levsn[i]
  dr = cdms.createVariable(levsn,id='thetao')
  newax = cdms.createAxis(ds.filled())
  dr.setAxis(0,newax)
################################

# if mod not in obs: v1.plot(d,line)
  line.linecolor = 'black'
  line.linewidth = 2.

  if mod == 'IPRC': line.linecolor = 'red'
  if mod == 'Hosoda-MOAA-PGV': line.linecolor = 'green'
  if mod == 'UCSD': line.linecolor = 'blue'
  if mod in ['IPRC','UCSD','Hosoda-MOAA-PGV']: line.linewidth = 4. 

  v.plot(dr,line, pn,bg=bkg)

  f.close()
  et = time.time() 
  print m, ' ', mod, '     ', `et-bt` 
  v.png(pathout + var) 
#print 'done with ' + var + '_' + mod
#w = sys.stdin.readline()
v.clear()

os.popen('chmod 775 -R  /work/gleckler1/www/thetaoClimMetrics/').readlines()





