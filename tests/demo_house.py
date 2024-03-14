from smarthouse.domain import Actuator, Sensor, SmartHouse, ActuatorWithSensor
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path

DEMO_HOUSE = SmartHouse()

# Building house structure
ground_floor = DEMO_HOUSE.register_floor(1)
entrance = DEMO_HOUSE.register_room(ground_floor, 13.5, "Entrance")
gr1 = DEMO_HOUSE.register_room(ground_floor, 8, "Guest Room 1")
bath1 = DEMO_HOUSE.register_room(ground_floor, 6.3, "Bathroom 1")
stue = DEMO_HOUSE.register_room(ground_floor, 39.75, "Living Room / Kitchen")
garage = DEMO_HOUSE.register_room(ground_floor, 19, "Garage")

first_floor = DEMO_HOUSE.register_floor(2)
bedroom = DEMO_HOUSE.register_room(first_floor, 17, "Master Bedroom")
dresser = DEMO_HOUSE.register_room(first_floor, 4, "Dressing Room")
gr3 = DEMO_HOUSE.register_room(first_floor, 10, "Guest Room 3")
office = DEMO_HOUSE.register_room(first_floor, 11.75, "Office")
bath2 = DEMO_HOUSE.register_room(first_floor, 9.25, "Bathroom 2")
gr2 = DEMO_HOUSE.register_room(first_floor, 8, "Guest Room 2")
hall = DEMO_HOUSE.register_room(first_floor, 10, "Hallway")

lock = Actuator("4d5f1ac6-906a-4fd1-b4bf-3a0671e4c4f1", "Guardian Lock 7000", "MythicalTech", "Smart Lock")
co2 = Sensor("8a43b2d7-e8d3-4f3d-b832-7dbf37bf629e", "Smoke Warden 1000", "ElysianTech", "CO2 Sensor", "g/m^2")
el_meter = Sensor("a2f8690f-2b3a-43cd-90b8-9deea98b42a7", "Volt Watch Elite", "MysticEnergy Innovations", "Electricity Meter", "kWh")
heat_pump = ActuatorWithSensor("5e13cabc-5c58-4bb3-82a2-3039e4480a6d", "Thermo Smart 6000", "ElysianTech", "Heat Pump")
motion = Sensor("cd5be4e8-0e6b-4cb5-a21f-819d06cf5fc5", "MoveZ Detect 69", "NebulaGuard Innovations", "Motion Sensor")
humidity = Sensor("3d87e5c0-8716-4b0b-9c67-087eaaed7b45", "Aqua Alert 800", "AetherCorp", "Humidity Sensor", "%")
oven = Actuator("8d4e4c98-21a9-4d1e-bf18-523285ad90f6", "Pheonix HEAT 333", "AetherCorp", "Smart Oven")
garage_door = Actuator("9a54c1ec-0cb5-45a7-b20d-2a7349f1b132", "Guardian Lock 9000", "MythicalTech", "Automatic Garage Door")
oven_2 = Actuator("c1e8fa9c-4b8d-487a-a1a5-2b148ee9d2d1", "Ember Heat 3000", "IgnisTech Solutions", "Smart Oven")
temp = Sensor("4d8b1d62-7921-4917-9b70-bbd31f6e2e8e", "SmartTemp 42", "AetherCorp", "Temperature Sensor", "°C")
air_quality = Sensor("7c6e35e1-2d8b-4d81-a586-5d01a03bb02c", "AeroGuard Pro", "CelestialSense Technologies", "Air Quality Sensor", "g/m^2")
plug = Actuator("1a66c3d6-22b2-446e-bf5c-eb5b9d1a8c79", "FlowState X", "MysticEnergy Innovations", "Smart Plug")
dehumid = Actuator("9e5b8274-4e77-4e4e-80d2-b40d648ea02a", "Hydra Dry 8000", "ArcaneTech Solutions", "Dehumidifier")
bulp = Actuator("6b1c5f6b-37f6-4e3d-9145-1cfbe2f1fc28", "Lumina Glow 4000", "Elysian Tech", "Light Bulp")

DEMO_HOUSE.register_device(entrance, lock)
DEMO_HOUSE.register_device(entrance, el_meter)
DEMO_HOUSE.register_device(stue, co2)
DEMO_HOUSE.register_device(stue, heat_pump)
DEMO_HOUSE.register_device(stue, motion)
DEMO_HOUSE.register_device(bath1, humidity)
DEMO_HOUSE.register_device(gr1, oven)
DEMO_HOUSE.register_device(garage, garage_door)
DEMO_HOUSE.register_device(bedroom, oven_2)
DEMO_HOUSE.register_device(bedroom, temp)
DEMO_HOUSE.register_device(gr3, air_quality)
DEMO_HOUSE.register_device(office, plug)
DEMO_HOUSE.register_device(bath2, dehumid)
DEMO_HOUSE.register_device(gr2, bulp)



