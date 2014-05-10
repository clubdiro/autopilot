# File: geodetic.py

import math


def deg2rad(deg):
    return deg*math.pi/180


def rad2deg(rad):
    return rad*180/math.pi


# Creates a point on the earth's surface at the supplied latitude / longitude

class LatLon:

    def __init__(self, lat, lon):

        # lat: latitude in degrees
        # lon: longitude in degrees

        self.lat = lat
        self.lon = lon
        self.radius = 6371

    def distance(self, other):

        # Returns the distance from this point to the
        # other point using Haversine formula

        # other: the LatLon to compute distance with

        phi1 = deg2rad(self.lat)
        lambda1 = deg2rad(self.lon)
        phi2 = deg2rad(other.lat)
        lambda2 = deg2rad(other.lon)
        deltaphi = phi2 - phi1
        deltalambda = lambda2 - lambda1

        a = math.sin(deltaphi/2) * math.sin(deltaphi/2) + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(deltalambda/2) * math.sin(deltalambda/2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return self.radius * c

    def bearing(self, other):

        # Returns the bearing from this point to the
        # other point

        # other: the LatLon to compute bearing to

        phi1 = deg2rad(self.lat)
        phi2 = deg2rad(other.lat)
        deltalambda = deg2rad(other.lon - self.lon)

        y = math.sin(deltalambda) * math.cos(phi2)
        x = math.cos(phi1)*math.sin(phi2) - \
            math.sin(phi1)*math.cos(phi2)*math.cos(deltalambda)
        theta = math.atan2(y, x)

        return rad2deg(theta) % 360


# Creates a location on the earth (altitude / latitude / longitude)

class Location:

    def __init__(self, alt, latlon):

        # alt: altitude in feet
        # latlon: LatLon giving latitude and longitude in degrees

        self.alt = alt
        self.latlon = latlon
