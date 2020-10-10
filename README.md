# Matrix Channel Bot
 **Channel Bot for Matrix-Messenger**
 
 The Bot is intended to use Matrix "Rooms" like Telegram Channels.
 It posts pictures from a defined path several times per day into the desired room.

 Multiple rooms can be handled. They are listed in the "roomlist.txt"

## Usage

- Add the rooms, that you want to send pictures to in the `roomlist.txt` file
  Use the room-ID, that you can find in the Matrix settings of each room.
  (the names should look like: `!CMZlAQQiSoEuRztFIE:matrix.org`)

- running the program for the first time:
  If you run the `main.py` for the first time, you will be asked for your login credits.
  Afterwards the tool stores a security-token, that will be used for future logins.
  You will be adviced to run the main.py again.

- Store the pictures you want to send to each room, in subfolders.
  The subfolders will be named with the corresponding room-ID.
  ATTENTION, under Windows first create the send folders manual. 
  There are some filesystem issues, on windows that prevent to create the folders automatic.
  Each room-ID folder will get a `send` subfolder.
  The send images will be moved to this send folder.
  ATTENTION, under Windows you also have to create this send folder manual!

- run the `main.py` via cronjob, to regulary send pictures to rooms.
  The pictures will be taken from the corresponding folder named with the room-ID.
