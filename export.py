#!./venv/bin/python
import collections
import logging
import math
import os
import pathlib
import re
import shutil
import sys

import ffmpeg

logging.basicConfig(stream=sys.stderr,
                    format='export: %(message)s', level=logging.INFO)


Album = collections.namedtuple('Album', [
    'name',
    'artist',
    'src',
    'dst',
])


def main():
    for album in filter(filter_albums, scan_albums()):
        copy_album(album)
    validate_export_size()


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '{} {}'.format(s, size_name[i])


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def validate_export_size(limit=34359738368): # 32 gig
    size = get_size('./export')
    if size > limit:
        logging.error('export folder is too big by %s', convert_size(size - limit))
    else:
        logging.info('export folder is small enough by %s', convert_size(limit - size))


def filter_albums(album):
    fav_artists = [
        'ADELE',
        'BEEGIE ADAIR',
        'BEYONCÉ',
        'BON IVER',
        'CELINE DION',
        'CHARLI XCX',
        'DANNY GO',
        'DC TALK',
        'FRANK OCEAN',
        'KANYE WEST',
        'KENNY BEATS',
        'KENNY LATTIMORE',
        'LIL NAS X',
        'LUTHER VANDROSS',
        'MARVIN GAYE',
        'NONAME',
        'SWITCHFOOT',
    ]
    if album.artist.upper() in fav_artists:
        return True

    fav_albums = [
        '10 DAY',
        'ACID RAP',
        'CHARLI',
        'CHRISTMAS AT HOME',
        'COLORING BOOK',
        'EVERMORE',
        'EVERY KINGDOM',
        'FOLKLORE',
        'JESUS IS BORN',
        'KIDS SEE GHOSTS',
        'LOVER',
        'THE TORTURED POETS DEPARTMENT',
        'SNACKTIME',
        'SPIDER-MAN: INTO THE SPIDER-VERSE',
        'SURF',
        'THE 20-20 EXPERIENCE (DELUX EDITION)',
        'MERRY CHRISTMAS LIL MAMA (THE GOOD PARTS)',
    ]
    if album.name.upper() in fav_albums:
        return True

    if album.name.upper().startswith('ALEX\'S'):
        return True

    return False


def copy_album(album):

    if not album.dst.is_dir():
        logging.info('copying %s', album.name)
        album.dst.mkdir()

    for t in album.src.glob('*.*'):
        # junk file
        if t.suffix in ('.txt', '.jpg', ''):
            continue

        # already converted
        if (album.dst / f'{t.stem}.mp3').is_file():
            continue

        # mp3s can be copied
        if t.suffix == '.mp3':
            shutil.copyfile(t, album.dst / t.name)
            continue

        # otherwise we have to convert
        logging.info('converting %s to mp3', t.name)
        (
            ffmpeg
            .input(str(t))
            .output(str(album.dst / f'{t.stem}.mp3'))
            .global_args('-loglevel', 'quiet')
            .run()
        )


def scan_albums() -> list[Album]:
    for d in pathlib.Path('./music').iterdir():
        if d.name.startswith('.'):
            continue

        if match := re.compile(r'^(?P<artist>.*?) - (?P<album>.*?) ?(?P<year>\(\d{4}\))?$').search(d.name):
            # Artist - Album (year)
            name = match.group(2)
            artist = match.group(1)
            dst = pathlib.Path(f'./export/{artist} - {name}')
            yield Album(name=name, artist=artist, src=d, dst=dst)
        elif match := re.compile(r'^(?P<album>.*?)$').search(d.name):
            # Name
            name = match.group(1)
            dst = pathlib.Path(f'./export/{name.replace(":", " - ")}')
            yield Album(name=name, artist='Various Artists', src=d, dst=dst)
        else:
            raise ValueError(f'{d.name} does not match any expected patterns!')


if __name__ == '__main__':
    main()
