import cdms2 as cdms
import MV2 as MV
import cdutil
import string, os, sys
import genutil
import vcs


obsmp = '/work/durack1/Shared/obs_data/WOD13/170425_WOD13_masks_1deg.nc' 
fo = cdms.open(obsmp)
do = fo('basinmask', longitude = (0.,359.5),depth = (0,0))(squeeze = 1)  # only extracting surface level of basin mask

mask_dic = {}

mask_dic['global'] = 0
mask_dic['atl'] = 1
mask_dic['pac'] = 2
mask_dic['ind'] = 3

zbands_dic = {} 

zbands_dic = {'50S30S':(-50,-30),
           '30S10S':(-30,-10), 
           '10N30N':(10,30),
           '30N50N':(30,50),
           'global':(-90.,90.),
           'NH':(0.,90),
           'SH':(-90.,0) }

levbot = 700. 

#"1: Atlantic Ocean; 2: Pacific Ocean; 3: Indian Ocean; 4: Mediterranean Sea; 5: Baltic Sea; 6: Black Sea; 7: Red Sea; 8: Persian Gulf; 9: Huds
#on Bay; 10: Southern Ocean; 11: Arctic Ocean; 12: Sea of Japan; 13: Kara Sea; 14: Sulu Sea; 15: Baffin Bay; 16: East Mediterranean; 17: West Mediterranean; 18: Sea of Okhotsk; 
#19: Banda Sea; 20: Caribbean Sea; 21: Andaman Basin; 22: North Caribbean; 23: Gulf of Mexico; 24: Beaufort Sea; 25: South China Sea; 26: Barents Sea; 27: Celebes Sea; 28: Aleut
#ian Basin; 29: Fiji Basin; 30: North American Basin; 31: West European Basin; 32: Southeast Indian Basin; 33: Coral Sea; 34: East Indian Basin; 35: Central Indian Basin; 36: So
#uthwest Atlantic Basin; 37: Southeast Atlantic Basin; 38: Southeast Pacific Basin; 39: Guatemala Basin; 40: East Caroline Basin; 41: Marianas Basin; 42: Philippine Sea; 43: Ara
#bian Sea; 44: Chile Basin; 45: Somali Basin; 46: Mascarene Basin; 47: Crozet Basin; 48: Guinea Basin; 49: Brazil Basin; 50: Argentine Basin; 51: Tasman Sea; 52: Atlantic Indian
# Basin; 53: Caspian Sea; 54: Sulu Sea II; 55: Venezuela Basin; 56: Bay of Bengal; 57: Java Sea; 58: East Indian Atlantic Basin;" 

v = vcs.init()
#v.plot(dm)
#w = sys.stdin.readline()

pathin = '/work/gleckler1/processed_data/thetao_clims/'   # for mods
pathin = '/work/durack1/Shared/170906_PaperPlots_OceanMetrics/'   # for obs

if pathin == '/work/gleckler1/processed_data/thetao_clims/': lst = os.popen('ls ' + pathin + '*-woa.nc').readlines()
if pathin == '/work/durack1/Shared/170906_PaperPlots_OceanMetrics/': lst = os.popen('ls ' + pathin + '*_000001-000012_ac.nc').readlines()

basins = ['global','atl','pac','ind']
basins = ['global']

for l in lst:  #[0:2]:
   fc = l[:-1]
   if pathin == '/work/gleckler1/processed_data/thetao_clims/':
    tmp = string.split(l,'/')[5]
    mod = string.split(tmp,'-picontrol')[0] 
    print 'starting mod ', mod
   if pathin == '/work/durack1/Shared/170906_PaperPlots_OceanMetrics/':
    tmp = string.split(l,'/')[5]
    tmp1 = tmp.split('thetao_')[1]
    mod = tmp1.split('_000001-000012_ac.nc')[0]

#   w = sys.stdin.readline()

   f = cdms.open(fc)
   var = 'thetao'
   if pathin == '/work/durack1/Shared/170906_PaperPlots_OceanMetrics/':var = 'to_AllAtOnce'
   d = f(var)

   if pathin == '/work/durack1/Shared/170906_PaperPlots_OceanMetrics/': d = MV.add(d,273.15)

#  print d.shape,' ', do.shape
#  print d.getLongitude()[:]
#  print do.getLongitude()[:]
#  w = sys.stdin.readline()

   g = cdms.open('data_regional/' + mod + '.nc','w+')

   for basin in mask_dic.keys():
    dmasked = d

    if basin != 'global':
     dmasked, dogrown = genutil.grower(dmasked,do)
     dmasked = MV.where(MV.equal(dogrown,mask_dic[basin]),dmasked,MV.masked)
#   v.plot(dmasked) 
#   w = sys.stdin.readline()
#   v.clear()

    for zband in zbands_dic:
     dzb = dmasked(levels=(0,levbot),latitude = zbands_dic[zband])
     dzbavi = cdutil.averager(dzb,axis='123')
     dzbavi.id = basin + '_vi_' + zband
     dzba = cdutil.averager(dzb,axis='23')
     dzba.id = basin + '_' + zband

     dzbavimam = MV.subtract(dzbavi,cdutil.averager(dzbavi,axis=0))
     dzbavimam.id = basin + '_vi_' + zband + '_mam'

     dzbamam = MV.subtract(dzba,cdutil.averager(dzba,axis=0))
     dzbamam.id = basin + '_' + zband + '_mam'

     dzba.index = ''
     dzbavi.index = ''
     dzbavimam.index = ''
     dzbamam.index = ''

     g.write(dzba)
     g.write(dzbavi)
     g.write(dzbavimam)
     g.write(dzbamam)

     print 'done writing ', mod,' ', basin,' ', zband
   g.close()
