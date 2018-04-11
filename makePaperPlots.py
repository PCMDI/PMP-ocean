#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 15:51:37 2018

Paul J. Durack 19th March 2018

This script generates a figure files for ocean metrics

PJD 20 Jan 2018     - Started
PJD  6 Apr 2018     - Update to run on durack1ml
PJD 11 Apr 2018     - Updated to run on oceanonly and moved to git:PMP-ocean
                    - TODO: Sort out Hosoda 60S+ and 70N+ missing values
                    - TODO: Sort out WOA13v2 grid
                    - TODO: Add in WOA05, EN4, Ishii datasets
                    - TODO: Update all obs
                    - TODO: For all depths, add depth mask to exclude continental halos
                    - TODO: Cleanup input data and sort out provenance beginning to end
                    - TODO: Ascertain if profile issue is also apparent with salinity (rather than just to)

@author: durack1
"""

'''
From: "Gleckler, Peter J." <gleckler1@llnl.gov>
Date: Thursday, January 11, 2018 at 1:16 PM
To: "Durack, Paul J." <durack1@llnl.gov>
Subject: ocean metrics plots...

Howdee..

This code: /export/gleckler1/processing/ohc_clim/ quick_look_clim_ts.py

Produces a simple 12 month line plot of mods/obs for a give basin/zonalband.

We need:

1)	A template to make a publication quality plot
2)	Think about how to arrange multiple panels
3)	Reassess the current set of zones:
'50S30S':(-50,-30),
'30S10S':(-30,-10),
'10N30N':(10,30),
'30N50N':(30,50)

Which are produced for atl, pac, ind (where possible)

VCS or matplotlib?

P

FIG. 1. Maps of vertically integrated amplitude of the annual cycle (Obs-only; 0-700m)
FIG. 1a. Maps of models (Fig 1)
FIG. 2. Zonal means of obs and models (global, pac, atl, ind; Use basinmasks)
FIG. 3. Taylor diagram of maps in 1 (Obs vs models; basins [pac, atl, ind] and hemis)
matplotlib: https://github.com/PCMDI/pcmdi_metrics/tree/345_pjg_taylor_diagram/src/python/devel/taylor_diagram_mpl
VCS: https://uvcdat.llnl.gov/Jupyter/Taylor_Diagrams/Taylor_Diagrams.html
FIG. 3a. Sensitivity tests (model native vs regridded, based on domain averages)
See https://oceanonly.llnl.gov/gleckler1/thetaoClimMetrics/plots_domain_AC_fcn_depth/atl_10N30N_ACCESS1-0.png hovmoeller
Hoevmoller - blue through white to red (colour axis)
Have to be careful of the insolation max, so constraining analysis to a hemisphere-only, rather than a hemi subset (10N-30N)
Consider "bleeding" of residual into the ocean interior during each annual cycle peak - if the annual cycle magnitude
increases year on year, then the residual should scale linearly with this - a process diagnostic for ocean heating?
FIG. 4. Hovmoller time evolution
https://oceanonly.llnl.gov/gleckler1/thetaoClimMetrics/plots_domain_AC_fcn_depth/
FIG. 5. RMS error 12 time points (seasonal cycle)
Elucidate how ohc amplitude looks spatially
FIG. 6. Profiles for regions/max rate of change (derivative) - global isn’t useful, as regionality of MLD is key
Movie: illustrative surface insolation with seasonally-evolving temperature profiles through depth (surface energy - WHOI
OAFlux, surface downwelling CERES)
'''
#%% Imports
import datetime,gc,glob,os,socket #,pdb
import cdms2 as cdm
import cdutil as cdu
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

#%% Change dir and set variables
if 'ocean' in socket.gethostname():
    homePath = '/work/durack1/Shared/170906_PaperPlots_OceanMetrics'
elif 'durack1ml' in socket.gethostname():
    homePath = '/sync/Shared/170906_PaperPlots_OceanMetrics'
os.chdir(homePath)
destPath = os.path.join(homePath,'paperPlots')
dataPath = os.path.join(homePath)
timeFormat = datetime.datetime.now().strftime('%y%m%d')

#%% Figure 1 - Maps of vertically integrated amplitude of annual cycle (1a: 150m, 1b: 300m, 1c: 500m; 1d: 700m: 1e: 1000m)
# Create dictionary of levels
depths = {'a':[150,[0,1,2,3,4,5,6,7,8,9,10]], # 150
          'b':[300,[0,1,2,3,4,5,6,7,8]], # 300
          'c':[500,[0,1,2,3,4,5,6]], # 500
          #'d':[700,[0,.5,1,1.5,2,2.5,3]], # 700
          'd':[700,[0,.25,.5,.75,1,1.25,1.5]], # 700
          'e':[1000,[0,.25,.5,.75,1,1.25,1.5,1.75,2]] # 1000
          }
depths = OrderedDict(sorted(depths.items()))

# Get file list
fileList = glob.glob(os.path.join(dataPath,'thetao*.nc'))
# Generate depth-averaged values
for count1, key in enumerate(depths.keys()): #[3]
    depthInt = depths.get(key)[0]
    depthScale = depths.get(key)[1]
    for count2,filePath in enumerate(fileList):
        print count2, filePath.split('/')[-1]
        fH = cdm.open(filePath)
        var = fH('to_AllAtOnce')
        if 'Hosoda' in filePath:
            varTmp = np.ma.masked_where(var==0.0,var) ; # Try replacing 60S+, 70N+
            varTmp = cdm.createVariable(varTmp)
            varTmp.setAxis(0,var.getAxis(0))
            varTmp.setAxis(1,var.getAxis(1))
            varTmp.setAxis(2,var.getAxis(2))
            varTmp.setAxis(3,var.getAxis(3))
            var = varTmp ; del(varTmp)
        elif 'WOA13v2' in filePath:
            varTmp = np.concatenate([var[:,:,:,180:],var[:,:,:,0:180]],axis=3)
            varTmp = np.ma.masked_where(varTmp==1e20,varTmp)
            varTmp = cdm.createVariable(varTmp)
            varTmp.setAxis(0,var.getAxis(0))
            varTmp.setAxis(1,var.getAxis(1))
            varTmp.setAxis(2,var.getAxis(2))
            varTmp.setAxis(3,var.getAxis(3))
            var = varTmp ; del(varTmp)
        lats = var.getLatitude()
        lons = var.getLongitude()
        fH.close()
        levs = var.getLevel()
        depthInd, = np.where(levs[:] == depthInt)[0]
        print count1, depths.get(key), depthInd
        tmp = cdu.averager(var[:,0:depthInd,],axis=1,
                           action='average')
#                           weights=levs.getBounds()[0:depthInd],
        tmpmin = np.amin(tmp,axis=0) ; # argmin - tmp.argmin(axis=0) - Returns int indexes
        tmpmax = np.amax(tmp,axis=0) ; # amin - Returns min values
        tmpdiff = tmpmax-tmpmin
        vars()[''.join(['depth',str(count2),'diff'])] = tmpdiff
        #vars()[''.join(['depth',str(count1),str(count2),'min'])] = tmpmin
        #vars()[''.join(['depth',str(count1),str(count2),'max'])] = tmpmax
        #vars()[''.join(['depth',str(count1),str(count2)])] = tmp
    # Plot all 4 obs
    axWidth = .44 ; axHeight = .28
    row3Y = .68 ; row2Y = .37 ; row1Y = .06
    col1X = .08 ; col2X = .54
    fontSize = 10 ; titPosition = (.5,.97)
    fig=plt.figure(num=None,figsize=(8, 6),dpi=300,facecolor='w',edgecolor='w')
    #fig.suptitle(''.join(['0-',str(depthInt),' depth-averaged temperature']))
    ax1 = plt.subplot(321)
    plt.set_cmap('RdBu_r')
    extendVal = 'max'
    #plt.tight_layout() ; # Fill out - but leads to axis overruns
    plt.contourf(lons,lats,depth0diff,depthScale,extend=extendVal)
    ax1.set_xticklabels([])
    txtAx1 = ax1.set_title('Hosoda-MOAA-PGV',fontsize=fontSize,position=titPosition)
    ax1.set_position([col1X,row3Y,axWidth,axHeight])
    ax2 = plt.subplot(322)
    plt.contourf(lons,lats,depth1diff,depthScale,extend=extendVal)
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])
    ax2.set_title('IPRC',fontsize=fontSize,position=titPosition)
    ax2.set_position([.54,row3Y,axWidth,axHeight])
    ax3 = plt.subplot(323)
    plt.contourf(lons,lats,depth2diff,depthScale,extend=extendVal)
    ax3.set_xticklabels([])
    ax3.set_title('UCSD',fontsize=fontSize,position=titPosition)
    ax3.set_position([col1X,row2Y,axWidth,axHeight])
    ax4 = plt.subplot(324)
    plt.contourf(lons,lats,depth3diff,depthScale,extend=extendVal)
    ax4.set_yticklabels([])
    ax4.set_title('WOA09',fontsize=fontSize,position=titPosition)
    ax4.set_position([col2X,row2Y,axWidth,axHeight])
    ax5 = plt.subplot(325)
    plt.contourf(lons,lats,depth4diff,depthScale,extend=extendVal)
    ax5.set_title('WOA13v2',fontsize=fontSize,position=titPosition)
    ax5.set_position([col1X,row1Y,axWidth,axHeight])
    ax6 = plt.subplot(326)
    ax6.axis('off')
    ax6.set_position([col2X,row1Y,axWidth,axHeight])
    #cbaxes = fig.add_axes([0.52, 0.3, 0.48, 0.1])
    #plt.colorbar(ax6,cax=cbaxes,orientation='horizontal',extend='both')
    # https://stackoverflow.com/questions/13310594/positioning-the-colorbar
    cbaxes = fig.add_axes([col2X,.17,axWidth,.025])
    cb = plt.colorbar(orientation='horizontal',cax=cbaxes)
    txt1 = fig.text(.55,.23,''.join(['0-',str(depthInt),'m depth-averaged temp diff (max-min)']))
    #plt.show()
    if depthInt == 700:
        outFile = ''.join([timeFormat,'_Fig1_temp-',str(depthInt),'m.png'])
    else:
        outFile = ''.join([timeFormat,'_Fig1s_temp-',str(depthInt),'m.png'])
    if os.path.exists(outFile):
        os.remove(outFile)
    print 'Saving:',outFile
    fig.savefig(outFile)
    #pdb.set_trace()
    del(count2,key,depthInt,depthInd,tmp,tmpmin,tmpmax,tmpdiff)
del(count1,filePath,levs,var) ; gc.collect()

#%% Figure 2 - Zonal means of obs and models (global, pac, atl, ind; Use basinmasks)

#%% Figure 3 - Taylor diagram of maps in 1 (Obs vs models; basins [pac, atl, ind] and hemis)

#%% Figure 4 - Hovmoller time evolution


#%% Plot test
'''
fig=plt.figure()
plt.subplot(221)
plt.contourf(lons,lats,depth00diff,np.arange(0,11))
plt.colorbar()

#ax=fig.add_axes([0.1,0.1,0.8,0.8])
'''