import sqlite3
from typing import Optional
from smarthouse.domain import Measurement, SmartHouse,Room,Floor, Sensor, ActuatorWithSensor, Actuator
from pathlib import Path
from datetime import datetime


class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    # Filsti for databasefila
    file = Path(__file__).parent / "../data/db.sql"

    #def __init__(self, file: str) -> None:
    #    self.file = file 
    #    self.conn = sqlite3.connect(file)

    def __init__(self, file: str) -> None:
        self.file = file
        self.conn = sqlite3.connect(file, check_same_thread=False)

    def __del__(self):
        self.conn.close()

    def cursor(self) -> sqlite3.Cursor:

        """
        Provides a _raw_ SQLite cursor to interact with the database.
        When calling this method to obtain a cursors, you have to 
        rememeber calling `commit/rollback` and `close` yourself when
        you are done with issuing SQL commands.
        """
        

        return self.conn.cursor()

    def reconnect(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.file)

    
    def load_smarthouse_deep(self):
        """
        This method retrives the complete single instance of the _SmartHouse_ 
        object stored in this database. The retrieval yields a _deep_ copy, i.e.
        all referenced objects within the object structure (e.g. floors, rooms, devices) 
        are retrieved as well. 
        """

        ## Kode for registering rooms and floors from database
        DEMO_HOUSE2 = SmartHouse()
        
        # Spørring for å finne alle rom og lagre dette til ei liste
        cursor = self.cursor()
        query = "SELECT DISTINCT floor FROM rooms r;" # Spørring som tar vekk duplikerte etasjer, og returnerer berre dei unike etasjene
        cursor.execute(query)
        FLoorExtract = cursor.fetchall()
        cursor.close()

        # Går gjennom alle etasjer og registrerer dei
        for floor in FLoorExtract:
            DEMO_HOUSE2.register_floor(floor[0])

        # Henter ei liste med alle etasjer
        floorList = DEMO_HOUSE2.get_floors()

        # Spørring for å finne alle rom og lagre dette til ei liste
        cursor = self.cursor()
        query = "SELECT * FROM rooms r"
        cursor.execute(query)
        RoomExtract = cursor.fetchall()
        cursor.close()

        # Kode for å registrere rom basert på antall etasjer
        for rooms in RoomExtract: # går gjennom alle rom
            for floor in floorList: # går gjennom alle etasjer
                if rooms[1] == floor.level: # er room == etasje, så blir rommet registrert
                    DEMO_HOUSE2.register_room(floor,rooms[2],rooms[3])

        # Lager ei liste over alle registrerte romm.        
        roomList = DEMO_HOUSE2.get_rooms()

        # Spørring for å hente ut informasjon om device og rooms basert på id
        cursor = self.cursor()
        query2 = "select * FROM rooms r inner join devices d on r.id = d.room;"
        cursor.execute(query2)
        DeviceExtract2 = cursor.fetchall()
        #cursor.close()

        # Kode for å registrere device i rett rom
        for devices in DeviceExtract2:
            if devices[7] == "sensor":
                device = Sensor(devices[4],devices[9],devices[8],devices[6])
                for room in roomList: # Går gjennom alle rom som er registrert
                    if devices[1] == 1: # Sjekker etasje
                        if str(devices[3]) == str(room.room_name): # Sjekker rom navn er like, gitt at dei er unike
                            DEMO_HOUSE2.register_device(room,device) # Registrerer devicen i rette rommet
                    if devices[1] == 2: # sjekker etasje
                        if str(devices[3]) == str(room.room_name): # Sjekker rom navn er like, gitt at dei er unike
                            DEMO_HOUSE2.register_device(room,device) # Registrerer devicen i rette rommet
            if devices[7] == "actuator":
                device = Actuator(devices[4],devices[9],devices[8],devices[6])
                for room in roomList: # Går gjennom alle rom som er registrert
                    if devices[1] == 1: # Sjekker etasje
                        if str(devices[3]) == str(room.room_name): # Sjekker rom navn er like, gitt at dei er unike
                            DEMO_HOUSE2.register_device(room,device) # Registrerer devicen i rette rommet
                    if devices[1] == 2: # sjekker etasje
                        if str(devices[3]) == str(room.room_name): # Sjekker rom navn er like, gitt at dei er unike
                            DEMO_HOUSE2.register_device(room,device) # Registrerer devicen i rette rommet

        
        for dev in DEMO_HOUSE2.get_devices():
            if isinstance(dev, Actuator):
                cursor.execute(f"SELECT state FROM states where device = '{dev.id}';")
                state = cursor.fetchone()[0]
                if state is None:
                    dev.turn_off()
                elif float(state) == 1.0:
                    dev.turn_on()
                else:
                    dev.turn_on(float(state))


        cursor.close()

        return DEMO_HOUSE2

    # Method for returning the latest measurment from a sensor
    def get_latest_reading(self, sensor) -> Optional[Measurement]:

        """
        Retrieves the most recent sensor reading for the given device if available.
        Returns None if the given device has no sensor readings.
        """
        
        # Lager spørring der eg velger value, ts og unit fra tabell measurments
        # where device = ?, der ? er ein plass holder for sensor.id som kjem seinare i koden
        # order by ts, desc, 
        # Limitert til 1 verdi
        cursor = self.cursor()
        query = """
            SELECT value, ts, unit
            FROM measurements
            WHERE device = ?
            ORDER BY ts DESC
            LIMIT 1;
        """

        # dette er ei try block, om det skulle vere ein feil i denne spørringa tl.d. 
        # så vil koden hoppe videre til finnaly og lukke close cursor
        try:
            cursor.execute(query, (sensor.id,))
            latest_reading_data = cursor.fetchone()
        finally:
            cursor.close()

        # Sjekker om det er noko data, om det er data. returnerer vi objetet Measurment og setter rett data på rett plass
        # Dersom ingen data, None vil bli returnert. 
        if latest_reading_data:
            return Measurement(value=latest_reading_data[0], timestamp=latest_reading_data[1], unit=latest_reading_data[2])
        else:
            return None
        


        # Method for returning the oldest measurment from a sensor
    def removing_oldest_reading_from_database(self, sensor) -> Optional[Measurement]:

        """
        Retrieves the most recent sensor reading for the given device if available.
        Returns None if the given device has no sensor readings.
        """
        
        # Lager ei spørring der eg finner den eldste verdien i tabellen, for den gitte sensoren
        cursor = self.cursor()
        query = """
        DELETE FROM measurements
        WHERE ts = (
            SELECT MIN(ts)
            FROM measurements
            WHERE device = ?
        )
        AND device = ?;
        """

        # dette er ei try block, om det skulle vere ein feil i denne spørringa tl.d. 
        # så vil koden hoppe videre til finnaly og lukke close cursor
        try:
            cursor.execute(query, (sensor.id, sensor.id))
            self.conn.commit()
            if cursor.rowcount > 0: # Sjekker om noen av radene har blitt fjernet
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            cursor.close()
    
    # Method for returning n: number of readings from a sensor
    def get_all_readings(self, sensor, limit) -> Optional[Measurement]:

        """
        Retrieves the most recent sensor reading for the given device if available.
        Returns None if the given device has no sensor readings.
        """
        
        # Lager spørring der eg velger value, ts og unit fra tabell measurments
        # where device = ?, der ? er ein plass holder for sensor.id som kjem seinare i koden
        # order by ts, desc, 
        # Limitert til 1 verdi
        cursor = self.cursor()
        query = """
            SELECT value, ts, unit
            FROM measurements
            WHERE device = ?
            ORDER BY ts DESC
            LIMIT ?;
        """

        #Lager ei tom liste
        readings = []
        # dette er ei try block, om det skulle vere ein feil i denne spørringa tl.d. 
        # så vil koden hoppe videre til finnaly og lukke close cursor
        try:
            cursor.execute(query, (sensor.id,limit))
            readingmeasurments = cursor.fetchall()
            for data in readingmeasurments:
                signelRow = Measurement(value=data[0], timestamp=data[1], unit=data[2])
                readings.append(signelRow)
        finally:
            cursor.close()

        if readings:
            return readings
    
        # Sjekker om det er noko data, om det er data. returnerer vi objetet Measurment og setter rett data på rett plass
        # Dersom ingen data, None vil bli returnert. 

    # Method for adding measurments to database, returning a bool true or false if implimentation was ok
    def add_measurment(self, sensor_ID : str , timestamp : datetime , value : float , unit : str ) -> bool: #Optional[Measurement]:

        # Oppretter forbindelse med database
        cursor = self.cursor()
        query = """
            INSERT INTO measurements(device, value, ts, unit)
            VALUES(?,?,?,?);
        """

        try:
            # Legger til måling i database
            cursor.execute(query,(sensor_ID, value, timestamp,unit))
            # Committer endringa til databasen
            self.conn.commit()
            return True

        except Exception as e:
        # Handle any exceptions
            print(f"An error occurred: {e}")
            return False
        finally:
            cursor.close()      
    
    # Metode tatt frå løysningsforslag
    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        if isinstance(actuator, Actuator):
            s = 'NULL'
            if isinstance(actuator.state, float):
                s = str(actuator.state)
            elif actuator.state is True:
                s = '1.0'
            query = f"""
                    UPDATE states 
                    SET state = {s}
                    WHERE device = '{actuator.id}';
                            """
            c = self.cursor()
            c.execute(query)
            self.conn.commit()
            c.close()


        # TODO: Implement this method. You will probably need to extend the existing database structure: e.g.
        #       by creating a new table (`CREATE`), adding some data to it (`INSERT`) first, and then issue
        #       and SQL `UPDATE` statement. Remember also that you will have to call `commit()` on the `Connection`
        #       stored in the `self.conn` instance variable.

    
    def calc_avg_temperatures_in_room(self, room, from_date: Optional[str] = None, until_date: Optional[str] = None) -> dict:
        """Calculates the average temperatures in the given room for the given time range by
        fetching all available temperature sensor data (either from a dedicated temperature sensor 
        or from an actuator, which includes a temperature sensor like a heat pump) from the devices 
        located in that room, filtering the measurement by given time range.
        The latter is provided by two strings, each containing a date in the ISO 8601 format.
        If one argument is empty, it means that the upper and/or lower bound of the time range are unbounded.
        The result should be a dictionary where the keys are strings representing dates (iso format) and 
        the values are floating point numbers containing the average temperature that day.
        """
        cursor = self.conn.cursor()

        # Spørring
        # ved å bruke measurments.unit = '°C', så tar spørringa med seg alle plasser der det er ein temperatur.
        query = """
        SELECT DATE(measurements.ts) as date, AVG(measurements.value) as avg_temp
        FROM measurements
        JOIN devices ON measurements.device = devices.id
        JOIN rooms ON devices.room = rooms.id
        WHERE rooms.name = ? AND measurements.unit = '°C'
        AND (DATE(measurements.ts) BETWEEN ? AND ? OR ? IS NULL OR ? IS NULL)
        GROUP BY DATE(measurements.ts);
        """

        # Spørring som kan brukest i dbeaver.
        """SELECT DATE(measurements.ts) as date, AVG(measurements.value) as avg_temp
        FROM measurements
        JOIN devices ON measurements.device = devices.id
        JOIN rooms ON devices.room = rooms.id
        WHERE (rooms.name = 'Living Room / Kitchen'  AND measurements.unit = '°C' AND devices.kind IN ('Temperature Sensor', 'Heat Pump','Smart Oven'))
        GROUP BY DATE(measurements.ts);"""


        # Eksekuterer spørringa, ? fra spørringa er referert til i cursor under
        cursor.execute(query, (room.room_name, from_date, until_date, from_date, until_date))
        rows = cursor.fetchall()

        # Konverterer rows in til ein dictionary
        avg_temps = {date: avg_temp for date, avg_temp in rows}

        cursor.close()
        return avg_temps

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        
        # Spørring for å rom id
        cursor = self.conn.cursor()
        room_id_query = "SELECT id FROM rooms WHERE name = ?"
        cursor.execute(room_id_query, (room.room_name,))
        room_id_result = cursor.fetchone()
        
        # Om ikkje id er funnet, returnerer tom liste
        if not room_id_result:
            return []  # Room not found

        # rom ID = første indeks i resultatet
        room_id = room_id_result[0]

        # Spørring
        query = """
        WITH AverageHumidity AS (
            SELECT AVG(measurements.value) as avg_humidity
            FROM measurements
            JOIN devices ON measurements.device = devices.id
            WHERE devices.room = ?
            AND DATE(measurements.ts) = ?
            AND devices.kind = 'Humidity Sensor'
        ),
        HourlyMeasurements AS (
            SELECT 
                strftime('%H', measurements.ts) as hour,
                measurements.value as humidity
            FROM measurements
            JOIN devices ON measurements.device = devices.id
            WHERE devices.room = ?
            AND DATE(measurements.ts) = ?
            AND devices.kind = 'Humidity Sensor'
        )
        SELECT hour
        FROM HourlyMeasurements, AverageHumidity
        WHERE humidity > avg_humidity
        GROUP BY hour
        HAVING COUNT(humidity) > 3;
        """

        # Setter inn rom id og dato inn i spørringa der det står ?
        cursor.execute(query, (room_id, date,room_id,date))
        rows = cursor.fetchall()
        cursor.close()

        # Converterer rekke in til ei liste av timer
        hours_with_high_humidity = [int(row[0]) for row in rows]
        return hours_with_high_humidity


