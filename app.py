

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
import argparse
import pesummary
from pesummary.io import read
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


events = ['GW191103A', \
          'GW191105C', \
          'GW191109A', \
          'GW191113B', \
          'GW191126C', \
          'GW191127B', \
          'GW191129G', \
          'GW191204A', \
          'GW191204G', \
          'GW191215G', \
          'GW191216G', \
          'GW191219E', \
          'GW191222A', \
          'GW191230H', \
          '200105F', \
          'GW200112H', \
          'GW200115A', \
          'GW200128C', \
          'GW200129D', \
          'GW200202F', \
          'GW200208G', \
          'GW200208K', \
          'GW200209E', \
          'GW200210B', \
          'GW200216G', \
          'GW200219D', \
          'GW200220E', \
          'GW200224H', \
          'GW200225B', \
          'GW200302A', \
          'GW200306A', \
          'GW200308G', \
          'GW200311L', \
          'GW200316I', \
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

#highlightDefaults = ['GW191109_010717', \
#                     'GW191215_223052', \
#                     'GW191230_180458', \
#                     'GW200105_162426', \
#                     'GW200115_042309', \
#                     'GW200210_092254', \
#                     'GW200316_215756' ]


# get namaees
with open('O3bScripts/names.json', 'r') as nameFile:
    data = nameFile.read()
names = json.loads(data)

print('\n\n names', type(names['FULLNAME']))

eventsFullNames = [ names['FULLNAME'][e] for e in events]



# sidebar stuff
highlightsSelected = st.sidebar.multiselect('Event to highlight',
                                            eventsFullNames,
                                            default=highlightDefaults)
                                            
eventsSelected = st.sidebar.multiselect('Events to be plotted (the default is all events):', 
                                         eventsFullNames, 
                                         default = eventsFullNames)






st.title('GWTC-3 contour plotter')


st.markdown('''
**This is a work in progress!**

This app shows selected parameter estimation results for gravitational wave events observed in the second part of the [LIGO](https://www.ligo.org/), [Virgo](https://www.virgo-gw.eu/), [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/) Observing Run 3 (O3b). 

**How to use this app**

Change which events to plot and highlight in the sidebar. Highlighting fewer events gives the best results as the plot can get quite cluttered! Choose which parameter combination you would like to plot below. 

''')


color_file = './O3bScripts/colors.pkl'
contour_dir = './contour_data'


downloadData(contour_dir)


#contour_dir = './contour_data'




# chosing the plot
plotChooseMcChiEff = 'Effective inspiral spin (y-axis) against source chirp mass (x-axis)'
plotChooseMTq      = 'Mass ratio (y-axis) against total source mass (x-axis)'

plotNames = [
    plotChooseMcChiEff,
    plotChooseMTq
]

def headerlabel(number):
    return "{0}".format(plotNames[number-1])

whichPlot = st.radio('What would you like to plot?', [1,2], format_func=headerlabel)



if whichPlot==1:#plotChooseMcChiEff: 
    var1, var2 = 'log_chirp_mass_source', 'chi_eff_infinity_only_prec_avg'

elif whichPlot==2:#plotChooseMTq:

    var1, var2 = 'log_total_mass_source', 'log_mass_ratio'

# can we print the data now? 


fig = make_contour_plot.make_plot(eventsSelected,
                                  contour_dir,  
                                  var1, var2,
                                  highlightsSelected,
                                  color_file,
                                  names)
st.pyplot(fig)



st.markdown('''
**About this app**

This app produces contour plots of parameter estimation results from the third Gravitational Wave Transient Catalog (GWTC-3). 

The plots are similar to Figures 8 and 9 in the [GWTC-3 paper](https://arxiv.org/abs/2111.03606). The app uses data release material from (doi.org/10.5281/zenodo.5546662)[doi.org/10.5281/zenodo.5546662] (contour_data.tar.gz). 

View the code for this app [here](https://github.com/hannahm8/gw-contour-plotter). 
Thank you to Jonah Kanner for inspiration and guidance in creating this app. Visit Jonah Kanner's [GW Quickview app](https://share.streamlit.io/jkanner/streamlit-dataview/app.py). 
''')


#st.markdown('writing virtual file')
#virtualFile = io.BytesIO()
#virtualFile.write(r.content)

#my_tar = tarfile.open(virtualFile)
#my_tar.extractall('.')
#my_tar.close()





