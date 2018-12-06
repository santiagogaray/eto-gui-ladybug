# Imports
import Eto.Drawing as drawing
import Eto.Forms as forms
import Rhino
import scriptcontext as sc
from Eto import FileAction
import rhinoscriptsyntax as rs
from etoutility import *
from ladybugeto import LadybugEto  
from System.Drawing import Color   


################################################################################
# sunLightHoursEtoPanel class
################################################################################
class SunLightHoursEtoPanel(forms.Panel):
    
    # Initializer
    def __init__(self):
        # Basic form initialization
        self.initialize_form()
        # Create the form's controls
        self.create_form_controls()
        #register doc events
        self.create_doc_events()
        #init members
        self.m_test_points = None
        self.m_pts_vectors = None
        self.m_output_mesh = []
        #layer data
        if sc.sticky.has_key('Eto_DisplayLayerIndex'):            
            sc.sticky['Eto_DisplayLayerIndex'] = None   
            
            
    # Basic form initialization
    def initialize_form(self):
        self.Title = 'Sunlight Hours'
        self.Padding = drawing.Padding(5)
        self.Resizable = False
        self.Maximizable = False
        self.Minimizable = False
        self.ShowInTaskbar = False
        self.MinimumSize = drawing.Size(210, 150)
        self.UnLoad += self.on_unload 
        
    # Create all of the controls used by the form
    def create_form_controls(self):
        # Create table layout
        layout = forms.TableLayout()
        layout.Padding = drawing.Padding(10)
        layout.Spacing = drawing.Size(20, 20)
        # Add controls to layout
        layout.Rows.Add(self.create_analysis_objects_group())
        layout.Rows.Add(self.create_global_settings_table())
        layout.Rows.Add(None)
        # Set the content
        self.Content = layout
        
        
        
    def create_analysis_objects_group(self):
        
        #Analyisis grid controls
        gridsurfs_label = forms.Label(Text = 'Analysis grid surfaces:') 
        gridsurfs_label.Size = drawing.Size(140, 15)         
        self.m_gridsurfs_list_box =  EtoUtil.create_list_box(
                    self,
                    size = drawing.Size(140, 60),
                    selected_event_method = self.on_selected_grid_item_changed)
        # 
        gridsize_label = forms.Label(Text = 'Grid size:') 
        gridsize_label.Size = drawing.Size(30, 15) 
        self.m_numeric_gridsize_updown = EtoUtil.create_numeric_stepper(
                                                 decimal_places = 2,
                                                 increment = 0.1,
                                                 value = 5, 
                                                 change_event_method =\
                                                  self.on_gridsize_value_changed)                                                
        
        distsurf_label = forms.Label(Text = 'Distance:') 
        self.m_numeric_distsurf_updown = EtoUtil.create_numeric_stepper(
                                                 decimal_places = 2,
                                                 increment = 0.1,
                                                 value = 0.1, 
                                                 change_event_method =\
                                                  self.on_distsurf_value_changed) 
                                                  
        self.m_add_object_button = EtoUtil.create_button(
                            text = 'Add',
                            size = drawing.Size(65, 21),  
                            click_event_method = self.on_click_add_grid_object)
                          
        self.m_remove_object_button = EtoUtil.create_button(
                            text = 'Remove',
                            size = drawing.Size(65, 21),
                            click_event_method = self.on_click_remove_grid_object)   
        
        layout_a1 = EtoUtil.create_layout_from_control_matrix([
                                                [gridsurfs_label],
                                                [self.m_gridsurfs_list_box]],
                                                padding=drawing.Padding(5, 5, 5, 0))

                                            
        layout_a2 = EtoUtil.create_layout_from_control_matrix([
                                                [gridsize_label], 
                                                [self.m_numeric_gridsize_updown],
                                                [distsurf_label], 
                                                [self.m_numeric_distsurf_updown]])
                                                  
        layout_a3 = EtoUtil.create_layout_from_control_matrix([
                                                [self.m_add_object_button,
                                                 self.m_remove_object_button]],
                                                 padding=drawing.Padding(5, 0, 5, 5))
                                                 
        layout_a = EtoUtil.create_layout_from_control_matrix([
                                                    [layout_a1, layout_a2],
                                                    [layout_a3, None]],
                                                    padding=drawing.Padding(0, 0, 0, 5))
        
        #HB Objects controls
        hb_objects_label = forms.Label(Text = 'HB surfaces:')   
        self.m_hb_object_ids = []  
        self.m_hb_column_cell_type = ['TextBox', 'DropDown', 'DropDown']
        column_headers = ['Object', 'Type', 'Material'] 
        self.m_hb_type_items = ['Auto','Wall', 'Und.Wall', 'Roof', 'Und.Ceiling',
                                'Floor','Und.Slab', 'SlabOnGrade', 'Exp.Floor',
                                'Ceiling','AirWall', 'Window', 'Context']
        self.m_hb_material_items = ['Refl.0.3','Refl.0.0', 'Refl.0.5', 'Refl.0.8',
                                    'Glass.0.3','Glass.0.6','Glass.0.9']
        column_widths = [85, 75, 75]   
        column_editables = [False, True, True]
        data_matrix = []   
                                       
        self.m_hb_objects_gridview = GridViewUtil.create_grid_view(
                                                3,
                                                self.m_hb_column_cell_type,                                                
                                                data_matrix,
                                                column_headers,
                                                column_widths,
                                                column_editables,
                                                self.on_hb_gridview_cell_changed)                                                
                                                                                    
        self.m_hb_objects_gridview.Size = drawing.Size(-1, 200)  
        
        self.m_add_hb_object_button = EtoUtil.create_button(
                            text = 'Add',
                            size = drawing.Size(65, 21), 
                            click_event_method = self.on_click_add_hb_object)
                            
        self.m_remove_hb_object_button = EtoUtil.create_button(
                            text = 'Remove',
                            size = drawing.Size(65, 21),  
                            click_event_method = self.on_click_remove_hb_object)  
                            
        self.m_props_hb_object_button = EtoUtil.create_button(
                            text = 'Properties',
                            size = drawing.Size(65, 21),  
                            click_event_method = self.on_click_props_hb_object,
                            is_enabled = False)
                            
        layout_b1 = EtoUtil.create_layout_from_control_matrix([
                                                [self.m_add_hb_object_button,
                                                 self.m_remove_hb_object_button,
                                                 self.m_props_hb_object_button]],
                                                 drawing.Padding(0, 0, 0, 5))
                                                      
        layout_b = EtoUtil.create_layout_from_control_matrix([
                                                     [hb_objects_label],
                                                     [self.m_hb_objects_gridview],
                                                     [layout_b1]],
                                                     drawing.Padding(5, 20, 5, 20))
                                                     
                                                     
        layout_main = EtoUtil.create_layout_from_control_matrix([[layout_a],
                                                                [layout_b]])
                         
        # return group with created layout       
        return EtoUtil.create_group_from_layout('Objects', layout_main)


    def create_global_settings_table(self):
        #project path and name
        project_path_label = forms.Label(Text = 'Project folder:') 
        self.m_project_path_picker = EtoUtil.create_file_picker(
                                            title = "Select project folder") 
                                             
                                             
        self.m_project_path_picker.FilePath = 'c:\ladybug'       
        self.m_project_path_picker.FileAction = FileAction.SelectFolder
        self.m_project_path = "c:\ladybug"        
        layout_a = EtoUtil.create_layout_from_control_matrix([
                                                    [project_path_label],
                                                    [self.m_project_path_picker]],
                                                    drawing.Padding(5, 30, 5, 0))

        project_name_label = forms.Label(Text = 'Project name:')  
        project_name_label.Size = drawing.Size(140, 14)
        self.m_project_name_text_box = forms.TextBox()   
        self.m_project_name_text_box.Text = "Project1" 
        
        self.m_save_file_check_box = forms.CheckBox()
        self.m_save_file_check_box.Text = "Write file only"

        self.m_run_analysis_button = EtoUtil.create_button(
                            text = 'Run Analysis',
                            size = drawing.Size(140, 24), 
                            click_event_method = self.on_click_run_analysis)
                            
        layout_b = EtoUtil.create_layout_from_control_matrix([
                                                    [project_name_label, None],
                                                    [self.m_project_name_text_box]],
                                                     drawing.Padding(5, 0, 5, 5))
        layout_c = EtoUtil.create_layout_from_control_matrix([
                                                     [self.m_run_analysis_button,
                                                      self.m_save_file_check_box,]],
                                                      drawing.Padding(5, 10, 5, 5))
                                                     
        return EtoUtil.create_layout_from_control_matrix([[layout_a],
                                                          [layout_b],
                                                          [layout_c]],
                                                          drawing.Padding(0,5))
                                                    
        
    #Event Handlers -----------------------------------------------------------
    
    #Analysis grid events
    def on_gridsize_value_changed(self, sender, e):
        print " grid size changed"
            
            
    def on_distsurf_value_changed(self, sender, e):
        print "distance to surf changed"
        
        
    def on_click_add_grid_object(self, sender, e):
        
        objects = sc.doc.Objects.GetSelectedObjects(False, False)
        item_list = [item.Tag for item in self.m_gridsurfs_list_box.Items]
        
        for obj in objects:
            #invalid selection type?
            if not rs.IsBrep(obj.Id) and not rs.IsMesh(obj.Id):
                return            
            #already in list?
            if obj.Id in item_list:
                return   
            #create list item
            item = forms.ListItem()
            item.Text = obj.ShortDescription(False)
            if obj.Name:
                item.Text += " - " + obj.Name
            item.Tag = obj.Id
            self.m_gridsurfs_list_box.Items.Add(item)
            
        self.lb_generate_test_points()
    
    
    def on_click_remove_grid_object(self, sender, e):
   
        objects = list(sc.doc.Objects.GetSelectedObjects(False, False))
        if len(objects):
            object = objects[0]
            for item in self.m_gridsurfs_list_box.Items:
                if item.Tag == object.Id:
                    self.m_gridsurfs_list_box.Items.Remove(item)
                    Rhino.RhinoApp.RunScript("_SelNone", False)                        
                    break
                    
        self.lb_generate_test_points()            


    def on_selected_grid_item_changed(self, sender, e):
        index = self.m_gridsurfs_list_box.SelectedIndex
        if index >= 0:
            item = self.m_gridsurfs_list_box.Items[index]
            Rhino.RhinoApp.RunScript("_SelNone", False)
            Rhino.RhinoApp.RunScript("_SelId " + item.Tag.ToString() + " _Enter", False)

    
    
    def on_click_add_hb_object(self, sender, e):
        
        objects = sc.doc.Objects.GetSelectedObjects(False, False)
        
        for obj in objects:
            if not rs.IsBrep(obj.Id) and not rs.IsMesh(obj.Id):
                return
            #check object on list
            if obj.Id in self.m_hb_object_ids:
                return 
            #create grid item row
            itemText = obj.ShortDescription(False)
            if obj.Name:
                itemText += " - " + obj.Name
            self.m_hb_object_ids += [obj.Id]
            datarow = [itemText, self.m_hb_type_items, self.m_hb_material_items]
            #update grid values
            self.m_hb_objects_gridview.DataStore += \
                [RowValues(datarow, self.m_hb_column_cell_type)]

            
            
    def on_click_remove_hb_object(self, sender, e):
        
        objects = list(sc.doc.Objects.GetSelectedObjects(False, False))
        
        if len(objects):
            rows_data = self.m_hb_objects_gridview.DataStore
            object = objects[0]
            for index, item in enumerate(self.m_hb_object_ids):
                if item == object.Id:
                    del self.m_hb_object_ids[index]
                    del rows_data[index]                    
                    Rhino.RhinoApp.RunScript("_SelNone", False)     
                    break
            #update grid values         
            self.m_hb_objects_gridview.DataStore = rows_data       
                     
            
    def on_click_props_hb_object(self, sender, e):
        pass        
        
    def on_hb_gridview_cell_changed(self, sender, e):
        try:
            index = self.m_hb_objects_gridview.SelectedRow
            if index >= 0 and index < len(self.m_hb_object_ids):
                id = self.m_hb_object_ids[index]
                Rhino.RhinoApp.RunScript("_SelNone", False)
                Rhino.RhinoApp.RunScript("_SelId " + id.ToString() + " _Enter", False)
        except Exception as e:
            print e        
        
        
        
    def on_click_run_analysis(self, sender, e):        
        self.lb_generate_analysis()
        
        
        
    # Document event handlers
    def on_close_document(self, sender, e):
        self.m_gridsurfs_list_box.Items.Clear()
        self.m_hb_objects_gridview.DataStore = ()
        self.m_hb_object_ids = []
        
        
    def on_select_objects(self, sender, e):
        
        if e.RhinoObjects.Length == 1:
            # select analysis grid surface object if in list
            i = 0
            for item in self.m_gridsurfs_list_box.Items:
                if item.Tag == e.RhinoObjects[0].Id:
                    self.m_gridsurfs_list_box.SelectedIndex = i
                    break
                else:
                    i += 1
            # select hb surface object if in grid view      
            i = 0            
            for item in self.m_hb_object_ids:
                if item == e.RhinoObjects[0].Id:
                    self.m_hb_objects_gridview.SelectedRow = i
                    break
                else:
                    i += 1                    
        else:
            self.m_gridsurfs_list_box.SelectedIndex = -1
            self.m_hb_objects_gridview.SelectedRow = -1
            
            
            
    def on_delete_rhino_object(self, sender, e):

        try:
            #delete from analysis grid object list if included
            for item in self.m_gridsurfs_list_box.Items:
                if item.Tag == e.ObjectId:
                    self.m_gridsurfs_list_box.Items.Remove(item)
                    break
                    
            #delete from hb object list if included 
            rows_data = self.m_hb_objects_gridview.DataStore            
            for index, item in enumerate(self.m_hb_object_ids):
                if item == e.ObjectId:
                    del self.m_hb_object_ids[index]                   
                    del rows_data[index] 
                    break
            #update grid values         
            self.m_hb_objects_gridview.DataStore = rows_data
            
        except Exception as e:
            print e                          
      
    # Create Rhino event handlers
    def create_doc_events(self):
        Rhino.RhinoDoc.CloseDocument += self.on_close_document
        Rhino.RhinoDoc.DeleteRhinoObject += self.on_delete_rhino_object
        Rhino.RhinoDoc.SelectObjects += self.on_select_objects
        
    # Remove Rhino event handlers
    def remove_doc_events(self):        
        Rhino.RhinoDoc.CloseDocument -= self.on_close_document
        Rhino.RhinoDoc.DeleteRhinoObject -= self.on_delete_rhino_object
        Rhino.RhinoDoc.SelectObjects -= self.on_select_objects

    def on_unload(self, sender, e):
        self.remove_doc_events()



    #---------------------------------------------------------------------------
    #Ladybug methods
    #---------------------------------------------------------------------------

    def lb_generate_test_points(self):
        
        
        try:
            #load breps/meshes from analysis grid object list
            brep_list = []
            mesh_list = []            
            for item in  self.m_gridsurfs_list_box.Items:
                    if rs.IsBrep(item.Tag):
                        brep_list += [Rhino.DocObjects.ObjRef(item.Tag).Brep()]
                    elif rs.IsMesh(item.Tag):
                        mesh_list += [Rhino.DocObjects.ObjRef(item.Tag).Mesh()]
                    else:
                        continue
                      
            #prepare grid paramers
            grid_size = self.m_numeric_gridsize_updown.Value   
            dist_base_surf = self.m_numeric_distsurf_updown.Value
            move_test_mesh = False
            
            #create meshes from breps, add to mesh list
            
            input_mesh = mesh_list + LadybugEto.createMesh(brep_list, grid_size)
            self.m_output_mesh = []
            self.m_test_points = []
            self.m_pts_vectors = []
            for index, mesh in enumerate(input_mesh):
                test_points, pts_vectors, faces_area, output_mesh = \
                                        LadybugEto.getTestPts(
                                                                [mesh], 
                                                                dist_base_surf, 
                                                                move_test_mesh)
                self.m_test_points += [test_points]
                self.m_pts_vectors += [pts_vectors]
                self.m_output_mesh += output_mesh
                
            #update meshes in scene
            LadybugEto.bakeGeo(self.m_output_mesh, 'lb_sunlighthours')

        except Exception as e:
            print e   
        
        
    def lb_generate_analysis(self):
        
        try:
            if self.m_test_points == None: 
                print "missing grid objects"
                return      
                
            #prepare paramters
            window_groups = []   #not included yet in eto interface  
            name = 'default_name'#not included yet in eto interface  
            sun_path_panel = list(self.Parents)[-1].get_sun_path_panel()  
            sun_vectors = sun_path_panel.m_vectors
            hoys = sun_path_panel.m_hoys        
            timestep = sun_path_panel.m_timestep     
            #hb objects data 
            hb_object_ids = self.m_hb_object_ids
            hb_object_types, hb_object_mats = self.lb_get_hb_objects_data()
            #project data
            folder = self.m_project_path_picker.FilePath
            filename = self.m_project_name_text_box.Text            
            save_file_only = self.m_save_file_check_box.Checked
            
            #turn off last results layers
            if 'Eto_DisplayLayerIndex' in sc.sticky and sc.sticky['Eto_DisplayLayerIndex']:
                last_layer_index = sc.sticky['Eto_DisplayLayerIndex']
                last_layer = Rhino.RhinoDoc.ActiveDoc.Layers.FindIndex(last_layer_index)
                last_layer_name = rs.LayerName(last_layer.Id, True)
                last_parentLayer = rs.LayerName(last_layer.ParentLayerId, True) 
                rs.LayerVisible(last_parentLayer, False)  
            results_layer = None
            
            # generate multiple analysis baked in scene - one analysis per mesh
            for index, mesh_item in enumerate(self.m_output_mesh): 
                rs.EnableRedraw(False)
                points_item = self.m_test_points[index]
                vectors_item = self.m_pts_vectors[index]
                LadybugEto.generateAnalysis(points_item,
                                            vectors_item,
                                            name,
                                            window_groups,
                                            sun_vectors,
                                            hoys,
                                            timestep,
                                            hb_object_ids,
                                            hb_object_types,
                                            hb_object_mats,
                                            folder,
                                            filename,
                                            save_file_only,
                                            [mesh_item])
                #consolidate multiple result objects into one layer (workaround to
                #solve current ladybug_ResultVisualization.bakeObjects behaviour)
                layer_index = sc.sticky['Eto_DisplayLayerIndex']
                last_layer = Rhino.RhinoDoc.ActiveDoc.Layers.FindIndex(layer_index)
                last_layer_name = rs.LayerName(last_layer.Id, True)
                p_layer_name = rs.LayerName(last_layer.ParentLayerId, True)  
                #use first analysis layers
                if index == 0: 
                    results_layer_index = layer_index
                    results_layer = last_layer_name
                    results_p_layer = p_layer_name
                #delte all subsequent analysis layers
                elif last_layer_name <> results_layer:
                    #Move all objects to analysis layer and delete layers       
                    objects_id = rs.ObjectsByLayer(last_layer_name)
                    res = list(rs.ObjectLayer(obj_id, results_layer) for obj_id in objects_id)  
                    rs.DeleteLayer(last_layer_name)
                    rs.DeleteLayer(p_layer_name)
                rs.EnableRedraw(True)
                
            #replace the sticky to results layer used    
            sc.sticky['Eto_DisplayLayerIndex'] = results_layer_index    
            
            #copy original analysis surfaces hb objects to analisys layer created
            rs.EnableRedraw(False)            

            #copy analysis grid
            new_layer_name = rs.AddLayer(results_p_layer+"::Analysis_grid_objects", color=Color.Red)
            gridsurfs_ids = list(item.Tag for item in self.m_gridsurfs_list_box.Items)
            new_grid_objects = rs.CopyObjects(gridsurfs_ids)
            res = list(rs.ObjectLayer(obj_id, new_layer_name) for obj_id in new_grid_objects)
            
            #copy hb objects 
            new_layer_name = rs.AddLayer(results_p_layer+"::HB_objects", color=Color.LightGreen)
            new_grid_objects = rs.CopyObjects(self.m_hb_object_ids)
            res = list(rs.ObjectLayer(obj_id, new_layer_name) for obj_id in new_grid_objects)  
             
            rs.EnableRedraw(True)
            
        except Exception as e:
            print e                                          

    def lb_get_hb_objects_data(self):
        #hb data
        rows = self.m_hb_objects_gridview.DataStore
        #extract types
        hb_objects_type_name = list(row.GetItemDataAt(1).GetSelectedItemValue() for row in rows)
        hb_types = {'Auto':None, 'Wall':0, 'Und.Wall':0.5, 'Roof':1, 'Und.Ceiling':1.5,  
                    'Floor':2,'Und.Slab':2.25, 'SlabOnGrade':2.5, 'Exp.Floor':2.75,
                    'Ceiling':3, 'AirWall':4, 'Window':5, 'Context':6}
        hb_objects_type =  list(hb_types[type_name] for type_name in hb_objects_type_name)      
        #extract materials
        hb_objects_mat_names = list(row.GetItemDataAt(2).GetSelectedItemValue() for row in rows)
        hb_materials = {'Refl.0.3':LadybugEto.create_opaque_material('Refl.0.3', 0.3),
                        'Refl.0.0':LadybugEto.create_opaque_material('Refl.0.0', 0.0),
                        'Refl.0.5':LadybugEto.create_opaque_material('Refl.0.5', 0.5),
                        'Refl.0.8':LadybugEto.create_opaque_material('Refl.0.8', 0.8),
                        'Glass.0.3':LadybugEto.create_glass_material('Glass.0.3', 0.3),                        
                        'Glass.0.6':LadybugEto.create_glass_material('Glass.0.6', 0.6),
                        'Glass.0.9':LadybugEto.create_glass_material('Glass.0.9', 0.9)}
        hb_objects_mat =  list(hb_materials[mat_name] for mat_name in hb_objects_mat_names)   
      
        return [hb_objects_type, hb_objects_mat]             
