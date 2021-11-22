__author__ = 'Nigel Dsouza'

import os
from osgeo import ogr
import LayerUtils
from ngeo.Workspaces import *

class FieldMap:
     
     def __init__(self,inputfieldName,outputFieldName):
        self.InFieldName = inputfieldName
        self.OutFieldName = outputFieldName

class FieldMapping:

    '''
    This class maps the fields between two feature classes.
    By default all the fields having the same name are auto mapped once the init method is called.
    If you wish to added your own field map the use the removeAllFieldMaps followed by the addFieldMap method.
    '''
    
    def __init__(self,in_table,dest_table):

        if in_table is None or in_table is None:
            raise TypeError
        
        self.__mappings = []
      
        self.src_table = in_table
        self.dest_table = dest_table    
        self.__tbl1LyrDef = self.src_table.GetLayerDefn()
        self.__tbl2LyrDef = self.dest_table.GetLayerDefn()

        for i in range(self.__tbl2LyrDef.GetFieldCount()):
            name = self.__tbl2LyrDef.GetFieldDefn(i).GetName()
            index = self.__tbl1LyrDef.GetFieldIndex(name)
            if index > -1:
                fldMap = FieldMap(name,name)
                self.__mappings.append(fldMap)


    def is_test(self):
        '''
        Returns True if all the fields of the source table match to that of the destination table
        '''
        return len(self.__mappings) == self.__tbl2LyrDef.GetFieldCount()

    def getFieldMappingCount(self):
        return len(self.__mappings)

    def removeAllFieldMaps(self):
        self.__mappings.clear()

    def addFieldMap(self,fieldMap):
        self.__mappings.append(fieldMap)

    def validateFieldMap(self):
        '''
        Removes any field map that contains fields that does not exists in the
        input and output feature classes
        '''
        for map in list(self.__mappings):
            inFldName = map.InFieldName
            outFldName = map.OutFieldName
            index = self.__tbl1LyrDef.GetFieldIndex(inFldName)           
            index2 = self.__tbl2LyrDef.GetFieldIndex(outFldName)
            if index == -1 or index2 == -1:
               self.__mappings.remove(map)

    def getFieldMappings(self):
        return self.__mappings

def Buffer(in_layer,outdir,outname,bufferDistance):

    try:
        # Create the in and out drivers

        shpWS = ShapeFileWorkspaceFactory(outdir)
        #Get the projection and gemoetry type of the input layer
        proj = in_layer.GetSpatialRef()


        # Create the empy layer with the layer definition(schema)

        out_lyr = shpWS.CreateLayer(outname, proj, ogr.wkbPolygon)

        in_layer.ResetReading()
        # Insert the records into the table
        for feature in in_layer:
            bufferFeature = feature.Clone()
            geo = feature.GetGeometryRef()
            bufferGeometry = geo.Buffer(bufferDistance)

            bufferFeature.SetGeometry(bufferGeometry)
            out_lyr.CreateFeature(bufferFeature)

       
    
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

def CalculateField(in_layer,field_Name,expression,code_block =None):
    '''
    This tool calculates a field based on a certain expression
    in_layer: Must be an ogr layer
    field_Name: The name of the field that the expression result will be applied
    expression: This can be a function name or a value that will be applied to the field_Name.
    code_block (Optional): Must be a python script containing some logic that will retrun a value to be applied 
                           to the input field. 
    '''
    firtindex = expression.find('(')
    lastindex = expression.find(')')
    columnNames = []
    
    try:
        #Do this only if there is a function to execute
        if code_block is not None:
            #Get the column names that will be used to calculate the input field
            tablevalues = expression[firtindex+1:lastindex]
            if tablevalues != '':
                columnNames = tablevalues.split(',')

            expression = "c = "+expression
            exec(code_block,globals())

        nameVal = {}

        in_layer.ResetReading()
        for f in in_layer:
            nameVal.clear()

            #Get the field values check the datatype and proceed
            for column in columnNames:
                val = f.GetField(column)

                if type(val) is str:
                    nameVal[column] =  "'"+val+"'"
                else:
                    nameVal[column] =  str(val)            

            finalStr = ''

            for key in nameVal.keys():
                finalStr =  expression.replace(key, nameVal[key] )

            if len(nameVal.keys()) == 0:
                finalStr = expression
            
          
            if code_block is None:
                f.SetField(field_Name,expression)  
            else:
                exec(finalStr,globals())     
                if c is not None:                   
                    f.SetField(field_Name,c)     
            
            in_layer.SetFeature(f)
        print('Field calculated!')
        
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
    except IndexError as e:
        raise e 
    except IndentationError as e:
        raise e         
    except Exception as e:
        raise e    
    finally:
        in_layer.ResetReading()


def JoinField(in_Layer,inField,joinLayer,joinField,fields):
    '''
    inLayer - Source input vector layer. The final attribute table will be added to this  layer.
    inField - The field in the inLayer table on which the join will be based
    joinLayer - Layer with the attribute table to join.
    JoinField - The field in the input table on which the join will be based.
    fields - Provide list of the fields to be joined to the input layer, input type is list.
    returns dictionary with created field name and orignal name

    '''
   
    try:
        fieldDic ={}
        # creating fields
        for field in fields:
            fieldindex = joinLayer.FindFieldIndex(field,0)
            layerdef=  joinLayer.GetLayerDefn()
            fielddef = layerdef.GetFieldDefn(fieldindex)
            Field = ogr.FieldDefn(field,fielddef.GetType())
            in_Layer.CreateField(Field)

            #Get the last field added to the field collection
            lastFieldIndex = in_Layer.GetLayerDefn().GetFieldCount()-1
            fieldDic[field]  = in_Layer.GetLayerDefn().GetFieldDefn(lastFieldIndex).GetName()

        in_Layer.ResetReading()
        joinLayer.ResetReading()

        for feature in in_Layer:

            joinKey = feature.GetField(inField)

        
            clause = LayerUtils.generateWhereClause(LayerUtils.getFieldDefn(joinLayer,joinField),joinKey,False,False)

            joinLayer.SetAttributeFilter(clause)
            joinfeature = joinLayer.GetNextFeature()
            if joinfeature is not None:

                for key,field in fieldDic.items():

                    value = joinfeature.GetField(key)
                    feature.SetField(field,value)
                    in_Layer.SetFeature(feature)
                
        
        joinLayer.SetAttributeFilter(None)
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
    except IndexError as e:
        raise e      
    except Exception as e:
        raise e      
    return fieldDic

def Append(in_layer,target_layer,schema_type = "TEST",customfieldMaps=None):
    '''
    This function appends two layers of the same type.
    '''
    try:
        schemaType  = ['NO_TEST','TEST']

        if customfieldMaps is not None:
            if type(customfieldMaps) is not FieldMapping:
                raise TypeError('Must be A Field mapping object')

        if schema_type not in schemaType:
            raise ValueError('Must be of type NO_TEST or TEST')

        if in_layer.GetGeomType() != target_layer.GetGeomType():
            raise Exception('Both input types must be of same geometry')    

        #Manage field mapping.
        fldMapping = FieldMapping(in_layer,target_layer)
        if schema_type == 'NO_TEST':
            if customfieldMaps is not None:
                fldMapping = customfieldMaps
                
        else:
            if not fldMapping.is_test():
                raise Exception('All fields of the input and out must be the same')

        in_layer.ResetReading()
        
        for inFeature in in_layer:

            newFeature = ogr.Feature(target_layer.GetLayerDefn())
            newFeature.SetGeometry(inFeature.GetGeometryRef())

            for f in fldMapping.getFieldMappings():
                inFld = f.InFieldName
                outFld = f.OutFieldName
                newFeature.SetField(outFld,inFeature.GetField(inFld))


            target_layer.CreateFeature(newFeature)
            newFeature = None
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