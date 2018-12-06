#---------------------------------------------------------------------------
#Ladybug methods called from Eto controls
#---------------------------------------------------------------------------

import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from itertools import chain
import System.Threading.Tasks as tasks


try:
    from honeybee.radiance.analysisgrid import AnalysisGrid
    from honeybee.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
    from honeybee.hbsurface import HBSurface
    from honeybee.hbfensurface import HBFenSurface    
    from honeybee.radiance.properties import RadianceProperties
    from honeybee.radiance.material.plastic import Plastic
    from honeybee.radiance.material.glass import Glass  
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


#loading instances from sticky (comming from somewhere in the Ladybug cosmos)
try:
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()    
except Exception as e:
    raise Exception('\nFailed to import ladybug_ladybug objects:\n\t{}'.format(e))    
    


class LadybugEto(object):
    
    
    @staticmethod
    def createMesh(brep, gridSize):
        ## mesh breps
        def makeMeshFromSrf(i, inputBrep):
            try:
                mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)[0]
                inputBrep.Dispose()
            except:
                print 'Error in converting Brep to Mesh...'
                pass
    
        # prepare bulk list for each surface
        mesh = [None] * len(brep)
    
        # set-up mesh parameters for each surface based on surface size
        meshParam = rc.Geometry.MeshingParameters.Default
        meshParam.MaximumEdgeLength = gridSize
        meshParam.MinimumEdgeLength = gridSize
        meshParam.GridAspectRatio = 1
    
        for i in range(len(mesh)): makeMeshFromSrf(i, brep[i])
        
        return mesh
    
    
    
    @staticmethod
    def getTestPts(inputMesh, movingDis, moveTestMesh= False, parallel = True):
            
            # preparing bulk lists
            testPoint = [[]] * len(inputMesh)
            srfNormals = [[]] * len(inputMesh)
            meshSrfCen = [[]] * len(inputMesh)
            meshSrfArea = [[]] * len(inputMesh)
            
            srfCount = 0
            for srf in inputMesh:
                testPoint[srfCount] = range(srf.Faces.Count)
                srfNormals[srfCount] = range(srf.Faces.Count)
                meshSrfCen[srfCount] = range(srf.Faces.Count)
                meshSrfArea[srfCount] = range(srf.Faces.Count)
                srfCount += 1
    
            try:
                def srfPtCalculator(i):
                    # calculate face normals
                    inputMesh[i].FaceNormals.ComputeFaceNormals()
                    inputMesh[i].FaceNormals.UnitizeFaceNormals()
                    
                    for face in range(inputMesh[i].Faces.Count):
                        srfNormals[i][face] = (inputMesh[i].FaceNormals)[face] # store face normals
                        meshSrfCen[i][face] = inputMesh[i].Faces.GetFaceCenter(face) # store face centers
                        # calculate test points
                        if srfNormals[i][face]:
                            movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                            testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                        # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                        tempMesh = rc.Geometry.Mesh()
                        tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].A]) #0
                        tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].B]) #1
                        tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].C]) #2
                        tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].D]) #3
                        tempMesh.Faces.AddFace(0, 1, 3, 2)
                        massData = rc.Geometry.AreaMassProperties.Compute(tempMesh)
                        meshSrfArea[i][face] = massData.Area
                        massData.Dispose()
                        tempMesh.Dispose()
                        
                        
            except:
                print 'Error in Extracting Test Points'
                pass

            # calling the function
            if parallel:
                tasks.Parallel.ForEach(range(len(inputMesh)),srfPtCalculator)
            else:
                for i in range(len(inputMesh)):
                    srfPtCalculator(i)
            
            if moveTestMesh:
                # find surfaces based on first normal in srfNormals 
                #- It is a simplification we can write a better function for this later
                for meshCount, mesh in enumerate(inputMesh):
                    vector = srfNormals[meshCount][0]
                    vector.Unitize()
                    vector = rc.Geometry.Vector3d.Multiply(movingDis, vector)
                    mesh.Translate(vector.X, vector.Y, vector.Z)
                    
            def flattenList(l):return list(chain.from_iterable(l))

                               
            return flattenList(testPoint), flattenList(srfNormals), flattenList(meshSrfArea), inputMesh        
            
            
    #Bake sun path objects to scene 
    @staticmethod
    def bakeGeo(geo_list, layer):
        
        rs.EnableRedraw(False)
        prev_doc = sc.doc
        sc.doc = rc.RhinoDoc.ActiveDoc
        if "SavedGeo"+layer not in sc.sticky: sc.sticky["SavedGeo"+layer] = []
        
        # delete previous objects from scene 
        for obj in sc.sticky["SavedGeo"+layer]:
            rs.DeleteObject(obj)
                    
        currLayer = rs.CurrentLayer()
        rs.AddLayer(layer)
        rs.CurrentLayer(layer)
        
        #add new objects to scene
        massingObjects = []    
        for geo in geo_list :
            #print geo.GetType()
            if geo.GetType() == rc.Geometry.Curve:
                objDoc = sc.doc.Objects.AddCurve(geo)
            if geo.GetType() == rc.Geometry.NurbsCurve:
                objDoc = sc.doc.Objects.AddCurve(geo)                
            elif geo.GetType() == rc.Geometry.Point3d:
                objDoc = sc.doc.Objects.AddPoint(geo)
            elif geo.GetType() == rc.Geometry.Circle:
                objDoc = sc.doc.Objects.AddCircle(geo)
            elif geo.GetType() == rc.Geometry.Arc:
                objDoc = sc.doc.Objects.AddArc(geo)      
            elif geo.GetType() == rc.Geometry.Mesh:
                objDoc = sc.doc.Objects.AddMesh(geo)    
            else:
                continue
            massingObjects += [rs.coerceguid(objDoc)]
        
        #store objects in sticky for deletion
        sc.sticky["SavedGeo"+layer] = massingObjects
        rs.CurrentLayer(currLayer)    
            
        sc.doc = prev_doc
        rs.EnableRedraw(True)
        
        
    @staticmethod    
    def create_opaque_material(name='default', reflect=0, spec=0, rough=0):
        material = Plastic.by_single_reflect_value(name, reflect, spec, rough)        
        return material
        
        
    @staticmethod    
    def create_glass_material(name='default', tVis=0.6):
        material = Glass.by_single_trans_value(name, tVis)      
        return material        
        
    #sun light hours  analysis    
    @staticmethod        
    def generateAnalysis(test_points,
                            pts_vectors,
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
                            grid_mesh):
                                
                                        
        try:                           
            analysis_grids = AnalysisGrid.from_points_and_vectors(
                                                            test_points,
                                                            pts_vectors,
                                                            name,
                                                            window_groups)
                                                            
            #get analysis recipe                                                
            analysis_recipe = None
            if sun_vectors and sun_vectors[0] != None and \
                hoys and hoys[0] != None and analysis_grids:
                # set a sunlight hours analysis recipe together if there are points
                analysis_recipe = SolarAccessGridBased(
                    sun_vectors, hoys, [analysis_grids], timestep)
            else:    
                print "missing sun vector data"
                return
            
            
            #HB surfaces

            #convert scene hb objects into rhino common
            geo_list = []
            for id in hb_object_ids:
                if rs.IsBrep(id):
                    geo_list += [rc.DocObjects.ObjRef(id).Brep()]
                elif rs.IsMesh(id):
                    geo_list += [rc.DocObjects.ObjRef(id).Mesh()]
                else:
                    continue    
                    
            #preapre paramters  
            if len(geo_list)!=0 and geo_list[0]!=None:
                names = None #not included yet in eto interface (could use scene object name)
                hb_objects = []
                for index, geo in enumerate(geo_list):
                    type = hb_object_types[index]
                    radMat = hb_object_mats[index]                   
                    
                    isNameSetByUser = False
                    if names:
                        isNameSetByUser = True
                        
                    isTypeSetByUser = True
                    if not type:
                        isTypeSetByUser = False
                    
                    rad_prop = RadianceProperties(radMat) if radMat else RadianceProperties()
                    ep_prop = None
                    
                    if radMat and radMat.__class__.__name__ == 'Plastic':
                        hb_objects += HBSurface.from_geometry(names, geo, type, isNameSetByUser,
                                                        isTypeSetByUser, rad_prop, ep_prop)
                    elif radMat and radMat.__class__.__name__ == 'Glass':
                        hb_objects += HBFenSurface.from_geometry(names, geo, isNameSetByUser,
                                                        rad_prop, ep_prop)           
                    
            else:
                print "No valid HB surfaces selected"
                return
            
            # Run analysis   
            rad_scene = None
            if not hb_objects or not analysis_recipe:
                print "Missing HB objects or analysis recipe"
                return
                
            try:
                for obj in hb_objects:
                    assert hasattr(obj, 'isHBObject')
            except AssertionError:
                raise ValueError("\n{} is not a valid Honeybee object.".format(obj))
           
            assert hasattr(analysis_recipe, 'isAnalysisRecipe'), \
                ValueError("\n{} is not a Honeybee recipe.".format(analysis_recipe))
            
            legend_par = analysis_recipe.legend_parameters
            
            #write to file
            

            # Add Honeybee objects to the recipe
            analysis_recipe.hb_objects = hb_objects
            analysis_recipe.scene = rad_scene

            batch_file = analysis_recipe.write(folder, filename)
            
            
            #run if 'save file only' is not checked
            outputs = None
            if not save_file_only:
                if analysis_recipe.run(batch_file, False):
                    try:
                        outputs = analysis_recipe.results()
                    except StopIteration:
                        raise ValueError(
                            'Length of the results is smaller than the analysis grids '
                            'point count [{}]. In case you have changed the analysis'
                            ' Grid you must re-calculate daylight/view matrix!'
                            .format(analysis_recipe.total_point_count)
                        )
            if outputs:
                LadybugEto.displayAnalysis(grid_mesh, outputs, legend_par, filename)
                                                                                                        
        except Exception as e:
            print e           
        
        
    @staticmethod        
    def displayAnalysis(input_mesh, analysis_output, legend_par, filename):
        #get total analysis values
        modes = {'total':0, 'direct':1, 'diffuse':2}
        analysis_result = list(LadybugEto.generateAnalysisGridValues(analysis_output[0], modes['total']))
        global lb_preparation
        global lb_visualization
            
        if lb_visualization  and input_mesh and len(analysis_result)!=0:
            result = LadybugEto.generateDisplay(analysis_result, input_mesh[0], 
                                              None, [], None, None, 
                                              1, 'sunlighthours_'+filename, None, None,
                                              lb_preparation, lb_visualization)
            if result!= -1:
                newLegend= []
                newMesh = result[0]
                [newLegend.append(item) for item in lb_visualization.openLegend(result[1])]
                legendBasePt = result[2]
                meshColors = result[3]
                legendColors = result[4]
                
                
    @staticmethod    
    def generateDisplay(analysisResult, inputMesh, heightDomain, legendPar, 
                   analysisTitle, legendTitle, bakeIt, layerName, lowBoundColor, 
                   highBoundColor, lb_preparation, lb_visualization):
                   
        conversionFac = lb_preparation.checkUnits()
        
        if inputMesh.Faces.Count == len(analysisResult):
            meshStruct = 0
        elif inputMesh.Vertices.Count == len(analysisResult):
            meshStruct = 1
        else:
            warning = 'length of the results [=' + str(len(analysisResult)) + \
                '] is not equal to the number of mesh faces [=' + \
                str(inputMesh.Faces.Count) + '] or mesh vertices[=' + \
                str(inputMesh.Vertices.Count) + '].'
            print warning
            return -1
        
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, \
        legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = \
                            lb_preparation.readLegendParameters(legendPar, False)
                           
        colors = lb_visualization.gradientColor(
            analysisResult, lowB, highB, customColors,lowBoundColor,highBoundColor)
        coloredChart = lb_visualization.colorMesh(colors, inputMesh, True, meshStruct)
        
        if heightDomain!=None:
            coloredChart = lb_visualization.create3DColoredMesh(coloredChart, 
                                analysisResult, heightDomain, colors, meshStruct)
        
        lb_visualization.calculateBB([coloredChart], True)
        
        if not legendTitle:  legendTitle = 'unknown units  '
        if not analysisTitle: analysisTitle = '\nno title'
        
        legendSrfs, legendText, legendTextCrv, textPt, textSize = \
                lb_visualization.createLegend(analysisResult
            , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar
            , legendBasePoint, legendScale
            , legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        
        # generate legend colors
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, 
                                                      customColors,lowBoundColor,
                                                      highBoundColor)
        
        # color legend surfaces
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        
        titlebasePt = lb_visualization.BoundingBoxPar[-2]
        if legendFont == None: legendFont = 'Veranda'
        if legendFontSize == None: 
            legendFontSize = legendScale * (lb_visualization.BoundingBoxPar[2]/20)
            
        titleTextCurve = lb_visualization.text2srf(["\n\n" + analysisTitle], 
                                                   [titlebasePt], legendFont, 
                                                   legendFontSize, legendBold)
        
        if legendBasePoint == None: 
            legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        if bakeIt > 0:
            formatString = "%."+str(decimalPlaces)+"f"
            for count, item in enumerate(legendText):
                try:
                    legendText[count] = formatString % item
                except:pass
            legendText.append(analysisTitle)
            textPt.append(titlebasePt)
            studyLayerName = 'CUSTOM_PRESENTATION'
            if layerName == None: layerName = 'Custom'

            # bake study objects    
            newLayerIndex, l = lb_visualization.setupLayers(
                'Modified Version', 'LADYBUG', layerName, studyLayerName)
            if bakeIt == 1: 
                lb_visualization.bakeObjects(
                    newLayerIndex, coloredChart, legendSrfs, legendText, textPt,
                    textSize, legendFont, None, decimalPlaces, True)
            else: 
                lb_visualization.bakeObjects(newLayerIndex, coloredChart, 
                    legendSrfs, legendText, textPt, textSize, legendFont, 
                    None, decimalPlaces, False)
                    
            #turn on layers (they are off out of bakeObjects method)
            layer = rc.RhinoDoc.ActiveDoc.Layers.FindIndex(newLayerIndex)
            parentIndex = rc.RhinoDoc.ActiveDoc.Layers.Find(layer.ParentLayerId, True)
            parentLayer = rc.RhinoDoc.ActiveDoc.Layers.FindIndex(parentIndex)
            parentLayer.IsVisible = True
            layer.IsVisible = True
            #save the layer on sticky for reference on sunlighthours
            sc.sticky['Eto_DisplayLayerIndex'] = newLayerIndex   
            
        return_data = [coloredChart, 
                       [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], 
                       legendBasePoint, colors, legendColors]
                      
        return return_data

    @staticmethod  
    def generateAnalysisGridValues(_analysisGrid, mode):
        if _analysisGrid:
            
            _modes = ('total', 'direct', 'diffuse')
            hoys_ = _analysisGrid.hoys
            blindStates_ = []
            assert mode < 3, '_mode_ can only be 0: total, 1: direct or 2: sky.'
            
            states = _analysisGrid.parse_blind_states(blindStates_)
            
            print('Loading sum of {} values.'.format(_modes[mode]))
            
            if mode < 2:
                return (v[mode] for v in
                          _analysisGrid.sum_values_by_id(hoys_, blinds_state_ids=states))
            else:
                cValues = _analysisGrid.sum_values_by_id(hoys_, blinds_state_ids=states)
                return (v[0] - v[1] for v in cValues)                
                