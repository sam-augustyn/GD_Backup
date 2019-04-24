#!/usr/bin/env python3

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from hurry.filesize import size
from pyrfc3339 import parse
from magic import from_file
import io, datetime

#SCOPES = ['https://www.googleapis.com/auth/drive']
#SERVICE_ACCOUNT_FILE = 'service.json'


def authenticate(apiName, apiVersion, apiScope):
    ''' Authenticate the user and returns a service object
    @apiName should be the name of the google api
    found here: https://developers.google.com/api-client-library/python/apis/
    @apiVerison should be the version of the api
    @apiScope should be the scope of the google api, this script uses OAuth2 Service Accounts
    found here: https://developers.google.com/identity/protocols/googlescopes '''

    #specify service account file (contains service account information)
    SERVICE_ACCOUNT_FILE = '../service.json'
    #create a credentials object with the service account file and the specificed scope
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=apiScope)
    #build the service object
    service = build(apiName, apiVersion, credentials=credentials)
    #return the service object
    return service

def buildFileDictionary(service):
    ''' Return a dictionary with the format files{name:id}
    @service should be the service object generated in authenticate '''

    # Call the Drive v3 API
    results = service.files().list(fields="files(id, name, size, md5Checksum, modifiedTime)").execute()
    # return an array of files with their associated id
    return results.get('files', [])

def printAllFiles(fileDictionary):
    ''' Prints out a list of files from a dictionary
    @fileDictionary should be a dictionary containing filenames and file ids '''
    print("{0:16} {1:34} {2:6} {3:20} {4:5}".format("Name", "Id", "Size", "Modified", "Hash"))
    for file in fileDictionary:
        print ("{0:16} {1:34} {2:6} {3:20} {4:5}".format(file['name'], file['id'],
                                    size(int(file['size'])),
                                    parse(file['modifiedTime']).strftime('%m/%d/%Y-%H:%M:%S'),
                                    file['md5Checksum']))

def downloadFile(fileId, fileName, service):
    ''' Downloads the file to the current working directory
    @fileId should be a file id
    @service should be a service object from the authenticate method '''

    #create a file to write the bytes too
    fileBuffer = io.FileIO(f'./{fileName}', 'wb')
    #get the file's content
    request = service.files().get_media(fileId=fileId)
    #create the download object, pass in fileBuffer and service request
    downloader = MediaIoBaseDownload(fileBuffer, request)
    done = False
    #while the file is downloading show progress
    while done is False:
        #download the next chunk, if it is done escape the loop
        status, done = downloader.next_chunk()
        #print the current progress to the screen
        print (f"Download {int(status.progress() * 100)}%.")
    #close the file so it can be opened elsewhere
    fileBuffer.close()

def uploadFile(fileName, service):
    ''' Uploads a file to a specificed location in the drive
    @fileName should be the file that should be uploaded
    @service should be a service object from the authenticate method '''

    #check the mimetype
    mimetype = from_file(fileName, mime=True)
    #creates a media file upload object
    ###consider chunk size in the future
    media = MediaFileUpload(fileName, mimetype=mimetype)
    #creates a new file
    file = service.files().create(body={'name': fileName.split('/')[-1]},
                                media_body=media).execute()

def checkDriveUseage(service):
    ''' Checks the drive useage for a service object
    @service should be a service object from the authenticate method '''

    #return the storage quota of the current service object
    return service.about().get(fields='storageQuota').execute()

def printStorageQuota(storageQuota):
    ''' Prints the storage quota for the current service object
    @storageQuota should be the result returned from about.get() '''

    #get google drive limit
    limit = float(storageQuota['limit'])
    #get the usage of the drive
    usage = float(storageQuota['usage'])
    #get the usage percentage
    usagePercentage = ("{0:.2f}".format(usage/limit))
    #print out the results
    print(f"Limit: {size(limit)} -- Usage: {size(usage)} -- Usage: {usagePercentage}%")

def main():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service = authenticate('drive', 'v3', SCOPES)
    files =  buildFileDictionary(service)
    printAllFiles(files)
    #downloadFile(files[0]["id"],files[0]["name"], service)
    #uploadFile('file.txt', service)
    #printAllFiles(buildFileDictionary(service))
    #printStorageQuota(checkDriveUseage(service).get('storageQuota'))

if __name__ == "__main__": main()
