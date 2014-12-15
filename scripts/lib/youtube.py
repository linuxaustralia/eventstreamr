'''
Copyright 2013, Google Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import httplib
import httplib2
import random
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow, OOB_CALLBACK_URN


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


# A limited OAuth 2 access scope that allows for uploading files, but not other
# types of account access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_youtube_service(credential_storage_file, client_id, client_secret):
    flow = OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope=YOUTUBE_UPLOAD_SCOPE,
        redirect_uri=OOB_CALLBACK_URN)

    storage = Storage(credential_storage_file)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        # Start Authorization Process
        authorize_url = flow.step1_get_authorize_url()

        # Give user URL for authorization
        print
        print authorize_url
        print

        # Prompt for authorization code
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)

        # Save credentials for next time
        storage.put(credentials)
        credentials.set_store(storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def resumable_upload(service, insert_request):
    response = None
    error = None
    retry = 0

    print "Starting upload"
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if response:
                print "Upload Complete"
                return response
            elif status:
                print "Upload %d%% complete." % int(status.progress() * 100)
        except HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print error
            retry += 1
            if retry > MAX_RETRIES:
                raise Exception("No longer attempting to retry")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print "Sleeping %f seconds and then retrying..." % sleep_seconds
            time.sleep(sleep_seconds)

def resumable_youtube_upload(youtube, filename, video_info):
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=video_info,
        # chunksize=-1 means that the entire file will be uploaded in a single
        # HTTP request. (If the upload fails, it will still be retried where it
        # left off.) This is usually a best practice, but if you're using Python
        # older than 2.6 or if you're running on App Engine, you should set the
        # chunksize to something like 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(filename, chunksize=-1, resumable=True)
    )
    return resumable_upload(youtube, insert_request)
