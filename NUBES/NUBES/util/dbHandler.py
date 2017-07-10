import subprocess
import sys
import pymysql
import operator

class dbHandler:
   def __init__(self):
       self.db = pymysql.connect(host='46.101.180.169', port= 3306, user='pi',password='eits2017',db='EITS')
       #self.db = pymysql.connect(host='192.168.43.114', port= 3306, user='Pi',password='eits2017',db='EITS')
       #self.db = pymysql.connect(host='localhost',user='root',password='',db='EITS')
       self.cursor =  self.db.cursor(pymysql.cursors.DictCursor)

   def get_points(self,Camera,FreeStorage,CPU,RAM,Temperature,Jobs_Num,time):
      max_storage = 8192
      max_hours = 168
      efficient = 3500

      total = 0
      total += 600 * (3 - Jobs_Num)
      total += 1000 * (1- Camera)
      total += 12 * (100 -CPU)
      total += 8 * (100 - RAM)
      total += 5 * (100 - FreeStorage )
      total += 10 * (80 - Temperature)
      total += 2 * (max_hours - time)
      return total

   def getBestPi(self):
     rp = {}
     best = -1
     temp = "none"

     query = 'SELECT Rp_Specs.Mac ,Rp_Specs.HasCamera, Current_Specs.FreeStorage , Current_Specs.RamUsage ,Current_Specs.CpuUsage ,Current_Specs.Temperature ,Rp_Log.Jobs_Num , TIMESTAMPDIFF(HOUR,Rp_Log.Start_time,NOW()) AS time FROM Rp_Log INNER JOIN Rp_Specs ON Rp_Log.Mac = Rp_Specs.Mac INNER JOIN Current_Specs ON Rp_Specs.Mac = Current_Specs.Mac ORDER BY rand()'
    #  query2 =  'UPDATE Rp_Log SET  Jobs_Num = Jobs_Num + 1 WHERE 1'
     try:
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for row in results:
            Mac = row["Mac"]
            Camera = row["HasCamera"]
            FreeStorage = row["FreeStorage"]
            CPU = row["CpuUsage"]
            Temperature = row["Temperature"]
            Jobs_Num = row["Jobs_Num"]
            RamUsage = row["RamUsage"]
            time = row["time"]
            rp[Mac] = dbHandler.get_points(self,Camera,FreeStorage,CPU,RamUsage,Temperature,Jobs_Num,time)
            print("Mac "+Mac + " points "+str(rp[Mac]))
            if rp[Mac] > best:
                best = rp[Mac]
                temp = Mac
        return temp
     except Exception as e:
      print(e)

   def incrementPi(self,mac):
     query = 'UPDATE `Rp_Log` SET `Jobs_Num`=Jobs_Num + 1 WHERE Mac = \'' + mac + '\''
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)

   def decrementPi(self,mac):
     query = 'UPDATE `Rp_Log` SET `Jobs_Num`=Jobs_Num - 1 WHERE Mac = \'' + mac + '\''
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)
   

   def getCameraPis(self):
     query = "SELECT `Mac` FROM `Rp_Specs` WHERE HasCamera = 1";
     self.cursor.execute(query)
     macs = []
     results = self.cursor.fetchall()
     for x in results:
         macs.append(x)
     return macs        

   def getLocatedPis(self,Locations):
     macs = []
     for x in Locations:
       query = "SELECT `Mac` FROM `Rp_Specs` WHERE HasCamera = 1";
       self.cursor.execute(query)
       results = self.cursor.fetchall()
       for y in results:
           macs.append(y)
     
     return macs


   def addProcess(self,containerID , imgID , IPAddress , port, userID ,processName , mac):
     query =  "UPDATE `Process` SET `Img_id`=\'"+imgID+"\',`Cont_id`=\'"+containerID+"\',`Cont_IP`=\'"+IPAddress+"\',`Mac`=\'"+mac+"\',`Process_State`=32141 WHERE Process_name = \'"+processName+"\' AND User_id = "+str(userID)
     try:
        self.cursor.execute(query)
        self.db.commit()
        self.incrementPi(mac)
        self.updateUserLog(userID,imgID,processName)
     except Exception as e:
        print(e)

   def updateUserLog(userID,imgID,processName):
     query =  "UPDATE `User_Log` SET `Img_id`= \""+imgID+"\" , Action = 22894 WHERE User_id = "+str(userID)+" AND Process_name = \""+processName+"\" ORDER BY Time DESC LIMIT 1"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)
      

   def adminKill(self,Admin_id , mac , Cont_id):
     query =  "INSERT INTO `Admin_Log`(`Admin_id`, `The_Actions`, `Mac` , `Cont_id`) VALUES ("+Admin_id+","+27693+",\'"+mac+"\',\'"+Cont_id+"\')"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)

   def shutPi(self,AdminID, mac ) :
     query =  "INSERT INTO `Admin_Log`(`Admin_id`, `The_Actions`, `Mac` , `Cont_id`) VALUES ("+Admin_id+","+12030+",\'"+mac+"\',\'None\')"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)
     query =  "UPDATE `Process` SET `Process_State`="+22198+" WHERE Mac = \'"+mac+"\'"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)

   def restartPi(self,AdminID, mac ) :
     query =  "INSERT INTO `Admin_Log`(`Admin_id`, `The_Actions`, `Mac` , `Cont_id`) VALUES ("+Admin_id+","+23456+",\'"+mac+"\',\'None\')"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)
     query =  "UPDATE `Process` SET `Process_State`="+22198+" WHERE Mac = \'"+mac+"\'"
     try:
        self.cursor.execute(query)
        self.db.commit()
     except Exception as e:
        print(e)

   def getSpecs(self,Mac):
     query2 = "SELECT Username , Password , PublicIP  FROM `Rp_Specs` WHERE Mac = \""+ Mac+" \""
     try:
       self.cursor.execute(query2)
       results = self.cursor.fetchall()
       for row  in results:
           result = row["Username"]
           result = result + ":"+row["Password"]
           result = result + ":"+row["PublicIP"]
       return result
     except Exception as e:
       print(e)

   def updateCurrentSpecs(self, Mac, PrivateIP, CPU_temp, CPU_usage, DISK_usage, RAM_usage):
      query = 'UPDATE Current_Specs SET PrivateIP = \''+ PrivateIP +'\', CpuUsage = %s, RamUsage = %s, FreeStorage = %s, Temperature = %s WHERE Mac = \''+Mac+'\''
      try:
         self.cursor.execute(query, [CPU_usage, RAM_usage, DISK_usage, CPU_temp])
         self.db.commit()
         print('updated')
      except Exception as e:
         self.db.rollback()
         print(e)

   def updateCriminalStatus(self, criminal):

        query = "UPDATE Criminals SET State = "+str(76767)+" WHERE Crim_id = \""+ str(criminal)+" \"   "
        try:
            self.cursor.execute(query)
            self.db.commit()
            print('updated')
        except Exception as e:
            self.db.rollback()
            print(e)