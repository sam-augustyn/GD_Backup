from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

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
    SERVICE_ACCOUNT_FILE = 'service.json'
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
    results = service.files().list(fields="nextPageToken, files(id, name)").execute()
    # return an array of files with their associated id
    return results.get('files', [])

def printAllFiles(fileDictionary):
    ''' Prints out a list of files from a dictionary
    @fileDictionary should be a dictionary containing filenames and file ids'''

    #print each file with its id
    for file in fileDictionary:
        print (f"{file['name']} : {file['id']}")

def downloadFile(fileId, fileName, service):
    ''' Downloads the file to the current working directory
    @fileId should be a file id
    @service should be a service object from the authenticate method'''

    # create a file to write the bytes too
    fileBuffer = io.FileIO(f'./{fileName}', 'wb')
    #
    request = service.files().get_media(fileId=fileId)
    downloader = MediaIoBaseDownload(fileBuffer, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print (f"Download {int(status.progress() * 100)}%.")
    #convert the buffer to a file

    fileBuffer.close()

def main():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service = authenticate('drive', 'v3', SCOPES)
    files =  buildFileDictionary(service)
    #printAllFiles(files)
    downloadFile(files[0]["id"],files[0]["name"], service)

if __name__ == "__main__": main()
