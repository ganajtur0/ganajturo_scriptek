#!/usr/bin/python3

import subprocess
import sys
import eyed3
import argparse
from os import path

def set_tags(filename, title, album_name, artist_name, index, cover=None):

    audio = eyed3.load(filename)

    if (audio.tag == None):
        audio.initTag()

    audio.tag.title=title

    audio.tag.album=album_name

    audio.tag.artist=artist_name

    audio.tag.track_num = str(index)

    if cover:
        audio.tag.images.set(3, open(cover,'rb').read(), 'image/jpeg')

    audio.tag.save()


def main():

    parser = argparse.ArgumentParser(description="Split an album into separate songs and tag them with the necessary data.")
    parser._action_groups.pop()
    
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument("album_file", help="The file to be split.")
    required.add_argument("tracklist_file", help="Tracklist information about the album")
    required.add_argument("--template", help="The template of the tracklist file.", required=True)
    required.add_argument("--artist", help="Name of the artist.", required=True)
    required.add_argument("--album", help="Title of the album.", required=True)

    optional.add_argument("--cover_art", help="The album's cover art.")
    optional.add_argument("--dest", help="Destination directory.")

    args = parser.parse_args()

    onlytwo = False

    # record command line args
    album_name = args.album
    artist_name = args.artist
    original_track = args.album_file
    track_list = args.tracklist_file
    template = args.template.split(',')
    cover_art = args.cover_art
    if not args.dest:
        dest = "."
    else:
        dest = path.abspath(path.expanduser(args.dest))

    extension = original_track.split('.')[-1]
    
    if len(template) <= 1 or len(template) >= 4:
        print('Error: Invalid template')
        return

    elif len(template) == 2:
        sindex = template.index('start')
        nindex   = template.index('name')
        if sindex == -1 or nindex == -1:
            print('Error: Invalid template')
            return
        onlytwo = True

    else:
        sindex = template.index('start')
        nindex = template.index('name')
        eindex = template.index('end')
        if sindex == -1 or nindex == -1 or eindex == -1:
            print('Error: Invalid template')
            return

    # create a template of the ffmpeg call in advance
    cmd_string = 'ffmpeg -i {tr} -acodec copy -ss {st} -to {en} '+dest+'/{nm}.'+extension

    # read each line of the track list and split into start, end, name
    with open(track_list, 'r') as f:

        if onlytwo:

            length = (subprocess.check_output('ffmpeg -i '+original_track+' 2>&1 | grep Duration | awk \'{print$2}\'', shell=True)[:-2]).decode("ascii")
            starts = []
            ends   = []
            names  = []

            for line in f:
                # skip comment and empty lines
                if line.startswith('#') or len(line) <= 1:
                    continue

                # create command string for a given track
                split_line = line.strip().split(';')
                start = split_line[sindex]
                name  = split_line[nindex]

                starts.append(start)
                ends.append(start)
                names.append(name)
            ends.append(length)

            for i,name in enumerate(names):
                command = cmd_string.format(tr=original_track, st=starts[i], en=ends[i+1], nm=str(i) )

                # use subprocess to execute the command in the shell
                subprocess.call(command, shell=True)

                if extension not in ['mp3', 'flac']:
                    continue
                set_tags(dest+'/'+str(i)+'.'+extension, name, album_name, artist_name, i+1 , cover_art)


        else:
            for i,line in enumerate(f):
                # skip comment and empty lines
                if line.startswith('#') or len(line) <= 1:
                    continue

                # create command string for a given track
                split_line = line.strip().split(";")
                start = split_line[sindex]
                name  = split_line[nindex]
                end   = split_line[eindex]
                command = cmd_string.format(tr='"'+original_track+'"', st=start, en=end, nm=str(i))

                # use subprocess to execute the command in the shell
                subprocess.call(command, shell=True)

                if extension not in ['mp3', 'flac']:
                    continue
                set_tags(dest+'/'+str(i)+'.'+extension, name, album_name, artist_name, i+1 , cover_art)


if __name__ == '__main__':
    main()

