from ahri import requests
from enum import Enum
from dotenv import dotenv_values

def __init__():
    global env
    env = dotenv_values(".env")
    CheckForEnvironmentVariables()



def CheckForEnvironmentVariables():
    print("Checking Envionment Variables... ",end="")
    
    required = [
        "WEBHOOK_URL",
    ]

    # If a required variable is missing, the entire program will exit
    for key in required:
        if not Exists(key):
            print("\n! Some or all essential environment variables have not been defined.\nSee 'Setup' in ReadME.md for more details.")
            exit()

    print("Done!")




def Exists(key):
    global env

    try:
        env[key]
        return True
    except KeyError as e:
        return False




def Get(key,default):
    if Exists(key):
        return env[key]
    else:
        return default
