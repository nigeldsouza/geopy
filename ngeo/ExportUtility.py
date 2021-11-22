__author__ = 'Nigel Dsouza'


import os
from subprocess import  call as sbCall
import requests
from osgeo import ogr
from tqdm import tqdm
from ngeo.Workspaces import *
import json

class Export:

    def __init__(self):
        self._mysqlConnection = None
        self._postgresConnection = None


    def setPostgresConnection(self,postGresConnection):

        self._postgresConnection = PostgreSQLWorkspaceFactory(postGresConnection)

    def setMySqlConnection(self,mysqlconnection):

        self._mysqlConnection = MySQLWorkspaceFactory(mysqlconnection)

    def featureClassToPostgres(self,in_layer,outname):
        """
            Exports a feature class/table to postgresSQL database.
            in_layer: Must be an OGR layer object. Use the GetLayer method on a Workspace object.
            postGresConnection: Must be of type "PostgreSQLConnection" present in the "WorkspaceManager" module.
            outname: The name of the output layer.
        """
        try:
            postGresWS = self._postgresConnection


            #Get the projection system and geometry type
            proj = in_layer.GetSpatialRef()
            geomType = in_layer.GetGeomType()

            #Create the schema
            lyr_def = in_layer.GetLayerDefn()

            out_lyr = postGresWS.CreateLayer(outname,lyr_def,geomType,proj)

            if out_lyr is not None:
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                out_lyr.StartTransaction()
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                    # Add field values from input Layer
                    for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
                        try:
                            outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                        except:
                            continue    
                    # Set geometry as centroid
                    geom = inFeature.GetGeometryRef()
                                
                    outFeature.SetGeometry(geom)
                    out_lyr.CreateFeature(outFeature)
                    outFeature = None
                out_lyr.CommitTransaction()    
                print('Exported to {}'.format(outname))
    
        except Exception as e:
            raise e   

    def featureClassToMySQL(self,in_layer,outname):
        """
            Exports a feature class/table to postgresSQL database.
            in_layer: Must be an OGR layer object. Use the GetLayer method on a Workspace object.
            mysqlconnection: Must be of type "MySQLConnection" present in the "WorkspaceManager" module.
            outname: The name of the output layer.
        """
        try:
            mysqlWS = self._mysqlConnection


            #Get the projection system and geometry type
            proj = in_layer.GetSpatialRef()
            geomType = in_layer.GetGeomType()

            #Create the schema
            lyr_def = in_layer.GetLayerDefn()

            out_lyr = mysqlWS.CreateLayer(outname,lyr_def,geomType,proj)

            if out_lyr is not None:
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                out_lyr.StartTransaction()
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                    # Add field values from input Layer
                    for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
                        try:
                            fld_val = inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef())
                            outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), fld_val)
                        except:
                            continue    
                    # Set geometry as centroid
                    geom = inFeature.GetGeometryRef()                           
                    outFeature.SetGeometry(geom)
                    out_lyr.CreateFeature(outFeature)
                    outFeature = None
                out_lyr.CommitTransaction()    
                print('Exported {}'.format( in_layer.GetName()))
    
        except Exception as e:
            raise e   


    def featureclassToshp(self,in_layer, outdir, outname, where_clause = None):
        """
        Exports a featureclass/table to another table or shapefile.
        in_layer: This input must be of type: OGRLayer .
        outdir: The output directory that the .shp will get created.
        outname: The name of the output shapefile.
        where clause(Optional): A subset will be exported based on the given SQL statement.
        Note:This will not work for File Geodatabase use shp_To_FileGDB Instead

        """


        try:

            shpWS = ShapeFileWorkspaceFactory(outdir)

            #Get the projection and gemoetry type of the input layer
            proj = in_layer.GetSpatialRef()
            geomType = in_layer.GetGeomType()
            lyr_def = in_layer.GetLayerDefn()

            out_lyr = shpWS.CreateLayer(outname,lyr_def,geomType,proj)

            if out_lyr is not None:

                if where_clause is not None:
                    in_layer.SetAttributeFilter(where_clause)    
                # Insert the records into the table
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                    # Add field values from input Layer
                    count = out_lyr.GetLayerDefn().GetFieldCount()
                    for i in range(0,count):
                        try:
                            outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                        except:
                            continue
                    # Set geometry as centroid
                    geom = inFeature.GetGeometryRef()
                                
                    outFeature.SetGeometry(geom)
                    out_lyr.CreateFeature(outFeature)
                    outFeature = None
            #Clear the where clause       
            if where_clause is not None:
                in_layer.SetAttributeFilter(None)

            print('Exported {}'.format(outname))    
        except Exception as e:
            raise e   


    def featureclass_To_FileGDB(self,in_layer,out_fdbPath,outname,where_clause = None):
        """
        Exports a featureclass/table to a ESRI file geodatabase
        in_layer: This input must be of type: OGRLayer. This can be a flat table or feature class.
        out_fdbPath: The out file geodatabase(.gdb) path.
        outname: Name of the feature class/table.
        where_clause(Optional): Export only the records what satisfies this condition.
        """

        try:
            outgdb = FileGDBWorkspaceFactory(out_fdbPath)


            #Get the projection and gemoetry type of the input layer
            proj = in_layer.GetSpatialRef()
            geomType = in_layer.GetGeomType()
            lyr_def = in_layer.GetLayerDefn()

            out_lyr = outgdb.CreateLayer(outname,lyr_def,geomType,proj)

            if where_clause is not None:
                in_layer.SetAttributeFilter(where_clause)   

            if out_lyr is not None:
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                    # Add field values from input Layer
                    for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
                        try:
                            outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                        except:
                            continue
                    # Set geometry as centroid
                    geom = inFeature.GetGeometryRef()
                                
                    outFeature.SetGeometry(geom)
                    out_lyr.CreateFeature(outFeature)
                    outFeature = None

                
            if where_clause is not None:
                in_layer.SetAttributeFilter(None)   

            print('Exported {}'.format(outname))    
        
        except ogr.OGRERR_UNSUPPORTED_GEOMETRY_TYPE as e:
            raise e
        except ogr.OGRERR_UNSUPPORTED_OPERATION as e:
            raise e
        except ogr.OGRERR_CORRUPT_DATA as e:
            raise e                 
        except ogr.OGRERR_FAILURE as e:
            raise e
        except Exception as e:
            raise e   


    def fileGDB_To_shp(self,in_gdb,out_dir,layers_to_export):
        """
        Exports ESRI file geodatabase layers to a shapefile/dbf
        layers_to_export:Specify the names of the layers to be exported. 
        Note:You can use the "list_layers_from_Workspace"
        method from the "WorkspaceManager" module if you do not know the name of the layer.
        out_dir: The directory where the feature classes/tables will be exported
    
        """
        try:

            if len(layers_to_export)==0:
                print('Please provide the names of layers to export.')
                return


            shpWs = ShapeFileWorkspaceFactory(out_dir)

            gdbWS = FileGDBWorkspaceFactory(in_gdb)

            for index in tqdm(range(len(layers_to_export)),desc='Exporting to '+out_dir):
            

                layer = gdbWS.GetLayer(layers_to_export[index])
                if layer is not None:

                    proj = layer.GetSpatialRef()
                    geomType = layer.GetGeomType()
                    lyr_def = layer.GetLayerDefn()

                    out_lyr = shpWs.CreateLayer(layers_to_export[index],lyr_def,geomType,proj)

                    if out_lyr is not None:
                        layer.ResetReading()
                        # fidArray =  [feature.GetFID() for feature in layer]
                        for inFeature in layer:
                            # inFeature = layer.GetFeature(i)
                            outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                            # Add field values from input Layer
                            for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
                                try:
                                    outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                                except:
                                    continue
                            # Set geometry as centroid
                            geom = inFeature.GetGeometryRef()
                                
                            outFeature.SetGeometry(geom)
                            out_lyr.CreateFeature(outFeature)
                            outFeature = None

            print('Exported layers to {}'.format(out_dir))  

        except ogr.OGRERR_UNSUPPORTED_GEOMETRY_TYPE as e:
            raise e
        except ogr.OGRERR_UNSUPPORTED_OPERATION as e:
            raise e
        except ogr.OGRERR_CORRUPT_DATA as e:
            raise e                 
        except ogr.OGRERR_FAILURE as e:
            raise e
        except TypeError as e:
            raise e    
        except Exception as e:
            raise e   


    def fileGDB_To_fileGDB(self,in_gdb,out_gdb,layers_to_export):
        """
        Exports multiple file gdb feature classes/ tables to another file gdb.
        in_gdb: The path of the .gdb containing the feature classes/tables to export.
        layers_to_export:Specify the names of the layers to be exported. 
        Note:You can use the "list_layers_from_Workspace"
        methond from the "WorkspaceManager" module if you do not know the name of the layer.
        out_gdb: The path to the destonation  .gdb

        """

        try:
        
            if len(layers_to_export)==0:
                raise Exception('No layer names provided to export')
                
            if in_gdb == out_gdb:
                raise Exception('Input and output GDB is the same')

            ingdb = FileGDBWorkspaceFactory(in_gdb)
            outgdb = FileGDBWorkspaceFactory(out_gdb)

            for index in tqdm(range(len(layers_to_export)),desc="Exporting to {}".format(outgdb.path)):
            

                layer = ingdb.GetLayer(layers_to_export[index])

                #Get the projection and gemoetry type of the input layer
                proj = layer.GetSpatialRef()
                geomType = layer.GetGeomType()
                lyr_def = layer.GetLayerDefn()

                out_lyr = outgdb.CreateLayer(layers_to_export[index],lyr_def,geomType,proj)

                if out_lyr is not None:
                    layer.ResetReading()
                    # fidArray =  [feature.GetFID() for feature in layer]
                    for inFeature in layer:
                        # inFeature = layer.GetFeature(i)
                        outFeature = ogr.Feature(out_lyr.GetLayerDefn())
                        # Add field values from input Layer
                        for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
                            try:
                                outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                            except:
                                continue
                        # Set geometry as centroid
                        geom = inFeature.GetGeometryRef()
                            
                        outFeature.SetGeometry(geom)
                        out_lyr.CreateFeature(outFeature)
                        outFeature = None

                        

            print('Exported layers to {}'.format(out_gdb))                           
        except ogr.OGRERR_UNSUPPORTED_GEOMETRY_TYPE as e:
            raise e
        except ogr.OGRERR_UNSUPPORTED_OPERATION as e:
            raise e
        except ogr.OGRERR_CORRUPT_DATA as e:
            raise e                 
        except ogr.OGRERR_FAILURE as e:
            raise e
        except TypeError as e:
            raise e    
        except Exception as e:
            raise e   


    def tableToTable(self,in_layer,outWS,outname):
        '''
        Exports a layer's attribute table to the out Workspace
        in_layer: Must be of type OGRLayer
        outWS: The workspace you wish to export the attributes to. Must be a workspace object.
        outname: Name of the copied layer
        This function will owerite an existing feature class
        Note: This function will export the attributes based on the filters applied on the input layer. If no filters are applied all features will be exported.
        '''
        try:
            if type(in_layer) is not ogr.Layer:
                raise TypeError('Must be of type OGRLayer')

            if outWS.ifLayerExists(in_layer.GetName()) and in_layer.GetName() == outname:
                print('out layer name cannot be the same as the copy layer in the same workspace.')
                return
                

            lyr_def = in_layer.GetLayerDefn()
            
            newLayer = outWS.CreateLayer(outname,lyr_def,ogr.wkbNone,None)
                        
            if newLayer is not None:
                # Insert the records into the table
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(newLayer.GetLayerDefn())
                    # Add field values from input Layer
                    for i in range(0, newLayer.GetLayerDefn().GetFieldCount()):
                        try:
                            outFeature.SetField(newLayer.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                        except:
                            continue
                    outFeature.SetGeometry(None)
                    newLayer.CreateFeature(outFeature)
                    outFeature = None

            print('Exported table {}'.format(outname))
    
        except TypeError as e:
            raise e    
        except Exception as e:
            raise e   
        return newLayer


    def copyLayer(self,in_layer,outWS,outname):
        '''
        Copy's a layer from one Workspace into the outWS
        in_layer: The layer you wish to copy. Must be of type OGRLayer
        outname: Name of the copied layer.
        outWS: The workspace you wish to export the attributes to. Must be a workspace object.
        This function will owerite an existing feature class
        Note: This function will export features based on the filters applied on the input layer. If no filters are applied all features will be exported.
        '''
        try:
            if type(in_layer) is not ogr.Layer:
                raise TypeError('Must be of type OGRLayer')

            if outWS.ifLayerExists(in_layer.GetName()) and in_layer.GetName() == outname:
                print('out layer name cannot be the same as the copy layer in the same workspace.')
                return
                

            proj = in_layer.GetSpatialRef()
            geomType = in_layer.GetGeomType()
            lyr_def = in_layer.GetLayerDefn()

            newLayer = outWS.CreateLayer(outname,lyr_def,geomType,proj)
            #Get only object id
                
            if newLayer is not None:
                # Insert the records into the table
                in_layer.ResetReading()
                # fidArray =  [feature.GetFID() for feature in in_layer]
                for inFeature in in_layer:
                    # inFeature = in_layer.GetFeature(i)
                    outFeature = ogr.Feature(newLayer.GetLayerDefn())
                    # Add field values from input Layer
                    for i in range(0, newLayer.GetLayerDefn().GetFieldCount()):
                        try:
                            outFeature.SetField(newLayer.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
                        except:
                            continue
                    
                    # Set geometry as centroid
                    geom = inFeature.GetGeometryRef()
                        
                    outFeature.SetGeometry(geom)
                    newLayer.CreateFeature(outFeature)
                    outFeature = None

            print('Copied {}'.format(outname))
        except ogr.OGRERR_UNSUPPORTED_GEOMETRY_TYPE as e:
            raise e
        except ogr.OGRERR_UNSUPPORTED_OPERATION as e:
            raise e
        except ogr.OGRERR_CORRUPT_DATA as e:
            raise e                 
        except ogr.OGRERR_FAILURE as e:
            raise e
        except TypeError as e:
            raise e    
        except Exception as e:
            raise e   
        return newLayer
    

    def exportShpFromGeoServer(self,url,workspace,layername,downloadLocation):
        """
        Downloads a geoserver layer.
        url: Service url.
        workspace: the workspace folder the layer is stored on the geoserver.
        layername: name of the layer.
        downloadLocation: The folder where the file will be downloaded to.
        """

        outfile = os.path.join(downloadLocation,layername)+'.zip'
        print('Starting download...')
        params = {'service': 'WFS',
                'version': '1.0.0',
                'request': 'GetFeature',
                'typeName': workspace+':'+layername,
                'outputFormat': 'SHAPE-ZIP'}
        try:
            r = requests.get(url=url, params=params)
            # total_size = int(r.headers.get('content-length', 0))
            chunkSize = 1024

            with open(outfile, "wb") as f:
                for data in r.iter_content(chunkSize):
                    f.write(data)
    
            print('Download Complete')
            f.close()
        except Exception as e:
            raise e


    def ExportGeoJson(self,workspace,layername):
        '''
        Exports a GeoJson representation of the input layer.
        '''
        jsonString = ""

        try:
            lyr = workspace.GetLayer(layername) 
            if lyr is None:
                print("layer does not exist in workspace")
                return ''
            fieldcount = lyr.GetLayerDefn().GetFieldCount()            
            d  = {}  
            features  = []
            for f in lyr:
                feature = {}

                geom = f.GetGeometryRef()
                geom  = json.loads(geom.ExportToJson())
                attributes = {}    
                
                layerDefinition = lyr.GetLayerDefn()

                fid = f.GetFID()
                attributes['fid'] = fid
                
                for i in range(layerDefinition.GetFieldCount()):
                    lyrdef = layerDefinition.GetFieldDefn(i)
                    name = lyrdef.GetName()
                    attributes[name] = f.GetField(name)
            
                # gdmid = f.GetField('gdmid')
                # name = f.GetField('name')
                # attributes  = {'fid':fid,'gdmid':gdmid,'name':name}
                feature = {'attributes':attributes,'geometry':geom}
                
                features.append(feature)
            d['features'] = features    
            jsonString = json.dumps(d)
            

        except Exception as e:
            raise e


        return jsonString