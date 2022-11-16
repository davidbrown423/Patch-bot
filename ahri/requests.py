from os import replace
from math import ceil
from time import sleep
from requests.api import get, post
import ahri.env
import requests
from bs4 import BeautifulSoup
from colorama import Fore

def __init__():
    global posted_urls
    posted_urls = []
    global failed_posts
    failed_posts = []



def ScrapePatchNotes():
    patch_notes_url = "https://na.leagueoflegends.com/en-us/news/tags/patch-notes/"
    patch_notes_prefix = "https://na.leagueoflegends.com"

    found_patches = []

    print("Pulling latest patch notes ... ",end="")

    try:
        patch_notes_page = requests.get(patch_notes_url,timeout = 60)
    except Exception as error:
        print(Fore.RED + "! Unable to connect ({}).".format(error.__class__.__name__) + Fore.WHITE)
        # We can just return an empty list if we cannot connect, as the program should proceed as if nothing new has been found
        return found_patches

    if patch_notes_page.status_code == 200: #OK
        # Find all 'a' elements with a href attribute held within (Any patch note entries currently listed)
        patch_entry_classes = BeautifulSoup(patch_notes_page.text,"html.parser").find_all("a", href=True)
    
        for entry in patch_entry_classes:
            # Grab Patch notes title in plaintext from the first h2 element found.
            entry_title = entry.find("h2").contents[0]
            # Grab the suffix for the Patch notes' URL to append to the original request URL.
            entry_link = patch_notes_prefix + entry["href"]
             
            found_patches.insert(0,(entry_title,entry_link))    
        
    print(Fore.GREEN + "Done." + Fore.WHITE)

    # Remove any patch notes that have already been posted in the past
    found_patches = PrunePatchNotes(found_patches)

    return found_patches



def PrunePatchNotes(patches_list):
    posted = []

    print("Pruning existing patch note entries ... ",end="")

    try:
        existing_notes = open("posted.dat", 'r')
        # Strip newline characters for an equal comparison
        for url in existing_notes:
            posted.append(url.replace("\n",""))
        existing_notes.close()

        # If any URLs match from the posted.txt file, then it should be removed as it has been already posted
        for url in posted:
            for entry in patches_list:
                if entry[1] == url:
                    patches_list.pop(patches_list.index(entry))
                    break

        print(Fore.GREEN + "Done." + Fore.WHITE)

        return patches_list
    except FileNotFoundError:
        # If a posted.txt file doesn't exist, then we can return the list as is, as they'll all be new by the time we post it and write it to file
        print(Fore.GREEN + "Done." + Fore.WHITE)
        return patches_list



def ResolveFailedPosts():
    # If we have have any succesfully scraped posts that could not send previously we will try to send them again.
    if len(failed_posts) > 0:
        posts = failed_posts.copy()
        failed_posts.clear()

        print(Fore.CYAN + "Attempting to post previously unsuccessful entries." + Fore.WHITE)
        for post in posts:
            PostMessage(post[0],post[1])

        LogPostedEntries()
        print()

def PostMessage(title,url):
    # Pull and prepare patch note message
    message_body = ahri.env.Get("UPDATE_MESSAGE",
    "{AT_SUBSCRIBERS}\n\n**{TITLE}** are now available:\n{LINK}"
    )

    # Include a mention to a particular role if specified
    if ahri.env.Exists("SUBSCRIBER_ROLE"):
        message_body = message_body.replace("{AT_SUBSCRIBERS}","<@&{}>".format(ahri.env.Get("SUBSCRIBER_ROLE","")))
    else:
        message_body = message_body.replace("{AT_SUBSCRIBERS}","")
    # Insert the title and URL of the patch note being posted.
    message_body = message_body.replace("{TITLE}",title)
    message_body = message_body.replace("{LINK}",url)
    
    # Prepare a JSON payload to go with the request
    message_content = {
        "content" : message_body
    }

    print("Posting message for {} ... ".format(Fore.CYAN + title + Fore.WHITE),end="")
    
    try:
        # We do not need to account for a webhook not existing, as it is checked for at startup
        webhook_url = str(ahri.env.Get("WEBHOOK_URL",""))
        # Strip any query string parameters if found as we will need to use 'wait', or append it if none have been specified.
        if webhook_url.find("?") != -1:  
            webhook_url = webhook_url[:webhook_url.find("?")] + "?wait=true"
        else:
            webhook_url += "?wait=true"
            
        sent_message = requests.post(webhook_url,json=message_content)
        recieved = sent_message.json()
        
        # Message ID has been returned by Discord, meaning it has been posted successfully.
        if recieved.get("id",0): 
            posted_urls.append(url)
            print(Fore.GREEN + "Done. (Message ID {})".format(recieved.get("id",0)) + Fore.WHITE)

            # If we are about to be rate limited by Discord, we will need to wait for however long is specified
            if ("X-RateLimit-Remaining" in sent_message.headers) and ("X-RateLimit-Reset-After" in sent_message.headers):
                remaining_requests = int(sent_message.headers["X-RateLimit-Remaining"])
                request_reset_wait = ceil(float(sent_message.headers["X-RateLimit-Reset-After"]))
                if remaining_requests == 0:
                    sleep(request_reset_wait)
        else:
            print(Fore.RED + "! Failed to send. (HTTP {})".format(str(sent_message.status_code)) + Fore.WHITE)
            failed_posts.append((title,url))
    except Exception as error:
            print(Fore.RED + "! Unable to connect ({}).".format(error.__class__.__name__) + Fore.WHITE)
            failed_posts.append((title,url))

        

def LogPostedEntries():
    print("Logging successfully posted entries to file ... ",end="")

    # Python will automatically create a file when using write or append-mode if it does not exist, we do not need to check it
    log_file = open("posted.dat","a")
    for url in posted_urls:
        log_file.write(url + "\n")
    log_file.close()

    posted_urls.clear()
    print(Fore.GREEN + "Done." + Fore.WHITE)