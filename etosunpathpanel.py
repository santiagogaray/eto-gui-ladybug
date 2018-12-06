################################################################################
# SunPathEtoModelessDialog.py
################################################################################

import System
import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms
import scriptcontext as sc
from etoutility import EtoUtil
from ladybugeto import LadybugEto  
    
try:
    from ladybug.sunpath import Sunpath
    import ladybug.geometry as geo
    import ladybug.location as loc
    import ladybug.dt as dt
    import ladybug.analysisperiod as ap
    import ladybug.epw as epw  
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e)) 

    
    
################################################################################
# SunPathEtoModelessDialog class
################################################################################
class SunPathEtoPanel(forms.Panel):
    
    # Initializer
    def __init__(self):
        
        # Basic form initialization
        self.initialize_form()
        # Create the form's controls
        self.create_form_controls()
        #generate initial sun path with default values
        self.lb_generate_sun_path()
        
    # Basic form initialization
    def initialize_form(self):
        self.Title = 'Sun Path'
        self.Padding = drawing.Padding(5)
        self.Resizable = False
        self.Maximizable = False
        self.Minimizable = False
        self.ShowInTaskbar = False
        self.MinimumSize = drawing.Size(210, 150)
        # FormClosed event handler
        #self.Closed += self.on_form_closed
        
    # Create all of the controls used by the form
    def create_form_controls(self):
        # Create table layout
        layout = forms.TableLayout()
        layout.Padding = drawing.Padding(10)
        layout.Spacing = drawing.Size(20, 20)
        # Add controls to layout
        layout.Rows.Add(self.create_north_table())
        layout.Rows.Add(self.create_location_group())
        layout.Rows.Add(self.create_date_time_group())
        layout.Rows.Add(self.create_global_settings_table())
        
        # Set the content
        self.Content = layout
        
    def create_north_table(self):
        northLabel = forms.Label(Text = 'North:')
        self.m_north_updown = EtoUtil.create_numeric_stepper(decimal_places = 0, 
                                                 increment = 1,
                                                 value = 0, 
                                                 min = 0,
                                                 max = 360,
                                                 format_string = "{0}\N{DEGREE SIGN}",
                                                 change_event_method =\
                                                  self.on_north_value_changed)          
        
        #layout.Rows.Add(forms.TableRow()
        return EtoUtil.create_layout_from_control_matrix([[northLabel, 
                                                        self.m_north_updown,
                                                        None]],
                                                       drawing.Padding(10, 0))
    
    def create_location_group(self):
        
        #location name layout
        self.m_loc_name_text_box = forms.TextBox()
        self.m_loc_name_text_box.PlaceholderText = "Location name" 
        layout_a = EtoUtil.create_layout_from_control_matrix([[self.m_loc_name_text_box]])
        #
        # lat/long layout
        lat_label = forms.Label(Text = 'Lat:') 
        self.m_numeric_lat_updown = EtoUtil.create_numeric_stepper(decimal_places = 3, 
                                                 increment = 1,
                                                 value = 0, 
                                                 min = -90,
                                                 max = 90,
                                                 format_string = "{0:f3}\N{DEGREE SIGN}",
                                                 change_event_method =\
                                                  self.on_latitude_value_changed)                                                
        
        long_label = forms.Label(Text = '   Long:') 
        self.m_numeric_long_updown = EtoUtil.create_numeric_stepper(decimal_places = 3, 
                                                 increment = 1,
                                                 value = 0, 
                                                 min = -90,
                                                 max = 90,
                                                 format_string = "{0:f3}\N{DEGREE SIGN}",
                                                 change_event_method =\
                                                  self.on_longitude_value_changed)            
        
        
        layout_b = EtoUtil.create_layout_from_control_matrix([[lat_label, 
            self.m_numeric_lat_updown, long_label, self.m_numeric_long_updown]],
            drawing.Padding(5,15,5,0))
        #
        # time zone layout
        timezone_label = forms.Label(Text = 'Time zone:') 
        self.m_timezone_dropdown = forms.DropDown()
        time_zones = ['(UTC -12:00)', '(UTC -11:00)', '(UTC -10:00)', '(UTC -09:00)',
                      '(UTC -08:00)', '(UTC -07:00)', '(UTC -06:00)', '(UTC -05:00)',
                      '(UTC -04:00)', '(UTC -03:00)', '(UTC -02:00)', '(UTC -01:00)',
                      '(UTC 00:00)', '(UTC 01:00)', '(UTC 02:00)', '(UTC 03:00)',
                      '(UTC 04:00)', '(UTC 05:00)', '(UTC 06:00)', '(UTC 07:00)',
                      '(UTC 08:00)', '(UTC 09:00)', '(UTC 10:00)', '(UTC 11:00)',
                      '(UTC 12:00)'
                      ]
        self.m_timezone_dropdown.DataStore = time_zones
        self.m_timezone_dropdown.SelectedIndex = 12
        self.m_timezone_dropdown.DropDownClosed += self.on_timezone_drop_down_closed
        layout_c = EtoUtil.create_layout_from_control_matrix([[timezone_label],
                                                           [self.m_timezone_dropdown]])
        #
        # elevation layout
        elev_label = forms.Label(Text = 'Elevation:') 
        elev_label.Size = drawing.Size(140,10) 
        self.m_elev_updown = EtoUtil.create_numeric_stepper(decimal_places = 3, 
                                                 increment = 1,
                                                 value = 0, 
                                                 change_event_method =\
                                                  self.on_elevation_value_changed)          
        layout_d = EtoUtil.create_layout_from_control_matrix([[elev_label, 
                                                            self.m_elev_updown]])
                                                            
        #Import location from epw layout 
        epw_file_label = forms.Label(Text = 'Import location from epw file:') 
        self.m_epw_file_picker = EtoUtil.create_file_picker(
                                            title = "Select epw file",
                                            filter = 'epw',
                                            file_path_changed_event_method =
                                             self.on_epw_file_path_changed)        
        self.m_epw_file = ""
        
        layout_e = EtoUtil.create_layout_from_control_matrix([[epw_file_label],
                                                           [self.m_epw_file_picker]])
         
        #
        # return group with created layout 
        group_layout = EtoUtil.create_layout_from_control_matrix([[layout_a],
                                                                  [layout_b],
                                                                  [layout_c], 
                                                                  [layout_d],
                                                                  [layout_e]])
                                                                  
        return EtoUtil.create_group_from_layout('Location', group_layout)
        
    
    def create_date_time_group(self):
        
        def date_time_controls(is_enabled,
                           picker_date_event_method, slider_date_event_method,
                           picker_time_event_method, slider_time_event_method):
                    
            current_date_time = System.DateTime.Now
            #date slider and pickers
            date = forms.DateTimePicker()
            date.Mode = forms.DateTimePickerMode.Date
            date.Value = current_date_time
            date.Size = drawing.Size(30,20)  
            date.ValueChanged += picker_date_event_method
            date.Enabled = is_enabled
            #
            date_label = forms.Label(Text = 'Day of year:')
            date_label.Size = drawing.Size(140,15)         
            date_slider = EtoUtil.create_slider(value = current_date_time.Now.DayOfYear,
                                        min = 1, max = 365, 
                                        snap_to_tick = False,
                                        tick_frequency = 31, 
                                        change_event_method = slider_date_event_method,
                                        is_enabled = is_enabled)
            
            # Time slider and picker
            time = forms.DateTimePicker()
            time.Mode = forms.DateTimePickerMode.Time
            time.Value = System.DateTime(1,1,1,current_date_time.Hour,0,0)     
            time.Size = drawing.Size(30,20) 
            time.ValueChanged += picker_time_event_method
            time.Enabled = is_enabled
            #          
            time_label = forms.Label(Text = 'Hour of day:') 
            time_label.Size = drawing.Size(140,15)     
            time_slider = EtoUtil.create_slider(value = current_date_time.Hour,
                                        min = 0, max = 23, 
                                        snap_to_tick = True,
                                        tick_frequency = 1, 
                                        change_event_method = slider_time_event_method,
                                        is_enabled = is_enabled)           

            layout = EtoUtil.create_layout_from_control_matrix(
                                                [[date_label],
                                                 [date_slider, date],
                                                 [time_label],
                                                 [time_slider, time]])
                                                 
            return layout, date, date_slider, time, time_slider
            
            
        #create layout a: From date/ time
        layout_a, self.m_date, self.m_date_slider, self.m_time, self.m_time_slider = \
                         date_time_controls(True,
                                        self.on_date_picker_changed,
                                        self.on_date_slider_changed,
                                        self.on_time_picker_changed,
                                        self.on_time_slider_changed)
                                  
        #layout b: on/off analysis period
        self.m_period_check_box = forms.CheckBox()
        self.m_period_check_box.Text = "Set analysis period"
        self.m_period_check_box.CheckedChanged += self.on_period_check_changed
        layout_b = EtoUtil.create_layout_from_control_matrix([[self.m_period_check_box]])
        
        #create layout c: To date/ time
        layout_c, self.m_to_date, self.m_to_date_slider, self.m_to_time, self.m_to_time_slider =\
                         date_time_controls(False,
                                        self.on_to_date_picker_changed,
                                        self.on_to_date_slider_changed,
                                        self.on_to_time_picker_changed,
                                        self.on_to_time_slider_changed)
                                  
        
        #layout b: on/off annual
        self.m_annual_check_box = forms.CheckBox()
        self.m_annual_check_box.Text = "Annual"
        self.m_annual_check_box.Checked = True
        self.m_annual_check_box.CheckedChanged += self.on_annual_check_changed
        
        #disable date.time controlls by default (annual is checked)
        neg_annual = not self.m_annual_check_box.Checked
        is_period = self.m_period_check_box.Checked
        self.disable_enable_date_time_controls(neg_annual, is_period) 
        
        layout_d = EtoUtil.create_layout_from_control_matrix([[self.m_annual_check_box]]) 
        
        
        # return group with created layout
                                              
        group_layout = EtoUtil.create_layout_from_control_matrix([[layout_a],
                                                                  [layout_b],
                                                                  [layout_c], 
                                                                  [layout_d]])
                                                                  
        return EtoUtil.create_group_from_layout('Date and Time', group_layout)                                              
        
        
    def create_global_settings_table(self):
        # Select button
        select_center_label = forms.Label(Text = 'Sun path center point:') 
        select_center_label.Size = drawing.Size(140,10) 

        select_center_button = EtoUtil.create_button(
                            text = 'Pick point', 
                            click_event_method = self.on_center_button)   
        
        sun_path_label = forms.Label(Text = 'Sun path scale:')    
        self.m_sun_path_updown = EtoUtil.create_numeric_stepper(decimal_places = 2, 
                                                 increment = 0.1,
                                                 value = 1, 
                                                 change_event_method =\
                                                 self.on_sun_path_scale_changed)
        
        sun_sphere_label = forms.Label(Text = 'Sun sphere scale:') 
        self.m_sun_sphere_updown = EtoUtil.create_numeric_stepper(decimal_places = 2, 
                                                 increment = 0.1,
                                                 value = 1, 
                                                 change_event_method =\
                                                 self.on_sun_sphere_scale_changed)        
        
        layout = EtoUtil.create_layout_from_control_matrix([[select_center_label,
                                                          select_center_button],
                                                         [sun_path_label, 
                                                          self.m_sun_path_updown],
                                                          [sun_sphere_label,
                                                          self.m_sun_sphere_updown]])
                                                          
        return layout
        

        
    # Event Handlers -----------------------------------------------------------
    
    #location events
    def on_north_value_changed(self, sender, e):
        print self.m_vectors
        self.lb_generate_sun_path()
        print self.m_vectors
        
    def on_latitude_value_changed(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_longitude_value_changed(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_timezone_drop_down_closed(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_elevation_value_changed(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_epw_file_path_changed(self, sender, e):
        self.m_epw_file = self.m_epw_file_picker.FilePath
        self.lb_generate_sun_path()
        
    #Date Time Events
    def on_date_slider_changed(self, sender, e):
        days_of_year = self.m_date.Value.DayOfYear 
        days_difference =   self.m_date_slider.Value - days_of_year
        self.m_date.Value = self.m_date.Value.AddDays(days_difference)
        #print "slider changed"
        self.lb_generate_sun_path()
        
    def on_date_picker_changed(self, sender, e):
        self.m_date_slider.Value = self.m_date.Value.DayOfYear
        self.lb_generate_sun_path()
        #print "date picker changed"; print self.m_date.Value
        
    def on_time_slider_changed(self, sender, e):
        hours_difference = self.m_time_slider.Value - self.m_time.Value.Hour
        self.m_time.Value = self.m_time.Value.AddHours(hours_difference)
        #print "hour slider shanged"
                
    def on_time_picker_changed(self, sender, e):
        self.m_time_slider.Value = self.m_time.Value.Hour
        self.lb_generate_sun_path()
        #print "hour picker shanged"
        
    def on_to_date_slider_changed(self, sender, e):
        days_of_year = self.m_to_date.Value.DayOfYear 
        days_difference =   self.m_to_date_slider.Value - days_of_year
        self.m_to_date.Value = self.m_to_date.Value.AddDays(days_difference)
        #print "to slider changed"
        
    def on_to_date_picker_changed(self, sender, e):
        self.m_to_date_slider.Value = self.m_to_date.Value.DayOfYear
        self.lb_generate_sun_path()
        #print "to date picker changed"; print self.m_date.Value
        
    def on_to_time_slider_changed(self, sender, e):
        hours_difference = self.m_to_time_slider.Value - self.m_to_time.Value.Hour
        self.m_to_time.Value = self.m_to_time.Value.AddHours(hours_difference)
        #print "to hour slider shanged"

    def on_to_time_picker_changed(self, sender, e):
        self.m_to_time_slider.Value = self.m_to_time.Value.Hour
        self.lb_generate_sun_path()
        #print "to hour picker shanged"     
        
    def on_period_check_changed(self, sender, e):
        is_period = self.m_period_check_box.Checked
        self.m_to_date_slider.Enabled = is_period
        self.m_to_time_slider.Enabled = is_period
        self.m_to_date.Enabled = is_period
        self.m_to_time.Enabled = is_period 
        self.lb_generate_sun_path()
        
    def on_annual_check_changed(self, sender, e): 
        not_annual = not self.m_annual_check_box.Checked
        is_period = self.m_period_check_box.Checked 
        self.disable_enable_date_time_controls(not_annual, is_period)    
        self.lb_generate_sun_path()
        
    def disable_enable_date_time_controls(self, not_annual, is_period):
        self.m_period_check_box.Enabled = not_annual
        self.m_date_slider.Enabled = not_annual
        self.m_time_slider.Enabled = not_annual   
        self.m_date.Enabled = not_annual
        self.m_time.Enabled = not_annual 
        
        self.m_to_date_slider.Enabled = is_period if not_annual else not_annual
        self.m_to_time_slider.Enabled = is_period if not_annual else not_annual    
        self.m_to_date.Enabled = is_period if not_annual else not_annual
        self.m_to_time.Enabled = is_period if not_annual else not_annual  
        
    # global events    
    def on_center_button(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_sun_path_scale_changed(self, sender, e):
        self.lb_generate_sun_path()
        
    def on_sun_sphere_scale_changed(self, sender, e):
        self.lb_generate_sun_path()
        
        

            
        
    #---------------------------------------------------------------------------
    #Ladybug methods
    #---------------------------------------------------------------------------
    
    # Generate sun path in scene based on dialog parameters
    def lb_generate_sun_path(self):
        
        #instance properties to be reterived by sunlight hours  panel
        self.m_vectors  = []
        self.m_hoys = []
        self.m_timestep = 1 #default - to be implemented in eto   
        
        location = self.lb_location(self.m_epw_file)
        self.m_epw_file = ""
        daylightSavingPeriod = None  # temporary until we fully implement it
        north = self.m_north_updown.Value
        centerPt = Rhino.Geometry.Point3d(0,0,0)
        scale = self.m_sun_path_updown.Value
        sunScale = self.m_sun_sphere_updown.Value
        annual = self.m_annual_check_box.Checked
        hoys = ()
        
        if not self.m_annual_check_box.Checked: 
            month = self.m_date.Value.Month
            day = self.m_date.Value.Day
            hour = self.m_time.Value.Hour
            minute = self.m_time.Value.Minute
            if not self.m_period_check_box.Checked:
                datetime = dt.DateTime(month, day, hour, minute)
                hoys = [datetime.hoy]            
            else:
                to_month = self.m_to_date.Value.Month
                to_day = self.m_to_date.Value.Day
                to_hour = self.m_to_time.Value.Hour
                to_minute = self.m_to_time.Value.Minute                
                anp = ap.AnalysisPeriod(\
                   month, day, hour, to_month, to_day, to_hour, self.m_timestep)
                if anp:
                    analysisPeriod = anp
                    dates = list(anp.datetimes)
                    hoys = list(anp.hoys)
                    
        # initiate sunpath based on location
        sp = Sunpath.from_location(location, north, daylightSavingPeriod)
        # draw sunpath geometry
        sunpath_geo = \
            sp.draw_sunpath(hoys, centerPt, scale, sunScale, annual)
        
        analemma = sunpath_geo.analemma_curves
        compass = sunpath_geo.compass_curves
        daily = sunpath_geo.daily_curves
        
        sunPts = sunpath_geo.sun_geos
        
        suns = sunpath_geo.suns
        self.m_vectors = list(geo.vector(*sun.sun_vector) for sun in suns)
        altitudes = (sun.altitude for sun in suns)
        azimuths = (sun.azimuth for sun in suns)
        centerPt = centerPt or geo.point(0, 0, 0)
        self.m_hoys = list(sun.hoy for sun in suns)
        datetimes = (sun.datetime for sun in suns)
        
        #bake geo in scene
        geo_list = list(sunPts) + list(analemma) + list(compass) + list(daily) + [centerPt]        
        LadybugEto.bakeGeo(geo_list,'lb_sunpath')
            
        return
        
        
    # Generate location from controls or epw file    
    def lb_location(self, epw_file = None):
        
        if epw_file.endswith(".epw"):
            ep = epw.EPW(epw_file)
            location = ep.location
            self.m_loc_name_text_box.Text = location.city
            self.m_numeric_lat_updown.Value = location.latitude
            self.m_numeric_long_updown.Value = location.longitude
            self.m_elev_updown.Value = location.elevation
            self.m_timezone_dropdown.SelectedIndex = location.time_zone + 12
        else:    
            name = self.m_loc_name_text_box.Text
            latitude = self.m_numeric_lat_updown.Value
            longitude = self.m_numeric_long_updown.Value
            timeZone = self.m_timezone_dropdown.SelectedIndex - 12
            elevation = self.m_elev_updown.Value
            location = loc.Location(name, '-', latitude, longitude, timeZone, elevation) 
            
        return location
           