from osgeo import ogr
from ngeo import Workspaces

path = r'Y:\Nigel\Data\test'


shpWS = Workspaces.ShapeFileWorkspaceFactory(path)

in_layer = shpWS.GetLayer('sample')


proj = in_layer.GetSpatialRef()
geomType = in_layer.GetGeomType()
lyr_def = in_layer.GetLayerDefn()

out_lyr = shpWS.CreateLayer('output1',lyr_def,geomType,proj)

for inFeature in in_layer:

    outFeature = ogr.Feature(out_lyr.GetLayerDefn())
    for i in range(0, out_lyr.GetLayerDefn().GetFieldCount()):
        try:
            outFeature.SetField(out_lyr.GetLayerDefn().GetFieldDefn(i).GetNameRef(), inFeature.GetField(in_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef()))
        except:
            continue
    # Set geometry as centroid
    geom = inFeature.GetGeometryRef()
                                    
    outFeature.SetGeometry(geom)
    out_lyr.CreateFeature(outFeature)
