#!/usr/bin/env python
'''
Parse PRESTO bestprof files.
'''
import sys
import re
import os
import traceback

def float_with_error(chunk):
    if chunk == 'N/A':
        return None, None
    value_str, err_str = chunk.split('+/-')
    return float(value_str), float(err_str)

SIGMA_REGEXP = re.compile(r'~(?P<sigma>\S+)\s+sigma\)')

def prob_parser(chunk):
    if chunk == 'N/A':
        return None
    try:
#        print chunk.split('(')
        value_str, sigma_str = chunk.split('(')
    except ValueError, e:
        value = float(chunk)
        sigma = None
    else:
        value = float(value_str)
        m = SIGMA_REGEXP.match(sigma_str)
        sigma = float(m.group('sigma'))
    return value, sigma


KEY_VALUE_MAPPING = {
    'Input file' : ['input_file', str],
    'Candidate' : ['candidate', str],
    'Telescope' : ['telescope', str],
    'Epoch_topo' : ['epoch_topo', float],
    'Epoch_bary (MJD)' : ['epoch_bary_mjd', float],
    'Epoch_bary' : ['epoch_bary', float],
    'T_sample' : ['t_sample', float],
    'Data Folded' : ['data_folded', int],
    'Data Avg' : ['data_avg', float],
    'Data StdDev' : ['data_stddev', float],
    'Profile Bins' : ['profile_bins', int],
    'Profile Avg' : ['profile_avg', float],
    'Profile StdDev' : ['profile_stddev', float],
    'Reduced chi-sqr' : ['reduced_chi_sq', float],
    'Prob(Noise)' : ['prob_noise', prob_parser],
    'Best DM' : ['best_dm', float],
    'P_topo (ms)' : ['p_topo', float_with_error],
    'P\'_topo (s/s)' : ['p_dot_topo', float_with_error],
    'P\'\'_topo (s/s^2)' : ['p_dot_dot_topo', float_with_error],
    'P_bary (ms)' : ['p_bary', float_with_error],
    'P\'_bary (s/s)' : ['p_dot_bary', float_with_error],
    'P\'\'_bary (s/s^2)' : ['p_dot_dot_bary', float_with_error],
    # TODO : Need to find example bestprof files to see what value the
    # following header entries take (for now, keep them as strings).
    'P_orb (s)' : ['p_orb', str],
    'asin(i)/c (s)' : ['asin_i_over_c', str],
    'eccentricity' : ['eccentricity', str],
    'w (rad)' : ['w_rad', str],
    'T_peri' : ['t_peri', str],
}

class Header(object):
    pass

class BestprofFile(object):
    def __init__(self, filename, verbose=False):
        '''
        Class to represent a PRESTO prepfold .bestprof file.
        '''
        header, profile = self.parse(filename, verbose)
        self.filename = os.path.abspath(filename)
        self.header = header
        self.profile = profile
        self.psr_name = ''

    def parse(self, filename, verbose):
        '''
        Parse the actual .bestprof file.
        '''
        tmp_profile = []
        profile = []
        tmp_header = {}
        tmp_header = Header()
        in_header = True

        with open(filename, 'r') as f:
            for line in f:
                if in_header == True and line[0] == '#':
                    key = line[2:19].strip()
                    value = line[20:].strip()
                    if key == '#################':
                        in_header = False
                        continue

                    if key not in KEY_VALUE_MAPPING:
                        if verbose:
                            print 'Unkown header keyword %s' % key
                        continue
                    try:
                        setattr(tmp_header, KEY_VALUE_MAPPING[key][0],
                            KEY_VALUE_MAPPING[key][1](value))
                    except Exception, e:
                        if verbose:
                            print 'Conversion failed %s' % line
                            print 'Key:', key
                            print 'Value:', value
                            traceback.print_exc(file=sys.stdout)
                        setattr(tmp_header, KEY_VALUE_MAPPING[key][0], None)
                    else:
                        pass
                else:
                    split_line = line.split()
                    if len(split_line) != 2:
                        if verbose:
                            print 'Can\'t deal with %s' % line
                    try:
                        bin_i = int(split_line[0])
                        value = float(split_line[1])
                    except ValueError, e:
                        if verbose:
                            print 'Can\'t deal with %s' % line
                    else:
                        tmp_profile.append((bin_i, value))
            last_bin_i = -1
            for bin_i, value in tmp_profile:
                if last_bin_i + 1 != bin_i:
                    raise Exception('Profile contains non consequetive values.')
                else:
                    profile.append(value)
                last_bin_i = bin_i

            if not len(profile) == tmp_header.profile_bins:
                raise Exception('Discrepancy between number of bins according to header and length of profile.')

            return tmp_header, profile

    def set_psr_name(self, psr_name):
        self.psr_name = psr_name

if __name__ == '__main__':

    import brp
    import copy
    import os

    from brp.svg.base import SVGCanvas, PlotContainer, TextFragment
    from brp.svg.plotters.line import LinePlotter

    def plot_profile(cv, x, y, width, height, bestprof_inst, *args, **kwargs):
        psr_name = kwargs.get('psr_name', '')
        data_set = kwargs.get('data_set', '')
        beam_ra = kwargs.get('beam_ra', None)
        beam_dec = kwargs.get('beam_dec', None)

        if beam_ra != None and beam_dec != None:
            if isintance(beam_ra, BaseString):
                pass
            elif isinstance(beam_ra, RightAscension):
                pass

        # Some futzing with the position and size because the axes are not
        # drawn, normally they get 50 px.
        pc = PlotContainer(x - 50, y - 50, width + 100, height + 100, data_padding=0)
        pc.hide_axes()

        bpf = bestprof_inst

        pp = LinePlotter(bpf.profile, use_markers=False)
        pc.add_plotter(pp)
        TEXTSIZE = 10
        cv.add_plot_container(pc)
        if psr_name:
            cv.add_plot_container(TextFragment(x + 0, y + height + TEXTSIZE,
                'PSR ' + psr_name, font_size=TEXTSIZE))
        elif bpf.psr_name:
            cv.add_plot_container(TextFragment(x + 0, y + height + TEXTSIZE,
                bpf.psr_name, font_size=TEXTSIZE))
        else:
            cv.add_plot_container(TextFragment(x + 0, y + height + TEXTSIZE,
                'PSR UNKNOWN', font_size=TEXTSIZE))
        cv.add_plot_container(TextFragment(x + 0, y + height + 2 * TEXTSIZE, 
            '%.2f ms' % bpf.header.p_bary[0], alignment='start', 
            font_size=TEXTSIZE))
        cv.add_plot_container(TextFragment(x + width, 
            y + height + 2 * TEXTSIZE, '%.3f pc cm^-3' % bpf.header.best_dm,
            alignment='end', font_size=TEXTSIZE))


    files = os.listdir(sys.argv[1])
    tmp = []
    for f in files:
        if f.endswith('.bestprof'):
            try:
                bpf = BestprofFile(os.path.join(sys.argv[1], f))
            except:
                print 'There was a problem reading %s' % os.path.join(sys.argv[1], f)
            else:
                tmp.append(bpf)
    tmp.sort(key=lambda x: x.header.reduced_chi_sq)
    tmp.reverse()

    cv = SVGCanvas(1140, 1240)
    N_HORIZONTAL = 5
    N_VERTICAL = 10
    for ix in range(N_HORIZONTAL):
        for iy in range(N_VERTICAL):
            try:
                plot_profile(cv, 220 * ix + 20, 140 * iy + 20, 200, 100, tmp[ix + N_HORIZONTAL * iy], psr_name='B0000+0000')
            except IndexError, e:
                pass
    cv.draw('test234.xml')
