

#response_API = requests.get('https://zenodo.org/api/records/5117762/files/search_data_GWTC2p1.tar.xml.gz')
#response_API = requests.get('https://zenodo.org/api/files/35914311-503b-452d-a67a-7a3587b91810/search_data_GWTC2p1.tar.xml.gz')

import streamlit as st
import requests, io
from os.path import exists
import json, tarfile
import h5py
import matplotlib.pyplot as plt
import json
import pickle
#import argparse
import pesummary
#from pesummary.io import read
#from peutils import *
#from makewaveform import make_waveform, plot_gwtc1_waveform
#from makealtair import make_altair_plots, get_params_intersect
#from makeskymap import make_skymap
from copy import deepcopy

import matplotlib
matplotlib.use('Agg')


from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock

import make_contour_plot


def downloadData(directory):
    if exists(directory)==True:
        st.markdown('Checked data is available, getting ready to plot...')
    else: 
        address = "https://zenodo.org/api/files/d7a70f99-e16a-48a2-ae27-0b1968b0840c/contour_data.tar.gz"
        st.markdown("Downloading contours, hold on - this can take several minutes...")
        r = requests.get(address)
        file_name = 'contour_data.tar.gz'
        with open(file_name, 'wb') as f:
            f.write(r.content)

        my_tar = tarfile.open(file_name)
        my_tar.extractall('.')
        my_tar.close()
    return None


events = ['GW191103A',
          'GW191105C',
          'GW191109A',
          'GW191113B',
          'GW191126C',
          'GW191127B',
          'GW191129G',
          'GW191204A',
          'GW191204G',
          'GW191215G',
          'GW191216G',
          'GW191219E',
          'GW191222A',
          'GW191230H',
          '200105F',
          'GW200112H',
          'GW200115A',
          'GW200128C',
          'GW200129D',
          'GW200202F',
          'GW200208G',
          'GW200208K',
          'GW200209E',
          'GW200210B',
          'GW200216G',
          'GW200219D',
          'GW200220E',
          'GW200220H',
          'GW200224H',
          'GW200225B',
          'GW200302A',
          'GW200306A',
          'GW200308G',
          'GW200311L',
          'GW200316I',
          'GW200322G']


#posHighlight = ['GW191230A', 'GW191109A', 'GW191129A', \
#                 'GW200115A', '200105A', 'GW200311A']


highlightDefaults = ['GW191204_171526', \
                     'GW191219_163120', \
                     'GW200105_162426', \
                     'GW200115_042309', \
                     'GW200210_092254', \
                     'GW200220_061928', \
                     'GW200225_060421']


# get namaees
with open('O3bScripts/names.json', 'r') as nameFile:
    data = nameFile.read()
names = json.loads(data)

print('\n\n names', type(names['FULLNAME']))

eventsFullNames = [ names['FULLNAME'][e] for e in events]



st.set_page_config(page_title='GWTC-3 Contour Plots', page_icon=":crocodile:")
print(eventsFullNames)
# sidebar stuff
highlightsSelected = st.sidebar.multiselect('Event to highlight (highlighted events should also be selected in "events to be plotted" below)',
                                            eventsFullNames,
                                            default=highlightDefaults)
                                            
eventsSelected = st.sidebar.multiselect('Events to be plotted (the default is all events):', 
                                         eventsFullNames, 
                                         default = eventsFullNames)







st.title('GWTC-3 Contour Plots')


st.markdown('''
GWTC-3 is the "third gravitational wave transient catalog" from the [LIGO](https://www.ligo.org/), [Virgo](https://www.virgo-gw.eu/), and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/) (LVK) Collaborations.
[GWTC-3](https://www.ligo.org/science/Publication-O3bCatalog/) updates the previous catalogs ([GWTC-1](https://www.ligo.org/science/Publication-O2Catalog/), [GWTC-2](https://www.ligo.org/science/Publication-O3aCatalog/), [GWTC-2.1](https://www.ligo.org/science/Publication-O3aFinalCatalog/)) with merger events observed during the second part of Observing Run 3 (O3b), which lasted from the 1st November 2019 to the 27th March 2020. 

As in the [GWTC-3 paper](https://dcc.ligo.org/LIGO-P2000318/public), the gravitational-wave events included in these plots are those that have a greater than 50% probability of being real astrophysical signals. 
Identical to the paper, we include one additional event (GW200105_162426) which, despite having a lower probability of being real, is still a clear outlier from the noise background (see the paper for more information).
The plots reproduce figures 8 and 9 from the paper. 
''')




st.subheader('How to use this app')

st.markdown('''
You can customise which gravitational-wave events to plot (gray contours) and/or highlight (color contours).
Choose which events to plot and highlight in the sidebar. 
Highlighting fewer events gives the best results as the plot can get quite cluttered!

Select which parameter combination you would like to see below. 
''')


color_file = './O3bScripts/colors.pkl'
contour_dir = './contour_data'




downloadData(contour_dir)


#contour_dir = './contour_data'




# chosing the plot
plotChooseMcChiEff = 'Source chirp mass (x-axis) and effective inspiral spin (y-axis).'
plotChooseMTq      = 'Source total mass (x-axis) and mass ratio (y-axis).'
plotChooseM1M2     = 'Primary mass (x-axis) and secondary mass (y-axis).'

plotNames = [
    plotChooseM1M2,
    plotChooseMTq,
    plotChooseMcChiEff
]

def headerlabel(number):
    return "{0}".format(plotNames[number-1])

whichPlot = st.radio('What would you like to plot?', [1,2,3], format_func=headerlabel)



if whichPlot==1: #plotChooseM1M2
    var1, var2 = 'mass_1_source', 'mass_2_source'

elif whichPlot==2: #plotChooseMTq:

    var1, var2 = 'log_total_mass_source', 'log_mass_ratio'

elif whichPlot==3: #plotChooseMcChiEff: 
    var1, var2 = 'log_chirp_mass_source', 'chi_eff_infinity_only_prec_avg'

with lock:
    fig = make_contour_plot.make_plot(eventsSelected,
                                      contour_dir,  
                                      var1, var2,
                                      highlightsSelected,
                                      color_file,
                                      names)
    st.pyplot(fig)

if whichPlot ==1: 
    st.markdown('''
    **About this plot:**
Credible-region contours in the plane of primary mass and secondary mass (see definitions below). 
Each contour represents the 90% credible region for an O3b gravitational-wave candidate. 
We define the parameters so that the primary mass is greater than the secondary mass so that there are no contours inside the upper shaded region (mass ratios great than 1). The lower shaded region indicates a mass ratio less than 1/50, which was the lower prior bound on mass ratio used in the analysis. 
''')

elif whichPlot ==2: 
    st.markdown('''
**About this plot:**
Credible-region contours in the plane of total mass and mass ratio (see definitions below). 
Each contour represents the 90% credible region for an O3b gravitational-wave candidate. 
The dotted lines shows the region where both the primary (m1) and secondary (m2) masses can have a mass below 3 solar masses. We use 3 solar masses as a robust upper limit on the maximum mass of a neutron star. 
''')

elif whichPlot ==3: 
    st.markdown('''
**About this plot:**
Credible-region contours in the plane of chirp mass and effective inspiral spin (see definitions below). 
Each contour represents the 90% credible region for an O3b gravitational-wave candidate. 
The dotted line marks a zero effective inspiral spin. 
''')




st.subheader('Parameter definitions')
st.markdown('''
Here are some useful definitions and links to find out more. 

* **Solar mass**: the mass of the Sun. [Solar mass](https://astronomy.swin.edu.au/cosmos/s/solar+mass) is a common unit for representing masses in astronomy. 
* **Primary mass**: the mass of the more massive object in the binary (in solar masses). 
* **Secondary mass** the mass of the less massive object in the binary (in solar masses). 
* **Chirp mass**: a combination of the primary and secondary masses that is typically well measured by gravitational wave observations. The mathematical definition can be found [here](https://emfollow.docs.ligo.org/userguide/glossary.html#term-chirp-mass).
* **Mass ratio**: defined as the secondary mass divided by the primary mass. 
* **Total mass**: the sum of the primary and the secondary masses.
* **Effective inspiral spin**: the best-measured parameter encoding spin information in a gravitational-wave signal. It describes how much of each individual black hole's spin is rotating in the same way as the orbital rotation (e.g. if the spin and the orbit are both clockwise or anticlockwise). 

Note that we define the masses in the source reference frame.  
''')


st.subheader('Find out more')
st.markdown('''
This app uses data release products associated with GWTC-3, the third Gravitational-Wave Transient Catalog from the [LIGO Scientific Collaboration](https://www.ligo.org/), the [Virgo Collaboration](https://www.virgo-gw.eu/), and the [KAGRA Collaboration](https://gwcenter.icrr.u-tokyo.ac.jp/en/).
The contour plots produced by this app are similar to figures 8 and 9 in the [GWTC-3 paper](https://dcc.ligo.org/LIGO-P2000318/public). 
The contour data (`IGWN-GWTC3p0-v2-PEContours.tar.gz`) can be found in the [GWTC-3 Parameter Estimation Data Release](https://doi.org/10.5281/zenodo.5546662) on Zenodo.
The Zenodo page also includes two python notebooks, one of which reproduces the plots shown here and allows greater customization (GWTC3p0PEPlotContourData.ipynb) and the other contains a guide to using parameter estimation results more generally (`GWTC3p0PEDataReleaseExample.ipynb`). 

Useful links: 
* Read the [GWTC-3 catalog paper](https://dcc.ligo.org/LIGO-P2000318/public).
* Visit the [GWTC-3 data release](https://www.gw-openscience.org/GWTC-3/) at the Gravitational Wave Open Science Centre. 
* Read the [GWTC-3 science summary](https://www.ligo.org/science/Publication-O3bCatalog/index.php).
* Read [behind the scenes stories](https://www.ligo.org/magazine/LIGO-magazine-issue20.pdf#page=6) from some members of the GWTC-3 team in the [LIGO Magazine](https://www.ligo.org/magazine).
* View the code for this app at [github.com/hannahm8/gw-contour-plotter](https://github.com/hannahm8/gw-contour-plotter). 

**Acknowledgements:**
This app makes use of data from the [LIGO](https://www.ligo.org/), [Virgo](https://www.virgo-gw.eu/), and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/) Collaborations.
Thanks to the [Gravitational Wave Open Science Center](https://www.gw-openscience.org) for inspiration and guidance in creating this app. 
Check out some other gravitational-wave apps: [GW Quickview](https://gw-quickview.streamlit.app/) and [PE Viewer](http://peviewer.igwn.org/). 
''')





