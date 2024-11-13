#!./venv/bin/python
import logging
import pathlib
import shutil
import sys


def main():
    thumbstick = pathlib.Path('/Volumes/MUSIC/')

    for result in thumbstick.glob('*'):
        if result.name == '.Spotlight-V100':
            continue
        shutil.rmtree(result)
        logging.info('removed %s', result)

    export_dir = pathlib.Path('./export')
    album_dirs = sorted([d for d in export_dir.glob('*') if d.is_dir()])
    for album_dir in album_dirs:
        album_dir_target = thumbstick / album_dir.name
        album_dir_target.mkdir()
        logging.info('created %s', album_dir_target)
        for song_file in sorted(album_dir.glob('*.*')):
            song_file_target = album_dir_target / song_file.name
            shutil.copy(song_file, song_file_target)
            logging.info('copied %s', song_file_target)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='copy: %(message)s')
    main()
