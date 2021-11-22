

class PostgreSQLConnection:

    """
    Class used to create a PostgreSQL Connection string
    """
    def __init__(self,server,dbanme,username,password):

       self.dbServer = server
       self.dbName = dbanme
       self.username = username
       self.password = password

    def connstring(self):
      return  "PG: host=%s dbname=%s user=%s password=%s" % (self.dbServer, self.dbName, self.username, self.password )


class MySQLConnection:
      """
      Class that creates a MySQLConnection string
      """

      def __init__(self,server,dbanme,username,password):
         self.dbServer = server
         self.dbName = dbanme
         self.username = username
         self.password = password

      def connstring(self):
         return "MYSQL:{0},host={1},user={2},password={3},port=3306".format(self.dbName,self.dbServer,self.username,self.password) 

