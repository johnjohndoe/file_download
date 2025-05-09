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

headers = {}

if os.path.exists(file_path + '.etag'):
    with open(file_path + '.etag', 'r') as f:
        etag = f.read().strip()
        headers['If-None-Match'] = etag

if os.path.exists(file_path + '.lastmod'):
    with open(file_path + '.lastmod', 'r') as f:
        last_modified = f.read().strip()
        headers['If-Modified-Since'] = last_modified

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
        print(f'Saved ETag "{etag}" to file {file_path}.etag')

    last_modified = response.headers.get('Last-Modified')
    if last_modified is not None:
        with open(file_path + '.lastmod', 'w') as f:
            f.write(last_modified)
        print(f'Saved Last-Modified date "{last_modified}" to file {file_path}.lastmod')

    if etag is None and last_modified is None:
        print(f'Response does not contain ETag nor Last-Modified headers')

else:
    print(f'Download failed with HTTP {response.status}')
    sys.exit(1)
