# gpx-download

Download .gpx files from a website.

```
usage: gpx-download.py [-h] --out-dir OUT_DIR <LINKS>

Find and download .gpx files on websites

positional arguments:
  <LINKS>            Path to a CSV file. Each line consists of <PREFIX>,<LINK>

options:
  -h, --help         show this help message and exit
  --out-dir OUT_DIR  Directory to download the .gpx files to
```

The script will download the HTML from the provided link and downloads
all links referencing a file ending with '.gpx'. The downloaded files
will be placed in the directory specified through the `--out-dir`
argument.

The input file `<LINKS` is expected to be a CSV file in the format
`<PREFIX>,<LINK>`, e.g.,
```
FOO,https://my.domain.com/thefoo
BAR,https://their.domain.com/gpx-files
```
