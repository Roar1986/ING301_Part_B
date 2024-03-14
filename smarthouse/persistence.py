import sqlite3
from typing import Optional
from smarthouse.domain import Measurement, SmartHouse,Room,Floor, Sensor, ActuatorWithSensor, Actuator
from pathlib import Path


class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    file = Path(__file__).parent / "../data/db.sql"
    #file = "C:\ING301\ing301local\ING301_Part_B\data\db.sql"

    def __init__(self, file: str) -> None:
        self.file = file 
        self.conn = sqlite3.connect(file)

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
        cursor.close()

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

        return DEMO_HOUSE2


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

    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        # TODO: Implement this method. You will probably need to extend the existing database structure: e.g.
        #       by creating a new table (`CREATE`), adding some data to it (`INSERT`) first, and then issue
        #       and SQL `UPDATE` statement. Remember also that you will have to call `commit()` on the `Connection`
        #       stored in the `self.conn` instance variable.
        pass


    # statistics

    
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
        # TODO: This and the following statistic method are a bit more challenging. Try to design the respective 
        #       SQL statements first in a SQL editor like Dbeaver and then copy it over here.  
        return NotImplemented

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        # TODO: implement
        return NotImplemented

