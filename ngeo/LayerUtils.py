from osgeo import ogr


def getFeatureCount(in_layer):
    '''
    Returns the feature count of the 
    in_layer: This must be a OGRLayer
    '''
    try:
        featureCount = in_layer.GetFeatureCount()
    except:
         raise Exception

    return featureCount

def getFieldDefn(in_layer,fieldname):
    '''
    Returns the field definition of the specified field name
    '''

    ldef = in_layer.GetLayerDefn()
    fieldIndex = ldef.GetFieldIndex(fieldname)
    fieldDef = ldef.GetFieldDefn(fieldIndex)  	
    
    return fieldDef

def getFieldIndex(in_layer,field_name):
    '''
    Returns the field index of the given Field name.  returns -1 if no field by the given name exists 
    in_layer: This must be a OGRLayer
    field_name: Name of the field.
   
    '''
    ldef = in_layer.GetLayerDefn()
    fieldIndex = ldef.GetFieldIndex(field_name)

    return  fieldIndex

def resetQueryFilters(in_layer):
    '''
    Resets any attribute or spatial filters applied on a certian layer
    in_layer: Must be a OGRLayer
    '''
    in_layer.SetAttributeFilter(None)
    in_layer.SetSpatialFilter(None)
    in_layer.ResetReading()

def getFieldNames(in_layer):
    """
     in_layer: This must be a OGRLayer.
     Returns an array of field names from the given table.
    """
    field_names = []

    layerDefinition = in_layer.GetLayerDefn()

    for i in range(layerDefinition.GetFieldCount()):
        field_names.append(layerDefinition.GetFieldDefn(i).GetName())

    return field_names

def addField(in_layer:str, field_name:str, field_type:str, field_precision:int, field_length:int):
    """
    Adds a field with given configuration.
    in_layer: This must be a OGRLayer.
    field_type: Can be any of the following 'TEXT','DOUBLE','INT','LONG','DATETIME'
    default_value: This is an optional parameter.
    """
 
    #Delete the field if it already exists
    ldef = in_layer.GetLayerDefn()
    fieldIndex = ldef.GetFieldIndex(field_name)
    if fieldIndex != -1:
        in_layer.DeleteField(fieldIndex)


    #Check if field type values are any of the following 'TEXT','DOUBLE','INT','LONG','DATETIME'
    #Print a message if not
    validFields = ['TEXT','DOUBLE','INT','LONG','DATETIME']
    if(field_type not in validFields):
        print('Field must be of type '+str(validFields))
        return

    #Set the length and precision
    field_defn = None

    if(field_type == 'TEXT'):
        field_defn = ogr.FieldDefn(field_name, ogr.OFTString)
        field_defn.SetWidth(field_length)
    if(field_type == 'DOUBLE'):
        field_defn = ogr.FieldDefn(field_name, ogr.OFTReal)
        field_defn.SetPrecision(field_precision)
    if (field_type == 'INT'):
        field_defn = ogr.FieldDefn(field_name, ogr.OFTInteger)
    if (field_type == 'LONG'):
        field_defn = ogr.FieldDefn(field_name, ogr.OFTInteger64)
    if (field_type == 'DATETIME'):
        field_defn = ogr.FieldDefn(field_name, ogr.OFTDateTime)

    

    #Create the field
    in_layer.CreateField(field_defn,True)
    print('Field '+field_name+' created')

def deleteField(in_layer,fields):
    '''
    Deletes the specified fields.
    in_layer: This must be a OGRLayer.
    fields: Must be a list of fields to delete
    '''
    #Delete the field if it already exists
    ldef = in_layer.GetLayerDefn()
    for fld in fields:
        fieldIndex = ldef.GetFieldIndex(fld)
        if fieldIndex != -1:
            in_layer.DeleteField(fieldIndex)
    
def copyfielddefn(in_layer, fieldName,fieldDef_template):
    """
    This method creates a field in the input feature class/Table 
    based on the field definition of the template field
    in_layer: The layer that the new field will be added to
    fieldName: The name of the field what will be added
    fieldDefn: The definition(datatype, precision) of the field that the field should apply 
    """
    try:
      

        ldef = in_layer.GetLayerDefn()
        fieldIndex = ldef.GetFieldIndex(fieldName)

        #Drop the field if it already exists
        if fieldIndex != -1:
            in_layer.DeleteField(fieldIndex)
        
        #Create a new field definition and copy all the properties of the template field
        newFldDef = ogr.FieldDefn()
        # newFldDef = fieldDef_template
        newFldDef.SetName(fieldName)
        newFldDef.SetType(fieldDef_template.GetType())
        newFldDef.SetWidth(fieldDef_template.GetWidth())
        newFldDef.SetPrecision(fieldDef_template.GetPrecision())

        #Create the field
        in_layer.CreateField(newFldDef,True)
    except Exception:
        raise Exception    

    
def generateWhereClause(field_def,value, useCaseSensitivity, useLikeOperator):
        '''
        Function generates a where clause based on the input value and out field definition.
        '''
        whereClause = ""
        fldType = field_def.GetType()
        if fldType == ogr.OFTString:
            valueString = str(value).replace("'", "''")
            if useCaseSensitivity:
                if not useLikeOperator:
                   whereClause = "{fieldname} ='{value}'".format(fieldname=field_def.GetName(),value=valueString)
                else:
                   whereClause = "{fieldname} LIKE '{value}%' ".format(fieldname=field_def.GetName(),value=valueString)
            else:
                if not useLikeOperator:
                    whereClause = "UPPER({fieldname}) = '{value}'".format(fieldname=field_def.GetName(),value = valueString.upper())
                else:
                    whereClause = "UPPER({fieldname})  LIKE '{value}%' ".format(fieldname=field_def.GetName(),value = valueString.upper())

        elif fldType == ogr.OFTInteger or fldType == ogr.OFTInteger64 or  fldType == ogr.OFTReal: 
            if str(value) != "":
                if useLikeOperator:
                    whereClause = "CAST({fieldname} AS VARCHAR({field_width}))  LIKE '{value}%'".format(fieldname=field_def.GetName(),field_width= str(field_def.GetWidth()) ,value = valueString.upper())
                else:
                    whereClause =  "{fieldname} = {value}".format(fieldname=field_def.GetName(),value=value)
            else:
                whereClause = "{fieldname} > -1".format(fieldname =field_def.GetName())
   
           

        return whereClause    





    
    
