import pymysql
import pandas as pd

# Connexion initiale pour créer la base de données si elle n'existe pas
initial_connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

initial_cursor = initial_connection.cursor()
initial_cursor.execute("CREATE DATABASE IF NOT EXISTS weather_dataWarehouse")
print("Database weather_dataWarehouse created")
initial_cursor.close()
initial_connection.close()


# Connexion à la base de données weather_dataWarehouse
db = pymysql.connect(host='localhost',
                     user= 'root',
                    password= '',
                    database= 'weather_dataWarehouse',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)

def create_weather_fact(cursor):

    cursor.execute("DROP TABLE IF EXISTS Weather_Fact")
    cursor.execute("CREATE TABLE Weather_Fact (StationID INT, Date_ID INT, PRCP float, TAVG float, \
                   TMAX float, TMIN float, SNWD float, PGTM float, SNOW float, WDFG float, WSFG float, \
                   PRIMARY KEY (StationID, Date_ID), FOREIGN KEY (StationID) REFERENCES Station_Dim(StationID), \
                   FOREIGN KEY (Date_ID) REFERENCES Date_Dim(Date_ID))")
    
    print("Table Weather_Fact Created")

def create_station_dim(cursor):

    cursor.execute("DROP TABLE IF EXISTS Station_Dim")
    cursor.execute("CREATE TABLE Station_Dim (StationID INT AUTO_INCREMENT, \
                   StationCode varchar(255), Name VARCHAR(255), Latitude float, Longitude float, \
                   Elevation float, Pays CHAR(2), PRIMARY KEY (StationID))")
    
    print("Table Station_Dim Created")

def create_date_dim(cursor):

    cursor.execute("DROP TABLE IF EXISTS Date_Dim")
    cursor.execute("CREATE TABLE Date_Dim (Date_ID INT PRIMARY KEY AUTO_INCREMENT, Date DATE, Year INT, Month INT, \
                   Day INT)")
    
    print("Table Date_Dim Created")

cursor = db.cursor()

#CREATE Data Warehouse shema

create_weather_fact(cursor)
create_station_dim(cursor)
create_date_dim(cursor)
print("Data Warehouse schema created")

#Populate the tables

data = pd.read_csv('./Dataset/Weather_data.csv')



stations = data[["STATION", "NAME", "LATITUDE", "LONGITUDE", "ELEVATION", "PAYS"]]

for index, row in stations.iterrows():
    cursor.execute("INSERT INTO Station_Dim (StationCode, Name, Latitude, Longitude, Elevation, Pays) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (row["STATION"], row["NAME"], row["LATITUDE"], row["LONGITUDE"], row["ELEVATION"], row["PAYS"]))
    
print("Station_Dim populated")

dates = data[["DATE", "YEAR", "MONTH", "DAY"]]

for index, row in dates.iterrows():
    cursor.execute("INSERT INTO Date_Dim (Date, Year, Month, Day) VALUES (%s, %s, %s, %s)", 
                   (row["DATE"], row["YEAR"], row["MONTH"], row["DAY"]))
    
print("Date_Dim populated")

weather = data[["PRCP", "TAVG", "TMAX", "TMIN", "SNWD", "PGTM", "SNOW", "WDFG", "WSFG"]]

for index, row in weather.iterrows():
    cursor.execute("INSERT INTO Weather_Fact (StationID, Date_ID, PRCP, TAVG, TMAX, TMIN, SNWD, PGTM, SNOW, WDFG, WSFG) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (index+1, index+1, row["PRCP"], row["TAVG"], row["TMAX"], row["TMIN"], row["SNWD"], row["PGTM"], row["SNOW"], row["WDFG"], row["WSFG"]))

    
print("Weather_Fact populated")


cursor.close()
db.commit()
db.close()