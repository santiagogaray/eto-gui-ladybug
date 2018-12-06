import rhinoscriptsyntax as rs
import Rhino.UI
import SunSystemEtoModelessTabbedDialog as LbSun
import scriptcontext as sc

__commandname__ = "ladybugsun"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
    
    print "Opening", __commandname__
    # See if the form is already visible
    if sc.sticky.has_key('sample_modeless_form'):
        return 1
    
    # Create and show form
    form = LbSun.SunSystemEtoModelessForm()
    form.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    form.Show()
    # Add the form to the sticky dictionary so it
    # survives when the main function ends.
    sc.sticky['sample_modeless_form'] = form  
  
    # you can optionally return a value from this function
    # to signify command result. Return values that make
    # sense are
    #   0 == success
    #   1 == cancel
    # If this function does not return a value, success is assumed
    return 0
  
RunCommand(True)