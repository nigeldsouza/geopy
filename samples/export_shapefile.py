from ngeo import WorkspaceManager,Workspaces,ConnectionObjects
from ngeo.ExportUtility import Export
from ngeo import LayerUtils

myslconn = ConnectionObjects.MySQLConnection('dbprodmysql1.corp.theweather.com.au','geo_client_data','geo_client_data','a3JFq3Dk')

shapfilews = Workspaces.ShapeFileWorkspaceFactory(r"Y:\Nigel\Data\powerlink")
shpNames = WorkspaceManager.list_layers_from_Workspace(shapfilews,'ALL')
export_utility = Export()
export_utility.setMySqlConnection(myslconn)

for shp in shpNames:
    
    
    lyr = shapfilews.GetLayer(shp)
    count = LayerUtils.getFeatureCount(lyr)
    try:
        outname  = "onefortyone_areas"
        #export_utility.featureClassToMySQL(lyr,outname)
        print("layer {0}, count:{1}".format(outname.lower(),count))
    except Exception as e:
        print("Error in {}".format(outname.lower()))    
    

