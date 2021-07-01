import ahri.env
import ahri.requests
from datetime import datetime
from time import sleep

def GetCurrentTimeString():
    return "{}".format(datetime.now().time().strftime("%H:%M:%S"))



while True:
    print("\n[{}]".format(GetCurrentTimeString()))

    patches = []
    patches = ahri.requests.ScrapePatchNotes()

    if(len(patches) > 0):
        print("{} new Patch Note post(s) have been found:".format(len(patches)))

        for entry in patches:
            print("    - {} : {}".format(entry[0],entry[1]))

        print()

        for entry in patches:
            ahri.requests.PostMessage(entry[0],entry[1])

        ahri.requests.LogPostedEntries()
    else:
        print("No new Patch Note entries have been found.")

    print("All done!\n\n")
    sleep(int(ahri.env.Get("QUERY_RATE",600)))