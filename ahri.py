import ahri.env
import ahri.requests
from datetime import datetime
from time import sleep
from colorama import Fore

def GetCurrentTimeString():
    return "{}".format(datetime.now().time().strftime("%H:%M:%S"))



while True:
    print(Fore.YELLOW + "\n[{}]".format(GetCurrentTimeString()) + Fore.WHITE)

    ahri.requests.ResolveFailedPosts();

    patches = []
    patches = ahri.requests.ScrapePatchNotes()

    if(len(patches) > 0):
        print("{} new Patch Note post(s) have been found:".format(len(patches)))

        for entry in patches:
            print("    - {} : {}".format(entry[0],Fore.CYAN + entry[1] + Fore.WHITE))

        print()

        for entry in patches:
            ahri.requests.PostMessage(entry[0],entry[1])

        ahri.requests.LogPostedEntries()
    else:
        print("No new Patch Note entries have been found.")

    print(Fore.YELLOW + "All done!\n\n" + Fore.WHITE)
    sleep(int(ahri.env.Get("QUERY_RATE",600)))
