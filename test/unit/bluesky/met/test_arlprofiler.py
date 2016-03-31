"""Unit tests for bluesky.arlprofiler"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime
import tempfile

from py.test import raises
from pyairfire import sun
from numpy.testing import assert_approx_equal

from bluesky.met import arlprofiler

##
## Tests for ARLProfile
##

PROFILE_ONE = """ Meteorological Profile: wrfout_d2.2014053000.f00-11_12hr01.arl
 File start time : 14  5 30  0  0
 File ending time: 14  5 30  1  0

___________________________________________________
 Profile Time:  14  5 30  0  0
 Profile Location:    37.43 -120.40  (136,160)

        PRSS  SHGT  T02M  U10M  V10M  PBLH  TPPA
         hPa                                  mm
     0   996   112  31.5   2.6  -1.8     0     0

        PRES  UWND  VWND  WWND  TEMP  SPHU     TPOT  WDIR  WSPD
               m/s   m/s  mb/h    oC  g/kg       oK   deg   m/s
   993   993   2.5  -1.9  -7.0  31.0   3.2    304.8 307.1   3.1
   984   984   2.5  -1.8  -7.0  29.5   3.0    304.0 305.4   3.1
   973   975   2.3  -1.7  -7.0  27.0   2.8    302.3 307.2   2.9
   958   961   2.4  -1.7  -7.0  25.5   2.5    302.1 305.5   3.0
   940   943   2.5  -1.7  -3.5  24.0   2.4    302.1 304.0   3.0
   918   922   2.6  -1.4  -5.3  22.1   2.4    302.2 299.0   2.9
   891   896   2.6 -0.80  -5.3  19.9   2.4    302.3 287.6   2.7
   855   862   2.3 -1E-1  -3.5  16.7   2.5    302.5 272.7   2.3
   811   820  0.75   1.5  -3.5  13.4   1.3    303.3 206.4   1.7
   766   778  -2.1   4.5  -3.5  11.8  0.24    306.2 155.5   5.0
   722   736  -2.3   3.8  -2.6   9.3  0.37    308.3 149.6   4.4
   662   678  -1.2   3.1  -1.8   4.8  0.33    310.6 158.9   3.4
   588   608   2.7   4.9  -1.3  -1.9  0.31    312.7 209.2   5.7
   520   544   6.5   7.8 -0.88  -8.7  0.85    314.8 219.8  10.2
   458   486   6.3  10.6 -0.66 -15.7  0.45    316.5 211.1  12.3
   402   432   8.8  13.1 -0.44 -22.1  0.75    319.3 214.0  15.8
   351   383  11.8  13.7 -0.33 -28.1  0.50    322.5 221.0  18.1
   304   339  16.4  14.5 -0.22 -34.3  0.46    325.6 228.9  21.9
   262   299  19.0  17.7 -0.11 -40.5  0.26    328.7 227.4  26.0
   224   263  17.5  20.1 -0.11 -47.7  0.11    330.5 221.4  26.6
   189   230  15.4  19.5 -1E-1 -54.5  5E-2    333.0 218.6  24.8
   158   200  16.2  18.3 -3E-2 -59.0  2E-2    339.1 221.9  24.4
   130   174  19.8  17.5 -2E-2 -57.7  2E-2    355.4 228.8  26.4
   106   150  19.6  15.6 -1E-2 -55.9  1E-2    373.6 231.8  25.1
    84   130  15.9  13.3 -1E-2 -57.1  1E-2    387.4 230.4  20.7
    65   112  11.6  10.6 -3E-3 -59.0  1E-2    400.4 228.0  15.7
    49  96.9   7.6   8.9 -2E-3 -60.7  1E-2    414.3 221.1  11.7
    35  83.6   3.8   9.1 -4E-4 -61.6  3E-3    430.2 202.8   9.8
    23  72.3  0.20   9.2 -2E-4 -62.0  1E-3    447.6 181.5   9.2
    13  62.4  -2.8   7.6 -3E-5 -61.9  1E-3    466.9 160.3   8.1
     4  53.9  -5.3   5.1     0 -61.3  2E-3    488.2 134.4   7.3

___________________________________________________
 Profile Time:  14  5 30  1  0
 Profile Location:    37.43 -120.40  (136,160)

        PRSS  SHGT  T02M  U10M  V10M  PBLH  TPPA
         hPa                                  mm
     0   996   112  30.2   3.3  -2.0  1474     0

        PRES  UWND  VWND  WWND  TEMP  SPHU     TPOT  WDIR  WSPD
               m/s   m/s  mb/h    oC  g/kg       oK   deg   m/s
   993   993   3.9  -1.2 -28.8  29.2   2.6    303.0 288.1   4.1
   984   984   4.2  -1.3 -29.9  28.3   2.6    302.8 287.5   4.4
   973   975   4.1  -1.5 -45.4  27.3   2.6    302.7 289.9   4.3
   958   961   4.0  -1.4 -47.4  26.0   2.6    302.6 289.9   4.3
   940   943   4.0  -1.6 -62.1  24.6   2.6    302.8 291.8   4.3
   918   921   3.8  -1.8 -62.0  22.5   2.6    302.7 295.1   4.2
   891   896   3.4  -1.9 -43.6  20.2   2.6    302.7 298.8   3.9
   855   862   2.9  -2.0 -14.8  16.9   2.4    302.7 304.9   3.5
   810   820  0.89  0.80  13.6  13.6   1.4    303.6 228.5   1.2
   766   778  -2.1   4.8  13.7  12.0  0.26    306.4 156.9   5.2
   722   736  -2.8   4.0     0   9.5  0.38    308.5 145.4   4.8
   662   678  -2.5   3.0     0   4.8  0.32    310.6 141.3   3.9
   588   608   1.3   4.0     0  -1.9  0.36    312.7 198.5   4.2
   520   544   5.2   6.8     0  -8.7  0.76    314.8 217.7   8.5
   458   486   5.8  10.4     0 -15.7  0.51    316.5 209.6  11.9
   402   432   8.8  12.9   4.3 -22.1  0.73    319.2 214.7  15.6
   351   383  11.5  13.4   4.5 -28.3  0.50    322.2 221.1  17.7
   304   339  15.6  13.6     0 -34.2  0.44    325.5 229.1  20.7
   262   299  17.5  15.9   3.5 -40.6  0.24    328.5 227.9  23.6
   224   263  16.6  18.0   5.3 -47.8  0.12    330.4 222.9  24.5
   189   230  15.0  18.2   4.3 -54.1  5E-2    333.6 219.9  23.6
   158   200  16.7  18.2   1.5 -57.9  2E-2    341.0 222.8  24.7
   130   174  19.1  17.3 -0.97 -57.2  2E-2    356.2 228.3  25.8
   106   150  18.8  14.9  -2.9 -55.7  1E-2    373.9 231.9  24.0
    84   130  15.0  12.0  -2.3 -57.0  1E-2    387.5 231.7  19.3
    65   112  11.2   9.7  -1.6 -59.2  1E-2    400.1 229.3  14.8
    49  96.9   8.0   8.5 -0.86 -61.2  5E-3    413.3 223.5  11.7
    35  83.6   5.2   9.4 -0.57 -62.2  3E-3    429.0 209.0  10.7
    23  72.3   2.2  10.3 -0.93 -62.6  1E-3    446.5 192.6  10.5
    13  62.4 -0.96   9.3  -1.0 -62.3  1E-3    466.1 174.4   9.4
     4  53.9  -4.2   6.9  88.0 -61.5  2E-3    487.8 149.1   8.1

___________________________________________________
 Profile Time:  14  5 30  2  0
 Profile Location:    37.43 -120.40  (136,160)

        PRSS  SHGT  T02M  U10M  V10M  PBLH  TPPA
         hPa                                  mm
     0   997   112  29.0   4.0  -1.7   809     0

        PRES  UWND  VWND  WWND  TEMP  SPHU     TPOT  WDIR  WSPD
               m/s   m/s  mb/h    oC  g/kg       oK   deg   m/s
   994   994   4.1  -2.0 -13.9  28.7   2.5    302.4 296.5   4.6
   985   985   4.4  -2.4  -6.6  27.9   2.5    302.4 299.2   5.0
   974   974   4.5  -2.7     0  27.0   2.5    302.4 300.7   5.3
   959   960   4.3  -2.9  21.6  25.8   2.5    302.4 304.4   5.1
   941   944   3.8  -3.0  35.2  24.2   2.5    302.3 308.2   4.8
   919   922   3.2  -2.9  48.6  22.4   2.5    302.4 312.6   4.3
   892   896   2.6  -2.3  41.5  20.0   2.4    302.6 311.7   3.5
   855   861   2.1  -1.2  28.6  17.1   2.0    302.9 299.3   2.4
   811   820   1.1   1.5  16.0  14.0   1.1    304.0 217.2   1.8
   767   778     0   5.0 -11.6  12.0  0.30    306.4 180.3   5.0
   723   736  -1.8   5.4 -25.5   9.1  0.29    308.2 162.1   5.7
   662   679  -3.6   4.9  -4.7   4.5  0.28    310.2 143.7   6.1
   588   608  -1.7   4.7  15.9  -2.2  0.40    312.4 160.6   5.0
   521   544   2.9   7.2  16.1  -8.6  0.71    314.9 202.0   7.8
   459   485   4.5  10.2  16.2 -15.5  0.65    316.8 204.1  11.1
   402   432   7.9  12.4  15.8 -21.8  0.64    319.6 212.9  14.7
   351   383  11.4  13.3  15.3 -27.8  0.52    322.8 220.8  17.5
   305   339  14.8  14.8  11.9 -34.1  0.36    325.8 225.3  21.0
   262   299  16.3  16.5   8.7 -40.7  0.20    328.3 224.9  23.2
   224   263  16.5  17.8   3.1 -47.6  0.10    330.6 223.1  24.2
   190   230  16.5  18.5  -1.2 -53.5  5E-2    334.4 222.1  24.8
   159   200  18.0  18.6  -3.6 -57.0  2E-2    342.4 224.4  25.9
   131   174  19.3  16.9  -2.4 -57.4  1E-2    355.9 229.1  25.7
   106   150  18.7  14.0     0 -56.6  1E-2    372.3 233.4  23.4
    84   130  14.9  10.8   2.5 -57.4  1E-2    387.0 234.2  18.4
    65   112  10.0   9.0   3.6 -59.1  1E-2    400.2 228.4  13.5
    49  96.9   7.0   8.2   4.0 -60.8  4E-3    414.1 220.6  10.8
    35  83.7   5.0   8.9   3.2 -61.7  2E-3    430.0 209.7  10.2
    23  72.3   2.2   9.2   1.1 -61.5  1E-3    448.7 193.7   9.4
    13  62.4 -0.71   7.3 -0.24 -61.3  1E-3    468.4 174.8   7.4
     4  53.9  -5.3   5.3 -27.8 -61.4  2E-3    488.0 135.3   7.5
"""

# HOURLY_PROFILES_ONE_HOUR_[0|1|2] contain all but surise and sunset hour,
# since that varies according to utc offset

HOURLY_PROFILES_ONE_HOUR_0 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937, 135.82881398535508, 230.2522349481686, 360.414411605392, 518.8055921541387, 715.7651461641137, 962.7815105469939, 1301.743826670549, 1732.0963974479655, 2192.250857281424, 2663.856567251226, 3345.982389068354, 4259.947450680663, 5186.011915491956, 6120.21175643276, 7056.643626913428, 8006.417923710241, 8986.451540456597, 9972.250805846712, 10981.449306410641, 12042.198782182653, 13124.193667771762, 14261.080058165118, 15406.309765306385, 16658.518561184595, 17976.158502586513, 19355.563010823662, 20904.261267868987, 22702.76242092459, 24927.524263410254, 28825.25346629527],
    'PBLH': 0.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,922.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [113.52118179569345, 115.07020100907351, 123.0476250403563, 118.30288856444385, 121.98572106270176, 133.76778670367295, 148.75653839851014, 181.90425174546766, 110.97738136160952, 21.490567359845436, 36.875009044515586, 40.97991571189952, 55.011821182593366, 221.53352322840786, 179.07326909419453, 444.9955979290613, 436.51125329612876, 613.0803545775004, 542.5612363701279, 409.0915794838193, 328.2356599163898, 183.5607632538291, 129.89359101516095, 43.10737045816838, 39.16865264033064, 37.757751935123075, 34.763505573192106, 8.291881754877862, 1.9054685441623844, 1.0641610896592033, 0.6095337384388296]
    'RELH': [11.352118179569345,11.507020100907351,12.30476250403563,11.830288856444385,12.198572106270176,13.376778670367295,14.875653839851014,18.190425174546766,11.097738136160952,2.1490567359845436,3.6875009044515586,4.097991571189952,5.5011821182593366,22.153352322840786,17.907326909419453,44.49955979290613,43.651125329612876,61.30803545775004,54.25612363701279,40.90915794838193,32.82356599163898,18.35607632538291,12.989359101516095,4.310737045816838,3.916865264033064,3.7757751935123075,3.4763505573192106,0.8291881754877862,0.19054685441623844,0.10641610896592033,0.06095337384388296],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [3.2,3.0,2.8,2.5,2.4,2.4,2.4,2.5,1.3,0.24,0.37,0.33,0.31,0.85,0.45,0.75,0.5,0.46,0.26,0.11,0.05,0.02,0.02,0.01,0.01,0.01,0.01,0.003,0.001,0.001,0.002],
    'T02M': 31.5,
    'TEMP': [31.0,29.5,27.0,25.5,24.0,22.1,19.9,16.7,13.4,11.8,9.3,4.8,-1.9,-8.7,-15.7,-22.1,-28.1,-34.3,-40.5,-47.7,-54.5,-59.0,-57.7,-55.9,-57.1,-59.0,-60.7,-61.6,-62.0,-61.9,-61.3],
    'TO2M': None,
    'TPOT': [304.8,304.0,302.3,302.1,302.1,302.2,302.3,302.5,303.3,306.2,308.3,310.6,312.7,314.8,316.5,319.3,322.5,325.6,328.7,330.5,333.0,339.1,355.4,373.6,387.4,400.4,414.3,430.2,447.6,466.9,488.2],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 2.6,
    'UWND': [2.5,2.5,2.3,2.4,2.5,2.6,2.6,2.3,0.75,-2.1,-2.3,-1.2,2.7,6.5,6.3,8.8,11.8,16.4,19.0,17.5,15.4,16.2,19.8,19.6,15.9,11.6,7.6,3.8,0.2,-2.8,-5.3],
    'V10M': -1.8,
    'VWND': [-1.9,-1.8,-1.7,-1.7,-1.7,-1.4,-0.8,-0.1,1.5,4.5,3.8,3.1,4.9,7.8,10.6,13.1,13.7,14.5,17.7,20.1,19.5,18.3,17.5,15.6,13.3,10.6,8.9,9.1,9.2,7.6,5.1],
    'WDIR': [307.1,305.4,307.2,305.5,304.0,299.0,287.6,272.7,206.4,155.5,149.6,158.9,209.2,219.8,211.1,214.0,221.0,228.9,227.4,221.4,218.6,221.9,228.8,231.8,230.4,228.0,221.1,202.8,181.5,160.3,134.4],
    'WSPD': [3.1,3.1,2.9,3.0,3.0,2.9,2.7,2.3,1.7,5.0,4.4,3.4,5.7,10.2,12.3,15.8,18.1,21.9,26.0,26.6,24.8,24.4,26.4,25.1,20.7,15.7,11.7,9.8,9.2,8.1,7.3],
    'WWND': [-7.0,-7.0,-7.0,-7.0,-3.5,-5.3,-5.3,-3.5,-3.5,-3.5,-2.6,-1.8,-1.3,-0.88,-0.66,-0.44,-0.33,-0.22,-0.11,-0.11,-0.1,-0.03,-0.02,-0.01,-0.01,-0.003,-0.002,-0.0004,-0.0002,-3e-05,0.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [33.21869307923373,31.933426648507066,30.549514804568673,28.34132324491975,27.3314691246797,26.939560623783223,26.446202617151414,26.45467475406241,15.01465433571667,-9.855673746450748,-4.890633166932844,-7.562573501077679,-9.910621609646341,2.171643685260335,-8.240899895145844,-3.1006721338965235,-10.281164967906477,-13.163389242763628,-21.94892987537702,-33.40845564121429,-43.288529626885236,-53.641638351327316,-55.39716723768163,-63.10622724045183,-65.01001633093503,-67.06671699877663,-69.28786256539487,-80.62964149370242,-90.63939879384043,-94.13712681828451,-96.42570734383574],
    'dew_point': [-2.6110043729268, -3.613589201269974, -4.69422550297827, -6.420876907421132, -7.211485363941563, -7.518472805734461, -7.905058134600324, -7.8984183067692015, -16.90368872898358, -36.75709441061073, -32.763026654858635, -34.91052410826424, -36.801382771693056, -27.108284348158378, -35.45641916245404, -31.326882687424245, -37.10009268087637, -39.42650955989245, -46.55014474202659, -55.91570028730223, -64.0582365042134, -72.6588478413272, -74.12419778849639, -80.583154334163, -82.18431173882925, -83.91679543932989, -85.79098402077531, -96.63446221386013, -96.91295483061481, -96.84331529836118, -96.42570734383574],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,811.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}
HOURLY_PROFILES_ONE_HOUR_1 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937,135.82881398535508,230.2522349481686,360.414411605392,518.8055921541387,715.7651461641137,962.7815105469939,1301.743826670549,1742.0947221259023,2192.250857281424,2663.856567251226,3345.982389068354,4259.947450680663,5186.011915491956,6120.21175643276,7056.643626913428,8006.417923710241,8986.451540456597,9972.250805846712,10981.449306410641,12042.198782182653,13124.193667771762,14261.080058165118,15406.309765306385,16658.518561184595,17976.158502586513,19355.563010823662,20904.261267868987,22702.76242092459,24927.524263410254,28825.25346629527],
    'PBLH': 1474.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,921.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [102.42075497187231,106.99940990055696,112.24258342641438,119.40509763179595,127.44170793758467,141.4049403631028,158.17153241270634,172.41920451559116,117.8221251652514,22.976815664117215,37.367340478710304,39.73810008426621,63.884695566882606,198.07703253363522,202.9497049734205,433.129048650953,444.3669459518837,580.9522520945848,505.80371957351826,451.0069790278619,313.8900183643308,161.5561808735467,122.63477535700021,42.14179258569039,38.72240258748246,38.65007617648791,18.44583359473801,8.910414657759606,2.048166503103062,1.1165462712957732,0.6242571740000024],
    'RELH': [10.242075497187231,10.699940990055696,11.224258342641438,11.940509763179595,12.744170793758467,14.14049403631028,15.817153241270634,17.241920451559116,11.78221251652514,2.2976815664117215,3.7367340478710304,3.973810008426621,6.3884695566882606,19.807703253363522,20.29497049734205,43.3129048650953,44.43669459518837,58.09522520945848,50.580371957351826,45.10069790278619,31.38900183643308,16.15561808735467,12.263477535700021,4.214179258569039,3.872240258748246,3.865007617648791,1.844583359473801,0.8910414657759606,0.2048166503103062,0.11165462712957732,0.06242571740000024],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [2.6,2.6,2.6,2.6,2.6,2.6,2.6,2.4,1.4,0.26,0.38,0.32,0.36,0.76,0.51,0.73,0.5,0.44,0.24,0.12,0.05,0.02,0.02,0.01,0.01,0.01,0.005,0.003,0.001,0.001,0.002],
    'T02M': 30.2,
    'TEMP': [29.2,28.3,27.3,26.0,24.6,22.5,20.2,16.9,13.6,12.0,9.5,4.8,-1.9,-8.7,-15.7,-22.1,-28.3,-34.2,-40.6,-47.8,-54.1,-57.9,-57.2,-55.7,-57.0,-59.2,-61.2,-62.2,-62.6,-62.3,-61.5],
    'TO2M': None,
    'TPOT': [303.0,302.8,302.7,302.6,302.8,302.7,302.7,302.7,303.6,306.4,308.5,310.6,312.7,314.8,316.5,319.2,322.2,325.5,328.5,330.4,333.6,341.0,356.2,373.9,387.5,400.1,413.3,429.0,446.5,466.1,487.8],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 3.3,
    'UWND': [3.9,4.2,4.1,4.0,4.0,3.8,3.4,2.9,0.89,-2.1,-2.8,-2.5,1.3,5.2,5.8,8.8,11.5,15.6,17.5,16.6,15.0,16.7,19.1,18.8,15.0,11.2,8.0,5.2,2.2,-0.96,-4.2],
    'V10M': -2.0,
    'VWND': [-1.2,-1.3,-1.5,-1.4,-1.6,-1.8,-1.9,-2.0,0.8,4.8,4.0,3.0,4.0,6.8,10.4,12.9,13.4,13.6,15.9,18.0,18.2,18.2,17.3,14.9,12.0,9.7,8.5,9.4,10.3,9.3,6.9],
    'WDIR': [288.1,287.5,289.9,289.9,291.8,295.1,298.8,304.9,228.5,156.9,145.4,141.3,198.5,217.7,209.6,214.7,221.1,229.1,227.9,222.9,219.9,222.8,228.3,231.9,231.7,229.3,223.5,209.0,192.6,174.4,149.1],
    'WSPD': [4.1,4.4,4.3,4.3,4.3,4.2,3.9,3.5,1.2,5.2,4.8,3.9,4.2,8.5,11.9,15.6,17.7,20.7,23.6,24.5,23.6,24.7,25.8,24.0,19.3,14.8,11.7,10.7,10.5,9.4,8.1],
    'WWND': [-28.8,-29.9,-45.4,-47.4,-62.1,-62.0,-43.6,-14.8,13.6,13.7,0.0,0.0,0.0,0.0,0.0,4.3,4.5,0.0,3.5,5.3,4.3,1.5,-0.97,-2.9,-2.3,-1.6,-0.86,-0.57,-0.93,-1.0,88.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [29.611085849971573,29.4586701744509,29.27019998327114,29.009776914500492,28.691614769871308,28.29707768409378,27.799706828016497,25.76731433060553,16.15430069456096,-8.810684446541984,-4.5307069855609825,-7.969406165725502,-7.95101193099913,0.5881826931797605,-6.581702158061773,-3.470193927454204,-10.280149861140615,-13.72670608075589,-22.892957017424294,-32.46557540216975,-43.29040951509293,-53.64650601667253,-55.39932772072072,-63.107021102632956,-65.01040987582863,-67.06593300977693,-74.55214478123997,-80.62754360799056,-90.6375076029571,-94.13591584005923,-96.56486634788743],
    'dew_point': [-5.42765482203572, -5.546825043351362, -5.6942046631419885, -5.897884865643221, -6.146778643829691, -6.455503674722991, -6.844828980687055, -8.437260184568345, -16.003036390407487, -35.91518551818217, -32.47408606577838, -35.23789531778891, -35.2230915632106, -28.373468697447066, -34.12165888183057, -31.62319884054662, -37.099274244974, -39.88180607415873, -47.31850427064765, -55.14193388932776, -64.05979181610769, -72.66290809805503, -74.12600240960018, -80.5838214977328, -82.18464297493045, -83.91613449838692, -90.24620262814281, -97.05226666666667, -97.3310214969402, -97.12193897560596, -96.56486634788743],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,810.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}

HOURLY_PROFILES_ONE_HOUR_2 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937,135.82881398535508,230.2522349481686,360.414411605392,518.8055921541387,715.7651461641137,962.7815105469939,1301.743826670549,1742.0947221259023,2192.250857281424,2663.856567251226,3345.982389068354,4259.947450680663,5186.011915491956,6120.21175643276,7056.643626913428,8006.417923710241,8986.451540456597,9972.250805846712,10981.449306410641,12042.198782182653,13124.193667771762,14261.080058165118,15406.309765306385,16658.518561184595,17976.158502586513,19355.563010823662,20904.261267868987,22702.76242092459,24927.524263410254,28825.25346629527],
    'PBLH': 1474.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,921.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [102.42075497187231,106.99940990055696,112.24258342641438,119.40509763179595,127.44170793758467,141.4049403631028,158.17153241270634,172.41920451559116,117.8221251652514,22.976815664117215,37.367340478710304,39.73810008426621,63.884695566882606,198.07703253363522,202.9497049734205,433.129048650953,444.3669459518837,580.9522520945848,505.80371957351826,451.0069790278619,313.8900183643308,161.5561808735467,122.63477535700021,42.14179258569039,38.72240258748246,38.65007617648791,18.44583359473801,8.910414657759606,2.048166503103062,1.1165462712957732,0.6242571740000024],
    'RELH': [10.242075497187231,10.699940990055696,11.224258342641438,11.940509763179595,12.744170793758467,14.14049403631028,15.817153241270634,17.241920451559116,11.78221251652514,2.2976815664117215,3.7367340478710304,3.973810008426621,6.3884695566882606,19.807703253363522,20.29497049734205,43.3129048650953,44.43669459518837,58.09522520945848,50.580371957351826,45.10069790278619,31.38900183643308,16.15561808735467,12.263477535700021,4.214179258569039,3.872240258748246,3.865007617648791,1.844583359473801,0.8910414657759606,0.2048166503103062,0.11165462712957732,0.06242571740000024],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [2.6,2.6,2.6,2.6,2.6,2.6,2.6,2.4,1.4,0.26,0.38,0.32,0.36,0.76,0.51,0.73,0.5,0.44,0.24,0.12,0.05,0.02,0.02,0.01,0.01,0.01,0.005,0.003,0.001,0.001,0.002],
    'T02M': 30.2,
    'TEMP': [29.2,28.3,27.3,26.0,24.6,22.5,20.2,16.9,13.6,12.0,9.5,4.8,-1.9,-8.7,-15.7,-22.1,-28.3,-34.2,-40.6,-47.8,-54.1,-57.9,-57.2,-55.7,-57.0,-59.2,-61.2,-62.2,-62.6,-62.3,-61.5],
    'TO2M': None,
    'TPOT': [303.0,302.8,302.7,302.6,302.8,302.7,302.7,302.7,303.6,306.4,308.5,310.6,312.7,314.8,316.5,319.2,322.2,325.5,328.5,330.4,333.6,341.0,356.2,373.9,387.5,400.1,413.3,429.0,446.5,466.1,487.8],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 3.3,
    'UWND': [3.9,4.2,4.1,4.0,4.0,3.8,3.4,2.9,0.89,-2.1,-2.8,-2.5,1.3,5.2,5.8,8.8,11.5,15.6,17.5,16.6,15.0,16.7,19.1,18.8,15.0,11.2,8.0,5.2,2.2,-0.96,-4.2],
    'V10M': -2.0,
    'VWND': [-1.2,-1.3,-1.5,-1.4,-1.6,-1.8,-1.9,-2.0,0.8,4.8,4.0,3.0,4.0,6.8,10.4,12.9,13.4,13.6,15.9,18.0,18.2,18.2,17.3,14.9,12.0,9.7,8.5,9.4,10.3,9.3,6.9],
    'WDIR': [288.1,287.5,289.9,289.9,291.8,295.1,298.8,304.9,228.5,156.9,145.4,141.3,198.5,217.7,209.6,214.7,221.1,229.1,227.9,222.9,219.9,222.8,228.3,231.9,231.7,229.3,223.5,209.0,192.6,174.4,149.1],
    'WSPD': [4.1,4.4,4.3,4.3,4.3,4.2,3.9,3.5,1.2,5.2,4.8,3.9,4.2,8.5,11.9,15.6,17.7,20.7,23.6,24.5,23.6,24.7,25.8,24.0,19.3,14.8,11.7,10.7,10.5,9.4,8.1],
    'WWND': [-28.8,-29.9,-45.4,-47.4,-62.1,-62.0,-43.6,-14.8,13.6,13.7,0.0,0.0,0.0,0.0,0.0,4.3,4.5,0.0,3.5,5.3,4.3,1.5,-0.97,-2.9,-2.3,-1.6,-0.86,-0.57,-0.93,-1.0,88.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [29.611085849971573,29.4586701744509,29.27019998327114,29.009776914500492,28.691614769871308,28.29707768409378,27.799706828016497,25.76731433060553,16.15430069456096,-8.810684446541984,-4.5307069855609825,-7.969406165725502,-7.95101193099913,0.5881826931797605,-6.581702158061773,-3.470193927454204,-10.280149861140615,-13.72670608075589,-22.892957017424294,-32.46557540216975,-43.29040951509293,-53.64650601667253,-55.39932772072072,-63.107021102632956,-65.01040987582863,-67.06593300977693,-74.55214478123997,-80.62754360799056,-90.6375076029571,-94.13591584005923,-96.56486634788743],
    'dew_point': [-5.42765482203572, -5.546825043351362, -5.6942046631419885, -5.897884865643221, -6.146778643829691, -6.455503674722991, -6.844828980687055, -8.437260184568345, -16.003036390407487, -35.91518551818217, -32.47408606577838, -35.23789531778891, -35.2230915632106, -28.373468697447066, -34.12165888183057, -31.62319884054662, -37.099274244974, -39.88180607415873, -47.31850427064765, -55.14193388932776, -64.05979181610769, -72.66290809805503, -74.12600240960018, -80.5838214977328, -82.18464297493045, -83.91613449838692, -90.24620262814281, -97.05226666666667, -97.3310214969402, -97.12193897560596, -96.56486634788743],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,810.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}

HOURLY_PROFILES_ONE_ALL_HOURS_WITH_OFFSET = {
    datetime.datetime(2014, 5, 29, 17, 0): dict(HOURLY_PROFILES_ONE_HOUR_0, sunrise_hour=6, sunset_hour=18),
    datetime.datetime(2014, 5, 29, 18, 0): dict(HOURLY_PROFILES_ONE_HOUR_1, sunrise_hour=6, sunset_hour=18),
    datetime.datetime(2014, 5, 29, 19, 0): dict(HOURLY_PROFILES_ONE_HOUR_2, sunrise_hour=6, sunset_hour=18)
}

HOURLY_PROFILES_ONE_ALL_HOURS_NO_OFFSET = {
    datetime.datetime(2014, 5, 30, 0, 0): dict(HOURLY_PROFILES_ONE_HOUR_0, sunrise_hour=13, sunset_hour=25),
    datetime.datetime(2014, 5, 30, 1, 0): dict(HOURLY_PROFILES_ONE_HOUR_1, sunrise_hour=13, sunset_hour=25),
    datetime.datetime(2014, 5, 30, 2, 0): dict(HOURLY_PROFILES_ONE_HOUR_2, sunrise_hour=13, sunset_hour=25)
}

HOURLY_PROFILES_ONE_PARTIAL_WITH_OFFSET = {
    datetime.datetime(2014, 5, 29, 18, 0): dict(HOURLY_PROFILES_ONE_HOUR_1, sunrise_hour=6, sunset_hour=18)
}

HOURLY_PROFILES_ONE_PARTIAL_NO_OFFSET = {
    datetime.datetime(2014, 5, 30, 1, 0): dict(HOURLY_PROFILES_ONE_HOUR_1, sunrise_hour=13, sunset_hour=25)
}



# TODO: get example of profile.txt with different colums
# PROFILE_TWO = """ Meteorological Profile: wrfout_d2.2014053000.f00-11_12hr01.arl
#  File start time : 14  5 30  0  0
#  File ending time: 14  5 30  1  0

# ___________________________________________________
#  Profile Time:  13  1  2  0  0
#  Profile Location:    40.61 -100.56  ( 93, 65)
#        TPP3  T02M  RH2M  U10M  V10M  PRSS
#                                      hPa
#  1013     0     0     0     0     0     0
#        UWND  VWND  HGTS  TEMP  WWND  RELH     TPOT  WDIR  WSPD
#         m/s   m/s          oC  mb/h     %       oK   deg   m/s
#  1000   2.6  0.96   196 -0.50     0  66.0    272.7 247.6   2.8
#   975   2.6   1.2   397  -1.8     0  66.0    273.4 243.6   2.8
#   950   2.7   1.1   603  -3.1     0  66.0    274.1 244.6   2.9
#   925   2.5  0.91   813  -5.0     0  67.0    274.2 247.6   2.7
#   900   7.6  -1.9  1029  -3.1   6.2  40.0    278.3 282.0   7.8
#   875   6.8  -3.5  1252  -2.9   6.2  50.0    280.8 294.8   7.6
#   850   7.1  -3.2  1481  -4.5   6.0  60.0    281.4 291.8   7.7
#   800   7.6  -3.1  1955  -7.7   2.6  63.0    283.0 289.7   8.2
#   750   7.0  -3.8  2454 -11.1  0.58  59.0    284.5 295.8   8.0
#   700   6.9  -3.6  2980 -13.5     0  54.0    287.5 295.2   7.8
#   650   8.5  -3.1  3541 -16.3     0  42.0    290.6 287.4   9.1
#   600  10.7  -1.3  4138 -19.7  0.94  35.0    293.4 274.6  10.8
#   550   9.3  -1.3  4779 -23.3   1.6  29.0    296.5 275.9   9.4
#   500   6.4  -2.3  5470 -28.2   1.2  22.0    298.6 287.4   6.8
#   450   2.6  -4.0  6216 -33.7     0  22.0    300.9 324.3   4.8
#   400  -1.6  -5.3  7032 -39.2  -3.3  26.0    304.1  14.5   5.6
#   350  -2.4  -4.2  7933 -45.2 -0.85  26.0    307.8  27.7   4.9
#   300   4.8  -1.1  8955 -47.5     0  19.0    318.4 281.0   5.0
#   250  13.5   2.9 10154 -49.1  -1.1  11.0    333.1 255.5  13.8
#   200  19.4   4.3 11618 -48.5   1.1   4.0    356.0 255.2  19.9
#   150  28.1   6.9 13505 -51.9  0.52   9.0    380.7 253.8  29.0
#   100  18.0   4.8 16116 -55.3 -0.75   2.0    421.0 252.7  18.7
#    50   6.8 -0.15 20468 -60.8  0.54   2.0    500.2 268.9   6.8
# """

# class MockSun(object):
#     def __init__(self, *args, **kwargs):
#         pass

#     def sunrise_hr(self, *args, **kwargs):
#         return 6

#     def sunset_hr(self, *args, **kwargs):
#         return 18

class TestARLProfile(object):

    def check_hourly_profiles(self, actual, expected):
        def check_vals(k, a, e):
            if isinstance(a, float):
                # assert_almost_equal(actual, desired, decimal=7, err_msg='', verbose=True)
                assert_approx_equal(a, e,
                    err_msg="Non-equal {} value - {} != {}".format(k, a, e))
            else:
                assert a == e

        assert set(expected.keys()) == set(actual.keys())
        for dt in expected:
            assert set(expected[dt].keys()) == set(actual[dt].keys())
            for k in expected[dt]:
                if isinstance(expected[dt][k], list):
                    for i in range(len(expected[dt][k])):
                        check_vals(k, actual[dt][k][i], expected[dt][k][i])
                else:
                    check_vals(k, actual[dt][k],   expected[dt][k])

    def monkeypatch_sun(self, monkeypatch):
        monkeypatch.setattr(sun.Sun, "sunrise_hr", lambda *args: 13)
        monkeypatch.setattr(sun.Sun, "sunset_hr", lambda *args: 25)
        #monkeypatch.setattr(arlprofiler, "Sun", MockSun)

    def test_one_all_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        with tempfile.NamedTemporaryFile() as f:
            f.write(PROFILE_ONE)
            f.flush()
            profiler = arlprofiler.ARLProfile(f.name,
                datetime.datetime(2014, 5, 30, 0, 0), # first
                datetime.datetime(2014, 5, 30, 0, 0), # start
                datetime.datetime(2014, 5, 30, 2, 0), # end
                -7, # utc offset
                37, # lat
                -122) # lng
            hourly_profiles = profiler.get_hourly_params()
            self.check_hourly_profiles(hourly_profiles, HOURLY_PROFILES_ONE_ALL_HOURS_WITH_OFFSET)

    def test_one_all_hours_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        with tempfile.NamedTemporaryFile() as f:
            f.write(PROFILE_ONE)
            f.flush()
            profiler = arlprofiler.ARLProfile(f.name,
                datetime.datetime(2014, 5, 30, 0, 0), # first
                datetime.datetime(2014, 5, 30, 0, 0), # start
                datetime.datetime(2014, 5, 30, 2, 0), # end
                0, # utc offset
                37, # lat
                -122) # lng
            hourly_profiles = profiler.get_hourly_params()
            self.check_hourly_profiles(hourly_profiles, HOURLY_PROFILES_ONE_ALL_HOURS_NO_OFFSET)

    def test_one_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        with tempfile.NamedTemporaryFile() as f:
            f.write(PROFILE_ONE)
            f.flush()
            profiler = arlprofiler.ARLProfile(f.name,
                datetime.datetime(2014, 5, 30, 0, 0), # first
                datetime.datetime(2014, 5, 30, 1, 0), # start
                datetime.datetime(2014, 5, 30, 1, 0), # end
                -7, # utc offset
                37, # lat
                -122) # lng
            hourly_profiles = profiler.get_hourly_params()
            self.check_hourly_profiles(hourly_profiles, HOURLY_PROFILES_ONE_PARTIAL_WITH_OFFSET)

    def test_one_partial_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        with tempfile.NamedTemporaryFile() as f:
            f.write(PROFILE_ONE)
            f.flush()
            profiler = arlprofiler.ARLProfile(f.name,
                datetime.datetime(2014, 5, 30, 0, 0), # first
                datetime.datetime(2014, 5, 30, 1, 0), # start
                datetime.datetime(2014, 5, 30, 1, 0), # end
                0, # utc offset
                37, # lat
                -122) # lng
            hourly_profiles = profiler.get_hourly_params()
            self.check_hourly_profiles(hourly_profiles, HOURLY_PROFILES_ONE_PARTIAL_NO_OFFSET)

