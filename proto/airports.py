# File: airports.py

from geodetic import Location, LatLon


# Creates a Runway

class Runway:

    def __init__(self, name, reverse, location):

        # name: name of runway
        # reverse: name of reverse runway
        # location: Location giving altitute, latitude and longitude

        self.name = name
        self.reverse = reverse
        self.location = location


# Creates an Airport

class Airport:

    def __init__(self, name, runways):

        # name: name of airport
        # runways: dictionnary of runways

        self.name = name
        self.runways = runways

    def runway_heading(self, name):

        # name: name of runway

        return self.runways[name].location.latlon.bearing(self.runways[self.runways[name].reverse].location.latlon)

    def runway_length(self, name):

        # name: name of runway

        return self.runways[name].location.latlon.distance(self.runways[self.runways[name].reverse].location.latlon)


airports = {

  # KSEA Seattle Tacoma International
  'KSEA': Airport('KSEA', {
                  '16L':
                     Runway('16L',
                            '34R',
                            Location(433, LatLon(47.46379733, -122.30775222))),
                  '34R':
                     Runway('34R',
                            '16L',
                            Location(347, LatLon(47.43117533, -122.30804122))),
                  '16C':
                     Runway('16C',
                            '34C',
                            Location(430, LatLon(47.46381133, -122.31098822))),
                  '34C':
                     Runway('34C',
                            '16C',
                            Location(363, LatLon(47.43797233, -122.31121322))),
                  '16R':
                     Runway('16R',
                            '34L',
                            Location(415, LatLon(47.46383763, -122.31786263))),
                  '34L':
                     Runway('34L',
                            '16R',
                            Location(356, LatLon(47.44053695, -122.31806463)))
                  }),

  # KBFI Boeing Field King Co Intl
  'KBFI': Airport('KBFI', {
                  '13L':
                     Runway('13L',
                            '31R',
                            Location( 18, LatLon(47.53799292, -122.30746100))),
                  '31R':
                     Runway('31R',
                            '13L',
                            Location( 17, LatLon(47.52916792, -122.30000000))),
                  '13R':
                     Runway('13R',
                            '31L',
                            Location( 17, LatLon(47.54051792, -122.31135600))),
                  '31L':
                     Runway('31L',
                            '13R',
                            Location( 21, LatLon(47.51672592, -122.29124200)))
                  }),

  # KRNT Renton Muni
  'KRNT': Airport('KRNT', {
                  '16':
                     Runway('16',
                            '34',
                            Location( 24, LatLon(47.50047200, -122.21685300))),
                  '34':
                     Runway('34',
                            '16',
                            Location( 32, LatLon(47.48579400, -122.21463300)))
                  }),

  # KTCM McChord Air Force Base
  'KTCM': Airport('KTCM', {
                  '16':
                     Runway('16',
                            '34',
                            Location(286, LatLon(47.15150600, -122.47655000))),
                  '34':
                     Runway('34',
                            '16',
                            Location(322, LatLon(47.12381400, -122.47638100)))
                  }),

  # S36 Crest Airpark
  'S36':  Airport('S36', {
                  '15':
                     Runway('15',
                            '33',
                            Location(472, LatLon(47.34154700, -122.10457500))),
                  '33':
                     Runway('33',
                            '15',
                            Location(472, LatLon(47.33264400, -122.10249700)))
                  }),

  # S50 Auburn Muni
  'S50':  Airport('S50', {
                  '16':
                     Runway('16',
                            '34',
                            Location( 63, LatLon(47.33234200, -122.22670300))),
                  '34':
                     Runway('34',
                            '16',
                            Location( 63, LatLon(47.32302800, -122.22660600)))
                  })

}


def runway_heading(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runway_heading(runway)

def runway_length(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runway_length(runway)

def runway_location(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runways[runway].location

def closest_runway(latlon):
    min_dist = float("+inf")
    min_rw = None
    for airport in airports:
        for runway in airports[airport].runways:
            rw = (airport, runway)
            d = runway_location(rw).latlon.distance(latlon)
            if (d < min_dist):
                min_dist = d
                min_rw = rw
    return min_rw
