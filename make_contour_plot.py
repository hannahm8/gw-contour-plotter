#!/usr/bin/env python
import matplotlib
#matplotlib.use('agg')

#matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['savefig.dpi'] = 300
#matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
matplotlib.rcParams['legend.fontsize'] = 9

import sys
#sys.path.append('/home/hannahm/repositories/o3b-cbc-catalog/scripts/')
#sys.path.append('/home/hannahm/repositories/o3b-cbc-catalog/scripts/plotting/')
sys.path.append('./O3bScripts/')

import json, tarfile
import numpy as np
import plotting_utils as pu
import pickle 
from matplotlib import pyplot as plt
from cycler import cycler
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter
from six import string_types
import matplotlib.patheffects as path_effects
import sys, os
import streamlit as st
sys.path.append(
            os.path.abspath(os.path.join(os.path.dirname(__file__), 
                os.path.pardir)))
import requests
#from zenodozen import readtoken, retrieve, download_file

#from plotting_utils import contour_label_positions, eta_to_q, q_to_eta

def massRatioLines_m2Equals3():
    """
    get constant mass line (at m2=3) for the 
    total mass - mass ratio plot
    """
    q = np.arange(0.0, 1.1, 0.01)
    Mt = 3.*(q+1)
    return np.log10(Mt), np.log10(q)


def massRatioLines_m1Equals3():
    """
    get constant mass line (at m1=3) for the 
    total mass - mass ratio plot
    """
    Mt = np.arange(2, 400, 1.)
    q = 3. / (Mt - 3)
    return np.log10(Mt), np.log10(q)
    

def get_key_from_value(d, val):
    """ 
    getting the keys - borrowed from: 
    https://note.nkmk.me/en/python-dict-get-key-from-value/
    """
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None
    

def download_data():
    """
    downloading the data
    """
    
    address = "https://zenodo.org/api/files/d7a70f99-e16a-48a2-ae27-0b1968b0840c/contour_data.tar.gz"

    r = requests.get(address)
        
    file_name = 'contour_data.tar.gz'
    with open(file_name, 'wb') as f:
        f.write(r.content)

    my_tar = tarfile.open(file_name)
    my_tar.extractall('.')
    my_tar.close()
    
    return ('.')

    
def unpickle_contour_data(event, post_name, contour_dir='./contour_dir'):
    """ 
    Unpickling the contour data  - this uses the functions from 
    o3b-cbc-catalog/scipts/plotting/O1_BBH_functions
    """

    infile = os.path.join(contour_dir, '{}_{}_contour_data.pkl'.format(event, post_name))
    
    try:    
        with open(infile, 'rb') as inp:
            cdata = pickle.load(inp)
    except:
        with st.spinner(text='Downloading data.  This will take a few minutes ...'):
            download_data()
        st.success('Download complete!')
        with open(infile, 'rb') as inp:
            cdata = pickle.load(inp)
            
    return cdata


def plot_bounded_2d_kde(data=None, data2=None, contour_data=None, levels=None,
                        shade=False, gridsize=500, cut=3, legend=True,
                        shade_lowest=True, ax=None, verbose=False, **kwargs):
    """ 
    this is adapted from the version in O1_BBH_functions in the O3b catalog
    paper repository in o3b-cbc-catalog/scipts/plotting/O1_BBH_functions.py
    """

    if ax is None:
        ax = plt.gca()

    xx = contour_data['xx']
    yy = contour_data['yy']
    z = contour_data['z']
    den = contour_data['kde']
    kde_sel = contour_data['kde_sel']
    Nden = len(den)


    # Black (thin) contours with while outlines by default
    kwargs['linewidths'] = kwargs.get('linewidths', 1.)
    kwargs['linestyles'] = kwargs.get('linestyles', 1.)

    # Plot the contours
    n_levels = kwargs.pop("n_levels", 1)
    cmap = kwargs.get("cmap", None)


    if cmap is None:
        kwargs['colors'] = kwargs.get('colors', 'k')
    if isinstance(cmap, string_types):
        if cmap.endswith("_d"):
            pal = ["#333333"]
            pal.extend(sns.palettes.color_palette(cmap.replace("_d", "_r"), 2))
            cmap = sns.palettes.blend_palette(pal, as_cmap=True)
        else:
            cmap = plt.cm.get_cmap(cmap)


    kwargs["cmap"] = cmap
    contour_func = ax.contourf if shade else ax.contour

    if levels:
        zvalues = np.empty(len(levels))
        for i, level in enumerate(levels):
            ilevel = int(np.ceil(Nden*level))
            ilevel = min(ilevel, Nden-1)
            zvalues[i] = den[ilevel]
        zvalues.sort()

        cset = contour_func(xx, yy, z, zvalues, **kwargs)

        for i, coll in enumerate(cset.collections):
            level = coll.get_paths()[0]

    return ax




def make_plot(events,contour_dir,var1,var2,highlight_events,color_file,namesDict):
    """
    making the plots
    """

    # load the event colors consistent with the GWTC-3 catalog paper
    with open(color_file,'rb') as f:
        color_dict = pickle.load(f)

    # setting up the figure
    fig,ax = plt.subplots(figsize=(6.75,3.75))
    
    
    if var1=='log_chirp_mass_source' and var2=='chi_eff_infinity_only_prec_avg':
    
        # plot settings - axis ranges and labels
        ax.set_xlim(0.3,2.0)
        ax.set_ylim(-1,1)
        ax.set_xlabel('Chirp mass in solar masses',fontsize=10)
        ax.set_ylabel('Effective inspiral spin',fontsize=10)
        
        # set up for the highlighed event labels
        labelPositionY = 0.85
        labelSpacingY = 0.11
        labelPositionX = np.log10(110)
        secondLabelColumnXShift=.42
        secondLabelColumnYShift=1.98
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))

        # reduce the number of ticks on the y axis
        yPositions = (-1.0, -0.5, 0.0, 0.5, 1.0)
        ax.set_yticks(yPositions)
        
        # relabel the x-axis to be in solar masses (not log)
        xPositions = (np.log10(2),np.log10(3), np.log10(10), np.log10(20), np.log10(50))
        xLabels = ([round(10**p) for p in xPositions])
        ax.set_xticks(xPositions)
        ax.set_xticklabels(xLabels)    
        
        # plot y=0 line
        
        ax.plot([0.3,2.0],[0,0],color='k',alpha=0.3,ls=':')                          
                              

    elif var1=='log_total_mass_source' and var2=='log_mass_ratio':
    
        # axis ranges and labels
        ax.set_xlim(0.7,np.log10(400))
        ax.set_ylim(-1.8,0)
        ax.set_xlabel('Total mass in solar masses',fontsize=10)
        ax.set_ylabel('Mass ratio',fontsize=10)
        
        # setting up for the highlighed event labels
        labelPositionY = -0.15
        labelSpacingY = 0.1
        labelPositionX = np.log10(480)
        secondLabelColumnXShift=.58
        secondLabelColumnYShift=1.8
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
                              
        # mass ratio lines and labels
        log10Mt, log10q = massRatioLines_m2Equals3()
        ax.plot(log10Mt,log10q,color='k',alpha=0.3,ls='--')
        ax.text(np.log10(3.4),np.log10(.35),r'$m_2=3M_{\odot}$',rotation=64,alpha=0.8)
        log10Mt, log10q = massRatioLines_m1Equals3()
        ax.plot(log10Mt,log10q,color='k',alpha=0.3,ls=':')
        ax.text(np.log10(100.),np.log10(.02),r'$m_1=3M_{\odot}$',rotation=324,alpha=0.8)
                              
        # relabelling the y axis to mass ratio (instead of log10)
        yValues = (.02,.03,.05,.08,.12,.20,.30,.45,.65,1.)
        yPositions = ([np.log10(v) for v in yValues])
        yLabels = (["{:.2f}".format(round(10**p,2)) for p in yPositions])
        ax.set_yticks(yPositions)
        ax.set_yticklabels(yLabels,fontsize=10)
        
        # relabelling the x-axis to solar masses (not log solar masses)
        xValues = (2, 4, 7, 10, 20, 40, 70, 100, 200, 400)
        xPositions = ([np.log10(v) for v in xValues])
        xLabels = ([round(10**p) for p in xPositions])
        ax.set_xticks(xPositions)
        ax.set_xticklabels(xLabels,fontsize=10)

    elif var1=='mass_1_source' and var2=='mass_2_source':
    
        # axis ranges and labels
        ax.set_xlim(2,200)
        ax.set_ylim(1,100)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Primary mass in solar masses',fontsize=10)
        ax.set_ylabel('Secondary mass in solar masses',fontsize=10)
        
        # twin the x axis - this is to help us with the highlighed event list
        ax2 = ax.twinx()
        ax2.yaxis.set_ticklabels([])
        ax2.tick_params(right=False)
        ax2.set_ylim(0,10)
        ax2.grid(False)
        
        # set up the highlighed event labels        
        labelPositionY = 9.
        labelSpacingY = 0.6
        labelPositionX = 210
        secondLabelColumnXShift=500
        secondLabelColumnYShift=10.8
        ax2.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))

        # make the shaded region for m2>m1                              
        m = np.logspace(0,np.log10(200),500)
        ax.plot(m,m,color='k')
        ax.fill_between(m,m,200,color='lightgrey')


    # cound the number of highlighted events - this is so we can split the
    # list in two at halfway
    highlightCount = 0
    
    for event in events:
        """ 
        plotting the contour lines
        """

        # swap full name for nickname for getting contour file
        nickname = get_key_from_value(namesDict['FULLNAME'], event)

        # get the data
        contour_data = unpickle_contour_data(nickname, \
                                             '{}_{}'.format(var1,var2), \
                                             contour_dir)
                                             
        if event in highlight_events:
            """
            plot the highlighed events in colour
            """  
            highlightCount += 1
            kwargs = {
                'ax':ax,
                'linestyles':'-',
                'colors':color_dict['colors'][nickname],
                'linewidths':1.5,'zorder':100,
                }

            print(event) 
            name = var1+'_'+var2

            plot_bounded_2d_kde(contour_data=contour_data, \
                                          levels=[0.9], **kwargs,label=str(event))

            display_name=event

            if var1=='mass_1_source':
                """
                as we are using ax2 for the m1/m2 plot
                """
                if highlightCount==19: 
                    """
                    shift the list once we reach the halfway point
                    """
                    labelPositionX+=secondLabelColumnXShift
                    labelPositionY+=secondLabelColumnYShift
                # write the label
                ax2.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',edgecolor='none',alpha=.7))
            else: 
                if highlightCount==19: 
                    """
                    shift the list once we reach the halfway point
                    """
                    labelPositionX+=secondLabelColumnXShift
                    labelPositionY+=secondLabelColumnYShift
                # write the label
                ax.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',edgecolor='none',alpha=.7))
                            
            # shift the label for the next event
            labelPositionY-=labelSpacingY
        else: 
            """
            plot the contours that are not highlighted (all in grey)
            """
            kwargs = {
                'ax':ax,
                'linestyles':None,
                'colors':'k',
                'linewidths':0.5,
                'alpha':0.3
                }
            plot_bounded_2d_kde(contour_data=contour_data, levels=[0.9], **kwargs)

    ax.grid(False)


    return fig

