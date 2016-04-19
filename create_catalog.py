# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import gzip
import json
import hashlib
import mimetypes
import os
import pprint
import uuid
import StringIO

FILES = [
    'mobile/android/fonts/CharisSILCompact-B.ttf',
    'mobile/android/fonts/CharisSILCompact-BI.ttf',
    'mobile/android/fonts/CharisSILCompact-I.ttf',
    'mobile/android/fonts/CharisSILCompact-R.ttf',
    'mobile/android/fonts/ClearSans-Bold.ttf',
    'mobile/android/fonts/ClearSans-BoldItalic.ttf',
    'mobile/android/fonts/ClearSans-Italic.ttf',
    'mobile/android/fonts/ClearSans-Light.ttf',
    'mobile/android/fonts/ClearSans-Medium.ttf',
    'mobile/android/fonts/ClearSans-MediumItalic.ttf',
    'mobile/android/fonts/ClearSans-Regular.ttf',
    'mobile/android/fonts/ClearSans-Thin.ttf',
]

try:
    import requests
except ImportError:
    raise RuntimeError("requests is required")


def sha256(content):
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()


def fetch_records(session, url):
    response = session.get(url)
    response.raise_for_status()
    return response.json()['data']


def files_to_upload(records, files):
    records_by_id = {r['id']: r for r in records if 'attachment' in r}
    to_upload = []
    for filepath in files:
        filename = os.path.basename(filepath)

        identifier = hashlib.md5(filename.encode('utf-8')).hexdigest()
        record_id = str(uuid.UUID(identifier))

        record = records_by_id.pop(record_id, None)
        if record:
            local_hash = sha256(open(filepath, 'rb').read())

            # If file was uploaded gzipped, compare with hash of uncompressed file.
            remote_hash = record.get('original', {}).get('hash')
            if not remote_hash:
                remote_hash = record['attachment']['hash']

            # If hash has changed, upload !
            if local_hash != remote_hash:
                print("File '%s' has changed." % filename)
                to_upload.append((filepath, record))
            else:
                print("File '%s' is up-to-date." % filename)
        else:
            record = {'id': record_id}
            to_upload.append((filepath, record))

    # XXX: add option to delete records when files are missing locally
    for id, record in records_by_id.items():
        print("Ignore remote file '%s'." % record['attachment']['filename'])

    return to_upload


def compress_content(content):
    out = StringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(content)
    return out.getvalue()


def create_collection(session, url, force):
    collection = url.split('/')[-1]
    bucket = url.split('/')[-3]
    bucket_endpoint = '/'.join(url.split('/')[:-2])

    resp = session.request('get', bucket_endpoint)
    data = {"permissions": {"read": ["system.Everyone"]}}

    if resp.status_code == 200:
        existing = resp.json()
        # adding the right permission
        read_perm = existing['permissions'].get('read', [])
        if not "system.Everyone" in read_perm:
            if force:
                session.request('patch', bucket_endpoint, json=data)
            else:
                print('Changing bucket permissions')
    else:
        # creating the bucket
        if force:
            session.request('put', bucket_endpoint, json=data)
        else:
            print('creating bucket')

    if force:
        session.request('put', url)
    else:
        print('adding the collection')


def upload_files(session, url, files, force):
    permissions = {}  # XXX not set yet

    for filepath, record in files:
        mimetype, _ = mimetypes.guess_type(filepath)
        if mimetype is None:
            raise TypeError("Could not recognize the mimetype for %s" % filepath)
        filename = os.path.basename(filepath)
        filecontent = open(filepath, "rb").read()

        attributes = {
            'type': 'asset-archive',  # Only supported type so far

            'original': {
                'filename': filename,
                'hash': sha256(filecontent),
                'mimetype': mimetype,
                'size': len(filecontent),
            }
        }

        if mimetype == 'application/x-font-ttf':
            attributes['kind'] = 'font'

        filename += '.gz'

        mimetype = 'application/x-gzip'

        filecontent = compress_content(filecontent)

        attachment_uri = '%s/%s/attachment' % (url, record['id'])
        multipart = [("attachment", (filename, filecontent, mimetype))]
        payload = {'data': json.dumps(attributes), 'permissions': json.dumps(permissions)}

        if force:
            response = session.post(attachment_uri, data=payload, files=multipart)
            response.raise_for_status()
            pprint.pprint(response.json())
        else:
            pprint.pprint(payload)


def main():
    parser = argparse.ArgumentParser(description='Upload files to Kinto')
    parser.add_argument('--url', dest='url', action='store', help='Collection URL', required=True)
    parser.add_argument('--auth', dest='auth', action='store', help='Credentials', required=True)
    parser.add_argument('--repository', dest='repository', action='store', help='Path to repository checkout (mozilla-central)',
                        default='.')
    parser.add_argument('--force', dest='force', action='store_true', help='Actually perform actions on the server. Without this no request will be sent')

    args = parser.parse_args()

    if not args.force:
        print('=== DRY RUN === (Use --force to actually perform those actions)')

    session = requests.Session()
    if args.auth:
        session.auth = tuple(args.auth.split(':'))

    url = args.url
    if url.endswith('/'):
        url = url[:-1]

    create_collection(session, url, args.force)

    if not url.endswith('records'):
        url += '/records'

    repository = args.repository
    if not repository.endswith('/'):
        repository += '/'

    existing = fetch_records(session, url=url)

    files = []
    for file in FILES:
        files.append(repository + file)

    to_upload = files_to_upload(existing, files)
    upload_files(session, url, to_upload, args.force)


if __name__ == '__main__':
    main()
