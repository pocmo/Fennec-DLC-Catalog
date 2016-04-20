# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import hashlib
import mimetypes
import gzip
import StringIO
import uuid
import os


def get_file_name(file):
	return os.path.basename(file)


def get_file_size(file):
	content = get_file_content(file)
	return len(content)


def get_file_content(file):
	return open(file, "rb").read()


def get_mime_type(file):
	mimeType, _ = mimetypes.guess_type(file)
	return mimeType


def generate_identifier(file):
	name = get_file_name(file)
	identifier = hashlib.md5(name.encode('utf-8')).hexdigest()
	return str(uuid.UUID(identifier))


def generate_checksum(file):
	content = get_file_content(file)
	return sha256(content)


def determine_kind(kind, file):
	if kind:
		return kind

	mimeType = get_mime_type(file)

	if mimeType == 'application/x-font-ttf':
		return 'font'

	raise Exception("Can't determine kind for MIME type: %s" % mimeType)


def compress(file):
	content = get_file_content(file)
	out = StringIO.StringIO()

	with gzip.GzipFile(fileobj=out, mode="w") as f:
		f.write(content)

	return out.getvalue()


def sha256(content):
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()