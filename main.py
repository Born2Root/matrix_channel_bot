#!/usr/bin/env python3

#Dependecy of the following packages:
# pip install matrix-nio
# for e2e encryption: pip install "matrix-nio[e2e]"
# pip install nio
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade Pillow

# Optional. Darüber könnte man den Filetype checken, dass es auch wirklich ein Bild ist
# pip install python-magic
# pip install python-libmagic

import asyncio
import json
import os
import sys
import getpass
from PIL import Image   #for handling images
import aiofiles.os
import random   #for randomizing
import shutil   #for handling files

from nio import AsyncClient, LoginResponse, UploadResponse  #for matrix

CONFIG_FILE = "credentials.json"

# Check out main() below to see how it's done.

def write_details_to_disk(resp: LoginResponse, homeserver) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Arguments:
        resp {LoginResponse} -- the successful client login response.
        homeserver -- URL of homeserver, e.g. "https://matrix.example.org"
    """
    # open the config file in write-mode
    with open(CONFIG_FILE, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": homeserver,  # e.g. "https://matrix.example.org"
                "user_id": resp.user_id,  # e.g. "@user:example.org"
                "device_id": resp.device_id,  # device ID, 10 uppercase letters
                "access_token": resp.access_token  # cryptogr. access token
            },
            f
        )


async def send_image(client, room_id, image):
    """Send image to room.

    Arguments:
    ---------
    client : Client
    room_id : str
    image : str, file name of image

    This is a working example for a JPG image.
        "content": {
            "body": "someimage.jpg",
            "info": {
                "size": 5420,
                "mimetype": "image/jpeg",
                "thumbnail_info": {
                    "w": 100,
                    "h": 100,
                    "mimetype": "image/jpeg",
                    "size": 2106
                },
                "w": 100,
                "h": 100,
                "thumbnail_url": "mxc://example.com/SomeStrangeThumbnailUriKey"
            },
            "msgtype": "m.image",
            "url": "mxc://example.com/SomeStrangeUriKey"
        }

    """
    #TODO: Here an file test could be done, to check if file is an image
    mime_type = "image/jpeg"
    if not mime_type.startswith("image/"):
        print("Drop message because file does not have an image mime type.")
        return

    im = Image.open(image)
    (width, height) = im.size  # im.size returns (width,height) tuple

    # first do an upload of image, then send URI of upload to room
    file_stat = await aiofiles.os.stat(image)
    async with aiofiles.open(image, "r+b") as f:
        resp, maybe_keys = await client.upload(
            f,
            content_type=mime_type,  # image/jpeg
            filename=os.path.basename(image),
            filesize=file_stat.st_size)
    if (isinstance(resp, UploadResponse)):
        print("")
        #print("Image was uploaded successfully to server. ")
    else:
        print(f"Failed to upload image. Failure response: {resp}")

    content = {
        #"body": os.path.basename(image),  # descriptive title, here it's filename, alternative Picture Description
        "body": "",
        "info": {
            "size": file_stat.st_size,
            "mimetype": mime_type,
            "thumbnail_info": None,  # TODO
            "w": width,  # width in pixel
            "h": height,  # height in pixel
            "thumbnail_url": None,  # TODO
        },
        "msgtype": "m.image",
        "url": resp.content_uri,
    }

    try:
        await client.room_send(
            room_id,
            message_type="m.room.message",
            content=content
        )
        #print("Image was sent successfully")
    except Exception:
        print(f"Image send of file {image} failed.")


async def main() -> None:
    # If there are no previously-saved credentials, we'll use the password
    if not os.path.exists(CONFIG_FILE):
        print("First time use. Did not find credential file. Asking for "
              "homeserver, user, and password to create credential file.")
        homeserver = "https://matrix.example.org"
        homeserver = input(f"Enter your homeserver URL: [{homeserver}] ")

        if not (homeserver.startswith("https://")
                or homeserver.startswith("http://")):
            homeserver = "https://" + homeserver

        user_id = "@user:example.org"
        user_id = input(f"Enter your full user ID: [{user_id}] ")

        device_name = "matrix-nio"
        device_name = input(f"Choose a name for this device: [{device_name}] ")

        client = AsyncClient(homeserver, user_id)
        pw = getpass.getpass()

        resp = await client.login(pw, device_name=device_name)

        # check that we logged in succesfully
        if (isinstance(resp, LoginResponse)):
            write_details_to_disk(resp, homeserver)
        else:
            print(f"homeserver = \"{homeserver}\"; user = \"{user_id}\"")
            print(f"Failed to log in: {resp}")
            sys.exit(1)

        print(
            "Logged in using a password. Credentials were stored.",
            "Try running the script again to login with credentials."
        )

    # Otherwise the config file exists, so we'll use the stored credentials
    else:
        # open the file in read-only mode
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            client = AsyncClient(config['homeserver'])

            client.access_token = config['access_token']
            client.user_id = config['user_id']
            client.device_id = config['device_id']


    # Automatic Bulk-Mode:
        try:
            #Read in roomlist file if existing. Otherwise switch to manual mode
            with open('roomlist.txt') as roomlist_file:
                rooms = [line.rstrip() for line in roomlist_file]
            
                for i in rooms:
                    print(i)
                    room_id = i
                    
                    #extract foldername (single number token) from complete room_id with special characters
                    foldername_raw = room_id.split(":")[0]
                    foldername = foldername_raw[1:] #remove the ! first character
                    
                    #get a random image from folder           
                    image = random.choice(os.listdir(foldername))
                    #send image to matrix-room              
                    await send_image(client, room_id, foldername + '/' + image)
                    
                    #move send picture to subfolder "send". If not existend, folder will be created
                    shutil.move(foldername + '/' + image, foldername + '/send/')
                                        
                    print("Automatic Mode: Sent one picture to room " + i)           
            
        except IOError:
    # Manual Send
            print('error automatic mode: roomlist.txt or picture folder missing. Switching to manual mode.')
            # Now we can send messages as the user
            room_id = "!myfavouriteroomid:example.org"
            room_id = input(f"Enter room id for image message: [{room_id}] ")

            image = "exampledir/samplephoto.jpg"
            image = input(f"Enter file name of image to send: [{image}] ")
            
            await send_image(client, room_id, image)
            print("Manual Mode: Logged in using stored credentials. Sent one picture.")

    # Close the client connection after we are done with it.
    await client.close()

asyncio.get_event_loop().run_until_complete(main())