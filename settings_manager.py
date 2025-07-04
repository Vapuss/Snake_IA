# settings_manager.py
import json
import os


SETTINGS_FILE = "settings.json"

def save_settings(name):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"player_name": name}, f)



def save_speed_to_settings(speed):
    try:
        with open("settings.json", "r") as f:
            data = json.load(f)
    except:
        data = {}

    data["snake_speed"] = speed

    with open("settings.json", "w") as f:
        json.dump(data, f, indent=2)


def save_full_settings(data: dict):
    with open("settings.json", "w") as f:
        json.dump(data, f, indent=2)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return data.get("player_name", "Player")
    return "Player"


def get_ai_snake_count():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("ai_snake_count", 8)
    except:
        return 8
    

def get_ai_only_snake_count():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("ai_only_snake_count", 10)
    except:
        return 10
    
def get_headstart_duration():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("headstart_duration", 10)
    except:
        return 10

def get_challengers_enabled():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("challengers_enabled", True)  # Default la True
    except:
        return True  # Dacă nu există setări, activăm challengeri


def get_snake_speed():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("snake_speed", 10)
    except:
        return 10
    


def get_block_size():
    try:
        with open("settings.json", "r") as f:
            return json.load(f).get("block_size", 50)
    except:
        return 50
