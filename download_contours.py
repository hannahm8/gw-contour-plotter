

#response_API = requests.get('https://zenodo.org/api/records/5117762/files/search_data_GWTC2p1.tar.xml.gz')
#response_API = requests.get('https://zenodo.org/api/files/35914311-503b-452d-a67a-7a3587b91810/search_data_GWTC2p1.tar.xml.gz')

import streamlit as st
import requests, io
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

st.title('Contour plot testing')

st.markdown('This is a work in progress, the results and event list are not finalised.')

st.markdown('You can change which events to plot and highlight in the sidebar. Highlighting fewer events gives the best results as the plot can get quite cluttered!') 

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
eventsSelected = st.sidebar.multiselect('Events to be plotted', 
                                         eventsFullNames, 
                                         default = eventsFullNames)


highlightsSelected = st.sidebar.multiselect('Event to highlight',
                                            eventsFullNames,
                                            default=highlightDefaults)




st.markdown("Let's download contour data.")


"""
eventSelect = st.sidebar.multiselect('Which events would you like to see?',
                                     eventList,
                                     default = 'GW190403_051519')

"""


address = "https://zenodo.org/api/files/d7a70f99-e16a-48a2-ae27-0b1968b0840c/contour_data.tar.gz"

st.markdown("Downloading contours, hold on")
r = requests.get(address)

file_name = 'contour_data.tar.gz'
with open(file_name, 'wb') as f:
    f.write(r.content)

my_tar = tarfile.open(file_name)
my_tar.extractall('.')
my_tar.close()

contour_dir = './contour_data'



#st.markdown('writing virtual file')
#virtualFile = io.BytesIO()
#virtualFile.write(r.content)

#my_tar = tarfile.open(virtualFile)
#my_tar.extractall('.')
#my_tar.close()



"""
# plotting 
for ev in eventSelect: 
    
    st.markdown('Downloading data for {}. This will take a little time...'.format(ev))
    address = 'https://zenodo.org/api/files/5fbd99a3-f2aa-4d6a-9409-4f767de2730a/IGWN-GWTC2p1-v1-{}_PEDataRelease.h5'.format(ev)
    st.markdown(address)
    r = requests.get(address)

    st.markdown('writing virtual file')

    virtualFile = io.BytesIO()
    virtualFile.write(r.content)


    data = h5py.File(virtualFile)
    key0 = list(data.keys())[0]


    dataarray = data[key0]

    pedata = dataarray['posterior_samples'][()]

    paramlist = pedata.dtype.names

    m1 = pedata['mass_1_source']
    m2 = pedata['mass_2_source']
    
    st.markdown(m1)
    st.markdown(m2)
    
    fig, axs = plt.subplots(1, 2)
    axs[0].hist(m1)
    axs[0].set_xlabel('m1 source mass (solar masses)')
    axs[1].hist(m2)
    st.pyplot(fig)
    
    del(virtualFile)
    #virtualFile.close()
"""

