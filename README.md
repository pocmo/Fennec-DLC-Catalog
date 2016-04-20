# Fennec DLC tool

Manage a catalog of downloadable content for Fennec in Kinto.

## Usage

```
usage: fennec-dlc [-h] [--auth AUTH] --url URL [--dry-run] [--version]
                  COMMAND ...

Manage a catalog of downloadable content for Fennec in Kinto

optional arguments:
  -h, --help   show this help message and exit
  --auth AUTH  credentials for HTTP auth.
  --url URL    URL pointing to the Kinto collection
  --dry-run    do everything except actually send the updates.
  --version    show program's version number and exit

commands:
  Action to perform on the online catalog

  COMMAND
    create     upload files to the catalog
    update     update files in the catalog
    delete     delete files from the catalog
    restrict   restrict download of files to specific app versions
    read       read and print the catalog in a human readable form
    sync       synchronize online catalog from a local manifest file
```

## Create - Uploading files to the catalog

```
usage: fennec-dlc create [-h] [--type TYPE] [--kind KIND] [--compress]
                         FILE [FILE ...]

positional arguments:
  FILE         a file to upload and add to the catalog

optional arguments:
  -h, --help   show this help message and exit
  --type TYPE  type of the content (default: asset-archive)
  --kind KIND  kind of the content (default: guess from MIME type)
  --compress   compress the file before uploading (gzip). Files of type
               "asset-archive" will always be compressed.
```

## Update - Updating files in the catalog

```
TBD
```

## Delete - Deleting files from the catalog

```
TBD
```

## Restrict - Restrict download of files

```
TBD
```

## Read - Print the catalog in a human readable form

```
TBD
```

## Sync - Synchronize the catalog with a local manifest file

```
TBD
```

## License

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
