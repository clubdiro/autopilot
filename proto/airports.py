# File: airports.py

from geodetic import Location, LatLon

runways = {}

# KSEA Seattle Tacoma International

runways['KSEA_16L'] = Location( 46.02, LatLon(47.46379733, -122.30775222))
runways['KSEA_34R'] = Location(121.92, LatLon(47.43117533, -122.30804122))
runways['KSEA_16C'] = Location( 67.97, LatLon(47.46381133, -122.31098822))
runways['KSEA_34C'] = Location(120.09, LatLon(47.43797233, -122.31121322))
runways['KSEA_16R'] = Location( 49.99, LatLon(47.46383763, -122.31786263))
runways['KSEA_34L'] = Location(120.09, LatLon(47.44053695, -122.31806463))

# KTCM McChord Air Force Base

runways['KTCM_16' ] = Location(304.80, LatLon(47.15150600, -122.47655000))
runways['KTCM_34' ] = Location(304.80, LatLon(47.12381400, -122.47638100))
runways['KTCM_16R'] = Location(  0.00, LatLon(47.14780800, -122.47741100))
runways['KTCM_34L'] = Location(  0.00, LatLon(47.13874200, -122.47734700))
