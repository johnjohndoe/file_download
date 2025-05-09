import urllib.request
import os
import sys
from http import HTTPStatus
from urllib.error import HTTPError

if len(sys.argv) != 3:
    print(f'Usage: python {sys.argv[0]} <url> <file_path>')
    sys.exit(1)

url = sys.argv[1]
file_path = sys.argv[2]

directory_path = os.path.dirname(file_path)
if not os.path.exists(directory_path):
    print(f'Error: directory "{directory_path}" does not exist')
    sys.exit(1)

if os.path.exists(file_path + '.etag'):
    with open(file_path + '.etag', 'r') as f:
        etag = f.read().strip()
        headers = {'If-None-Match': etag}
else:
    headers = {}

req = urllib.request.Request(url, headers=headers)
try:
    response = urllib.request.urlopen(req)
except HTTPError as e:
    if e.code == HTTPStatus.NOT_MODIFIED:
        print('File has not been modified')
        sys.exit(0)
    else:
        print(f'Download failed with HTTP {e.code}')
        sys.exit(1)

if response.status == HTTPStatus.OK:
    content_length = response.headers.get('Content-Length')
    if content_length is not None:
        file_size = int(content_length)
        print(f'File size is {file_size} bytes')
    else:
        print('Could not determine file size')

    with open(file_path, 'wb') as f:
        f.write(response.read())
    print(f'Downloaded file from "{url}" to "{file_path}" successfully')

    downloaded_file_size = os.path.getsize(file_path)
    if content_length is not None:
        if downloaded_file_size == file_size:
            print('File size matches expected size')
        else:
            print(f'Error: downloaded file size ({downloaded_file_size} bytes) does not match expected size ({file_size} bytes)')

    etag = response.headers.get('ETag')
    if etag is not None:
        with open(file_path + '.etag', 'w') as f:
            f.write(etag)
        print(f'Saved ETag {etag} to file {file_path}.etag')
    else:
        print(f'Response does not contain an ETag header')

else:
    print(f'Download failed with HTTP {response.status}')
    sys.exit(1)
