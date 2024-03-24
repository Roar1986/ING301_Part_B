import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path
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
def get_smarthouse_floor() -> dict[str,int | float]:
    return{
       "no_floors": len(smarthouse.get_floors()),
        
    }

# Få informasjon om ein gitt etasje gitt av "fid" = FloorID
@app.get("/smarthouse/floor/{fid}")
def get_smarthouse_floor_specific() -> dict[str,int | float]:
    pass

# Få informasjon om alle room på ein gitt etasje "fid" = FloorID
@app.get("/smarthouse/floor/{fid}/room")
def get_smarthouse_AllroomsAtSpecificFloor() -> dict[str,int | float]:
    pass

# Informasjon om ein spesific rom {rid} "RoomID" på ein gitt etasje {fid} "FloorID" 
@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_smarthouse_roomAtSpecificFloor()-> dict[str,int | float]:
    pass

# --------- Det skal finnes endepunkter for tilgang til enheter -------------------------------------

# Informasjon om alle devicer
@app.get("/smarthouse/device")
def get_smarthouse_device()-> dict[str,int | float]:
    pass

# Informasjon om ein gitt device identifisert av "uuid" = DeviceID
@app.get("/smarthouse/device/{uiid}")
def get_smarthouse_device()-> dict[str,int | float]:
    pass

# --------- Det skal finnes spesielle endepunkter for tilgang til sensor funksjoner -----------------

# Get current sensor måling for sensor "uuid" = DeviceID 
@app.get("smarthouse/sensor/{uuid}/current")
def get_smarthouse_sensor_currentMeasurment()-> dict[str,int | float]:
    pass

# Legg til måling for sensor "uuid" = DeviceID 
@app.post("smarthouse/sensor/{uuid}/current")
def post_smarthouse_sensor_Measurment()-> dict[str,int | float]:
    pass

#  get n siste målinger for sensor uuid. om query parameter ikkje er tilgjengelig, den alle tilgjengelege målinger.
@app.get("GET smarthouse/sensor/{uuid}/values?limit=n")
def get_smarthouse_sensor_MeasurmentLatestAvailable()-> dict[str,int | float]:
    pass

# Slett gamleste måling for sensor uuid
@app.delete("smarthouse/sensor/{uuid}/oldest")
def delete_smarthouse_sensor_MeasurmentLatestAvailable()-> dict[str,int | float]:
    pass

# --------- Det skal finnes spesielle endepunkter for tilgang til aktuator funskjoner ---------------

# get current state for actuator uuid
@app.get("smarthouse/actuator/{uuid}/current")
def get_smarthouse_actuatorCurrentState()-> dict[str,int | float]:
    pass

# oppdater current state for actuator uuid
@app.put("smarthouse/device/{uuid}")
def put_smarthouse_actuatorCurrentState()-> dict[str,int | float]:
    pass




# TODO: implement the remaining HTTP endpoints as requested in
# https://github.com/selabhvl/ing301-projectpartC-startcode?tab=readme-ov-file#oppgavebeskrivelse
# here ...


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)


