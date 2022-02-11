
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

    print(type(cset))

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
        ax.set_xlabel('Chirp mass in solar masses')
        ax.set_ylabel('Effective inspiral spin')
        labelPositionY = 0.85
        labelSpacingY = 0.11
        labelPositionX = 2.2
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
    elif var1=='total_mass_source' and var2=='mass_ratio':
        ax.set_xlim(2,400)
        ax.set_ylim(0,1)
        ax.set_xlabel('Total mass in solar masses')
        ax.set_ylabel('Mass ratio')
        labelPositionY = 0.9
        labelSpacingY = 0.06
        labelPositionX = 450
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
                    color='k',
                    bbox=dict(boxstyle='round',
                              facecolor='white',
                              edgecolor='none',
                              alpha=.7))
    elif var1=='log_total_mass_source' and var2=='log_mass_ratio':
        ax.set_xlim(0.7,3)
        ax.set_ylim(-1.8,0)
        ax.set_xlabel('Log Total mass in solar masses')
        ax.set_ylabel('Log Mass ratio')
        labelPositionY = -0.2
        labelSpacingY = 0.1
        labelPositionX = 3.1
        ax.text(labelPositionX,labelPositionY+labelSpacingY,'Highlighted events',
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


    ax.set_xscale('log')
    xlim = ax.get_xlim()
    #newticks = pu.custom_log_ticks(xlim,[1,2,4,7])
    #ax.set_xticks(newticks)

    ax.tick_params(axis='both',size=6,labelsize=12)

    tick = ScalarFormatter()
    ax.xaxis.set_major_formatter(tick)
    ax.yaxis.set_major_formatter(tick)

    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')



    return fig

