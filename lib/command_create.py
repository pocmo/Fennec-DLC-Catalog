# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import util
import kinto
import json

def perform(args):
	for file in args.files:
		create(args, file)


def create(args, file):
	record_id = util.generate_identifier(file)

	record_data = create_record(args, file)
	permissions = {}

	payload = {'data': json.dumps(record_data), 'permissions': json.dumps(permissions)}
	attachment = create_multipart_attachment(args, file)

	kinto.post(args)
	
	pass


def create_record(args, file):
	return {
		'original': {
			'filename': util.get_file_name(file),
			'hash': util.generate_checksum(file),
			'mimetype': util.get_mime_type(file),
			'size': util.get_file_size(file)
		},
		'kind': util.determine_kind(args.kind, file),
		'type': args.type,
	}


def create_multipart_attachment(args, file):
	name = util.get_file_name(file)
	if args.compress:
		name += 'gz'

	content = (util.get_file_content, util.compress)[args.compress](file)

	mimeType = 'application/x-gzip' if args.compress else util.get_mime_type(file)

	return [("attachment", (name, content, mimeType))]


def evaluate(args):
	if args.type == 'asset-archive':
		args.compress = true

