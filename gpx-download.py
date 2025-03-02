#!/bin/env python3

import argparse
from html.parser import HTMLParser
from os import path
from urllib.error import URLError
from urllib.parse import urlparse, unquote
from urllib.request import urlopen
import sys

class ParserError(RuntimeError):
    def __init__(self, fmt, *args, **kwargs):
        super().__init__(fmt.format(*args, **kwargs))

class DownloadError(RuntimeError):
    def __init__(self, fmt, *args, **kwargs):
        super().__init__(fmt.format(*args, **kwargs))

class GpxParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self._gpx_links = []

        if isinstance(html, str):
            pass
        elif isinstance(html, bytes):
            html = html.decode('utf8')
        else:
            raise ParserError('cannot parse html: request returned {}', html.__class__)
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                try:
                    url = urlparse(value, scheme='https')
                except ValueError:
                    continue
                if attr == 'href' and url.path.endswith('.gpx'):
                    self._gpx_links.append(url)

    def found_links(self):
        return len(self._gpx_links) != 0

    @property
    def links(self):
        for link in self._gpx_links:
            yield link

class GpxDownloader:
    def __init__(self, prefix):
        self._prefix = prefix

    def download(self, link, destination):
        with urlopen(link) as response:
            body = response.read()
            gpx = GpxParser(body)
            if not gpx.found_links():
                raise DownloadError('no gpx files found at <{}>', link)

            for link in gpx.links:
                name = unquote(link.path.split('/')[-1])
                file_name = self._prefix + ' ' + name
                file_name = file_name.replace(' ', '_')

                name = file_name.removesuffix('.gpx')
                try:
                    with urlopen(link.geturl()) as dl:
                        gpx_file = path.join(destination, file_name)
                        with open(gpx_file, mode='bx') as f:
                            f.write(dl.read())
                        print('downloaded <{}>: {}'.format(name, gpx_file))
                except (URLError, FileExistsError, FileNotFoundError) as e:
                    raise DownloadError('failed to download <{}>: {}', link.geturl(), e)

def main():
    parser = argparse.ArgumentParser(description='Find and download .gpx files on websites')
    parser.add_argument('--out-dir', required=True, help='Directory to download the .gpx files to')
    parser.add_argument('links', metavar='<LINKS>',
                        help='Path to a CSV file. Each line consists of <PREFIX>,<LINK>')
    args = parser.parse_args()

    errors = 0
    with open(args.links) as links:
        for line in links:
            parts = line.strip().split(',')
            if len(parts) != 2:
                print(f'skipping line <{line}>: need two columns', file=sys.stderr)
                errors = errors + 1
                continue
            desc = parts[0]
            link = parts[1]
            try:
                GpxDownloader(desc).download(link, args.out_dir)
            except DownloadError as e:
                print(f'GPX download failed: {e}', file=sys.stderr)
                errors = errors + 1

    if errors != 0:
        exit(1)

if __name__ == '__main__':
    main()
