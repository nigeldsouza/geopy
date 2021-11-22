__author__ = 'Nigel Dsouza'

import os
from osgeo import ogr


def createFileGDB(dir,name):
    """
    Creates a file gdb at the specified location  and returns the data source
    """

    gdbPath = os.path.join(dir,name+'.gdb')

    driver = ogr.GetDriverByName('FileGDB')
    if driver is None:
       raise Exception("FileGDB driver not available.")

    ds = driver.CreateDataSource(gdbPath)

    return  ds

def connectToFileGDB(fgb_path):
    """
    Connects to a ESRI File Geodatabase and returns the data source
    """

    driver = ogr.GetDriverByName('FileGDB')
    if driver is None:
        raise Exception("FileGDB driver not available.")

    ds = driver.Open(fgb_path,1)
    
    return ds

def connectToPostGresSql(postgre_connection):
    """
   Connect to postgres SQl database
    """
    ds = ogr.Open(postgre_connection.connstring(),1)

    return ds 

def connectToMySql(mysql_connection):
    """
    Connect to postgres SQl database
    """
    ds = ogr.Open(mysql_connection.connstring(),1)

    return ds 


def list_layers_from_Workspace(workspace,geomtype):
    """
    Returns layer names in a workspace based on the geometry type.
    workspace: The must be  Workspace object.
    geomtype: Can be any of the following options: 'ALL','POLYGON','POLYLINE','POINT','TABLE'

    """
    try:
        layernames = []
        
        geomtypes = {'ALL':'ALL',
                    'POLYGON':[ogr.wkbPolygon,ogr.wkbMultiPolygon,ogr.wkbPolygonZM,ogr.wkbPolygonM,ogr.wkbMultiPolygonM,ogr.wkbMultiPolygonZM],
                    'POLYLINE':[ogr.wkbLineString,ogr.wkbLineStringZM,ogr.wkbLineStringM,ogr.wkbMultiLineString,ogr.wkbMultiLineStringM,ogr.wkbMultiLineStringZM],
                    'POINT':[ogr.wkbPoint,ogr.wkbPointM,ogr.wkbPointZM,ogr.wkbMultiPoint,ogr.wkbMultiPointZM,ogr.wkbMultiPointM],
                    'TABLE':[ogr.wkbNone]}


        if geomtype not in list(geomtypes.keys()):
            print('geomtype must be one of the following values {}'.format(str(geomtypes)))
            return

        
        layerCount = workspace.GetLayerCount()
        if layerCount < 1:
            print('No layers present in workspace')
            return

        if workspace.WorkspaceType() == "ESRI Shapefile":
            names = workspace._ShapeFileWorkspaceFactory__shpFilesDict
            if(geomtype == 'ALL'):
                layernames = list(names.keys()) 
            else:
                gtype = geomtypes[geomtype]
                layernames =  [name for name in names if workspace.GetLayer(name).GetGeomType() in gtype]   
        else: 
            if(geomtype == 'ALL'):
                layernames =  [workspace.GetLayerByIndex(featsClass_idx).GetName() for featsClass_idx in range(layerCount)]   
            else:      
                gtype = geomtypes[geomtype]
                layernames =  [workspace.GetLayerByIndex(featsClass_idx).GetName() for featsClass_idx in range(layerCount) if workspace.GetLayerByIndex(featsClass_idx).GetGeomType() in gtype]   
    except TypeError as e:
        raise e
    except AttributeError as e:
            raise e
    # except ogr.OGRERR_FAILURE as e:
    #         raise e    
    except Exception as e:
            raise e     
    return layernames