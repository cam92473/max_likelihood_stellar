import numpy as np
import scipy.optimize as opt
import pandas as pd

class ChiSquared():
    def __init__(self):
        self.filenamevar = ""
        self.file2namevar= ""
        self.chosenstar = "     1-cluster fit     "
        self.checked3set = 0
        self.checker1set = 1
        self.checker2set = 1
        self.checker3set = 1
        self.checker4set = 1
        self.sliderval1set = 0
        self.bestnameset = "best_params.csv"
        self.avgnameset = "avg_params.csv"
        self.imgnameset = "plot_so_rowX.png"
        self.rownumberset = ""
        self.sliderstring1set = "log-log axes"

        while True:
            self.switch = False
            self.intro_gui()
            self.extract_measured_flux()
            self.extract_sourceids()
            self.convert_to_AB()
            self.convert_to_bandflux()
            self.import_param_vals()
            self.prepare_for_interpolation()
            self.minimize_chisq()
            self.save_output()
            self.display_all_results()

    
    def intro_gui(self):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        mwin = tk.Tk()
        mwin.geometry("830x550+600+200")
        mwin.title("Maximum Likelihood Fitting -- Stellar")
        mwin.config(bg='wheat1')
        mwin.resizable(0,0)

        def collectfilename():
            from tkinter import messagebox
            if user_filename.get() == "":
                tk.messagebox.showinfo('Error', 'Please enter a filename.')
                return None
            elif user_file2name.get() == "":
                tk.messagebox.showinfo('Error', 'Please enter a filename.')
                return None

            if "," in user_rownumber.get():
                        rowlist = user_rownumber.get().split(',')
                        for elem in rowlist:
                            try:
                                rowint = int(elem)
                            except:
                                tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                                return None
                            else:
                                introwlist = [int(i) for i in rowlist]
                                lowestelem = introwlist[0]
                                highestelem = introwlist[-1]

            elif ":" in user_rownumber.get():
                rowlist = user_rownumber.get().split(':')
                for elem in rowlist:
                    try:
                        rowint = int(elem)
                    except:
                        tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                        return None
                    else:
                        import numpy as np
                        introwlist = np.arange(int(rowlist[0]),int(rowlist[-1])+1).tolist()
                        lowestelem = introwlist[0]
                        highestelem = introwlist[-1]
            else:
                try:
                    rowint = int(user_rownumber.get())
                except:
                    tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                    return None
                else:
                    introwlist = [rowint]
                    lowestelem = rowint
                    highestelem = rowint

            try:
                import pandas as pd
                self.measuredata = pd.read_csv("{}".format(user_filename.get(),delimiter=","))
                self.filenamevar = user_filename.get()
            except:
                tk.messagebox.showinfo('Error', "Could not find input file for measured fluxes. Please place the file in the program folder and try again.")
                return None
            try:
                import pandas as pd
                self.disc_params = pd.read_csv("{}".format(user_file2name.get(),delimiter=","))
                if starno_chosen.get() == "     1-cluster fit     ":
                    if "log(Z)" not in self.disc_params:
                        tk.messagebox.showinfo('Error', "Please make sure the parameters file has the correct columns for the fitting method you are trying to use.")
                        return None
                if starno_chosen.get() == "     2-cluster fit     ":
                    if "log(Z_hot)" not in self.disc_params:
                        tk.messagebox.showinfo('Error', "Please make sure the parameters file has the correct columns for the fitting method you are trying to use.")
                        return None

                self.file2namevar = user_file2name.get()

            except:
                tk.messagebox.showinfo('Error', "Could not find input file for discrete parameters. Please place the file in the program folder and try again.")
                return None
            else:
                if highestelem > len(self.measuredata)+1 or lowestelem < 2:
                    tk.messagebox.showinfo('Error', "Rows specified are out of range.")
                    return None
                if (checker2.get() == 1 and bestname.get()[-4:] != ".csv") or (checker3.get() == 1 and avgname.get()[-4:] != ".csv"):
                    tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .csv extension.")
                    return None
                elif checker4.get() == 1 and (imgname.get()[-4:] != ".png" and imgname.get()[-4:] != ".jpg"):
                    tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .png or .jpg extensions.")
                    return None
                else:
                    try:
                        a = int(bestname.get()[0])
                        b = int(avgname.get()[0])
                        c = int(imgname.get()[0])
                        return None
                    except:
                        try:
                            self.rows = [i-2 for i in introwlist]
                            self.rownumberset = user_rownumber.get()
                            self.dispresults = checker1.get()
                            self.bestchiparams = checker2.get()
                            self.avgchiparams = checker3.get()
                            self.saveplots = checker4.get()
                            self.plotscale = currentsliderval1.get()
                            self.checker1set = checker1.get()
                            self.checker2set = checker2.get()
                            self.checker3set = checker3.get()
                            self.checker4set = checker4.get()
                            self.sliderval1set = currentsliderval1.get()
                            self.sliderstring1set = sliderstring1.get()


                            if checker2.get() == 1:
                                self.bestfilename = bestname.get()
                            if checker3.get() == 1:
                                self.avgfilename = avgname.get()
                            if checker4.get() == 1:
                                self.imgfilename = imgname.get()
                            
                            self.single_cluster = False
                            self.double_cluster = False
                            self.chosenstar = starno_chosen.get()
                            if self.chosenstar == "     1-cluster fit     ":
                                self.single_cluster = True

                            elif self.chosenstar == "     2-cluster fit     ":
                                self.double_cluster = True
                        except:
                                tk.messagebox.showinfo('Error', "One or more parameters seem to have been entered incorrectly. Please reenter the values and try again.")
                                return None
                        else:
                            self.switch = True
                            mwin.destroy()
        
        def openrows3():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help", "One of the components of the model flux is an interpolation term that performs a 2-D interpolation inside a grid whose axes are Z and log(age)/10. The term accepts a coordinate (Z, log(age)/10) and returns a flux for every filter, subsequently to be used in calcuating the model flux. One property of the data grid of fluxes is left as a choice to the user: its resolution. The program actually contains two grids which the user can choose between. The finer grid is a 13 X 19 grid, and the coarser grid is a 10 X 16 grid, whose ranges in Z and log(age)/10 are roughly the same. The coarser grid was introduced to prevent the optimizer from getting stuck (as it tends to when performing 2-cluster fits). The lower resolution of the grid seems to help remove any local dips in the fluxes, and makes the 2-D landscape more monotonic.")

        user_rownumber = tk.StringVar()
        user_rownumber.set(self.rownumberset)
        enterrownumberpack = tk.Frame(mwin)
        enterrownumberpack.place(x=37,y=195)
        enterrownumber = tk.Entry(enterrownumberpack,textvariable=user_rownumber,width=12)
        enterrownumber.pack(ipady=3)
        labelwhich = tk.Label(mwin,text="Read rows", bg="wheat1")
        labelwhich.place(x=39,y=165)
        def openrows():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help","  •  Use csv row labelling (which should start at row 2)\n\n  •  Specify multiple rows with commas: 2,5,6\n\n  •  Specify a selection of rows with a colon: 3:8")
        whichbutton = tk.Button(mwin,text="?",font=("TimesNewRoman 8"),command = openrows)
        whichbutton.place(x=117,y=196)
        canvas2 = tk.Canvas(mwin,relief=tk.RIDGE,bd=2,width=330,height=380,bg='wheat2')
        canvas2.place(x=310,y=150)
        starno_chosen = tk.StringVar()
        
        gobutton = tk.Button(mwin,text="Fit data",font=("Arial",10),command = collectfilename,pady=10,padx=25,bd=2)
        gobutton.place(x=680,y=170)
        checker1 = tk.IntVar()
        checker1.set(self.checker1set)
        checker2 = tk.IntVar()
        checker2.set(self.checker2set)
        checker3 = tk.IntVar()
        checker3.set(self.checker3set)
        checker4 = tk.IntVar()
        checker4.set(self.checker4set)
        sliderstring1 = tk.StringVar()
        currentsliderval1 = tk.IntVar()
        currentsliderval1.set(self.sliderval1set)
        bestname = tk.StringVar()
        bestname.set(self.bestnameset)
        avgname = tk.StringVar()
        avgname.set(self.avgnameset)
        imgname = tk.StringVar()
        imgname.set(self.imgnameset)
        sliderstring1.set(self.sliderstring1set)
        def changesliderstring1(useless):
            if currentsliderval1.get() == 1:
                sliderstring1.set(" linear axes  ")
            elif currentsliderval1.get() == 0:
                sliderstring1.set("log-log axes")
        
        def grent1():
            if plotslider1['state'] == tk.NORMAL:
                plotslider1['state'] = tk.DISABLED
                sliderstring1.set("                     ")
                sliderlabel1.config(bg="gray95")
            elif plotslider1['state'] == tk.DISABLED:
                plotslider1['state'] = tk.NORMAL
                sliderlabel1.config(bg="white")
                if currentsliderval1.get() == 1:
                    sliderstring1.set(" linear axes  ")
                elif currentsliderval1.get() == 0:
                    sliderstring1.set("log-log axes")

        def grent2():
            if buttentry2['state'] == tk.NORMAL:
                buttentry2.delete(0,30)
                buttentry2['state'] = tk.DISABLED
            elif buttentry2['state'] == tk.DISABLED:
                buttentry2['state'] = tk.NORMAL
                buttentry2.insert(tk.END,"{}".format(self.bestnameset))
        def grent3():
            if buttentry3['state'] == tk.NORMAL:
                buttentry3.delete(0,30)
                buttentry3['state'] = tk.DISABLED
            elif buttentry3['state'] == tk.DISABLED:
                buttentry3['state'] = tk.NORMAL
                buttentry3.insert(tk.END,"{}".format(self.avgnameset))
        def grent4():
            if buttentry4['state'] == tk.NORMAL:
                buttentry4.delete(0,30)
                buttentry4['state'] = tk.DISABLED
            elif buttentry4['state'] == tk.DISABLED:
                buttentry4['state'] = tk.NORMAL
                buttentry4.insert(tk.END,"{}".format(self.imgnameset))
                
        checkbutt1 = tk.Checkbutton(mwin,text="Display results",variable=checker1,command=grent1,bg='wheat2')
        plotslider1 = tk.Scale(mwin,from_=0,to=1,orient=tk.HORIZONTAL,showvalue=0,length=65,width=25,variable=currentsliderval1, command=changesliderstring1)
        plotslider1.place(x=500,y=200)
        grayframe1= tk.Frame(mwin,bg="gray95",bd=3)
        grayframe1.place(x=350,y=200)
        sliderlabel1 = tk.Label(grayframe1,textvariable=sliderstring1,padx=5,bg='white')
        sliderlabel1.pack()
        if currentsliderval1.get() == 0:
            plotslider1.set(0)
        if currentsliderval1 == 1:
            plotslider1.set(1)
        checkbutt2 = tk.Checkbutton(mwin,text="Save best-fit parameter data",variable=checker2,command=grent2,bg='wheat2')
        checkbutt3 = tk.Checkbutton(mwin,text="Save averages, variances, and other info",variable=checker3,command=grent3,bg='wheat2')
        checkbutt4 = tk.Checkbutton(mwin,text="Save plot images (1 per source X)",variable=checker4,command=grent4,bg='wheat2')
        buttentry2 = tk.Entry(mwin, textvariable = bestname,width=26)
        buttentry3 = tk.Entry(mwin, textvariable = avgname,width=26)
        buttentry4 = tk.Entry(mwin,textvariable = imgname,width=26)
        if checker2.get() == 0:
            buttentry2['state'] = tk.DISABLED
        if checker3.get() == 0:
            buttentry3['state'] = tk.DISABLED
        if checker4.get() == 0:
            buttentry4['state'] = tk.DISABLED
        checkbutt1.place(x=340,y=170)
        checkbutt2.place(x=340,y=270)
        checkbutt3.place(x=340,y=365)
        checkbutt4.place(x=340,y=460)
        buttentry2.place(x=345,y=300)
        buttentry3.place(x=345,y=395)
        buttentry4.place(x=345,y=490)

        starlabel = tk.Label(mwin,text="Fitting method",bg="wheat1").place(x=38,y=460)
        starno_chosen.set(self.chosenstar)
        staroptions = ["     1-cluster fit     ","     2-cluster fit     "]
        starmenu = tk.OptionMenu(mwin,starno_chosen,*staroptions)
        starmenu.place(x=32,y=490)

        user_filename = tk.StringVar()
        user_filename.set(self.filenamevar)
        enterfilename = tk.Entry(mwin,textvariable = user_filename,width=72)
        enterfilename.place(x=224,y=34)
        user_file2name = tk.StringVar()
        user_file2name.set(self.file2namevar)
        enterfile2name = tk.Entry(mwin,textvariable = user_file2name,width=57)
        enterfile2name.place(x=347,y=93)
        labeltop = tk.Label(mwin,text="Input measured flux file: ", bg='white',border=2,relief=tk.RIDGE,padx=6,pady=5)
        labeltop.place(x=35,y=29)
        labelbot = tk.Label(mwin,text="Input non-theta_r^2 parameter values file: ", bg='white',border=2,relief=tk.RIDGE,padx=6,pady=5)
        labelbot.place(x=35,y=89)
        grent2()
        grent2()
        grent3()
        grent3()
        grent4()
        grent4()
        mwin.mainloop()

    def extract_measured_flux(self):

        assert self.switch == True, "Program terminated"
        
        import pandas as pd
        import numpy as np
        import tkinter as tk
        
        raw_columns = ["F148W_AB","F148W_err","F169M_AB","F169M_err","F172M_AB","F172M_err","N219M_AB","N219M_err","N279N_AB","N279N_err","f275w_vega","f275w_err","f336w_vega","f336w_err","f475w_vega","f475w_err","f814w_vega","f814w_err","f110w_vega","f110w_err","f160w_vega","f160w_err"]

        self.raw_magnitudes_frame = pd.DataFrame()
        for rawname in raw_columns:
            self.raw_magnitudes_frame["{}".format(rawname)] = ""

        savebadcols = []
        for rowno in self.rows:
            curr_rowdict = {}
            for colname in raw_columns:
                try:
                    curr_rowdict[colname] = self.measuredata.at[rowno,colname].item()
                except:
                    curr_rowdict[colname] = -999
                    savebadcols.append(colname)
            self.raw_magnitudes_frame.loc[self.raw_magnitudes_frame.shape[0]] = curr_rowdict

        savebadcols = list(dict.fromkeys(savebadcols))
        badstr = ""
        for badcol in savebadcols:
            badstr += "{} or ".format(badcol)
        badstr = badstr[:-4]

        if len(badstr) != 0:
            import tkinter as tk
            miniwin = tk.Tk()
            miniwin.geometry("10x10+800+500")
            response = tk.messagebox.askquestion('Warning',"No entries found for {}. Do you wish to proceed?\n\n(These filters will not be fitted. If a single column is missing without its error or vice versa, you should double check the file for naming typos)".format(badstr))
            if response == "yes":
                miniwin.destroy()
            if response == "no":
                assert response == "yes", "Program terminated"

        for rowind,row in self.raw_magnitudes_frame.iterrows():
            for colind,colelement in enumerate(row):
                if colelement == -999:
                    self.raw_magnitudes_frame.iat[rowind,colind] = np.nan

    
    def extract_sourceids(self):
        self.source_ids = []
        for rowno in self.rows:
            self.source_ids.append(self.measuredata['Source_ID'][rowno])
        
    def convert_to_AB(self):
        self.ab_magnitudes_frame = self.raw_magnitudes_frame
        for col in self.ab_magnitudes_frame:
                if col == "f275w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.496))
                elif col == "f336w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.188))
                elif col == "f475w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - 0.091)
                elif col == "f814w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.427))
                elif col == "f110w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.7595))
                elif col == "f160w_vega":
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.2514))
        
        self.ab_magnitudes_frame.rename(columns={"f275w_vega" : "f275w_AB", "f336w_vega" : "f336w_AB", "f475w_vega" : "f475w_AB", "f814w_vega" : "f814w_AB", "f110w_vega" : "f110w_AB", "f160w_vega" : "f160w_AB"},inplace=True)
    
    def convert_to_bandflux(self):

        self.filternames = ["F148W","F169M","F172M","N219M","N279N","f275w","f336w","f475w","f814w","f110w","f160w"]
        self.bandfluxes = pd.DataFrame()
        self.bandfluxerrors = pd.DataFrame()
        self.avgwvlist = [148.1,160.8,171.7,219.6,279.2,270.4,335.5,477.3,802.4,1153.4,1536.9]
        #self.avgwvlist = [150.2491,161.4697,170.856,199.1508,276.0,267.884375,336.8484,476.0,833.0,1096.7245,1522.1981]
        #self.allextinct = [5.52548923, 5.17258596, 5.0540947, 5.83766858, 3.49917568, 3.25288368, 1.95999799, 0.62151591, -1.44589933, -2.10914243, -2.51310314]
        self.allextinct = [ 5.62427152,  5.18640888,  5.04926289,  6.99406125,  3.15901211,  3.42340971, 1.97787612,  0.61008783, -1.33280758, -2.18810981, -2.52165626]

        for colind,col in enumerate(self.ab_magnitudes_frame):
            if colind%2 == 0:
                self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: (10**(-0.4*(48.60+x)))*10**26)
                self.bandfluxes["{}".format(col)] = self.ab_magnitudes_frame[col]
            elif colind%2 != 0:
                for rowind in range(len(self.ab_magnitudes_frame[col])):
                    self.ab_magnitudes_frame.iloc[rowind,colind] = self.ab_magnitudes_frame.iloc[rowind,colind-1]*self.ab_magnitudes_frame.iloc[rowind,colind]/1.0857
                self.bandfluxerrors["{}".format(col)] = self.ab_magnitudes_frame[col]
        

    def import_param_vals(self):
        import pandas as pd

        if self.single_cluster == True:

            raw_columns = ["log(g)","T/10000","log(Z)","E(B-V)"]

            self.refined_param_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.refined_param_frame["{}".format(rawname)] = ""

            for rowno in range(len(self.disc_params.axes[0])):
                curr_rowdict = {}
                for colname in raw_columns:
                    curr_rowdict[colname] = self.disc_params.at[rowno,colname].item()
                self.refined_param_frame.loc[self.refined_param_frame.shape[0]] = curr_rowdict

        if self.double_cluster == True:

            raw_columns = ["log(g_hot)","T_hot/10000","log(Z_hot)","E(B-V)_hot","T_cool/10000","E(B-V)_cool"]

            self.refined_param_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.refined_param_frame["{}".format(rawname)] = ""

            for rowno in range(len(self.disc_params.axes[0])):
                curr_rowdict = {}
                for colname in raw_columns:
                    curr_rowdict[colname] = self.disc_params.at[rowno,colname].item()
                self.refined_param_frame.loc[self.refined_param_frame.shape[0]] = curr_rowdict

        
        print(self.refined_param_frame)
        
    def prepare_for_interpolation(self):
        import xarray as xr
        import numpy as np
        ds_disk = xr.open_dataset("saved_on_disk.nc")
        self.da = ds_disk.to_array()

    def interpolate(self,g,T,Z,valid_filters_this_row):
        interpolist = []
        interpolated = self.da.interp(Abundance = Z, Temperature = T, Log_of_surface_gravity = g)
        for valid_filter in valid_filters_this_row:
            interpolist.append(interpolated.sel(Filter = valid_filter).data.item()*10**8*(self.avgwvlist[valid_filter]*10**-7)**2/(2.998*10**10)*10**26)
        return interpolist
    
    def extinction(self,valid_filters_this_row):
        extinctlist = []
        for valid_filter in valid_filters_this_row:
            extinctlist.append(self.allextinct[valid_filter])
        return extinctlist

    def minichisqfunc_single(self,tup,valid_filters_this_row):
        g, T, Z, theta_r_sq, E_bv = tup
      
        best_models = []
        interpolist = self.interpolate(g,10000*T,Z,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            best_models.append(interpolist[i]*(theta_r_sq*1e-24)*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))
        
        return best_models

    def minichisqfunc_double(self,tup,valid_filters_this_row):
        g1, T1, Z1, theta_r1_sq, E_bv1, T2, theta_r2_sq, E_bv2 = tup
      
        bestmodels1 = []
        interpolist1 = self.interpolate(g1,10000*T1,Z1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels1.append(interpolist1[i]*(theta_r1_sq*1e-24)*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        bestmodels2 = []
        interpolist2 = self.interpolate(2.5,10000*T2,-1.5,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels2.append(interpolist2[i]*(theta_r2_sq*1e-24)*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))
        
        return bestmodels1,bestmodels2


    def chisqfunc(self,g,T,Z,theta_r_sq,E_bv,valid_filters_this_row,curr_row):
        print("Testing row {} with g1, T1, Z1, theta_r1_sq, E_bv1: ".format(self.rows[curr_row]+2), g,T,Z,theta_r_sq,E_bv)

        models = []
        interpolist = self.interpolate(g,10000*T,Z,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(interpolist[i]*(theta_r_sq*1e-24)*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")

        return chisq

    def Tf(self,g,T,Z,E_bv,valid_filters_this_row,curr_row):

        models = []
        interpolist = self.interpolate(g,10000*T,Z,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(interpolist[i]*1e-24*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf = sum(summands)

        return Tf


    def Tm(self,g,T,Z,E_bv,valid_filters_this_row,curr_row):
        
        models = []
        interpolist = self.interpolate(g,10000*T,Z,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(interpolist[i]*1e-24*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((models[i]/(self.bandfluxerrors.iat[curr_row,valid_ind]))**2)

        Tm = sum(summands)

        return Tm

    def chisqfunc2(self,g1,T1,Z1,theta_r1_sq,E_bv1,T2,theta_r2_sq,E_bv2,valid_filters_this_row,curr_row):
        print("Testing row {} with g1, T1, Z1, theta_r1_sq, E_bv1, T2, theta_r2_sq, E_bv2: ".format(self.rows[curr_row]+2), g1, T1, Z1, theta_r1_sq, E_bv1, T2, theta_r2_sq, E_bv2)

        models1 = []
        interpolist1 = self.interpolate(g1,T1*10000,Z1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(theta_r1_sq*1e-24)*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        models2 = []
        interpolist2 = self.interpolate(2.5,T2*10000,-1.5,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(theta_r2_sq*1e-24)*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i] - models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")
        return chisq

    def Tf1(self,g1,T1,Z1,E_bv1,valid_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(g1,T1*10000,Z1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*1e-24*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models1[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf1 = sum(summands)
        return Tf1

    def Tf2(self,T2,E_bv2,valid_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(2.5,T2*10000,-1.5,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*1e-24*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf2 = sum(summands)
        return Tf2

    def Tm11(self,g1,T1,Z1,E_bv1,valid_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(g1,T1*10000,Z1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*1e-24*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((models1[i]/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm11 = sum(summands)
        return Tm11

    def Tm12(self,g1,T1,Z1,E_bv1,T2,E_bv2,valid_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(g1,T1*10000,Z1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*1e-24*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        
        models2 = []
        interpolist2 = self.interpolate(2.5,T2*10000,-1.5,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*1e-24*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))


        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((models1[i]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm12 = sum(summands)
        return Tm12

    def Tm22(self,T2,E_bv2,valid_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(2.5,T2*10000,-1.5,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*1e-24*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            summands.append((models2[i]/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm22 = sum(summands)
        return Tm22

    def minimize_chisq(self):
        import numpy as np
        
        if self.single_cluster == True:
            self.bestthetas = []
            self.bestcoords = []
            self.bestchisqs = []
            self.avglist = []
            self.varilist = []
            self.errlist = []

            for curr_row in range(self.bandfluxes.shape[0]):

                print("\n\n ********************* WORKING ON ROW {} ********************* \n\n".format(self.rows[curr_row]+2))

                valid_filters_this_row = []
                for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                    if np.isnan(bflux) == False:
                        valid_filters_this_row.append(valid_ind)

                Tfsthisrow = []
                Tmsthisrow = []
                thetasthisrow = []
                coordinatesthisrow = []
                chisqsthisrow = []
                for g in self.refined_param_frame['log(g)']:
                    for T in self.refined_param_frame['T/10000']:
                        for Z in self.refined_param_frame['log(Z)']:
                            for E_bv in self.refined_param_frame['E(B-V)']:
                                print("------------------------------------------\n")
                                coord = [g,T,Z,E_bv]
                                print("COORD \n",coord)
                                coordinatesthisrow.append(coord)
                                Tfthiscoord = self.Tf(g,T,Z,E_bv,valid_filters_this_row,curr_row)
                                print("TF \n",Tfthiscoord)
                                Tfsthisrow.append(Tfthiscoord)
                                Tmthiscoord = self.Tm(g,T,Z,E_bv,valid_filters_this_row,curr_row)
                                print("TM \n",Tmthiscoord)
                                Tmsthisrow.append(Tmthiscoord)
                                thetathiscoord = Tfthiscoord/Tmthiscoord
                                print("theta_sq \n",thetathiscoord)
                                thetasthisrow.append(thetathiscoord)
                                chisqthiscoord = self.chisqfunc(coord[0],coord[1],coord[2],thetathiscoord,coord[3],valid_filters_this_row,curr_row)
                                print("CHISQ \n",chisqthiscoord)
                                chisqsthisrow.append(chisqthiscoord)
                

                print("CHISTHISROW \n",chisqsthisrow)
                print("BEST INDEX \n",chisqsthisrow.index(min(chisqsthisrow)))
                self.bestchisqs.append(chisqsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST CHIs \n",self.bestchisqs)
                print("msthisrow \n",thetasthisrow)
                self.bestthetas.append(thetasthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST THETAs \n",self.bestthetas)
                self.bestcoords.append(coordinatesthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("coordsthisrow \n",coordinatesthisrow)
                print("BEST Coords \n", self.bestcoords)

                import math

                g_numer_addends = []
                T_numer_addends = []
                Z_numer_addends = []
                theta_numer_addends = []
                E_bv_numer_addends = []
                denom_addends = []
                norm_chisqs = []
                norm_chisqs = [chisq-self.bestchisqs[curr_row] for chisq in chisqsthisrow]
                print("NORM CHISQS \n", norm_chisqs)
                print("\n------------- CALCULATING AVERAGES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,theta in zip(norm_chisqs,coordinatesthisrow,thetasthisrow):
                    print("CHISQ, COORD, THETA \n", chisq,coord,theta)
                    g_numer_addends.append(math.e**(-chisq/2)*coord[0])
                    T_numer_addends.append(math.e**(-chisq/2)*coord[1])
                    Z_numer_addends.append(math.e**(-chisq/2)*coord[2])
                    theta_numer_addends.append(math.e**(-chisq/2)*theta)
                    E_bv_numer_addends.append(math.e**(-chisq/2)*coord[3])
                    denom_addends.append(math.e**(-chisq/2))
                    print("g NUMERATOR = e^(-chisq/2)*g \n", g_numer_addends)
                    print("T NUMERATOR = e^(-chisq/2)*T \n", T_numer_addends)
                    print("Z NUMERATOR = e^(-chisq/2)*Z \n", Z_numer_addends)
                    print("theta NUMERATOR = e^(-chisq/2)*theta \n", theta_numer_addends)
                    print("E_BV NUMERATOR = e^(-chisq/2)*E_bv \n", E_bv_numer_addends)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)
                g_avg = sum(g_numer_addends)/sum(denom_addends)
                T_avg = sum(T_numer_addends)/sum(denom_addends)
                Z_avg = sum(Z_numer_addends)/sum(denom_addends)
                theta_avg = sum(theta_numer_addends)/sum(denom_addends)
                E_bv_avg = sum(E_bv_numer_addends)/sum(denom_addends)

                print("Averages for this row: \n",g_avg,T_avg,Z_avg,theta_avg,E_bv_avg)

                g_numer_addends2 = []
                T_numer_addends2 = []
                Z_numer_addends2 = []
                theta_numer_addends2 = []
                E_bv_numer_addends2 = []
                denom_addends2 = []
                print("\n------------- CALCULATING VARIANCES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,theta in zip(norm_chisqs,coordinatesthisrow,thetasthisrow):
                    print("CHISQ, COORD, theta \n", chisq,coord,theta)
                    g_numer_addends2.append(math.e**(-chisq/2)*(coord[0]-g_avg)**2)
                    T_numer_addends2.append(math.e**(-chisq/2)*(coord[1]-T_avg)**2)
                    Z_numer_addends2.append(math.e**(-chisq/2)*(coord[2]-Z_avg)**2)
                    theta_numer_addends2.append(math.e**(-chisq/2)*(theta-theta_avg)**2)
                    E_bv_numer_addends2.append(math.e**(-chisq/2)*(coord[3]-E_bv_avg)**2)
                    denom_addends2.append(math.e**(-chisq/2))
                    print("g NUMERATOR = e^(-chisq/2)*(g-gavg)^2 \n", g_numer_addends2)
                    print("T NUMERATOR = e^(-chisq/2)*(T-Tavg)^2 \n", T_numer_addends2)
                    print("Z NUMERATOR = e^(-chisq/2)*(Z-Zavg)^2 \n", Z_numer_addends2)
                    print("theta NUMERATOR = e^(-chisq/2)*(theta-thetaavg)^2 \n", theta_numer_addends2)
                    print("E_BV NUMERATOR = e^(-chisq/2)*(E_bv-E_bvavg)^2 \n", E_bv_numer_addends2)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends2)
                g_vari = sum(g_numer_addends2)/sum(denom_addends2)
                T_vari = sum(T_numer_addends2)/sum(denom_addends2)
                Z_vari = sum(Z_numer_addends2)/sum(denom_addends2)
                theta_vari = sum(theta_numer_addends2)/sum(denom_addends2)
                E_bv_vari = sum(E_bv_numer_addends2)/sum(denom_addends2)

                print("Variances for this row: \n",g_vari,T_vari,Z_vari,theta_vari,E_bv_vari)

                g_err = math.sqrt(g_vari)
                T_err = math.sqrt(T_vari)
                Z_err = math.sqrt(Z_vari)
                theta_err = math.sqrt(theta_vari)
                E_bv_err = math.sqrt(E_bv_vari)

                print("Errors for this row: \n",g_err,T_err,Z_err,theta_err,E_bv_err)

                self.avglist.append([g_avg,T_avg,Z_avg,theta_avg,E_bv_avg])
                self.varilist.append([g_vari,T_vari,Z_vari,theta_vari,E_bv_vari])
                self.errlist.append([g_err,T_err,Z_err,theta_err,E_bv_err])

            print("AVGLIST \n",self.avglist,"\n")
            print("VARILIST \n",self.varilist,"\n")
            print("ERRLIST \n",self.errlist,"\n")

        
        elif self.double_cluster == True:
            from numpy.linalg import solve
            self.bestthetas = []
            self.bestcoords = []
            self.bestchisqs = []
            self.avglist = []
            self.varilist = []
            self.errlist = []

            for curr_row in range(self.bandfluxes.shape[0]): 

                print("\n\n ********************* WORKING ON ROW {} ********************* \n\n".format(self.rows[curr_row]+2))

                valid_filters_this_row = []
                for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                    if np.isnan(bflux) == False:
                        valid_filters_this_row.append(valid_ind)

                Tf1sthisrow = []
                Tf2sthisrow = []
                Tm11sthisrow = []
                Tm12sthisrow = []
                Tm22sthisrow = []
                thetavectorsthisrow = []
                coordinatesthisrow = []
                chisqsthisrow = []
                for g1 in self.refined_param_frame['log(g_hot)']:
                    for T1 in self.refined_param_frame['T_hot/10000']:
                        for Z1 in self.refined_param_frame['log(Z_hot)']:
                            for E_bv1 in self.refined_param_frame['E(B-V)_cool']:
                                for T2 in self.refined_param_frame['T_cool/10000']:
                                    for E_bv2 in self.refined_param_frame['E(B-V)_cool']:
                                        print("------------------------------------------\n")
                                        coord = [g1,T1,Z1,E_bv1,T2,E_bv2]
                                        print("COORD \n",coord)
                                        coordinatesthisrow.append(coord)
                                        Tf1thiscoord = self.Tf1(g1,T1,Z1,E_bv1,valid_filters_this_row,curr_row)
                                        print("TF1 \n",Tf1thiscoord)
                                        Tf1sthisrow.append(Tf1thiscoord)
                                        Tf2thiscoord = self.Tf2(T2,E_bv2,valid_filters_this_row,curr_row)
                                        print("TF2 \n",Tf2thiscoord)
                                        Tf2sthisrow.append(Tf2thiscoord)
                                        Tm11thiscoord = self.Tm11(g1,T1,Z1,E_bv1,valid_filters_this_row,curr_row)
                                        print("TM11 \n",Tm11thiscoord)
                                        Tm11sthisrow.append(Tm11thiscoord)
                                        Tm12thiscoord = self.Tm12(g1,T1,Z1,E_bv1,T2,E_bv2,valid_filters_this_row,curr_row)
                                        print("TM12 \n",Tm12thiscoord)
                                        Tm12sthisrow.append(Tm12thiscoord)
                                        Tm22thiscoord = self.Tm22(T2,E_bv2,valid_filters_this_row,curr_row)
                                        print("TM22 \n",Tm22thiscoord)
                                        Tm22sthisrow.append(Tm22thiscoord)
                                        matrixA = np.array([[Tm11thiscoord,Tm12thiscoord],[Tm12thiscoord,Tm22thiscoord]])
                                        print("matrixA \n",matrixA)
                                        vectorA = np.array([Tf1thiscoord,Tf2thiscoord])
                                        print("vectorA \n",vectorA)
                                        thetavectorthiscoord = solve(matrixA,vectorA)
                                        print("thetasqvector \n",thetavectorthiscoord)
                                        thetavectorsthisrow.append(thetavectorthiscoord)
                                        chisqthiscoord = self.chisqfunc2(coord[0],coord[1],coord[2],thetavectorthiscoord[0],coord[3],coord[4],thetavectorthiscoord[1],coord[5],valid_filters_this_row,curr_row)
                                        print("CHISQ \n",chisqthiscoord)
                                        chisqsthisrow.append(chisqthiscoord)
                

                print("CHISTHISROW \n",chisqsthisrow)
                print("BEST INDEX \n",chisqsthisrow.index(min(chisqsthisrow)))
                self.bestchisqs.append(chisqsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST CHIs \n",self.bestchisqs)
                print("mvectorsthisrow \n",thetavectorsthisrow)
                self.bestthetas.append(thetavectorsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST thetas \n",self.bestthetas)
                self.bestcoords.append(coordinatesthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("coordsthisrow \n",coordinatesthisrow)
                print("BEST Coords \n", self.bestcoords)

                import math

                g1_numer_addends = []
                T1_numer_addends = []
                Z1_numer_addends = []
                theta1_numer_addends = []
                E_bv1_numer_addends = []
                T2_numer_addends = []
                theta2_numer_addends = []
                E_bv2_numer_addends = []
                denom_addends = []
                norm_chisqs = []
                norm_chisqs = [chisq-self.bestchisqs[curr_row] for chisq in chisqsthisrow]
                print("NORM CHISQS \n", norm_chisqs)
                print("\n------------- CALCULATING AVERAGES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,theta in zip(norm_chisqs,coordinatesthisrow,thetavectorsthisrow):
                    print("CHISQ, COORD, THETA \n", chisq,coord,theta)
                    g1_numer_addends.append(math.e**(-chisq/2)*coord[0])
                    T1_numer_addends.append(math.e**(-chisq/2)*coord[1])
                    Z1_numer_addends.append(math.e**(-chisq/2)*coord[2])
                    theta1_numer_addends.append(math.e**(-chisq/2)*theta[0])
                    E_bv1_numer_addends.append(math.e**(-chisq/2)*coord[3])
                    T2_numer_addends.append(math.e**(-chisq/2)*coord[4])
                    theta2_numer_addends.append(math.e**(-chisq/2)*theta[1])
                    E_bv2_numer_addends.append(math.e**(-chisq/2)*coord[5])
                    denom_addends.append(math.e**(-chisq/2))
                    print("g1 NUMERATOR = e^(-chisq/2)*g1 \n", g1_numer_addends)
                    print("T1 NUMERATOR = e^(-chisq/2)*T1 \n", T1_numer_addends)
                    print("Z1 NUMERATOR = e^(-chisq/2)*Z1 \n", Z1_numer_addends)
                    print("theta1 NUMERATOR = e^(-chisq/2)*theta1 \n", theta1_numer_addends)
                    print("E_BV1 NUMERATOR = e^(-chisq/2)*E_bv1 \n", E_bv1_numer_addends)
                    print("T2 NUMERATOR = e^(-chisq/2)*T2 \n", T2_numer_addends)
                    print("theta2 NUMERATOR = e^(-chisq/2)*theta2 \n", theta2_numer_addends)
                    print("E_BV2 NUMERATOR = e^(-chisq/2)*E_bv2 \n", E_bv2_numer_addends)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)
                g1_avg = sum(g1_numer_addends)/sum(denom_addends)
                T1_avg = sum(T1_numer_addends)/sum(denom_addends)
                Z1_avg = sum(Z1_numer_addends)/sum(denom_addends)
                theta1_avg = sum(theta1_numer_addends)/sum(denom_addends)
                E_bv1_avg = sum(E_bv1_numer_addends)/sum(denom_addends)
                T2_avg = sum(T2_numer_addends)/sum(denom_addends)
                theta2_avg = sum(theta2_numer_addends)/sum(denom_addends)
                E_bv2_avg = sum(E_bv2_numer_addends)/sum(denom_addends)

                print("Averages for this row: \n",g1_avg,T1_avg,Z1_avg,theta1_avg,E_bv1_avg,T2_avg,theta2_avg,E_bv2_avg)

                g1_numer_addends2 = []
                T1_numer_addends2 = []
                Z1_numer_addends2 = []
                theta1_numer_addends2 = []
                E_bv1_numer_addends2 = []
                T2_numer_addends2 = []
                theta2_numer_addends2 = []
                E_bv2_numer_addends2 = []
                denom_addends2 = []
                print("\n------------- CALCULATING VARIANCES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,theta in zip(norm_chisqs,coordinatesthisrow,thetavectorsthisrow):
                    g1_numer_addends2.append(math.e**(-chisq/2)*(coord[0]-g1_avg)**2)
                    T1_numer_addends2.append(math.e**(-chisq/2)*(coord[1]-T1_avg)**2)
                    Z1_numer_addends2.append(math.e**(-chisq/2)*(coord[2]-Z1_avg)**2)
                    theta1_numer_addends2.append(math.e**(-chisq/2)*(theta[0]-theta1_avg)**2)
                    E_bv1_numer_addends2.append(math.e**(-chisq/2)*(coord[3]-E_bv1_avg)**2)
                    T2_numer_addends2.append(math.e**(-chisq/2)*(coord[4]-T2_avg)**2)
                    theta2_numer_addends2.append(math.e**(-chisq/2)*(theta[1]-theta2_avg)**2)
                    E_bv2_numer_addends2.append(math.e**(-chisq/2)*(coord[5]-E_bv2_avg)**2)
                    denom_addends2.append(math.e**(-chisq/2))
                    print("g1 NUMERATOR = e^(-chisq/2)*(g1-g1avg)^2 \n", g1_numer_addends2)
                    print("T1 NUMERATOR = e^(-chisq/2)*(T1-T1avg)^2 \n", T1_numer_addends2)
                    print("Z1 NUMERATOR = e^(-chisq/2)*(Z1-Z1avg)^2 \n", Z1_numer_addends2)
                    print("theta1 NUMERATOR = e^(-chisq/2)*(theta1-theta1avg)^2 \n", theta1_numer_addends2)
                    print("E_BV1 NUMERATOR = e^(-chisq/2)*(E_bv1-E_bv1avg)^2 \n", E_bv1_numer_addends2)
                    print("T2 NUMERATOR = e^(-chisq/2)*(T2-T2avg)^2 \n", T2_numer_addends2)
                    print("theta2 NUMERATOR = e^(-chisq/2)*(theta2-theta2avg)^2 \n", theta2_numer_addends2)
                    print("E_BV2 NUMERATOR = e^(-chisq/2)*(E_bv2-E_bv2avg)^2 \n", E_bv2_numer_addends2)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends2)
                g1_vari = sum(g1_numer_addends2)/sum(denom_addends2)
                T1_vari = sum(T1_numer_addends2)/sum(denom_addends2)
                Z1_vari = sum(Z1_numer_addends2)/sum(denom_addends2)
                theta1_vari = sum(theta1_numer_addends2)/sum(denom_addends2)
                E_bv1_vari = sum(E_bv1_numer_addends2)/sum(denom_addends2)
                T2_vari = sum(T2_numer_addends2)/sum(denom_addends2)
                theta2_vari = sum(theta2_numer_addends2)/sum(denom_addends2)
                E_bv2_vari = sum(E_bv2_numer_addends2)/sum(denom_addends2)

                print("Variances for this row: \n",g1_vari,T1_vari,Z1_vari,theta1_vari,E_bv1_vari,T2_vari,theta2_vari,E_bv2_vari)

                g1_err = math.sqrt(g1_vari)
                T1_err = math.sqrt(T1_vari)
                Z1_err = math.sqrt(Z1_vari)
                theta1_err = math.sqrt(theta1_vari)
                E_bv1_err = math.sqrt(E_bv1_vari)
                T2_err = math.sqrt(T2_vari)
                theta2_err = math.sqrt(theta2_vari)
                E_bv2_err = math.sqrt(E_bv2_vari)

                print("Variances for this row: \n",g1_err,T1_err,Z1_err,theta1_err,E_bv1_err,T2_err,theta2_err,E_bv2_err)

                self.avglist.append([g1_avg,T1_avg,Z1_avg,theta1_avg,E_bv1_avg,T2_avg,theta2_avg,E_bv2_avg])
                self.varilist.append([g1_vari,T1_vari,Z1_vari,theta1_vari,E_bv1_vari,T2_vari,theta2_vari,E_bv2_vari])
                self.errlist.append([g1_err,T1_err,Z1_err,theta1_err,E_bv1_err,T2_err,theta2_err,E_bv2_err])
            
            print("AVGLIST \n",self.avglist,"\n")
            print("VARILIST \n",self.varilist,"\n")
            print("ERRLIST \n",self.errlist,"\n")

    def display_all_results(self):
        if self.dispresults == 1:
            if self.single_cluster == True:
                for curr_row in range(self.bandfluxes.shape[0]):
                    self.display_results_single(curr_row)
            elif self.double_cluster == True:
                for curr_row in range(self.bandfluxes.shape[0]): 
                    self.display_results_double(curr_row)

    def save_output(self):

        import numpy as np
        import pandas as pd
        
        if self.single_cluster == True:

            models = self.bandfluxes.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                    if np.isnan(bflux) == False:
                        valid_filters_this_row.append(valid_ind)

                best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestcoords[curr_row][2],self.bestthetas[curr_row],self.bestcoords[curr_row][3])
                model = self.minichisqfunc_single(best_tup,valid_filters_this_row)
                used = 0 
                for colno,col in enumerate(models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        models.iat[curr_row,colno] = model[used]
                        used += 1
            

            if self.bestchiparams == 1:
    
                colnames = {'Source_ID' : [], "Chi^2_best" : [], "log(g)_best" : [], "T/10000_best" : [], "log(Z)_best" : [], "(theta_r_sq)*1e24_best" : [], "E(B-V)_best" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_best" : self.bestchisqs[curr_row], "log(g)_best" : self.bestcoords[curr_row][0], "T/10000_best" : self.bestcoords[curr_row][1], "log(Z)_best" : self.bestcoords[curr_row][2], "(theta_r_sq)*1e24_best" : self.bestthetas[curr_row], "E(B-V)_best" : self.bestcoords[curr_row][3]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.bestfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            if self.avgchiparams == 1:
                colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(g)_avg" : [], "T/10000_avg" : [], "log(Z)_avg" : [], "(theta_r_sq)*1e24_avg" : [], "E(B-V)_avg" : [], "log(g)_vari" : [], "T/10000_vari" : [], "log(Z)_vari" : [], "(theta_r_sq)*1e24_vari" : [], "E(B-V)_vari" : [], "log(g)_err" : [], "T/10000_err" : [], "log(Z)_err" : [], "(theta_r_sq)*1e24_err" : [], "E(B-V)_err" : [], "F148W_model_flux_AvgParams [mJy]" : [], "F169M_model_flux_AvgParams [mJy]" : [], "F172M_model_flux_AvgParams [mJy]" : [], "N219M_model_flux_AvgParams [mJy]" : [], "N279N_model_flux_AvgParams [mJy]" : [], "f275w_model_flux_AvgParams [mJy]" : [], "f336w_model_flux_AvgParams [mJy]" : [], "f475w_model_flux_AvgParams [mJy]" : [], "f814w_model_flux_AvgParams [mJy]" : [], "f110w_model_flux_AvgParams [mJy]" : [], "f160w_model_flux_AvgParams [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    valid_filters_this_row = []
                    for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                        if np.isnan(bflux) == False:
                            valid_filters_this_row.append(valid_ind)
                    print("Running chisqfunc with average parameters to get Chi^2_avg to save in output.")
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],valid_filters_this_row,curr_row), "log(g)_avg" : self.avglist[curr_row][0], "T/10000_avg" : self.avglist[curr_row][1], "log(Z)_avg" : self.avglist[curr_row][2], "(theta_r_sq)*1e24_avg" : self.avglist[curr_row][3], "E(B-V)_avg" : self.avglist[curr_row][4], "log(g)_vari" : self.varilist[curr_row][0], "T/10000_vari" : self.varilist[curr_row][1], "log(Z)_vari" : self.varilist[curr_row][2], "(theta_r_sq)*1e24_vari" : self.varilist[curr_row][3], "E(B-V)_vari" : self.varilist[curr_row][4], "log(g)_err" : self.errlist[curr_row][0], "T/10000_err" : self.errlist[curr_row][1], "log(Z)_err" : self.errlist[curr_row][2], "(theta_r_sq)*1e24_err" : self.errlist[curr_row][3], "E(B-V)_err" : self.errlist[curr_row][4], "F148W_model_flux_AvgParams [mJy]" : models.iat[curr_row,0], "F169M_model_flux_AvgParams [mJy]" : models.iat[curr_row,1], "F172M_model_flux_AvgParams [mJy]" : models.iat[curr_row,2], "N219M_model_flux_AvgParams [mJy]" : models.iat[curr_row,3], "N279N_model_flux_AvgParams [mJy]" : models.iat[curr_row,4], "f275w_model_flux_AvgParams [mJy]" : models.iat[curr_row,5], "f336w_model_flux_AvgParams [mJy]" : models.iat[curr_row,6], "f475w_model_flux_AvgParams [mJy]" : models.iat[curr_row,7], "f814w_model_flux_AvgParams [mJy]" : models.iat[curr_row,8], "f110w_model_flux_AvgParams [mJy]" : models.iat[curr_row,9], "f160w_model_flux_AvgParams [mJy]" : models.iat[curr_row,10]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.avgfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            
        elif self.double_cluster == True:

            hotmodels = self.bandfluxes.copy(deep=True)
            coolmodels = self.bandfluxes.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                    if np.isnan(bflux) == False:
                        valid_filters_this_row.append(valid_ind)
    
                best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestcoords[curr_row][2],self.bestthetas[curr_row][0],self.bestcoords[curr_row][3],self.bestcoords[curr_row][4],self.bestthetas[curr_row][1],self.bestcoords[curr_row][5])
                hot,cool = self.minichisqfunc_double(best_tup,valid_filters_this_row)
                usedhot = 0
                usedcool = 0
                for colno,col in enumerate(hotmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        hotmodels.iat[curr_row,colno] = hot[usedhot]
                        usedhot += 1
                for colno,col in enumerate(coolmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        coolmodels.iat[curr_row,colno] = cool[usedcool]
                        usedcool += 1


            if self.bestchiparams == 1:
    
                colnames = {'Source_ID' : [], "Chi^2_best" : [], "log(g_hot)_best" : [], "T_hot/10000_best" : [], "log(Z_hot)_best" : [], "(theta_r_hot_sq)*1e24_best" : [], "E(B-V)_hot_best" : [], "T_cool/10000_best" : [], "(theta_r_cool_sq)*1e24_best" : [], "E(B-V)_cool_best" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_best" : self.bestchisqs[curr_row], "log(g_hot)_best" : self.bestcoords[curr_row][0], "T_hot/10000_best" : self.bestcoords[curr_row][1], "log(Z_hot)_best" : self.bestcoords[curr_row][2], "(theta_r_hot_sq)*1e24_best" : self.bestthetas[curr_row][0], "E(B-V)_hot_best" : self.bestcoords[curr_row][3], "T_cool/10000_best" : self.bestcoords[curr_row][4], "(theta_r_cool_sq)*1e24_best" : self.bestthetas[curr_row][1], "E(B-V)_cool_best" : self.bestcoords[curr_row][5]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.bestfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            if self.avgchiparams == 1:
                colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(g_hot)_avg" : [], "T_hot/10000_avg" : [], "log(Z_hot)_avg" : [], "(theta_r_hot_sq)*1e24_avg" : [], "E(B-V)_hot_avg" : [], "T_cool/10000_avg" : [], "(theta_r_cool_sq)*1e24_avg" : [], "E(B-V)_cool_avg" : [], "log(g_hot)_vari" : [], "T_hot/10000_vari" : [], "log(Z_hot)_vari" : [], "(theta_r_hot_sq)*1e24_vari" : [], "E(B-V)_hot_vari" : [], "T_cool/10000_vari" : [], "(theta_r_cool_sq)*1e24_vari" : [], "E(B-V)_cool_vari" : [], "log(g_hot)_err" : [], "T_hot/10000_err" : [], "log(Z_hot)_err" : [], "(theta_r_hot_sq)*1e24_err" : [], "E(B-V)_hot_err" : [], "T_cool/10000_err" : [], "(theta_r_cool_sq)*1e24_err" : [], "E(B-V)_cool_err" : [], "F148W_hot_flux_AvgParams [mJy]" : [], "F148W_cool_flux_AvgParams [mJy]" : [], "F169M_hot_flux_AvgParams [mJy]" : [], "F169M_cool_flux_AvgParams [mJy]" : [], "F172M_hot_flux_AvgParams [mJy]" : [], "F172M_cool_flux_AvgParams [mJy]" : [], "N219M_hot_flux_AvgParams [mJy]" : [], "N219M_cool_flux_AvgParams [mJy]" : [], "N279N_hot_flux_AvgParams [mJy]" : [], "N279N_cool_flux_AvgParams [mJy]" : [], "f275w_hot_flux_AvgParams [mJy]" : [], "f275w_cool_flux_AvgParams [mJy]" : [], "f336w_hot_flux_AvgParams [mJy]" : [], "f336w_cool_flux_AvgParams [mJy]" : [], "f475w_hot_flux_AvgParams [mJy]" : [], "f475w_cool_flux_AvgParams [mJy]" : [], "f814w_hot_flux_AvgParams [mJy]" : [], "f814w_cool_flux_AvgParams [mJy]" : [], "f110w_hot_flux_AvgParams [mJy]" : [], "f110w_cool_flux_AvgParams [mJy]" : [], "f160w_hot_flux_AvgParams [mJy]" : [], "f160w_cool_flux_AvgParams [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    valid_filters_this_row = []
                    for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                        if np.isnan(bflux) == False:
                            valid_filters_this_row.append(valid_ind)
                    print("Running chisqfunc2 with average parameters to get Chi^2_avg to save in output.") 
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc2(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],valid_filters_this_row,curr_row), "log(g_hot)_avg" : self.avglist[curr_row][0], "T_hot/10000_avg" : self.avglist[curr_row][1], "log(Z_hot)_avg" : self.avglist[curr_row][2], "(theta_r_hot_sq)*1e24_avg" : self.avglist[curr_row][3], "E(B-V)_hot_avg" : self.avglist[curr_row][4], "T_cool/10000_avg" : self.avglist[curr_row][5], "(theta_r_cool_sq)*1e24_avg" : self.avglist[curr_row][6], "E(B-V)_cool_avg" : self.avglist[curr_row][7], "log(g_hot)_vari" : self.varilist[curr_row][0], "T_hot/10000_vari" : self.varilist[curr_row][1], "log(Z_hot)_vari" : self.varilist[curr_row][2], "(theta_r_hot_sq)*1e24_vari" : self.varilist[curr_row][3], "E(B-V)_hot_vari" : self.varilist[curr_row][4], "T_cool/10000_vari" : self.varilist[curr_row][5], "(theta_r_cool_sq)*1e24_vari" : self.varilist[curr_row][6], "E(B-V)_cool_vari" : self.varilist[curr_row][7], "log(g_hot)_err" : self.errlist[curr_row][0], "T_hot/10000_err" : self.errlist[curr_row][1], "log(Z_hot)_err" : self.errlist[curr_row][2], "(theta_r_hot_sq)*1e24_err" : self.errlist[curr_row][3], "E(B-V)_hot_err" : self.errlist[curr_row][4], "T_cool/10000_err" : self.errlist[curr_row][5], "(theta_r_cool_sq)*1e24_err" : self.errlist[curr_row][6], "E(B-V)_cool_err" : self.errlist[curr_row][7], "F148W_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,0], "F148W_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,0], "F169M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,1],"F169M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,1], "F172M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,2], "F172M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,2], "N219M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,3], "N219M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,3], "N279N_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,4], "N279N_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,4], "f275w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,5], "f275w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,5], "f336w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,6], "f336w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,6], "f475w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,7], "f475w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,7], "f814w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,8], "f814w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,8], "f110w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,9], "f110w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,9], "f160w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,10], "f160w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,10]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.avgfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            

    def display_results_single(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
            if np.isnan(bflux) == False:
                valid_filters_this_row.append(valid_ind)

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.bandfluxerrors.iat[curr_row,valid_ind])

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestcoords[curr_row][2],self.bestthetas[curr_row],self.bestcoords[curr_row][3])
        avg_tup = (self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_avgwv_this_row,valid_fluxes_this_row,yerr=valid_errors_this_row,fmt="o",color="orange")
        abc.plot(valid_avgwv_this_row,self.minichisqfunc_single(avg_tup,valid_filters_this_row),color="blue")

        if self.plotscale == 1:
            pass

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            abc.set_xticks([140,200,500,1000,1500])
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=220)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=250)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=420)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=450)
        label4 = tk.Label(topw,text="Avg. model fluxes (y, blue):")
        label4.place(x=50,y=620)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_single(avg_tup,valid_filters_this_row)):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=650)
        groove1 = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove1.place(x=405,y=625)
        label5 = tk.Label(topw,text="Best chi^2 value")
        label5.place(x=425,y=635)
        label5a = tk.Label(topw,text="{}".format(format(self.bestchisqs[curr_row],'.6e')),font=("Arial",12))
        label5a.place(x=437,y=685)
        groove2 = tk.Canvas(topw,width=285,height=120,bd=4,relief=tk.RIDGE)
        groove2.place(x=405,y=755)
        label6 = tk.Label(topw,text="Chi^2 value for average parameters")
        label6.place(x=425,y=765)
        print("Running chisqfunc with average parameters to get Chi^2_avg to display in output window.")
        label6a = tk.Label(topw,text="{}".format(format(self.chisqfunc(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],valid_filters_this_row,curr_row),'.6e')),font=("Arial",12))
        label6a.place(x=437,y=815)
        
        import math
        g_sticker1 = format(self.bestcoords[curr_row][0],'.6e')
        g_sticker2 = format(self.avglist[curr_row][0],'.6e')
        g_sticker3 = format(self.varilist[curr_row][0],'.6e')
        g_sticker4 = format(self.errlist[curr_row][0],'.6e')

        T_sticker1 = format(self.bestcoords[curr_row][1],'.6e')
        T_sticker2 = format(self.avglist[curr_row][1],'.6e')
        T_sticker3 = format(self.varilist[curr_row][1],'.6e')
        T_sticker4 = format(self.errlist[curr_row][1],'.6e')

        Z_sticker1 = format(self.bestcoords[curr_row][2],'.6e')
        Z_sticker2 = format(self.avglist[curr_row][2],'.6e')
        Z_sticker3 = format(self.varilist[curr_row][2],'.6e')
        Z_sticker4 = format(self.errlist[curr_row][2],'.6e')

        theta_sticker1 = format(self.bestthetas[curr_row],'.6e')
        theta_sticker2 = format(self.avglist[curr_row][3],'.6e')
        theta_sticker3 = format(self.varilist[curr_row][3],'.6e')
        theta_sticker4 = format(self.errlist[curr_row][3],'.6e')

        ebv_sticker1 = format(self.bestcoords[curr_row][3],'.6e')
        ebv_sticker2 = format(self.avglist[curr_row][4],'.6e')
        ebv_sticker3 = format(self.varilist[curr_row][4],'.6e')
        ebv_sticker4 = format(self.errlist[curr_row][4],'.6e')

        colpack1 = tk.Frame(topw)
        colpack1.place(x=850,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=965,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=1100,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1220,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1330,y=600)

        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=10)
        parameter1 = tk.Label(colpack1,text="log(g)").pack(pady=8)
        parameter2 = tk.Label(colpack1,text="T/10000").pack(pady=8)
        parameter3 = tk.Label(colpack1,text="log(Z)").pack(pady=8)
        parameter4 = tk.Label(colpack1,text="theta_r_sq*1e24").pack(pady=8)
        parameter5 = tk.Label(colpack1,text="E(B-V)").pack(pady=8)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=10)
        best1 = tk.Label(colpack2,text="{}".format(g_sticker1)).pack(pady=8)
        best2 = tk.Label(colpack2,text="{}".format(T_sticker1)).pack(pady=8)
        best3 = tk.Label(colpack2,text="{}".format(Z_sticker1)).pack(pady=8)
        best4 = tk.Label(colpack2,text="{}".format(theta_sticker1)).pack(pady=8)
        best5 = tk.Label(colpack2,text="{}".format(ebv_sticker1)).pack(pady=8)
        errlohead = tk.Label(colpack3,text="Average value",bg="azure").pack(pady=10)
        errlo1 = tk.Label(colpack3,text="{}".format(g_sticker2)).pack(pady=8)
        errlo2 = tk.Label(colpack3,text="{}".format(T_sticker2)).pack(pady=8)
        errlo3 = tk.Label(colpack3,text="{}".format(Z_sticker2)).pack(pady=8)
        errlo4 = tk.Label(colpack3,text="{}".format(theta_sticker2)).pack(pady=8)
        errlo5 = tk.Label(colpack3,text="{}".format(ebv_sticker2)).pack(pady=8)
        noteslohead = tk.Label(colpack4,text="Variance",bg="azure").pack(pady=10)
        noteslo1 = tk.Label(colpack4,text="{}".format(g_sticker3)).pack(pady=8)
        noteslo2 = tk.Label(colpack4,text="{}".format(T_sticker3)).pack(pady=8)
        noteslo2 = tk.Label(colpack4,text="{}".format(Z_sticker3)).pack(pady=8)
        noteslo4 = tk.Label(colpack4,text="{}".format(theta_sticker3)).pack(pady=8)
        noteslo5 = tk.Label(colpack4,text="{}".format(ebv_sticker3)).pack(pady=8)
        errhihead = tk.Label(colpack5,text="Error",bg="azure").pack(pady=10)
        errhi1 = tk.Label(colpack5,text="{}".format(g_sticker4)).pack(pady=8)
        errhi2 = tk.Label(colpack5,text="{}".format(T_sticker4)).pack(pady=8)
        errhi3 = tk.Label(colpack5,text="{}".format(Z_sticker4)).pack(pady=8)
        errhi4 = tk.Label(colpack5,text="{}".format(theta_sticker4)).pack(pady=8)
        errhi5 = tk.Label(colpack5,text="{}".format(ebv_sticker4)).pack(pady=8)

        def closethesource():
            topw.destroy()

        groove3 = tk.Canvas(topw,width=200,height=120,bd=4,relief=tk.RIDGE)
        groove3.place(x=605,y=625)
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=632,y=670)
        topw.mainloop()

    
    def display_results_double(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
            if np.isnan(bflux) == False:
                valid_filters_this_row.append(valid_ind)

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.bandfluxerrors.iat[curr_row,valid_ind])

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])
    

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        #best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3],self.results[curr_row].x[4],self.results[curr_row].x[5],self.results[curr_row].x[6],self.results[curr_row].x[7])
        avg_tup = (self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_avgwv_this_row,valid_fluxes_this_row,yerr=valid_errors_this_row,fmt="o",color="orange")
        hotmod = self.minichisqfunc_double(avg_tup,valid_filters_this_row)[0]
        coolmod = self.minichisqfunc_double(avg_tup,valid_filters_this_row)[1]
        abc.plot(valid_avgwv_this_row,hotmod,color="red")
        abc.plot(valid_avgwv_this_row,coolmod,color="blue")
        sumofmodels = [hotmod[i] + coolmod[i] for i in range(len(hotmod))]
        abc.plot(valid_avgwv_this_row,sumofmodels,color="limegreen")

        if self.plotscale == 1:
            pass

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            abc.set_xticks([140,200,500,1000,1500])
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=195)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=225)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=370)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=400)
        label4 = tk.Label(topw,text="Hot cluster model fluxes (y, red):")
        label4.place(x=50,y=545)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(avg_tup,valid_filters_this_row)[0]):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=575)
        label5 = tk.Label(topw,text="Cool cluster model fluxes (y, blue):")
        label5.place(x=50,y=720)
        textbox5 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(avg_tup,valid_filters_this_row)[1]):
            textbox5.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox5.place(x=50,y=750)
        groove1 = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove1.place(x=405,y=625)
        label5 = tk.Label(topw,text="Best chi^2 value")
        label5.place(x=425,y=635)
        label5a = tk.Label(topw,text="{}".format(format(self.bestchisqs[curr_row],'.6e')),font=("Arial",12))
        label5a.place(x=437,y=685)
        groove2 = tk.Canvas(topw,width=285,height=120,bd=4,relief=tk.RIDGE)
        groove2.place(x=405,y=755)
        label6 = tk.Label(topw,text="Chi^2 value for average parameters")
        label6.place(x=425,y=765)
        print("Running chisqfunc2 with average parameters to get Chi^2_avg to display in output window.")
        label6a = tk.Label(topw,text="{}".format(format(self.chisqfunc2(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],valid_filters_this_row,curr_row),'.6e')),font=("Arial",12))
        label6a.place(x=437,y=815)

        import math
        g_hot_sticker1 = format(self.bestcoords[curr_row][0],'.6e')
        g_hot_sticker2 = format(self.avglist[curr_row][0],'.6e')
        g_hot_sticker3 = format(self.varilist[curr_row][0],'.6e')
        g_hot_sticker4 = format(self.errlist[curr_row][0],'.6e')

        T_hot_sticker1 = format(self.bestcoords[curr_row][1],'.6e')
        T_hot_sticker2 = format(self.avglist[curr_row][1],'.6e')
        T_hot_sticker3 = format(self.varilist[curr_row][1],'.6e')
        T_hot_sticker4 = format(self.errlist[curr_row][1],'.6e')
        
        Z_hot_sticker1 = format(self.bestcoords[curr_row][2],'.6e')
        Z_hot_sticker2 = format(self.avglist[curr_row][2],'.6e')
        Z_hot_sticker3 = format(self.varilist[curr_row][2],'.6e')
        Z_hot_sticker4 = format(self.errlist[curr_row][2],'.6e')

        theta_hot_sticker1 = format(self.bestthetas[curr_row][0],'.6e')
        theta_hot_sticker2 = format(self.avglist[curr_row][3],'.6e')
        theta_hot_sticker3 = format(self.varilist[curr_row][3],'.6e')
        theta_hot_sticker4 = format(self.errlist[curr_row][3],'.6e')

        ebv_hot_sticker1 = format(self.bestcoords[curr_row][3],'.6e')
        ebv_hot_sticker2 = format(self.avglist[curr_row][4],'.6e')
        ebv_hot_sticker3 = format(self.varilist[curr_row][4],'.6e')
        ebv_hot_sticker4 = format(self.errlist[curr_row][4],'.6e')

        T_cool_sticker1 = format(self.bestcoords[curr_row][4],'.6e')
        T_cool_sticker2 = format(self.avglist[curr_row][5],'.6e')
        T_cool_sticker3 = format(self.varilist[curr_row][5],'.6e')
        T_cool_sticker4 = format(self.errlist[curr_row][5],'.6e')

        theta_cool_sticker1 = format(self.bestthetas[curr_row][1],'.6e')
        theta_cool_sticker2 = format(self.avglist[curr_row][6],'.6e')
        theta_cool_sticker3 = format(self.varilist[curr_row][6],'.6e')
        theta_cool_sticker4 = format(self.errlist[curr_row][6],'.6e')

        ebv_cool_sticker1 = format(self.bestcoords[curr_row][5],'.6e')
        ebv_cool_sticker2 = format(self.avglist[curr_row][7],'.6e')
        ebv_cool_sticker3 = format(self.varilist[curr_row][7],'.6e')
        ebv_cool_sticker4 = format(self.errlist[curr_row][7],'.6e')

        colpack1 = tk.Frame(topw)
        colpack1.place(x=850,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=980,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=1100,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1220,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1330,y=600)
        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=3)
        parameter1 = tk.Label(colpack1,text="log(g_hot)").pack(pady=3)
        parameter2 = tk.Label(colpack1,text="T_hot/10000").pack(pady=3)
        parameter3 = tk.Label(colpack1,text="log(Z_hot)").pack(pady=3)
        parameter4 = tk.Label(colpack1,text="theta_r_hot_sq*1e24").pack(pady=3)
        parameter5 = tk.Label(colpack1,text="E(B-V)_hot").pack(pady=3)
        parameter6 = tk.Label(colpack1,text="T_cool/10000").pack(pady=3)
        parameter7 = tk.Label(colpack1,text="theta_r_cool_sq*1e24").pack(pady=3)
        parameter8 = tk.Label(colpack1,text="E(B-V)_cool").pack(pady=3)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=3)
        best1 = tk.Label(colpack2,text="{}".format(g_hot_sticker1)).pack(pady=3)
        best2 = tk.Label(colpack2,text="{}".format(T_hot_sticker1)).pack(pady=3)
        best3 = tk.Label(colpack2,text="{}".format(Z_hot_sticker1)).pack(pady=3)
        best4 = tk.Label(colpack2,text="{}".format(theta_hot_sticker1)).pack(pady=3)
        best5 = tk.Label(colpack2,text="{}".format(ebv_hot_sticker1)).pack(pady=3)
        best6 = tk.Label(colpack2,text="{}".format(T_cool_sticker1)).pack(pady=3)
        best7 = tk.Label(colpack2,text="{}".format(theta_cool_sticker1)).pack(pady=3)
        best8 = tk.Label(colpack2,text="{}".format(ebv_cool_sticker1)).pack(pady=3)
        errlohead = tk.Label(colpack3,text="Average value",bg="azure").pack(pady=3)
        errlo1 = tk.Label(colpack3,text="{}".format(g_hot_sticker2)).pack(pady=3)
        errlo2 = tk.Label(colpack3,text="{}".format(T_hot_sticker2)).pack(pady=3)
        errlo3 = tk.Label(colpack3,text="{}".format(Z_hot_sticker2)).pack(pady=3)
        errlo4 = tk.Label(colpack3,text="{}".format(theta_hot_sticker2)).pack(pady=3)
        errlo5 = tk.Label(colpack3,text="{}".format(ebv_hot_sticker2)).pack(pady=3)
        errlo6 = tk.Label(colpack3,text="{}".format(T_cool_sticker2)).pack(pady=3)
        errlo7 = tk.Label(colpack3,text="{}".format(theta_cool_sticker2)).pack(pady=3)
        errlo8 = tk.Label(colpack3,text="{}".format(ebv_cool_sticker2)).pack(pady=3)
        noteslohead = tk.Label(colpack4,text="Variance",bg="azure").pack(pady=3)
        noteslo1 = tk.Label(colpack4,text="{}".format(g_hot_sticker3)).pack(pady=3)
        noteslo2 = tk.Label(colpack4,text="{}".format(T_hot_sticker3)).pack(pady=3)
        noteslo3 = tk.Label(colpack4,text="{}".format(Z_hot_sticker3)).pack(pady=3)
        noteslo4 = tk.Label(colpack4,text="{}".format(theta_hot_sticker3)).pack(pady=3)
        noteslo5 = tk.Label(colpack4,text="{}".format(ebv_hot_sticker3)).pack(pady=3)
        noteslo6 = tk.Label(colpack4,text="{}".format(T_cool_sticker3)).pack(pady=3)
        noteslo7 = tk.Label(colpack4,text="{}".format(theta_cool_sticker3)).pack(pady=3)
        noteslo8 = tk.Label(colpack4,text="{}".format(ebv_cool_sticker3)).pack(pady=3)
        errhihead = tk.Label(colpack5,text="Error",bg="azure").pack(pady=3)
        errhi1 = tk.Label(colpack5,text="{}".format(g_hot_sticker4)).pack(pady=3)
        errhi2 = tk.Label(colpack5,text="{}".format(T_hot_sticker4)).pack(pady=3)
        errhi3 = tk.Label(colpack5,text="{}".format(Z_hot_sticker4)).pack(pady=3)
        errhi4 = tk.Label(colpack5,text="{}".format(theta_hot_sticker4)).pack(pady=3)
        errhi5 = tk.Label(colpack5,text="{}".format(ebv_hot_sticker4)).pack(pady=3)
        errhi6 = tk.Label(colpack5,text="{}".format(T_cool_sticker4)).pack(pady=3)
        errhi7 = tk.Label(colpack5,text="{}".format(theta_cool_sticker4)).pack(pady=3)
        errhi8 = tk.Label(colpack5,text="{}".format(ebv_cool_sticker4)).pack(pady=3)

        def closethesource():
            topw.destroy()
        groove3 = tk.Canvas(topw,width=200,height=120,bd=4,relief=tk.RIDGE)
        groove3.place(x=605,y=625)
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=632,y=670)
        topw.mainloop()



go = ChiSquared()