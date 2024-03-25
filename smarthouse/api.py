import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path
from typing import List,Dict,Union
import os

def setup_database():
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "data" / "db.sql" # you have to adjust this if you have changed the file name of the database
    return SmartHouseRepository(str(db_file.absolute()))

app = FastAPI()

repo = setup_database()

smarthouse = repo.load_smarthouse_deep()

if not (Path.cwd() / "www").exists():
    os.chdir(Path.cwd().parent)
if (Path.cwd() / "www").exists():
    # http://localhost:8000/welcome/index.html
    app.mount("/static", StaticFiles(directory="www"), name="static")


# http://localhost:8000/ -> welcome page
@app.get("/")
def root():
    return RedirectResponse("/static/index.html")


# Health Check / Hello World
@app.get("/hello")
def hello(name: str = "world"):
    return {"hello": name}


# Starting point ...
# Får all informasjon frå smarthuset
@app.get("/smarthouse")
def get_smarthouse_info() -> dict[str, int | float]:
    """
    This endpoint returns an object that provides information
    about the general structure of the smarthouse.
    """
    return {
        "no_rooms": len(smarthouse.get_rooms()),
        "no_floors": len(smarthouse.get_floors()),
        "registered_devices": len(smarthouse.get_devices()),
        "area": smarthouse.get_area()
    }


# --------------- Det skal finnes endepunkter for å inspisere strukturen til huset ---------------
# Note
# fid = FloorID
# rid = RoomID
# uuid = "Universally Unique Identifier", i vårt tilfelle tenker eg t.d. DeviceID "4d5f1ac6-906a-4fd1-b4bf-3a0671e4c4f1"

# Få informasjon frå alle etasjar
@app.get("/smarthouse/floor")
def get_smarthouse_floor() -> List[Dict[str, Union[int | List]]]:
    floorInfo = smarthouse.get_floors()
    floorsList = []  # Lager ei tom liste
    for floor in floorInfo: # Går gjennom alle etasjer
        floorData = {
            "floor level": floor.level,
        }
        floorsList.append(floorData)  # Legger til etasje i ei liste
    return floorsList  # Returnerer ei liste som inneheld alle etasjer


# Få informasjon om ein gitt etasje gitt av "fid" = FloorID
@app.get("/smarthouse/floor/{fid}")
def get_smarthouse_floor_specific(fid: int) -> dict[str,int]:
    
    floorInfo = smarthouse.get_floors()
    floorData = "", None
    for floors in floorInfo:
        if floors.level == fid:
            return {
                "Floor Level": floors.level
            }
         
    raise HTTPException(status_code=404, detail="No given floor with this id was found")
         
    
# Få informasjon om alle room på ein gitt etasje "fid" = FloorID
@app.get("/smarthouse/floor/{fid}/room")
def get_smarthouse_AllroomsAtSpecificFloor(fid : int) -> List[Dict[str, int | str | float]]:
    
    # Henter alle rom
    getAllRooms = smarthouse.get_rooms()
    # Oppretter ei tom liste
    roomList = []

    # Sjekker om etasjen eksisterer
    checkFloor = get_smarthouse_floor_specific(fid)

    if checkFloor:
        for rooms in getAllRooms:
            if int(rooms.floor.level) == int(fid):
                roomData = {
                    "Floor Level" : rooms.floor.level,
                    "room name" : rooms.room_name,
                    "room size" : rooms.room_size
                }
                roomList.append(roomData)
        return roomList


# Informasjon om ein spesific rom {rid} "RoomID" på ein gitt etasje {fid} "FloorID" 
@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_smarthouse_roomAtSpecificFloor(fid : int, rid : str)-> List[Dict[str, int | str | float]]:

    # Sjekker om etasjen eksisterer
    HenterData = get_smarthouse_floor_specific(fid)
    getAllRooms = smarthouse.get_rooms()
    roomList = []

    if HenterData:
        for rooms in getAllRooms:
            if str(rooms.room_name) == str(rid) and int(rooms.floor.level) == int(fid):
                roomData = {
                    "Floor Level" : rooms.floor.level,
                    "room name" : rooms.room_name,
                    "room size" : rooms.room_size
                }
                roomList.append(roomData)
        # Sjekker om rommet eksisterer, om ikkje vil ein exeption bli returnert
        if roomList:
            return roomList
        else: 
            raise HTTPException(status_code=404, detail="Dette rommet eksisterer ikkje")

    
# --------- Det skal finnes endepunkter for tilgang til enheter -------------------------------------

# Informasjon om alle devicer
@app.get("/smarthouse/device")
def get_smarthouse_device()-> List[Dict[str, int | str | float]]:
    
    allDevices = smarthouse.get_devices()
    deviceList = []
    for devices in allDevices:
        deviceData = {
            "Device id" : devices.id,
            "Model Name" : devices.model_name,
            "Supplier" : devices.supplier,
            "Device In Room" : devices.room.room_name
        } 
        deviceList.append(deviceData)


    #Ingen failsafe trengst      
    return deviceList

# Informasjon om ein gitt device identifisert av "uuid" = DeviceID
@app.get("/smarthouse/device/{uiid}")
def get_smarthouse_device_by_id(uiid : str)-> List[dict[str, int | float | str]]:

    allDevices = smarthouse.get_devices()
    deviceList = []

    for devices in allDevices:        
        if str(devices.id) == str(uiid):
            deviceData = {
                "Device id" : devices.id,
                "Model Name" : devices.model_name,
                "Supplier" : devices.supplier,
                "Device In Room" : devices.room.room_name                           
            }
            deviceList.append(deviceData)

    if deviceList:
        return deviceList
    else:
        raise HTTPException(status_code=404, detail="Denna id'n matcher ikkje")

   


# --------- Det skal finnes spesielle endepunkter for tilgang til sensor funksjoner -----------------

# Get current sensor måling for sensor "uuid" = DeviceID 
@app.get("/smarthouse/sensor/{uuid}/current")
def get_smarthouse_sensor_currentMeasurment(uiid:str)-> List[Dict[str, int | float | str]]:
    
    device = smarthouse.get_devices() # Henter alle devices
    deviceList = [] # Lager ei tom liste

    for sensor in device: # Går gjennom alle sensorer i smarhuset
        if str(sensor.id) == str(uiid): # Sjekker sensor ID opp mot ID som er tastet inn
            SensorReading = repo.get_latest_reading(sensor) # Laster inn siste avlesninger frå sensor
            if SensorReading: # Sjekker om avlesningen eksisterer
                sensorData = { # Skriver data
                    "Verdi" : SensorReading.value,
                    "Unit" : SensorReading.unit,
                    "Tid" : SensorReading.timestamp
                }
                deviceList.append(sensorData) # Legger sensorData i ei liste

    # Sjekker om device list eksisterer, ellers blir HTTPExeption sendt
    if deviceList:
        return deviceList
    else:
        raise HTTPException(status_code=404, detail="Denna sensoren har ikkje noko siste målinger")

# Legg til måling for sensor "uuid" = DeviceID 
@app.post("/smarthouse/sensor/{uuid}/current")
def post_smarthouse_sensor_Measurment()-> dict[str,int | float]:
    pass

#  get n siste målinger for sensor uuid. om query parameter ikkje er tilgjengelig, den alle tilgjengelege målinger.
@app.get("/smarthouse/sensor/{uuid}/values?limit=n")
def get_smarthouse_sensor_MeasurmentLatestAvailable()-> dict[str,int | float]:
    pass

# Slett gamleste måling for sensor uuid
@app.delete("/smarthouse/sensor/{uuid}/oldest")
def delete_smarthouse_sensor_MeasurmentLatestAvailable()-> dict[str,int | float]:
    pass

# --------- Det skal finnes spesielle endepunkter for tilgang til aktuator funskjoner ---------------

# get current state for actuator uuid
@app.get("/smarthouse/actuator/{uuid}/current")
def get_smarthouse_actuatorCurrentState()-> dict[str,int | float]:
    pass

# oppdater current state for actuator uuid
@app.put("/smarthouse/device/{uuid}")
def put_smarthouse_actuatorCurrentState()-> dict[str,int | float]:
    pass




# TODO: implement the remaining HTTP endpoints as requested in
# https://github.com/selabhvl/ing301-projectpartC-startcode?tab=readme-ov-file#oppgavebeskrivelse
# here ...


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)


