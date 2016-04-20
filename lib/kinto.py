# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests

# A very minimalistic Kinto client customized for our purposes

def post(args):
	session = requests.Session()
	if args.auth:
		session.auth = tuple(args.auth.split(':'))

	url = args.url
	if url.endswith('/'):
		url = url[:-1]
	if not url.endswith('records'):
		url += '/records'

	if args.dryrun:
		dump("POST", url)
		return


def dump(method, url):
	print method, url

