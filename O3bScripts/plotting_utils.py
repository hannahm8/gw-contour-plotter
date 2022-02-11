import json
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import cm
from scipy.stats import gaussian_kde as kde
from glob import glob
import os

# -*- coding: utf-8 -*-
#
#       Copyright 2020
#       Zoheyr Doctor <zoheyr.doctor@ligo.org>
#       Leo Tsukada <leo.tsukada@ligo.org>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

# ----------------- HARD CODED QUANTITIES FOR PLOTS ---------------------------
"""
column_name2tex_name = {
        'total_mass_source':r'M/M_\odot',
        'chirp_mass_source':r'\mathcal{{M}}/M_\odot',
        'mass_1_source':r'm_1/M_\odot',
        'mass_2_source':r'm_2/M_\odot',
        'chi_eff':r'\chi_{{\rm eff}}',
        'chi_p':r'\chi_p',
        'luminosity_distance':r'D_{\rm L}/{\rm Gpc}',
        'redshift':r'z',
        'mass_ratio':r'q',
        'lambda_2':r'\Lambda_2',
        'lambda_1':r'\Lambda_1',
        'cos_tilt_1':r'\cos(\theta_1)',
        'cos_tilt_2':r'\cos(\theta_2)',
        'symmetric_mass_ratio':r'\eta',
        }
"""

# label positions for minimal names
#mtot_q_label_positions = {
#    'GW190425A': (3.6,0.9,0),
#    'GW190426A': (4,0.1,0),
#    'GW190412A': (40,0.14,0),
#    'GW190521A': (150,0.3,0),
#    'GW190814A': (14, .05, 0),
#    'GW190929A': (120,0.07,0),
#    'GW190828B': (15,0.18,0),
#    'GW190924A': (6.5,0.8,0)
#}
#
#mc_chi_eff_label_positions = {
#    'GW190425A': (1.1,-0.15,0),
#    'GW190426A': (1.8,0.52,0),
#    'GW190412A': (10,0.45,0),
#    'GW190521A': (45,-0.55,0),
#    'GW190814A': (4.5, -0.25, 0),
#    'GW190517A': (20, 0.82, 0),
#    'GW190514A': (20,-.7,0)
#}

# label positions when full names are used
mtot_q_label_positions = {
#    'GW191230A': ,
#    'GW191109A': ,
#    'GW191129A': ,
#    'GW200223A': , 
#    'GW200115A':,
#    'GW200105A': ,
#    'GW200311A': , 
#
    "GW200316I": (22.,0.4,275),
    "GW200311L": (70.5,0.55,270),
#    "GW200311A": (2.7, 0.5,315),
    "GW200308G": (61,0.03,0),
    "GW200306A": (29,0.5,272),
    "GW200302A": (40,0.55,270),
    "GW200225B": (27,0.55,273),
    "GW200224H": (81,0.55,270),
#    'GW200223A': (30, 0.07, 315)
#    "GW200220A": (185,0.3,270),
#    "GW200219B": (1,0,0),
    "GW200219D": (45,0.5,270),
#    "GW200216A": (1,0,0),
    "GW200210B": (9,0.04,0),
    "GW200209E": (40,0.5,272),
#    "GW200208B": (1,0,0),
    "GW200208I": (75,0.5,270),
    "GW200202F": (13.5,0.55,273),
#    "GW200201A": (1,0,0),
#    "GW200129A": (1,0,0),
    "GW200128C": (47,0.5,270),
#    "GW200121A": (1,0,0),
    "GW200115A": (4.3, 0.3, 280), 
#    "GW200112A": (75,0.4,270),
    "200105F": (8.3, 0.1, 300),
    "GW191230H": (58, 0.55, 270),
    "GW191222A": (80,0.25,280),
#    "GW191219A": (1,0,0),
    "GW191216G": (20.5,0.45,275),
    "GW191215G": (32,0.45,275),
    "GW191204B": (21, 0.4, 275),
    "GW191204A": (33,0.55,270),
    "GW191129F": (13, 0.4, 275),
    "GW191127B": (102,0.55,270),
    "GW191126C": (22.5,0.45,275),
#    "GW191118A": (1,0,0),
    "GW191109A": (140, 0.4, 270),
#    "GW191105A": (1,0,0),
    "GW191103A": (12,0.4,280)
}

mc_chi_eff_label_positions = {
    "GW200316I": (5.,0.55,0),
    "GW200311L": (18,0.2,0),
#    "GW200311A": (1.05, 0.22,0),
    "GW200308G": (25,0.9,0),
    "GW200306A": (12,0.7,0),
    "GW200302A": (24,0.35,0),
    "GW200225B": (7,-0.45,0),
    "GW200224H": (30,-0.15,0),
#    "GW200220A": (30,0.59,0),
#    "GW200219B": (1,0,0),
    "GW200219D": (15,-0.55,0),
#    "GW200216A": (1,0,0),
    "GW200210B": (4,-0.59,0),
    "GW200209E": (17,0.3,0),
#    "GW200208B": (1,0,0),
    "GW200208I": (17,-0.48,0),
    "GW200202F": (4.8,-0.15,0),
#    "GW200201A": (1,0,0),
#    "GW200129A": (1,0,0),
    "GW200128C": (30,0.4,0),
#    "GW200121A": (1,0,0),
    "GW200115A": (1.5, -0.8, 0), 
#    "GW200112A": (30,0,0),
    "200105F": (1.8,0.35,0),
    "GW191230H": (20, -0.5,0),
    "GW191222A": (34,-.51,0),
#    "GW191219A": (1,0,0),
    "GW191216G": (2.5,0.25,0),
    "GW191215G": (9.5,0.19,0),
    "GW191204B": (5,-0.04,0),
    "GW191204A": (12,0.42,0),
    "GW191129F": (4.2, -0.5, 0),
    "GW191127B": (33,0.65,0),
    "GW191126C": (6,0.45,0),
#    "GW191118A": (1,0,0),
    "GW191109A": (25, 0.7, 0),
#    "GW191105A": (1,0,0),
    "GW191103A": (6,-.3,0)
}



mtot_eta_label_positions = {
    'GW191230A': (150,0.17,0),
    'GW191109A': (0, 0, 0),
    'GW191109A': (0, 0, 0), 
    'GW200223A': (0, 0, 0), 
    'GW200115A': (0, 0, 0), 
    'GW200105A': (0, 0, 0) 
}

contour_label_positions = {
    'total_mass_source_mass_ratio':mtot_q_label_positions,
    'chirp_mass_source_chi_eff':mc_chi_eff_label_positions,
    'total_mass_source_symmetric_mass_ratio':mtot_eta_label_positions,
}

# --------------------- OTHER FUNCTIONS ---------------------------------------

def custom_log_ticks(lim,tick_ints):
    """
    Makes custom ticks on a log scale.  
    For example, could show 1,5,10,50...
    or 1,3,6,10,30,60,100...

    Parameters
    ----------
    lim: len(2) list
        min and max plot limits.  Used to figure out
        the bounds of the ticks
    tick_ints:list
        list of integer multipliers of
        powers of ten at which to put ticks

    Returns
    -------
    newticks: list
        list of new values at which to put ticks
    """
    logmin = np.floor(np.log10(lim[0]))
    logmax = np.ceil(np.log10(lim[1]))
    power10ticks = np.power(10,np.arange(logmin,logmax+1))
    newticks = []
    for ticky in power10ticks:
        for tick_int in tick_ints:
            newticks.append(tick_int*ticky)
    newticks=np.array(newticks)
    print(newticks,lim)
    minval = newticks[newticks <= lim[0]][-1]
    maxval = newticks[newticks >= lim[1]][0]
    return newticks[(newticks>=minval) & (newticks<=maxval)]

def map_colors(event_list, random_seed=None,cmap='viridis'):
    """
    A function to map an arbitrary number of events to colors
    """
    if isinstance(cmap,str):
        cm_spectral = cm.get_cmap(cmap)
    else: 
        cm_spectral = cmap
    
    cm_indices = np.linspace(0, 1, num=len(event_list))
    
    if random_seed is not None:
        np.random.seed(random_seed)
        np.random.shuffle(cm_indices)
    color_dict = {event_name:matplotlib.colors.to_hex(cm_spectral(cm_index)) for event_name, cm_index in zip(event_list, cm_indices)}
    return color_dict

def find_skymap(event,skymap_file_name=None):
    """
    Finds the \'best\' skymap from O3 runs
    """
    template = '/home/cbc/public_html/pe/O3/{}/samples/{}.fits'
    if skymap_file_name is not None:
        skymap_file = template.format(event,skymap_file_name)
        if os.path.exists(skymap_file):
            return skymap_file
        else:
            print('could not find the file you wanted.  Using default')
    fits_files = np.array(glob(template.format(event,'*')))
    Offline_file = template.format(event,'Offline_skymap')
    LI_file = template.format(event,'lalinference')
    newer_fits_sel = ~np.in1d(fits_files,[Offline_file,LI_file])
    if np.sum(newer_fits_sel)==0:
        if os.path.exists(LI_file):
            skymap_file = LI_file
        elif os.path.exists(Offline_file):
            skymap_file = Offline_file
        else:
            print('No skymap found')
            return None
    else:
        skymap_file = fits_files[newer_fits_sel][0]
    return skymap_file


class Bounded_2d_kde(kde):
    r"""Represents a two-dimensional Gaussian kernel density estimator
    for a probability distribution function that exists on a bounded
    domain."""

    def __init__(self, pts, xlow=None, xhigh=None, ylow=None, yhigh=None, *args, **kwargs):
        """Initialize with the given bounds.  Either ``low`` or
        ``high`` may be ``None`` if the bounds are one-sided.  Extra
        parameters are passed to :class:`gaussian_kde`.

        :param xlow: The lower x domain boundary.

        :param xhigh: The upper x domain boundary.

        :param ylow: The lower y domain boundary.

        :param yhigh: The upper y domain boundary.
        """
        pts = np.atleast_2d(pts)

        assert pts.ndim == 2, 'Bounded_kde can only be two-dimensional'

        super(Bounded_2d_kde, self).__init__(pts.T, *args, **kwargs)

        self._xlow = xlow
        self._xhigh = xhigh
        self._ylow = ylow
        self._yhigh = yhigh

    @property
    def xlow(self):
        """The lower bound of the x domain."""
        return self._xlow

    @property
    def xhigh(self):
        """The upper bound of the x domain."""
        return self._xhigh

    @property
    def ylow(self):
        """The lower bound of the y domain."""
        return self._ylow

    @property
    def yhigh(self):
        """The upper bound of the y domain."""
        return self._yhigh

    def evaluate(self, pts):
        """Return an estimate of the density evaluated at the given
        points."""
        pts = np.atleast_2d(pts)
        assert pts.ndim == 2, 'points must be two-dimensional'

        x, y = pts.T
        pdf = super(Bounded_2d_kde, self).evaluate(pts.T)
        if self.xlow is not None:
            pdf += super(Bounded_2d_kde, self).evaluate([2*self.xlow - x, y])

        if self.xhigh is not None:
            pdf += super(Bounded_2d_kde, self).evaluate([2*self.xhigh - x, y])

        if self.ylow is not None:
            pdf += super(Bounded_2d_kde, self).evaluate([x, 2*self.ylow - y])

        if self.yhigh is not None:
            pdf += super(Bounded_2d_kde, self).evaluate([x, 2*self.yhigh - y])

        if self.xlow is not None:
            if self.ylow is not None:
                pdf += super(Bounded_2d_kde, self).evaluate([2*self.xlow - x, 2*self.ylow - y])

            if self.yhigh is not None:
                pdf += super(Bounded_2d_kde, self).evaluate([2*self.xlow - x, 2*self.yhigh - y])

        if self.xhigh is not None:
            if self.ylow is not None:
                pdf += super(Bounded_2d_kde, self).evaluate([2*self.xhigh - x, 2*self.ylow - y])
            if self.yhigh is not None:
                pdf += super(Bounded_2d_kde, self).evaluate([2*self.xhigh - x, 2*self.yhigh - y])

        return pdf

    def __call__(self, pts):
        pts = np.atleast_2d(pts)
        out_of_bounds = np.zeros(pts.shape[0], dtype='bool')

        if self.xlow is not None:
            out_of_bounds[pts[:, 0] < self.xlow] = True
        if self.xhigh is not None:
            out_of_bounds[pts[:, 0] > self.xhigh] = True
        if self.ylow is not None:
            out_of_bounds[pts[:, 1] < self.ylow] = True
        if self.yhigh is not None:
            out_of_bounds[pts[:, 1] > self.yhigh] = True

        results = self.evaluate(pts)
        results[out_of_bounds] = 0.
        return results

def q_to_eta(q):
    """transform from q to etq"""
    return q/(1.+q)**2

def eta_to_q(eta):
    """transform from eta to q"""
    return np.array([(-(2.*et - 1.) - np.sqrt(1.-4.*et))/(2.*et) if et!=0. else 0. for et in eta])


def m1m2_to_mcq(pts):
    """
    transforms from m1m2 to chirp mass and q
    """
    m1,m2 = pts[:,0],pts[:,1]
    mc = ((m1*m2)**(3./5.))/((m1+m2)**(1./5.))
    q = m2/m1
    return np.array([mc,q]).T

def Meta_to_mcq(pts):
    M,eta = pts[:,0],pts[:,1]
    q = eta_to_q(eta)
    Mc = M*1./(1./q + q + 2.)
    return np.array([Mc,q]).T
