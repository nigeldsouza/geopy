__author__ = 'Nigel Dsouza'

from abc import ABC,abstractmethod
from osgeo import ogr
import os
from ngeo import WorkspaceManager
from ngeo.ConnectionObjects import *


class Workspace(ABC):

    def __init__(self,path):
        self.path = path
        

    @abstractmethod
    def GetLayer(self,layername):pass

    @abstractmethod
    def CreateLayer(self,layername,layerDef,geometryType,spatialReference=None):pass

    @abstractmethod
    def DeleteLayer(self,layername):pass

    @abstractmethod    
    def ifLayerExists(self,layername):pass

    @abstractmethod    
    def GetLayerCount(self):pass    

    @abstractmethod
    def WorkspaceType(self):pass

class ShapeFileWorkspaceFactory(Workspace):
    
    def __init__(self,path):
       
        self.path = path
        self.__in_driver  = ogr.GetDriverByName('ESRI Shapefile')
        self.__shpFilesDict = {}
 
    def GetLayer(self,layername):
        layer = None

        try:
            self.__loadShpWorkspace()
            if layername in self.__shpFilesDict.keys():
                name = self.__shpFilesDict[layername]                             
                fullname = os.path.join(self.path,name)
                self.ds = self.__in_driver.Open(fullname, 1)   
                layer = self.ds.GetLayer()
        except IndexError as e:
            raise e        
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e    
        except Exception as e:
            raise e    
        return layer   

    def CreateLayer(self,layername,layerDef,geometryType,spatialReference=None):
        '''
        The method creates a layer/Table in the given workspace.
        layerName: The name of the output layer
        fieldDefn: The fields that will make up the schema of the layer. OBJECTID/FID and SHAPE field will be auto created by the datasource.
        geometryType: ogr.wkbPolygon,ogr.wkbPoint etc
        spatiaReference: Tyhe out put spatial reference. Incase of table pass None
        '''    
        out_lyr = None
        try:
            
            extn = '.shp' 

            if geometryType is not None:
                if geometryType == ogr.wkbNone:
                    spatialReference = None
                    extn = '.dbf'

                    
            self.__loadShpWorkspace()    
            if layername in self.__shpFilesDict.keys():
                print('Shapefile by this name already exists')
                self.DeleteLayer(layername)
                                                     
            
            fullname = os.path.join(self.path,layername+extn)
               

            self.ds = self.__in_driver.CreateDataSource(fullname)

            out_lyr =  self.ds.CreateLayer(layername, spatialReference, geometryType)   

            #Add the fields from the field definition        
            if layerDef is not None:
                count = layerDef.GetFieldCount()
                for i in range(0,count):
                    fld_defn = layerDef.GetFieldDefn(i)
                    out_lyr.CreateField(fld_defn)


        except IndexError as e:
            raise e
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e    
        return out_lyr

    def DeleteLayer(self,layername):
        
        try:
            if self.ifLayerExists(layername):                
                name = self.__shpFilesDict[layername]
                fullname = os.path.join(self.path,name)
                self.__in_driver.DeleteDataSource(fullname)
        except IndexError as e:
            raise e
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e    

    def ifLayerExists(self,layername):
        self.__loadShpWorkspace()
        return layername in self.__shpFilesDict.keys()

    def GetLayerCount(self):
        self.__loadShpWorkspace()
        return len(self.__shpFilesDict)
 
    def WorkspaceType(self):
        return 'ESRI Shapefile'           

    def __loadShpWorkspace(self):
         #Get all the available shapefiles present in the dir
        self.__shpFilesDict.clear()
        tableFilesDict = {}
        for file in os.listdir(self.path):
            
            extIndex = file.find('.')
            name = file[0:extIndex]
            if file.endswith(".shp"):
                self.__shpFilesDict[name] = file
            elif file.endswith('.dbf'):
                tableFilesDict[name] = file

        for key,value in tableFilesDict.items():
            if key not in  self.__shpFilesDict.keys():
                 self.__shpFilesDict[key] = value

class FileGDBWorkspaceFactory(Workspace):

    def __init__(self,path):
       
        self.path = path
        self.__in_driver  = ogr.GetDriverByName('FileGDB')
        self.__ds = WorkspaceManager.connectToFileGDB(self.path)          
     
    def GetLayer(self,layername):

        layer = None
        try:
            layer = self.__ds.GetLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e        
        
        return layer    

    
    def CreateLayer(self,layername,layerDef,geometryType,spatialReference=None):

        '''
        The method creates a layer/Table in the given workspace.
        layerName: The name of the output layer
        fieldDefn: The fields that will make up the schema of the layer. OBJECTID/FID and SHAPE field will be auto created by the datasource.
        geometryType: ogr.wkbPolygon,ogr.wkbPoint etc
        spatiaReference: Tyhe out put spatial reference. Incase of table pass None
        '''
        out_lyr = None
        try:
            if self.ifLayerExists(layername):
                self.DeleteLayer(layername)

            if geometryType is None:
                raise ValueError('Geometry type cannot be None')

            if geometryType is not None and geometryType == ogr.wkbNone:
                spatialReference = None

            out_lyr =  self.__ds.CreateLayer(layername, spatialReference, geometryType)   

            #Add the fields from the field definition        
            if layerDef is not None:
                for i in range(0,layerDef.GetFieldCount()):
                    out_lyr.CreateField(layerDef.GetFieldDefn(i))
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e    
        return out_lyr

    def ifLayerExists(self,layername):
        '''
        Checks if a layer by the given name exists in a workspace
        '''
        layer = None
        try:
            layer = self.GetLayer(layername)
        except:
            pass   
        return layer is not None

    def DeleteLayer(self,layername):
        
        try:
            if self.ifLayerExists(layername):
                self.__ds.DeleteLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e    
    
    def GetLayerCount(self):
        return self.__ds.GetLayerCount()
    
    def GetLayerByIndex(self,index):

        return self.__ds.GetLayerByIndex(index)

    def WorkspaceType(self):
        return 'FileGDB'

class PostgreSQLWorkspaceFactory(Workspace):

    def __init__(self,postgresConn):
        
        if type(postgresConn) is not PostgreSQLConnection:
            raise TypeError('Value must be of type PostgreSQLConnection')

        self.path = postgresConn
        self.__in_driver  = ogr.GetDriverByName('PostgreSQL')
        self.__ds = WorkspaceManager.connectToPostGresSql(self.path)          
     
    def GetLayer(self,layername):
        layer = None
        try:
            layer = self.__ds.GetLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e  
        return layer    

    def GetLayerByIndex(self,index):
        return self.__ds.GetLayerByIndex(index)


class MySQLWorkspaceFactory(Workspace):

    def __init__(self,mysqlConn):
        
        if type(mysqlConn) is not MySQLConnection:
            raise TypeError('arg must be of type MySQLConnection')

        self.path = mysqlConn
        self.__in_driver  = ogr.GetDriverByName('MySQL')
        self.__ds = WorkspaceManager.connectToMySql(self.path)          
     
    def GetLayer(self,layername):
        layer = None
        try:
            layer = self.__ds.GetLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e  
        return layer    

    def GetLayerByIndex(self,index):
        return self.__ds.GetLayerByIndex(index)
   
   
    def CreateLayer(self,layername,layerDef,geometryType,spatialReference=None):

        '''
        The method creates a layer/Table in the given workspace.
        layerName: The name of the output layer
        fieldDefn: The fields that will make up the schema of the layer. OBJECTID/FID and SHAPE field will be auto created by the datasource.
        geometryType: ogr.wkbPolygon,ogr.wkbPoint etc
        spatiaReference: Tyhe out put spatial reference. Incase of table pass None
        '''
        out_lyr = None
        
        try:

            if self.ifLayerExists(layername):
                self.DeleteLayer(layername)

            if geometryType is None:
                raise ValueError('Geometry type cannot be None')

            if geometryType is not None and geometryType == ogr.wkbNone:
                spatialReference = None

            out_lyr =  self.__ds.CreateLayer(layername, spatialReference, geometryType)   

            #Add the fields from the field definition        
            if layerDef is not None:
                for i in range(0,layerDef.GetFieldCount()):
                    out_lyr.CreateField(layerDef.GetFieldDefn(i))
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e   
        except Exception as e:
            raise e  
        
        return out_lyr

    def ifLayerExists(self,layername):
        '''
        Checks if a layer by the given name exists in a workspace
        '''
        layer = None
        try:
            layer = self.GetLayer(layername)
        except:
            pass   
        return layer is not None


    def DeleteLayer(self,layername):
        
        try:
            if self.ifLayerExists(layername):
                self.__ds.DeleteLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e  

    def GetLayerCount(self):
        return self.__ds.GetLayerCount()


    def WorkspaceType(self):
        return 'PostgreSQL'

class MemoryWorkspaceFactory(Workspace):

    def __init__(self,name):
       
        self.path = name
        self.__in_driver  = ogr.GetDriverByName('MEMORY')
        self.__ds = self.__in_driver.CreateDataSource(self.path) 
        self.__in_driver.Open(self.path,1)            
     
    def GetLayer(self,layername):
        layer = None
        try:
            layer = self.__ds.GetLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e      
        return layer    

    
    def CreateLayer(self,layername,layerDef,geometryType,spatialReference=None):

        '''
        The method creates a layer/Table in the given workspace.
        layerName: The name of the output layer
        fieldDefn: The fields that will make up the schema of the layer. OBJECTID/FID and SHAPE field will be auto created by the datasource.
        geometryType: ogr.wkbPolygon,ogr.wkbPoint etc
        spatiaReference: Tyhe out put spatial reference. Incase of table pass None
        '''
        out_lyr = None
        try:
            if self.ifLayerExists(layername):
                self.DeleteLayer(layername)

            if geometryType is None:
                raise ValueError('Geometry type cannot be None')

            if geometryType is not None and geometryType == ogr.wkbNone:
                spatialReference = None

            out_lyr =  self.__ds.CreateLayer(layername, spatialReference, geometryType)   

            #Add the fields from the field definition        
            if layerDef is not None:
                for i in range(0,layerDef.GetFieldCount()):
                    out_lyr.CreateField(layerDef.GetFieldDefn(i))
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e  
        except Exception as e:
            raise e        


        return out_lyr

    def ifLayerExists(self,layername):
        '''
        Checks if a layer by the given name exists in a workspace
        '''
        layer = None
        try:
            layer = self.GetLayer(layername)
        except:
            pass   
        return layer is not None


    def DeleteLayer(self,layername):
        
        try:
            if  self.ifLayerExists(layername):
                self.__ds.DeleteLayer(layername)
        except TypeError as e:
            raise e
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e      
    
    def GetLayerCount(self):
        return self.__ds.GetLayerCount()

    def WorkspaceType(self):
        return 'MEOMORY'


