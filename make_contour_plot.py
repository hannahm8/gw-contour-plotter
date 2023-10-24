#!/usr/bin/env python
import matplotlib

matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['legend.fontsize'] = 9

import sys
sys.path.append('./O3bScripts/')

import json
import numpy as np
import pickle 
from matplotlib import pyplot as plt
from six import string_types
import matplotlib.patheffects as path_effects
import sys, os
import streamlit as st


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


def unpickle_contour_data(event, param_name, contour_dir):
    """
    This will unpickle the contour data from contour_data_dir
    
    Parameters
    ----------
    event: string
        the nickname of the event, e.g., GW191103A
        
    param_name: string
        the name of the two parameters to be plotted, must be one of: 
           - 'mass_1_source_mass_2_source'
           - 'log_chirp_mass_source_chi_eff_infinity_only_prec_avg',
           - 'log_total_mass_source_log_mass_ratio',
            
    contour_dir: string
        the path to the contour directory (see above)
    
    """
    infile = os.path.join(contour_dir, '{}_{}_contour_data.pkl'.format(event, param_name))
    with open(infile, 'rb') as inp:
        cdata = pickle.load(inp)
        
    return cdata
    

def plot_bounded_2d_kde(data=None, data2=None, contour_data=None, levels=None,
                        shade=False, gridsize=500, cut=3, legend=True,
                        shade_lowest=True, ax=None, verbose=False, **kwargs):

    """ 
    This function creates the contours at some chosen credible level
    The value of levels is passed from the make_contour_plot function.
    """

    if ax is None:
        ax = plt.gca()

    xx = contour_data['xx']
    yy = contour_data['yy']
    z = contour_data['z']
    den = contour_data['kde']
    kde_sel = contour_data['kde_sel']
    Nden = len(den)


    # Black (thin) contours 
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



def makeContourPlot(var1,var2,names,colors,highlight_events):
    
    """
    Read the contour data and call the contour plotting function 
    (plot_bounded_2d_kde). 
    
    Parameters
    ----------
    var1: string
        the name of parameter 1. Must be one of: 
         - 'mass_1_source'
         - 'log_chirp_mass_source',
         - 'log_total_mass_source'.
        Note: this must match with the correct var2.
    
    var2: string
        the name of parameter 2. Must be one of: 
         - 'mass_2_source'
         - 'chi_eff_infinity_only_prec_avg',
         - 'log_mass_ratio',
        Note: this must match with the correct var1.
    
    colors: dictionary
        contains the color to plot each event in so that the 
        plots match the paper.
        
    highlight_events: list
        the list of events to be highlighted (plotted in color).
    """

    # figure size 
    fig,ax = plt.subplots(figsize=(10,5.5))
    
    # line style
    ls = '-'

    # loop over the event names (short)
    shortNames = names.keys()
    
    for event in shortNames:
        
        
        contour_data = unpickle_contour_data(event, \
                                             '{}_{}'.format(var1,var2), \
                                             contour_dir)

        # get the full name for this event
        fullname = names[event]

        # Plotting the contours. 
        if fullname in highlight_events:
            """
            If the event is in the highlighted list, plot the contour
            in color
            """
            kwargs = {
                'ax':ax,
                'linestyles':ls,
                'colors':colors[event],
                'linewidths':1.5,'zorder':100,
                }
            plot_bounded_2d_kde(contour_data=contour_data,
                                levels=[0.9], 
                                **kwargs)
        else: 
            """
            Else, plot the contour in gray.
            """
            kwargs = {
                'ax':ax,
                'linestyles':None,
                'colors':'k',
                'linewidths':0.5,
                'alpha':0.3
                }
            ax = plot_bounded_2d_kde(contour_data=contour_data, 
                                     levels=[0.9], 
                                     **kwargs)
    # set no grid
    ax.grid(False)
        
    return fig,ax
    
    


def make_plot(events,contour_dir,var1,var2,highlight_events,
              color_file,names_dictionary):

    """
    Read the contour data and call the contour plotting function 
    for each plot variation (which uses plot_bounded_2d_kde). 
    
    Parameters
    ----------
    events: list of strings
        the list of events to be plotted.
        
    contour_dir: string
        path to the contour data directory.
    
    var1: string
        the name of parameter 1. Must be one of: 
         - 'mass_1_source'
         - 'log_chirp_mass_source',
         - 'log_total_mass_source'.
        Note: this must match with the correct var2.
    
    var2: string
        the name of parameter 2. Must be one of: 
         - 'mass_2_source'
         - 'chi_eff_infinity_only_prec_avg',
         - 'log_mass_ratio',
        Note: this must match with the correct var1.
    
    highlight_events: list of strings
        the list of events to be highlighted (plotted in color).
        
    color_file: string
        path to the colors.pkl file
    
    names_dictionary: dictionary
        dictionary to convert between event nicknames and event fullnames
    
    """



    # load the event colors consistent with the GWTC-3 catalog paper
    with open(color_file,'rb') as f:
        color_dict = pickle.load(f)

    # setting up the figure
    fig,ax = plt.subplots(figsize=(6.75,3.75))


    
    # setting up for the plots - different settings for each parameter pair
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
        ax.text(labelPositionX,labelPositionY+labelSpacingY,
                    'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=1.0))

        # reduce the number of ticks on the y axis
        yPositions = (-1.0, -0.5, 0.0, 0.5, 1.0)
        ax.set_yticks(yPositions)
        
        # relabel the x-axis to be in solar masses (not log)
        xPositions = (np.log10(2),np.log10(3),np.log10(10),
                      np.log10(20),np.log10(50))
        xLabels = ([round(10**p) for p in xPositions])
        ax.set_xticks(xPositions)
        ax.set_xticklabels(xLabels, fontsize=10)  
        ax.set_yticklabels(yPositions, fontsize=10)
  
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
        ax.text(labelPositionX,labelPositionY+labelSpacingY,
                    'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=1.0))

                              
        # mass ratio lines and labels
        log10Mt, log10q = massRatioLines_m2Equals3()
        ax.plot(log10Mt,log10q,color='k',alpha=0.3,ls='--')
        ax.text(np.log10(2.4),np.log10(.03),'Secondary mass = 3 solar masses',rotation=80,alpha=0.8)
        log10Mt, log10q = massRatioLines_m1Equals3()
        ax.plot(log10Mt,log10q,color='k',alpha=0.3,ls=':')
        ax.text(np.log10(42.),np.log10(.019),'Primary mass = 3 solar masses',rotation=324,alpha=0.8)
                              
        # relabelling the y axis to mass ratio (instead of log10)
        yValues = (.02,.03,.05,.08,.12,.20,.30,.45,.65,1.)
        yPositions = ([np.log10(v) for v in yValues])
        yLabels = (["{:.2f}".format(round(10**p,2)) for p in yPositions])
        ax.set_yticks(yPositions, fontsize=10)
        ax.set_yticklabels(yLabels, fontsize=10)
        
        # relabelling the x-axis to solar masses (not log solar masses)
        xValues = (2, 4, 7, 10, 20, 40, 70, 100, 200, 400)
        xPositions = ([np.log10(v) for v in xValues])
        xLabels = ([round(10**p) for p in xPositions])
        ax.set_xticks(xPositions, fontsize=10)
        ax.set_xticklabels(xLabels, fontsize=10)


    elif var1=='mass_1_source' and var2=='mass_2_source':


        # axis ranges, scales and labels
        ax.set_xlim(2,200)
        ax.set_ylim(1,100)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Primary mass in solar masses',fontsize=10)
        ax.set_ylabel('Secondary mass in solar masses',fontsize=10)
        
        # twin the x axis - this is for the highlighted event list spacing
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
        ax2.text(labelPositionX,labelPositionY+labelSpacingY,
                     'Highlighted events',
                     color='k',
                     bbox=dict(boxstyle='round',
                               facecolor='white',
                               edgecolor='none',
                               alpha=1.0))


        xValues = (2, 4, 7, 10, 20, 40, 70, 100, 200)
        ax.set_xticks(xValues, fontsize=10)
        ax.set_xticklabels(xValues, fontsize=10)
        yValues = (1, 2, 4, 7, 10, 20, 40, 70, 100, 200)
        ax.set_yticks(yValues, fontsize=10)
        ax.set_yticklabels(yValues, fontsize=10)
        
        # make the shaded region for m2>m1                              
        m = np.logspace(0,np.log10(200),500)
        ax.fill_between(m,m,200,color='lightgrey',zorder=10000)
        ax.plot(m,m,color='k',zorder=10001)
        ax.text(11,14,r'mass ratio = 1',rotation=25,color='k',\
                    fontsize=10,zorder=10002)

        
        # shaded region for q=/50
        m2=m/50
        ax.fill_between(m,m2,1,color='lightgrey',zorder=10000)
        ax.plot(m,m2,color='k',zorder=10001)
        ax.text(75,1.15,r'mass ratio = 1/50',rotation=25,color='k',\
                    fontsize=10,zorder=10002)


    # count the number of highlighted events - this is so we can split the
    # list in two at halfway
    highlightCount = 0
    
    for event in events:
        """ 
        plotting the contour lines for each event
        """

        # swap full name for nickname for getting contour file
        nickname = get_key_from_value(names_dictionary['FULLNAME'], event)

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
                we use ax2 for the m1/m2 plot
                """
                if highlightCount==19: 
                    """
                    shift the highlighted list once we reach the halfway point
                    """
                    labelPositionX+=secondLabelColumnXShift
                    labelPositionY+=secondLabelColumnYShift
                # write the label
                ax2.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',\
                                  edgecolor='none',alpha=.7))
            else: 
                if highlightCount==19: 
                    """
                    shift the highlighted list once we reach the halfway point
                    """
                    labelPositionX+=secondLabelColumnXShift
                    labelPositionY+=secondLabelColumnYShift
                # write the label
                ax.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',\
                                  edgecolor='none',alpha=.7))
                            
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
            plot_bounded_2d_kde(contour_data=contour_data,levels=[0.9],**kwargs)

    # no grid
    ax.grid(False)

    return fig

