import numpy as np
import pandas as pd
import ipywidgets as ipw
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
        iso_table.to_csv('./{0}/iso_all_{1}txt'.format(drct,name),sep=' ',header=None,index=False)
    
    return iso_table

def FS(min, max, step, inval, description, readout='.1f'):
    """
    Floating point slider.
    Don't update until I release the slider.
    """
    return ipw.FloatSlider(min=min, max=max, step=step, value=inval,
                           description=description, readout_format=readout,
                           continuous_update=False)


def COLUMNS(filter1,filter2):
    """
    Creates x and y axis labels for CMD. 
    """
    columns = {
        "F275W" : 2 ,
        "F336W" : 7,
        "F438W" : 12,
        "F555W" : 17,
        "F814W" : 22}
    
    column1 = columns[filter1] 
    column2 = columns[filter2]
    return column1,column2

def ISOCHRONE_COLUMNS(filter1,filter2):
    """
    Gets correct column numbers for isochrone file.
    """
    columns = {
        "F275W" : 1,
        "F336W" : 2,
        "F438W" : 3,
        "F555W" : 4,
        "F814W" : 5}
    
    column1 = columns[filter1]
    column2 = columns[filter2]
    return column1, column2


def interactive_cmd(data,iso,snr0,sharp0,round0,crowd0,dmod=29.6,
                    snrmax=10,sharpmax=1.5,roundmax=10,crowdmax=3,
                    xmin=8,xmax=8,ymin=8,ymax=8,
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
    # Widgets
    blue_drop = ipw.Dropdown(options=filters[:-1],value=filters[0],description='Blue Filter')
    red_drop = ipw.Dropdown(options=filters[1:],value=filters[1],description='Red Filter')
    filter_ui = ipw.HBox([blue_drop, red_drop])
    
    snrslide = FS(0.5, snrmax, 0.5, snr0, 'Signal/Noise')
    sharpslide = FS(0.05, sharpmax+0.005, 0.05, sharp0, 'Sharpness', '.2f')
    roundslide = FS(0.1, roundmax, 0.1, round0, 'Roundness')
    crowdslide = FS(0.1, crowdmax+0.05, 0.1, crowd0, 'Crowding')
    cutbox1 = ipw.VBox([snrslide, sharpslide])
    cutbox2 = ipw.VBox([crowdslide, roundslide])
    cut_ui = ipw.HBox([cutbox1, cutbox2])
    cut_accord = ipw.Accordion(children=[cut_ui])
    cut_accord.set_title(0, 'Cutting Parameters')
    
    zoomslide_xmin = FS(0, xmin, 0.5, 0, 'Color Min')
    zoomslide_xmax = FS(0, xmax, 0.5, 0, 'Color Max')
    zoomslide_ymin = FS(0, ymin, 0.5, 0, 'Mag Min')
    zoomslide_ymax = FS(0, ymax, 0.5, 0, 'Mag Max')
    
    #xrangeslide = ipw.FloatRangeSlider(value=[xmin,xmax], min=xmin, max=xmax, 
    #                                   step=0.1, description='X Range',
    #                                   readout_format='.1f', continuous_update=False)
    #yrangeslide = ipw.FloatRangeSlider(value=[ymin,ymax], min=ymin, max=ymax, 
    #                                   step=0.1, description='Y Range',
    #                                   readout_format='.1f', continuous_update=False)
    #zoom_ui = ipw.HBox([xrangeslide,yrangeslide])
    
    zoombox1 = ipw.VBox([zoomslide_xmin, zoomslide_xmax])
    zoombox2 = ipw.VBox([zoomslide_ymin, zoomslide_ymax])
    zoom_ui = ipw.HBox([zoombox1, zoombox2])
    zoom_accord = ipw.Accordion(children=[zoom_ui])
    zoom_accord.set_title(0, 'Change Limits')
    
    iso_button = ipw.ToggleButton(value=False,description='Isochrones')
    zoom_button = ipw.ToggleButton(value=False,description='Zoom Removed')
    button_ui = ipw.HBox([iso_button, zoom_button])
    
    all_widgets = ipw.VBox([filter_ui, cut_accord, zoom_accord, button_ui])
       
    def CMD(data,iso,distmod,filter1,filter2,
            SNR,Sharp,Round,Crowd,
            #xrange, yrange,
            zoom_xmin,zoom_xmax,zoom_ymin,zoom_ymax,
            isochrones=False,zoomRIGHT=False):
        """
        Makes CMD to interact with.
        
        SNR is Signal-to-Noise Ratio cut.
        Sharp is Sharpness squared cut.
        Round is Roundness squared cut.
        Crowd is Crowding cut.
        """
        Filter1, Filter2 = COLUMNS(filter1,filter2)
        
        grab = data[(data[Filter1] < 99.999) & (data[Filter2] < 99.999)]
        cut1 = (grab[Filter1+1]>SNR) & ((grab[Filter1+2])**2<Sharp) & ((grab[Filter1+3])**2<Round) & (grab[Filter1+4]<Crowd)
        cut2 = (grab[Filter2+1]>SNR) & ((grab[Filter2+2])**2<Sharp) & ((grab[Filter2+3])**2<Round) & (grab[Filter2+4]<Crowd)
        passed = grab[cut1 & cut2]
        notpass = grab[~grab.index.isin(passed.index)]
        passed_color = passed[Filter1] - passed[Filter2]
        notpass_color = notpass[Filter1] - notpass[Filter2]
        
        fig, ax = plt.subplots(1,2)
        fig.set_size_inches(14,7)
        
        ax[0].plot(passed_color,passed[Filter2],'o',ms=4,alpha=0.5,label='Stars')
        ax[1].plot(notpass_color,notpass[Filter2],'o',ms=4,alpha=0.5,label='Not Stars')
        
        if isochrones:
            iso10,iso20,iso30 = iso[iso[6]==10],iso[iso[6]==20],iso[iso[6]==30]
            iso40,iso50 = iso[iso[6]==40],iso[iso[6]==50]
            
            iso_filt1, iso_filt2 = ISOCHRONE_COLUMNS(filter1,filter2)
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
            
        ax[0].set_xlim(ax[0].get_xlim()[0]+zoom_xmin, ax[0].get_xlim()[1]-zoom_xmax)
        ax[0].set_ylim(ax[0].get_ylim()[0]+zoom_ymin, ax[0].get_ylim()[1]-zoom_ymax)
        
        #ax[0].set_xlim(xrange[0],xrange[1])
        #ax[0].set_ylim(yrange[0],yrange[1])

        for i in range(2):
            ax[i].invert_yaxis()
            ax[i].set_xlabel('${0}-{1}$'.format(filter1,filter2),fontsize=14)
            ax[i].set_ylabel('${0}$'.format(filter2),fontsize=14)
            ax[i].tick_params(axis='both', labelsize=13) 
        ax[0].set_title('Kept',fontsize=16)
        ax[1].set_title('Removed',fontsize=16)
        
        if zoomRIGHT:
            ax[1].set_xlim(ax[0].get_xlim()[0]-1, ax[0].get_xlim()[1]+2)
            ax[1].set_ylim(ax[0].get_ylim()[0]+1, ax[0].get_ylim()[1]-2)
            
        return 
    
    out = ipw.interactive_output(CMD, {"data":ipw.fixed(data),"iso":ipw.fixed(iso),
                                       "distmod":ipw.fixed(dmod),
                                       "filter1":blue_drop, "filter2":red_drop,
                                       "SNR":snrslide, "Sharp":sharpslide,
                                       "Round":roundslide, "Crowd":crowdslide,
                                       #"xrange":xrangeslide, "yrange":yrangeslide,
                                       "zoom_xmin":zoomslide_xmin,"zoom_xmax":zoomslide_xmax,
                                       "zoom_ymin":zoomslide_ymin,"zoom_ymax":zoomslide_ymax,
                                       "isochrones":iso_button,"zoomRIGHT":zoom_button})
    
    
    
    display(all_widgets,out)
    return
