import numpy as np
import pandas as pd
from ipywidgets import interact, fixed, FloatSlider
import matplotlib.pyplot as plt

"""
lower case functions are for use in Jupyter Notebook.
UPPER CASE functions are for internal use.
"""

def make_one_iso(nfilts=5,filters=['F275Wmag1','F336Wmag','F438Wmag','F555Wmag','F814Wmag'],
               drct='isochrones/ngc3344',name='solar',save=False):
    """
    Makes single file isochrone to give interactive_cmd.
    
    Each input isochrone file must be named in the following format: iso_<name>_<age>.txt (Padova gives stupidly unhelpful names)
    Padova gives isochrones with lots of info at top of isochrone files, ok to keep as long as it has '#' in front. 
    Remove the '#' from before the column names or make the filters the column numbers (integers not strings).
    
    nfilters is the number of filters you are giving.
    """
    iso_table = pd.DataFrame(columns=np.arange(0,nfilts+2))
    
    for age in [10,20,30,40,50]:
        data = []
        iso = pd.read_csv('./{0}/iso_{1}_{2}.txt'.format(drct,name,age),delim_whitespace=True,comment='#')
        grab = iso[iso["Mini"]>4].reset_index(drop=True)
        data += [grab['Mini']]
        for filt in filters:
            data += [grab[filt]]
        data += [np.ones(len(grab)) * age]
        tmp = pd.DataFrame(data=data).T
        iso_table.append(tmp,ignore_index=True)
        
    iso_table.round(3)
    
    if save:
        iso_table.to_csv('./{0}/iso_{1}_all.txt'.format(drct,name),sep=' ',header=None,index=False)
    
    return iso_table

def FS(min, max, step, inval):
    """
    Don't update plot until I release the slider
    """
    return FloatSlider(min=min, max=max, step=step, value=inval, continuous_update=False)

def LABELS(filter1,filter2):
    """
    Creates x and y axis labels for CMD. 
    """
    labels = {
        2 : "F275W",
        7 : "F336W",
        12 : "F438W",
        17 : "F555W",
        22 : "F814W"}
    
    label1 = labels[filter1]
    label2 = labels[filter2]
    color = label1 + "-" + label2 
    return color,label2

def ISOCHRONE_COLUMNS(filter1,filter2):
    """
    Gets correct column numbers for isochrone file.
    """
    columns = {
        2 : 1,
        7 : 2,
        12 : 3,
        17 : 4,
        22 : 5}
    
    column1 = columns[filter1]
    column2 = columns[filter2]
    return column1, column2
    
def interactive_cmd(data,iso,snr0,sharp0,round0,crowd0,dmod=29.6,
                    snrmax=10,sharpmax=1.5,roundmax=10,crowdmax=3,
                    filters=['F275W','F336W','F438W','F555W','F814W']):
    """
    Makes interactive CMD for NGC 3344 Data.
    
    isos is output from make_one_iso
    Format: Mass | Filter 1 | ... | Filter 5 | Age 
    
    snr0 is initial Signal-to-Noise Ratio cut.
    sharp0 is intial Sharpness squared cut.
    round0 is initial Roundness squared cut.
    crowd0 is intial Crowding cut.
    """
    def CMD(data,iso,distmod,Filter1,Filter2,SNR,Sharp,Round,Crowd,
            isochrones=False,zoomLEFT=False,zoomRIGHT=False):
        """
        Makes CMD to interact with.
        
        SNR is Signal-to-Noise Ratio cut.
        Sharp is Sharpness squared cut.
        Round is Roundness squared cut.
        Crowd is Crowding cut.
        """
        grab = data[(data[Filter1] < 99.999) & (data[Filter2] < 99.999)]
        cut1 = (grab[Filter1+1]>SNR) & ((grab[Filter1+2])**2<Sharp) & ((grab[Filter1+3])**2<Round) & (grab[Filter1+4]<Crowd)
        cut2 = (grab[Filter2+1]>SNR) & ((grab[Filter2+2])**2<Sharp) & ((grab[Filter2+3])**2<Round) & (grab[Filter2+4]<Crowd)
        passed = grab[cut1 & cut2]
        notpass = grab[~grab.index.isin(passed.index)]
        passed_color = passed[Filter1] - passed[Filter2]
        notpass_color = notpass[Filter1] - notpass[Filter2]
        
        fig, ax = plt.subplots(1,2)
        fig.set_size_inches(14,7)
        xlabel, ylabel = LABELS(Filter1,Filter2)
        for i in range(2):
            ax[i].invert_yaxis()
            ax[i].set_xlabel('{0}'.format(xlabel),fontsize=14)
            ax[i].set_ylabel('{0}'.format(ylabel),fontsize=14)
        ax[0].set_title('Kept',fontsize=15)
        ax[1].set_title('Removed',fontsize=15)
        
        ax[0].plot(passed_color,passed[Filter2],'o',ms=4,alpha=0.5,label='Stars')
        ax[1].plot(notpass_color,notpass[Filter2],'o',ms=4,alpha=0.5,label='Not Stars')
        
        if isochrones:
            iso10,iso20,iso30 = iso[iso[6]==10],iso[iso[6]==20],iso[iso[6]==30]
            iso40,iso50 = iso[iso[6]==40],iso[iso[6]==50]
            
            iso_filt1, iso_filt2 = ISOCHRONE_COLUMNS(Filter1,Filter2)
            iso_color10 = iso10[iso_filt1] - iso10[iso_filt2]
            iso_color20 = iso20[iso_filt1] - iso20[iso_filt2]
            iso_color30 = iso30[iso_filt1] - iso30[iso_filt2]
            iso_color40 = iso40[iso_filt1] - iso40[iso_filt2]
            iso_color50 = iso50[iso_filt1] - iso50[iso_filt2]
            
            for i in range(2):
                ax[i].plot(iso_color10,iso10[iso_filt2]+distmod,'-',c='b',lw=2,label='10 Myr')
                ax[i].plot(iso_color20,iso20[iso_filt2]+distmod,'-',c='#89fe05',lw=2,label='20 Myr')
                ax[i].plot(iso_color30,iso30[iso_filt2]+distmod,'-',c='k',lw=2,label='30 Myr')
                ax[i].plot(iso_color40,iso40[iso_filt2]+distmod,'-',c='#dbb40c',lw=2,label='40 Myr')
                ax[i].plot(iso_color50,iso50[iso_filt2]+distmod,'-',c='r',lw=2,label='50 Myr')
            ax[1].legend(loc=0)
 
        if zoomLEFT:
            ax[0].set_ylim(ax[0].get_ylim()[0]-4,ax[0].get_ylim()[1])
        if zoomRIGHT:
            ax[1].set_ylim(ax[0].get_ylim()[0]+1,ax[0].get_ylim()[1]-2)
            ax[1].set_xlim(ax[0].get_xlim()[0]-1,ax[0].get_xlim()[1]+2)
            
        return 
    
    return interact(CMD, data=fixed(data), iso=fixed(iso), distmod=fixed(dmod),
                    Filter1=[(filters[0], 2), (filters[1], 7), (filters[2], 12), (filters[3], 17)],
                    Filter2=[(filters[1], 7), (filters[2], 12), (filters[3], 17), (filters[4], 22)],
                    SNR=FS(0.5, snrmax, 0.5, snr0),Sharp=FS(0.05, sharpmax, 0.05, sharp0),
                    Round=FS(0.05, roundmax, 0.05, round0),Crowd=FS(0.1, crowdmax, 0.1, crowd0),
                    isochrones=False, zoomLEFT=False,zoomRIGHT=False)
