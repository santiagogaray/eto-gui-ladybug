
# Imports
import System
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

class EtoUtil(object):
    
    ##########################################################################    
    #Controls section         
    ##########################################################################
    @staticmethod
    def create_numeric_stepper(decimal_places = 2, increment = 1, value = 0, 
                               min = None, max = None, format_string = None,
                               change_event_method = None):
                                   
        numeric_stepper = forms.NumericStepper()
        numeric_stepper.DecimalPlaces = decimal_places
        numeric_stepper.Increment = increment
        numeric_stepper.Value = value
        if max:
            numeric_stepper.MaxValue = max
        if min:
            numeric_stepper.MinValue = min      
        if format_string:
            numeric_stepper.FormatString = format_string
        if change_event_method:
            numeric_stepper.ValueChanged += change_event_method      
        return numeric_stepper
        
        
        
    @staticmethod    
    def create_slider(value = 0, min = None, max = None, 
                      snap_to_tick = False, tick_frequency = 1,
                      change_event_method = None, is_enabled = True):
                          
        slider = forms.Slider()
        slider.Value = value         
        if max:
            slider.MaxValue = max
        if min:
            slider.MinValue = min
        slider.SnapToTick = True
        slider.TickFrequency = 1
        if change_event_method:
            slider.ValueChanged += change_event_method
        slider.Enabled = is_enabled
        return slider
        
        
    @staticmethod          
    def create_list_box(self, size = drawing.Size(200, 100),
                        selected_event_method = None):
        # Create the listbox
        listbox = forms.ListBox()
        listbox.Size = size
        if selected_event_method :
            listbox.SelectedIndexChanged += selected_event_method
        return listbox
        
        
    @staticmethod       
    def create_button(text='Button', size = None, click_event_method = None, 
        is_enabled = True):
        
        button = forms.Button(Text = text)
        if size :
            button.Size = size
        if click_event_method:
            button.Click += click_event_method   
        button.Enabled = is_enabled
        return button
        

    @staticmethod       
    def create_file_picker(title = 'file picker', 
                           filter = None,
                           file_path_changed_event_method = None):
                                                                   
        file_picker = forms.FilePicker()
        file_picker.Title = title
        if filter:
            file_picker.Filters.Add(forms.FileFilter(filter, ('.'+filter)))
        if file_path_changed_event_method:
            file_picker.FilePathChanged += file_path_changed_event_method 
            
        return file_picker
        
        
    ###########################################################################    
    #layout creation methods 
    ###########################################################################    
    
    @staticmethod    
    def create_group_from_layout(title, layout):
        groupbox = forms.GroupBox(Text = title)
        groupbox.Padding = drawing.Padding(5)
        groupbox.Content = layout        
        return groupbox    
        
        
    @staticmethod
    def create_layout_from_control_matrix(control_matrix,
                                          padding=drawing.Padding(5, 5),
                                          scale_height = False,
                                          spacing = drawing.Size(5, 5)):
        layout = forms.TableLayout(Spacing = spacing)
        layout.Padding = padding
        for control_row in control_matrix:
            cells = [forms.TableCell(elem) for elem in control_row]
            row = forms.TableRow(cells)
            row.ScaleHeight = scale_height
            layout.Rows.Add(row)
            
        return layout 
            




################################################################################
# 
# GridViewUtil Section 
# 
################################################################################



################################################################################
# DropDownCollection & DropDownItem classes
################################################################################
class MultiDataItem(object):
    def __init__(self, item):
        self.item = item

class MultiDataCollection(list):
     
     def __init__(self):
         self.m_multidata_selected_index = 0
         
     @property
     def SelectedIndex(self):
         return self.m_multidata_selected_index
         
     @SelectedIndex.setter    
     def SelectedIndex(self, sel_index):
         self.m_multidata_selected_index = sel_index
         
     def GetItemValueAt(self, index):
        return self[index].item
        
     def GetSelectedItemValue(self):
        return self[self.SelectedIndex].item
         
################################################################################
# RowValues class
################################################################################
class RowValues(object):
   
    # Initializer
    def __init__(self, row_values, row_types, mult_values_index = 0):
        
        self.m_row_data = row_values
        self.m_row_types = row_types
        
        #create MultiDataCollections with MultDataItems with data lists
        for index, type in enumerate(self.m_row_types):
            if type == 'DropDown' or type == 'ListBox':
                multidata_items = MultiDataCollection()
                for item in  row_values[index]:
                    multidata_items.Add(MultiDataItem(item))
                multidata_items.SelectedIndex = mult_values_index
                self.m_row_data[index] = multidata_items
         
    
    def GetItemTypeAt(self, index):
        return self.m_row_types[index]
        
    def SetItemTypeAt(self, index, type):
        self.m_row_types[index] = type      
        
    def GetLengthTypes(self):
        return len(self.m_row_types)         
        
    def GetItemDataAt(self, index):
        return self.m_row_data[index]
    
    def SetItemDataAt(self, index, data):
        self.m_row_data[index] = data
        
    def GetLengthData(self):
        return len(self.m_row_data)    

        
        
################################################################################
# GridViewUtil class
################################################################################
class GridViewUtil(object):
    

    @staticmethod        
    def create_grid_view(num_columns, 
                         column_cell_types,
                         data_matrix,
                         column_headers=None, 
                         column_widths=None,
                         column_editable=True,
                         cell_selection_changed_event_method=None):
                               
        try:          
            #Create Gridview with gridview settings    
            gridview = forms.GridView()  
            
            if not isinstance(column_cell_types, list):
                column_cell_types = [column_cell_types]*num_columns   
                
            
            #Create RowValues objects with data rows and column data types
            collection = [] 
            if isinstance(data_matrix, list):
                for datarow in data_matrix:
                    collection.append(RowValues(datarow, column_cell_types))        
                gridview.DataStore = collection
                    
            if column_headers:
                gridview.ShowHeader = True
            if cell_selection_changed_event_method:
                gridview.SelectionChanged += cell_selection_changed_event_method                
                
            #Create columns with cells  
            
            for type_index in range(num_columns):
                
                cell_type = column_cell_types[type_index]  
                
                # column creation
                if cell_type == 'TextBox':
                    # create text box cell
                    column = GridViewUtil.create_textbox_column(type_index)
                if cell_type == 'CheckBox':  
                    #create checkbox cell    
                    column = GridViewUtil.create_checkbox_column(type_index)
                if cell_type == 'DropDown':
                    #create dropdown custom cell
                    column = GridViewUtil.create_dropdown_column(type_index)
                if cell_type == 'ListBox':
                    column = GridViewUtil.create_listbox_column(type_index)              
                
                #width 
                if isinstance(column_widths, list):
                    if len(column_widths) <= type_index:
                        column.Width = column_widths[-1]
                    else:
                        column.Width = column_widths[type_index]
                #headers
                if isinstance(column_headers, list) and \
                    len(column_headers) > type_index:
                    column.HeaderText = column_headers[type_index]
                    
                #editable
                if isinstance(column_editable, list):
                    if len(column_editable) <= type_index:
                        column.Editable = column_editable[-1]
                    else:
                        column.Editable = column_editable[type_index]
                else:
                    column.Editable = column_editable
                
                #add column to grid    
                gridview.Columns.Add(column)
        except Exception as e:
            print e
            
        return gridview   
     
    
    @staticmethod       
    def create_textbox_column(index):
        try:
            # text box Delegates
            def rowvalues_get_name_delegate(row_values):
                return row_values.GetItemDataAt(index)
                
            def rowvalues_set_name_delegate(row_values, name):
                row_values.SetItemDataAt(index, name)
                #for test log:
                #print row_values.GetItemDataAt(index) + " is new name"
                
            # column with text boxes creation
            column = forms.GridColumn(
                DataCell = forms.TextBoxCell(
                Binding = forms.Binding.Delegate
                 [RowValues, System.String](
                  rowvalues_get_name_delegate, rowvalues_set_name_delegate)))
        except Exception as e:
            print e                 
        return column
            
            
    @staticmethod               
    def create_checkbox_column(index):
        try:
            # check box delegates
            def rowvalues_get_check_delegate(row_values):
                return row_values.GetItemDataAt(index)
                
            def rowvalues_set_checked_delegate(row_values, check):
                row_values.SetItemDataAt(index, check)
                #for test log:
                #print row_values.GetItemDataAt(0) + " ckeckbox is now set to " + \
                    #str(row_values.GetItemDataAt(index))
                    
            #column with check boxes creation
            column = forms.GridColumn(
                        DataCell = forms.CheckBoxCell(
                        Binding = forms.Binding.Delegate
                         [RowValues, System.Nullable[System.Boolean]]
                          (rowvalues_get_check_delegate, 
                           rowvalues_set_checked_delegate)))         
        except Exception as e:
            print e                      
        return column
            
            
    @staticmethod               
    def create_dropdown_column(index):
        return GridViewUtil.create_multidata_colum(index, 'DropDown')
        
    @staticmethod           
    def create_listbox_column(index):
        return GridViewUtil.create_multidata_colum(index, 'ListBox')

    @staticmethod   
    def create_multidata_colum(index, type):
        
        #custom cell create event
        def create_multidata_custom_cell_event(eventArgs):
            try:
                row_values = eventArgs.Item
                control = None
                if type == 'DropDown':
                    control = forms.DropDown() 
                elif type == 'ListBox':
                    control = forms.ListBox()
                else:
                    return
                #drop down delegates
                def multidata_get_item_delegate(multidata_item):
                    return multidata_item.item
                    
                def multidata_get_selected_index_delegate():
                    return row_values.GetItemDataAt(index).SelectedIndex
                    
                def multidata_set_selected_index_delegate(sel_index):
                    row_values.GetItemDataAt(index).SelectedIndex = sel_index
                    #for test log:
                    #name = row_values.GetItemDataAt(0)
                    #num = row_values.GetItemDataAt(index).SelectedIndex 
                    #item = row_values.GetItemDataAt(index).GetItemValueAt(num)
                    #print name + " multidata is now set to " + item                         
                    
                control.ItemTextBinding = \
                    forms.DirectBinding.Delegate[MultiDataItem, System.String]\
                                        (multidata_get_item_delegate)
                                      
                delegate = forms.DirectBinding.Delegate[System.Int32](
                               multidata_get_selected_index_delegate, 
                               multidata_set_selected_index_delegate)
                control.SelectedIndexBinding.Bind(delegate)
                
                control.DataStore = row_values.GetItemDataAt(index)
                #control.BackgroundColor = drawing.Color(0,0,1)
                #control.ShowBorder = False
                #control.SelectedIndexChanged += self.OnSelectedIndexChanged
                print "creating..."
            except Exception as e:
                print e         
            return control        
        
        #create drop down custom cell and drop down column
        cell = forms.CustomCell()
        cell.CreateCell = create_multidata_custom_cell_event
        column = forms.GridColumn(DataCell = cell)
                 
        return column              
            
