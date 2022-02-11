import streamlit as st
import requests, io
import json, tarfile
import h5py
import matplotlib.pyplot as plt

#response_API = requests.get('https://zenodo.org/api/records/5117762/files/search_data_GWTC2p1.tar.xml.gz')
#response_API = requests.get('https://zenodo.org/api/files/35914311-503b-452d-a67a-7a3587b91810/search_data_GWTC2p1.tar.xml.gz')




st.title('Practicing downloading data')


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

