
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
    q = np.arange(0.0, 1.1, 0.01)
    Mt = 3.*(q+1)
    return np.log10(Mt), np.log10(q)

def massRatioLines_m1Equals3():
    Mt = np.arange(2, 400, 1.)
    q = 3. / (Mt - 3)
    return np.log10(Mt), np.log10(q)
    

def get_key_from_value(d, val):
    """ 
    from 
    https://note.nkmk.me/en/python-dict-get-key-from-value/
    """
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

def download_data():

    address = "https://zenodo.org/api/files/d7a70f99-e16a-48a2-ae27-0b1968b0840c/contour_data.tar.gz"

    r = requests.get(address)
        
    file_name = 'contour_data.tar.gz'
    with open(file_name, 'wb') as f:
        f.write(r.content)

    my_tar = tarfile.open(file_name)
    my_tar.extractall('.')
    my_tar.close()
    
    return ('.')
#def download_data():
#
#    # -- Read token
#    token = readtoken('/Users/jkanner/.zenodo-contour-test')
#    
#    # -- Get zenodo response
#    response = retrieve('942135', token)
#    
#    # -- Download file
#    filename = download_file(token, response)
#    print('Looking to untar:',filename)
#    
#    # -- untar
#    print('Extracting ', filename)
#    my_tar = tarfile.open(filename)
#    my_tar.extractall('.')
#    my_tar.close()
#
#    # -- Return path to file
#    return('.')
    
def unpickle_contour_data(event, post_name, contour_dir='./contour_dir'):
    """ 
    This is from o3b-cbc-catalog/scipts/plotting/O1_BBH_functions
    """

    #contour_dir = './contour_data'
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

    with open(color_file,'rb') as f:
        color_dict = pickle.load(f)



    #event ='GW191109A'
    fig,ax = plt.subplots(figsize=(6.75,3.75))
    ls = '-'


    #var1, var2 = "chirp_mass_source", "chi_eff"
    if var1=='chirp_mass_source' and var2=='chi_eff':
        ax.set_xlim(2,100)
        ax.set_ylim(-1,1)
        ax.set_xlabel('Chirp mass in solar masses')
        ax.set_ylabel('Effective inspiral spin')
        labelPositionY = 0.85
        labelSpacingY = 0.11
        labelPositionX = 110
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
    if var1=='log_chirp_mass_source' and var2=='chi_eff_infinity_only_prec_avg':
        ax.set_xlim(0.3,2.0)
        ax.set_ylim(-1,1)
        ax.set_xlabel('Chirp mass in solar masses',fontsize=10)
        ax.set_ylabel('Effective inspiral spin',fontsize=10)
        labelPositionY = 0.85
        labelSpacingY = 0.11
        labelPositionX = np.log10(105)
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))

        # reduce the number of ticks on the y axis
        yPositions = (-1.0, -0.5, 0.0, 0.5, 1.0)

        ax.set_yticks(yPositions)
        ax.set_yticklabels(yPositions,fontsize=10)
        # relabel the x-axis to be in solar masses (not log)
        xPositions = (np.log10(2),np.log10(3), np.log10(10), np.log10(20), np.log10(50))
        xLabels = ([round(10**p) for p in xPositions])
        ax.set_xticks(xPositions)
        ax.set_xticklabels(xLabels)                              
                              
    elif var1=='total_mass_source' and var2=='mass_ratio':
        ax.set_xlim(2,400)
        ax.set_ylim(0,1)
        ax.set_xlabel('Total mass in solar masses',fontsize=10)
        ax.set_ylabel('Mass ratio',fontsize=10)
        labelPositionY = 0.9
        labelSpacingY = 0.06
        labelPositionX = 410
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
    elif var1=='log_total_mass_source' and var2=='log_mass_ratio':
        ax.set_xlim(0.7,np.log10(400))
        ax.set_ylim(-1.8,0)
        ax.set_xlabel('Total mass in solar masses',fontsize=10)
        ax.set_ylabel('Mass ratio',fontsize=10)
        labelPositionY = -0.2
        labelSpacingY = 0.1
        labelPositionX = np.log10(430)
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
        # mass ratio lines
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
        labelPositionY = 9.#-0.2
        labelSpacingY = 0.6
        labelPositionX = 210
        ax.set_xlim(2,200)
        ax.set_ylim(1,100)
        ax.set_xscale('log')
        ax.set_yscale('log')

        ax2 = ax.twinx()
        ax2.yaxis.set_ticklabels([])
        ax2.tick_params(right=False)
        ax2.set_ylim(0,10)
        ax2.grid(False)
        
        m = np.logspace(0,np.log10(200),500)
        ax.plot(m,m,color='k')
        ax.fill_between(m,m,200,color='lightgrey')
        ax.set_xlabel('Primary mass in solar masses',fontsize=10)
        ax.set_ylabel('Secondary mass in solar masses',fontsize=10)
        
        ax2.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
    for event in events:

        # swap full name for nickname for getting contour file
        nickname = get_key_from_value(namesDict['FULLNAME'], event)

        contour_data = unpickle_contour_data(nickname, \
                                             '{}_{}'.format(var1,var2), \
                                             contour_dir)

        if event in highlight_events:
            kwargs = {
                'ax':ax,
                'linestyles':ls,
                'colors':color_dict['colors'][nickname],
    #            'colors':'g',
                'linewidths':1.5,'zorder':100,
    #            'label':str(event)
                }

            print(event) 
            name = var1+'_'+var2
            #print(contour_label_positions[name].keys())
            #positions = contour_label_positions[name][nickname]

            plot_bounded_2d_kde(contour_data=contour_data, \
                                          levels=[0.9], **kwargs,label=str(event))

            #display_name=event
            display_name = event.replace('_','-')

            if var1=='mass_1_source':
                ax2.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',edgecolor='none',alpha=.7))
            else: 
                ax.text(labelPositionX,labelPositionY,display_name,
                        fontdict=dict(color=kwargs['colors']),
                        bbox=dict(boxstyle='round',facecolor='white',edgecolor='none',alpha=.7))
                        
            #ax.text(positions[0],positions[1],display_name,rotation=positions[2],
            #        fontdict=dict(color=kwargs['colors']),
            #        bbox=dict(boxstyle='round',facecolor='white',edgecolor='none',alpha=0.7),
            #        path_effects = [path_effects.withSimplePatchShadow(offset=(.2,-.2),
            #                                                           shadow_rgbFace='k',
            #                                                           alpha=1)])
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
    #fig.tight_layout()


    #ax.set_xscale('log')
    #xlim = ax.get_xlim()
    # we want 
    
    

    #ax.set_xticklabels(labels)
    
    
    #print('xticks ', ax.get_xticks)
    #ticks = [1, 2, 4, 7, 10, 20, 40, 70, 100]
    #ax.set_xticks([np.log10(tick) for tick in ticks])
    #ax.set_xticklabels(['${}$'.format(tick) for tick in ticks])
        #ax.set_xticks(np.log10([3, 5, 6, 8, 9, 15, 30, 50, 60, 80, 90]), minor=True) 
        
        
    #ticks = [0.02, 0.03, 0.05, 0.08, 0.12, 0.20, 0.30, 0.45, 0.65, 1]
    #ax.set_yticks([np.log10(tick) for tick in ticks])
    #ax.set_yticklabels(['${:.1f}$'.format(tick) for tick in ticks])
      
    #ticks = [-1.8, -1.6, -1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2]
    #ax.set_xticks([np.log10(tick) for tick in ticks])
    #ax.set_xticklabels(['${}$'.format(tick) for tick in ticks])
    #ax.set_xticks(np.log10([5, 6, 8, 9, 15, 30, 50, 60, 80, 90, 150, 300]), minor=True)
    
    #newticks = pu.custom_log_ticks(xlim,[1,2,4,7])
    #newticks = ax.get_xticks()
    #newticks[3] = '5'    
    #ax.set_xticks(newticks)
    #print('xlim', xlim)
    #print(ax.get_xticks())

    #ax.tick_params(axis='both',size=6,labelsize=12)

    #tick = ScalarFormatter()
    #ax.xaxis.set_major_formatter(tick)
    #ax.yaxis.set_major_formatter(tick)

    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')



    return fig

