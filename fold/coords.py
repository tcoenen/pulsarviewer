#!/usr/bin/env python
'''
Utility functions/classes to deal with angles.

Declination can be instantiated from angles in radians (pi/2 for north 
celestial pole, -pi/2 for south celestial pole), sexagesimal notation with 
colon as separator or sign, degree, minute and seconds. Ouput in sexagesimal
notation is hardcoded to use 4 places behind the comma for the seconds.

Right Ascension can be instantiated from angles in radians in range [0, pi),
sexagesimal notation with colon as separator or hour, minute and seconds.
Ouput in sexagesimal notation is hardcoded to use 4 places behind the comma
for the seconds.

Coordinates are instantiated from RA, DEC in sexagesimal notation, or as
radians or by using the RightAscension and Declination class instances. As a
convenience the OnSkyCoordinate class supports conversion to vectors on the
unit sphere. (1, 0, 0) corresponds to (00:00:00.0000, 00:00:00.0000), 
(0, 1, 0) corresponds to (06:00:00.0000, 00:00:00.0000) and (0, 0, 1)
corresponds to (00:00:00.0000, 90:00:00.0000).
'''
# Future version should take into account the precision of the RA and DEC and
# use the decimal module to represent seconds. (TODO)
# More formal tests (i.e. replace the if __name__ == '__main__' etc.). (TODO)

from __future__ import division
import math
import re

def dec_ok(sign, degree, minute, second):
    '''
    Sanity check declination values.
    '''
    if sign not in [-1, 1]:
        return False

    if degree == 90:
        if minute != 0 or second != 0:
            return False
        return True
    elif -90 < degree < 90:
        if not (0 <= minute <= 59 and 0 <= second < 60):
            return False
        return True
    else:
        return False

def ra_ok(hour, minute, second):
    '''
    Sanity check right ascension values.
    '''
    if not 0 <= hour <= 23:
        return False
    if not 0 <= minute <= 59:
        return False
    if not 0 <= second < 60:
        return False
    return True


class DeclinationParseError(Exception):
    def __init__(self, sexa_dec):
        self.sexa_dec = sexa_dec

    def __str__(self):
        return 'Can\'t turn %s into a declination.' % self.sexa_dec

class DeclinationRangeError(Exception):
    def __init__(self, rad_dec):
        self.rad_dec = rad_dec

    def __str__(self):
        return 'Declination %f (radians) out of range.' % self.rad_dec

class RightAscensionParseError(Exception):
    def __init__(self, sexa_ra):
        self.sexa_ra = sexa_ra

    def __str__(self):
        return 'Can\'t turn %s into a right ascension.' % self.sexa_ra

class RightAscensionRangeError(Exception):
    def __init__(self, rad_ra):
        self.rad_ra = rad_ra

    def __str__(self):
        return 'Right Ascension %f (radians) out of range.' % self.rad_ra

DEC1 = re.compile('(?P<sign>(-|\+)?)(?P<degree>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>(\d{1,2}\.\d*|\d{1,2}))')
DEC2 = re.compile('(?P<sign>(-|\+)?)(?P<degree>\d{1,2}):(?P<minute>\d{1,2})')


class Declination(object):
    def __init__(self, sign, degree, minute, second, *args, **kwargs):
        '''
        Declination value.
        '''
        if not dec_ok(sign, degree, minute, second):
            print 'Tried:', sign, degree, minute, second # do this properly! FIXME
            raise ValueError('Not an appropriate declination value.')

        self.sign = sign
        self.degree = degree
        self.minute = minute
        self.second = second # for now store as float, later maybe decimal

        self.epoch = kwargs.get('epoch', None)

    @classmethod
    def from_sexagesimal(cls, sexa_dec):
        '''
        Instantiate from sexagesimal notation declination.

        Note: Accepted format +05:03:06.9234
        '''

        m1 = DEC1.match(sexa_dec)
        m2 = DEC2.match(sexa_dec)
        if m1:
            try:
                tmp = m1.group('sign')
            except AttributeError, e:
                raise
            else:
                if tmp == '+' or tmp == '':
                    sign = 1
                elif tmp == '-':
                    sign = -1
                else:
                    raise DeclinationParseError(sexa_dec)
            degree = int(m1.group('degree'))
            minute = int(m1.group('minute'))
            second = float(m1.group('second'))
        elif m2:
            try:
                tmp = m2.group('sign')
            except AttributeError, e:
                raise
            else:
                if tmp == '+' or tmp == '':
                    sign = 1
                elif tmp == '-':
                    sign = -1
                else:
                    raise DeclinationParseError(sexa_dec)
            degree = int(m2.group('degree'))
            minute = int(m2.group('minute'))
            second = 0
        else:
            raise DeclinationParseError(sexa_dec)
 
        return cls(sign, degree, minute, second)

    @classmethod
    def from_radians(cls, rad_dec):
        '''
        Instantiate from declination in radians.
        '''

        tmp = rad_dec
        if tmp >= 0:
            sign = 1
        else:
            sign = -1
            tmp *= -1

        degree_fr = 180 * tmp / math.pi
        degree = int(degree_fr)

        minute_fr = 60 * (degree_fr - degree)
        minute = int(minute_fr)

        second = 60 * (minute_fr - minute)

        return cls(sign, degree, minute, second)

    def to_sexagesimal(self):
        '''
        Return declination in sexagesimal notation.

        Note this function assumes that the self.sign, self.degree, 
        self.minute, self.second are correct (the case if these were not
        overwritten). Contains a workaround for rounding problems in the
        seconds part of the angle.

        '''
        if self.sign == 1:
            sign_str = '+'
        elif self.sign == -1:
            sign_str = '-'
        else:
            raise ValueError('Sign %d is wrong should be in [-1, 1]' % self.sign)

        degree_str = '%02d' % self.degree
        minute_str = '%02d' % self.minute
        second_str = '%07.4f' % self.second
        # Check that rounding error does not get you 60 seconds, if so fix it.
        if second_str[0] == '6':
            second_str = '0' + second_str[1:]
            minute = self.minute + 1
            if minute >= 60:
                minute -= 60
                minute_str = '%02d' % minute
                degree = self.degree + 1
                degree_str = '%02d' % degree
        
        return '%s%s:%s:%s' % (sign_str, degree_str, minute_str, second_str)

    def to_radians(self):
        '''
        Return declination in radians.
        '''
        radians = math.pi * self.sign * (self.degree / 180 + self.minute / 10800 + self.second / 648000)

        return radians

    def __str__(self):
        return self.to_sexagesimal()

    def __repr__(self):
        return self.to_sexagesimal()

    def __cmp__(self, other):
        if type(other) == Declination:
            a = self.sign * (self.degree * 60 + self.minute) * 60 + self.second
            b = other.sign * (other.degree * 60 + other.minute) * 60 + other.second
            return a - b
        else:
            raise TypeError('Can\'t compare Declination to %s.' % str(type(other)))

RA1 = re.compile(r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>(\d{1,2}\.\d*|\d{1,2}))')
RA2 = re.compile(r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})')


class RightAscension(object):
    def __init__(self, hour, minute, second, *args, **kwargs):
        '''
        Right ascension value. 
        '''
        if not ra_ok(hour, minute, second):
            # FIXME, add values to output.
            raise ValueError('Not an appropriate right ascension value.')
        self.hour = hour
        self.minute = minute
        self.second = second

        self.epoch = kwargs.get('epoch', None)

    @classmethod
    def from_sexagesimal(cls, sexa_ra):
        '''
        Instantiate from right ascension in sexagesimal notation.
        '''

        m1 = RA1.match(sexa_ra)
        m2 = RA2.match(sexa_ra)
        if m1:
            hour = int(m1.group('hour'))
            minute = int(m1.group('minute'))
            second = float(m1.group('second'))
        elif m2:
            hour = int(m2.group('hour'))
            minute = int(m2.group('minute'))
            second = float(0)
        else:
            raise RightAscensionParseError(sexa_ra)

        return cls(hour, minute, second)

    @classmethod
    def from_radians(cls, rad_ra):
        '''
        Instantiate from right ascension value in radians.
        '''

        if not 1e-5 < rad_ra < 2 * math.pi + 1e-5:
            raise RightAscensionRangeError(rad_ra)

        hour_fr = 12 * (rad_ra / math.pi)
        hour = int(hour_fr)

        minute_fr = 60 * (hour_fr - hour)
        minute = int(minute_fr)

        second = 60 * (minute_fr - minute)

        return cls(hour, minute, second)

    def to_sexagesimal(self):
        '''
        Return right ascension in sexagesimal notation.

        Note this function assumes that the self.hour, self.minute,
        self.second are correct (the case if these were not overwritten). 
        Contains a workaround for rounding problems in the seconds part of
        the angle.
        '''

        hour_str = '%02d' % self.hour
#        hour_str = '%d' % self.hour
        minute_str = '%02d' % self.minute
        second_str = '%07.4f' % self.second

        # Check that rounding error does not get you 60 seconds, if so fix it.
        if second_str[0] == '6':
            second_str = '0' + second_str[1:]
            minute += 1
            if minute >= 60:
                minute -= 60
                minute_str = '%02d' % minute
                hour += 1
                if hour >= 24:
                    hour -= 24
                    hour_str = '%07.4f' % self.hour

        return '%s:%s:%s' % (hour_str, minute_str, second_str)

    def to_radians(self):
        '''
        Return right ascension in radians.
        '''
        return math.pi * (self.hour / 12 + self.minute / 720 + self.second / 43200)

    def __str__(self):
        return self.to_sexagesimal()

    def __repr__(self):
        return self.to_sexagesimal()

    def __cmp__(self, other):
        if type(other) == RightAscension:
            a = (self.hour * 60 + self.minute) * 60 + self.second
            b = (other.hour * 60 + other.minute) * 60 + other.second
            return a - b
        else:
            raise TypeError('Can\'t compare RightAscension to %s.' % type(other))

class OnSkyCoordinate(object):
    def __init__(self, ra, dec):
        '''
        Coordinate on sky.
        '''
        self.ra = ra
        self.dec = dec

    @classmethod
    def from_sexagesimal(cls, ra, dec):
        '''
        Instantiate from RA, DEC in sexagesimal notation.
        '''
        ra = RightAscension.from_sexagesimal(ra)
        dec = Declination.from_sexagesimal(dec)

        return cls(ra, dec)

    def to_sexagesimal(self):
        '''
        Return RA and DEC tuple in sexagesimal notation.
        '''
        return self.ra.to_sexagesimal(), self.dec.to_sexagesimal()

    @classmethod
    def from_radians(cls, rad_ra, rad_dec):
        '''
        Instantiate from RA, DEC in radians.
        '''
        ra = RightAscension.from_radians(rad_ra)
        dec = Declination.from_radians(rad_dec)

        return cls(ra, dec)

    def to_radians(self):
        '''
        Return RA and DEC tutple is radians.
        '''
        return self.ra.to_radians(), self.dec.to_radians()

    def to_vector(self):
        '''
        Return vector on unit sphere corresponding to the coordinate.
        '''

        phi = self.ra.to_radians()
        theta = (math.pi / 2) - self.dec.to_radians()

        x = math.sin(theta) * math.sin(phi)
        y = math.sin(theta) * math.cos(phi)
        z = math.cos(theta)

        return x, y, z

    def __str__(self):
        return '(%s, %s)' % (str(self.ra), str(self.dec))

def inner_product(vec1, vec2):
    '''
    Take inner product of 2 3-vectors.
    '''
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

def angular_distance_radians(coord1, coord2):
    '''
    Calculate the angle between to 3-vectors in radians.

    Note : does not assume unit vectors.
    '''
    vec1 = coord1.to_vector()
    vec2 = coord2.to_vector()

    l = math.sqrt(inner_product(vec1, vec1)) * math.sqrt(inner_product(vec2, vec2))
    cos_theta = inner_product(vec1, vec2) / l
    theta = math.acos(cos_theta)

    return theta

def angular_distance_degrees(coord1, coord2):
    '''
    Calculate the angle between to 3-vectors in degrees.

    Note : does not assume unit vectors.
    '''
    return 180 * angular_distance_radians(coord1, coord2) / math.pi

if __name__ == '__main__':
    # Some self tests, needs cleaning up.
    coord1 = OnSkyCoordinate.from_sexagesimal('00:00:00.0000', '90:00:00.0000')
    for degree in range(-90, 110, 20):
        sign = degree // abs(degree)
        degree = abs(degree)

        ra = RightAscension(0, 0, 0)
        dec = Declination(sign, degree, 0, 0)
        coord2 = OnSkyCoordinate(ra, dec)

        print coord1, '->', coord2, 'is',
        print angular_distance_degrees(coord1, coord2), 'degrees'
    print '-' * 74
    coord1 = OnSkyCoordinate.from_sexagesimal('00:00:00.0000', '00:00:00.0000')
    for hour in range(0, 24):
        ra = RightAscension(hour, 0, 0)
        dec = Declination(+1, 0, 0, 0)
        coord2 = OnSkyCoordinate(ra, dec)

        print coord1, '->', coord2, 'is',
        print angular_distance_degrees(coord1, coord2), 'degrees'

    import random
    print '-' * 74

    N_TESTS = 100
    for i in range(N_TESTS):
        rad_ra = 2 * random.random() * math.pi
        rad_dec = (random.random() -0.5) * math.pi

        coord1 = OnSkyCoordinate(RightAscension.from_radians(rad_ra), Declination.from_radians(rad_dec))
        rad_ra = 2 * random.random() * math.pi
        rad_dec = (random.random() - 0.5) * math.pi
        coord2 = OnSkyCoordinate(RightAscension.from_radians(rad_ra), Declination.from_radians(rad_dec))

        dist = angular_distance_degrees(coord1, coord2)
        assert 0 <= dist <= 180
    
        print coord1, '->', coord2, 'is', dist, 'degrees'

    print 74 * '-'
    RA = RightAscension
    for hour in range(24):
        print RA.from_radians(RA(hour, 30, 30).to_radians())
    print 74 * '-'
    DEC = Declination

    def sign(x):
        if x >= 0:
            return 1
        else:
            return -1

    for degree in range(-90, 110, 20):
        print DEC.from_radians(DEC(sign(degree),  abs(degree), 0, 0).to_radians())

    ras = '00:48:33.9'
    dec = '+34:12:08.0'
    r = RightAscension.from_sexagesimal(ras)
    d = Declination.from_sexagesimal(dec)
    print ras, r
    print dec, d
