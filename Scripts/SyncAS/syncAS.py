#!/usr/bin/python3

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from os import listdir, chdir
from _thread import start_new_thread
from inotify.adapters import Inotify
from pickle import dump, load
from httplib2 import ServerNotFoundError
from requests import get, exceptions

AS_ID = "1g0wTNqgz2UXbCdBFkLLek7eRLKgBrBKg"
DIRS = ["Fisica/", "Inglese/", "Italiano/", "Latino/", "Scienze/", "Storia/", "Scienze/Slide originali/"]
ID = {"Scienze" : "1l61Sv77O4dqwOsAMr7ZNr2uA725xS1Do",
    "Latino": "1BsE1-fUJVoDHrFV7YMp4GvYvS4xJ0_d3",
    "Italiano": "1gyDGXHzEsurxPx1yptf9yzSlEpEwSETM",
    "Inglese": "1aau0oPBTO-GJNPG7i3QojpnrCqeLtpLq",
    "Fisica": "17VRyHuRC5W5uqWGszGFCdUHCcra3dflm",
    "Storia": "1Hnr3D3pI0V6VR4c1_-uhxGLKvq_z7-E5",
    "Slide originali": "1EWloBpYFCcuY6UcdrxtLXHOaKiUcx0zX"}
NEW_WRITE = ["IN_CREATE", "IN_OPEN", "IN_MODIFY", "IN_CLOSE_WRITE", "IN_OPEN", "IN_CLOSE_NOWRITE"]
OVERWRITE = ["IN_OPEN", "IN_ACCESS", "IN_CLOSE_NOWRITE", "IN_OPEN", "IN_MODIFY", "IN_CLOSE_WRITE",
    "IN_OPEN", "IN_MODIFY", "IN_CLOSE_WRITE", "IN_OPEN", "IN_CLOSE_NOWRITE"]
COPIED_TO_OTHER_FOLDER_TERM = ["IN_OPEN", "IN_CREATE", "IN_OPEN", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS",
    "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS",
    "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS",
    "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_ACCESS", "IN_MODIFY", "IN_CLOSE_WRITE",
    "IN_CLOSE_NOWRITE", "IN_OPEN", "IN_CLOSE_NOWRITE"]
COPIED_TO_OTHER_FOLDER_GUI = ["IN_OPEN", "IN_CREATE", "IN_OPEN", "IN_MODIFY", "IN_CLOSE_NOWRITE",
    "IN_CLOSE_WRITE", "IN_ATTRIB", "IN_OPEN", "IN_CLOSE_NOWRITE"]
COPIED_TO_SAME_FOLDER_TERM = ["IN_CREATE", "IN_OPEN", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY",
    "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY", "IN_MODIFY",
    "IN_MODIFY", "IN_CLOSE_WRITE", "IN_OPEN", "IN_CLOSE_NOWRITE"]
COPIED_TO_SAME_FOLDER_GUI = ["IN_CREATE", "IN_OPEN", "IN_MODIFY", "IN_CLOSE_WRITE", "IN_ATTRIB", "IN_OPEN", "IN_CLOSE_NOWRITE"]
RESTORED = ["IN_MOVED_TO", "IN_OPEN", "IN_CLOSE_NOWRITE"]
MOVED = ["IN_MOVED_FROM", "IN_MOVED_TO"]
DELETED = ["IN_DELETE"]

CREDENTIALS = "/home/catomaior/Scripts/SyncAS/credentials.txt"
QUERY = "/home/catomaior/Scripts/SyncAS/query.pkl"

def newFolder(folderName):
    folder_metadata = {
        "title" : folderName,
        "mimeType" : "application/vnd.google-apps.folder",
        "parents" : [{"kind": "drive#fileLink", "id": AS_ID}]
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder["id"]

def uploadAll():
    for dir in DIRS:
        id = newFolder(dir[:-1])
        for pdf in listdir(dir):
            if not pdf[0] == "." and pdf.endswith(".pdf"):
                file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": id}]})
                file.SetContentFile(dir + pdf)
                print("Uploading file " + pdf)
                file["title"] = pdf
                file.Upload()

def updateFile(path, id):
    try:
        if not (path.split("/")[1].lower().endswith(".pdf") or path.split("/")[1].lower().endswith(".pptx")):
            folder = path.split("/")[1]
            file = path.split("/")[2]
        else:
            folder, file = path.split("/")
        newFile = drive.CreateFile()
        file_list = drive.ListFile({"q": "\"" + ID[folder] + "\" in parents and trashed=false"}).GetList()
        for el in file_list:
            if el["title"] == file:
                newFile["id"] = el["id"]
        newFile.SetContentFile(path)
        newFile["title"] = file
        newFile.Upload()
        print("Uploaded file " + path + " to cloud")
        query[id][2] = 2
    except:
        pass

def newFile(path, id):
    try:
        if not (path.split("/")[1].lower().endswith(".pdf") or path.split("/")[1].lower().endswith(".pptx")):
            folder = path.split("/")[1]
            file = path.split("/")[2]
        else:
            folder, file = path.split("/")
        newFile = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": ID[folder]}]})
        newFile.SetContentFile(path)
        newFile["title"] = file
        newFile.Upload()
        print("Uploaded file " + path + " to cloud")
        query[id][2] = 2
    except:
        pass

def deleteFile(path, id):
    try:
        if not (path.split("/")[1].lower().endswith(".pdf") or path.split("/")[1].lower().endswith(".pptx")):
            folder = path.split("/")[1]
            file = path.split("/")[2]
        else:
            folder, file = path.split("/")
        newFile = drive.CreateFile()
        file_list = drive.ListFile({"q": "\"" + ID[folder] + "\" in parents and trashed=false"}).GetList()
        for el in file_list:
            if el["title"] == file:
                newFile["id"] = el["id"]
                newFile.Trash()
                break
        print("Deleted file " + path + " from cloud")
        query[id][2] = 2
    except:
        pass

def moveFile(pathFrom, pathTo):
    deleteFile(pathFrom)
    newFile(pathTo)
    print("Moved file " + pathFrom + " to " + pathTo + " on cloud")

def login():
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(CREDENTIALS)
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile(CREDENTIALS)
        drive = GoogleDrive(gauth)
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(CREDENTIALS)
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile(CREDENTIALS)
        return GoogleDrive(gauth)
        print("Connected to cloud")
    except ServerNotFoundError:
        print("Cannot connect to cloud")
        return True

def isConnected():
    url = "http://www.google.com/"
    try:
        _ = get(url, timeout=0.3)
        return True
    except:
        print("Cannot connect to cloud")
        return False

drive = login()

query = []
"""
[[(Arguments), method, 0/1],
 [(Arguments), method, 0/1],
 ...
 [(Arguments), method, 0/1],
 [(Arguments), method, 0/1]]
"""
try:
    queryFile = open(QUERY, "rb")
    print("Found file query.pkl")
    tempQuery = load(queryFile)
    queryFile.close()
    for el in tempQuery:
        if not el[2] == 2:
            query.append([(el[0][0], len(query),), el[1], el[2]])
except (IOError, UnicodeDecodeError) as e:
    print("File query.pkl not found or corrupt, creating new empty query")

chdir("/home/catomaior/Documents/Scuola/A.S. 2019-2020")

if isConnected():
    for el in query:
        el[2] = 1
        start_new_thread(el[1], el[0])

i = Inotify()
for dir in DIRS:
    i.add_watch(dir)

lastEvent = ()
operations = {"temp": "temp"}
for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event

    if (filename.endswith(".pdf") or filename.endswith(".pptx")) and not (filename[0] == "." or (path, filename, type_names) == lastEvent):
        if not filename in operations:
            operations[filename] = []
        operations[filename].append(type_names[0])
        #print(operations[filename], filename, path)

        lastKey = "temp"
        for key in operations:

            if operations[key][-len(NEW_WRITE):] == NEW_WRITE:
                print("Written new file " + path + filename)
                query.append([(path + filename, len(query),), newFile, 0])
                operations[key] = []

            elif operations[key][-len(OVERWRITE):] == OVERWRITE:
                print("Overwritten file " + path + filename)
                query.append([(path + filename, len(query),), updateFile, 0])
                operations[key] = []

            elif (operations[key][-len(COPIED_TO_OTHER_FOLDER_TERM):] == COPIED_TO_OTHER_FOLDER_TERM or
                    operations[key][-len(COPIED_TO_OTHER_FOLDER_GUI):] == COPIED_TO_OTHER_FOLDER_GUI or
                    operations[key][-len(COPIED_TO_SAME_FOLDER_TERM):] == COPIED_TO_SAME_FOLDER_TERM or
                    operations[key][-len(COPIED_TO_SAME_FOLDER_GUI):] == COPIED_TO_SAME_FOLDER_GUI):
                print("Copied file to " + path + filename)
                query.append([(path + filename, len(query),), newFile, 0])
                operations[key] = []

            # elif len(operations[lastKey]) > 0 and len(operations[key]) > 0:
            # print("lastKey", lastKey, "key", key)
            # if operations[lastKey][-1] == MOVED[0] and operations[key][-1] == MOVED[1]:
            #     print("Moved " + lastEvent[0] + lastEvent[1] + " to " + path + filename)
            #     if path in DIRS:
            #         moveFile(lastEvent[0] + lastEvent[1], path + filename)
            #     else:
            #         start_new_thread(deleteFile, (lastEvent[0] + lastEvent[1],))
            #         operations[key] = []"""

            elif operations[key][-len(RESTORED):] == RESTORED:
                print("Restored file " + path + filename)
                query.append([(path + filename, len(query),), updateFile, 0])
                operations[key] = []

            elif len(operations[key]) > 0 and len(operations[key]) > 0:
                if (operations[key][-1] == DELETED[0] or operations[key][-1] == MOVED[0]):
                    print("Deleted file " + path + filename)
                    query.append([(path + filename, len(query),), deleteFile, 0])
                    operations[key] = []
            #lastKey = key
            lastEvent = (path, filename, type_names)

        queryFile = open(QUERY, "wb")
        dump(query, queryFile)
        queryFile.close()

    for el in query:
        if el[2] == 0:
            if isConnected():
                drive = login()
                el[2] = 1
                start_new_thread(el[1], el[0])
            else:
                drive = login()
                if not drive:
                    print("Could not sync cloud. Adding to queue")
