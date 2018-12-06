################################################################################
# SunSystemEtoModelessTabbedDialog.py
################################################################################

# Imports
import System
import Eto.Drawing as drawing
import Eto.Forms as forms
import scriptcontext as sc
from etosunpathpanel import SunPathEtoPanel
from etosunlighthourspanel import SunLightHoursEtoPanel
from ladybugeto import LadybugEto  

class SunSystemEtoModelessForm(forms.Form):
    
    def __init__(self):
        self.Rnd = System.Random()
        self.Title = "Ladybug Sun System"
        self.Padding = drawing.Padding(10)
        self.Resizable = True
        self.Content = self.create_tabs()   
        # FormClosed event handler
        self.Closed += self.on_form_closed        
        
        
    def create_tabs(self):  
    
        # creates a tab control
        self.TabControl = forms.TabControl()
        # Orient the tabs at the top
        self.TabControl.TabPosition = forms.DockPosition.Top
        
        # create and add a tab page 1
        tab1 = forms.TabPage()
        tab1.Text = 'Sun Path'
        tab1.Content = SunPathEtoPanel()
        self.TabControl.Pages.Add(tab1)
        
        # create and add a tab page 2
        tab2 = forms.TabPage()
        tab2.Text = 'Sunlight Hours'
        tab2.Content = SunLightHoursEtoPanel()
        self.TabControl.Pages.Add(tab2) 
        
        return self.TabControl 
        
    def get_sun_path_panel(self):
        return self.TabControl.Pages[0].Content
        
    def get_sun_ligh_hours_panel(self):
        return self.TabControl.Pages[1].Content
        
    # form closed event
    def on_form_closed(self, sender, e):
        try:        
            #cleanup scene objects
            LadybugEto.bakeGeo([], 'lb_sunpath')
            LadybugEto.bakeGeo([], 'lb_sunlighthours')
            
            # Dispose of the form and remove it from the sticky dictionary
            if sc.sticky.has_key('sample_modeless_form'):
                form = sc.sticky['sample_modeless_form']
                if form:
                    form.Dispose()
                    form = None
                sc.sticky.Remove('sample_modeless_form')
        except Exception as e:
            print e 
            
            

