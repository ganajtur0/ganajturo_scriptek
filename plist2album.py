#!/usr/bin/python3

import yt_dlp
import eyed3
import argparse


def tag_mp3(file, track_num, track_index, artist, album, title):

    audiofile = eyed3.load(file)

    audiofile.tag.artist = artist
    audiofile.tag.album = album
    audiofile.tag.title = title
    audiofile.tag.track_num = (track_index, track_num)

    audiofile.tag.save()


def download_playlist(playlist_url, album, artist, nodownload):

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(playlist_index)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        playlist_info = ydl.extract_info(playlist_url, download=False)

        videos = playlist_info['entries']

        if videos is not None:

            titles = [video['title'] for video in videos]

            if not nodownload:
                ydl.download(playlist_url)

            for i, title in enumerate(titles):
                try:
                    tag_mp3(f"{str(i+1).zfill(2)}.mp3",
                            len(videos),
                            i+1,
                            artist,
                            album,
                            title)
                except OSError:
                    tag_mp3(f"{str(i+1)}.mp3",
                            len(videos),
                            i+1,
                            artist,
                            album,
                            title)
            print("Done")

        else:
            print("No videos found in the playlist.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="plist2album",
                                     description="""Downloads and tags the
                                     videos of a playlist as mp3s""",
                                     epilog="Come on come over")

    parser.add_argument('list_id',
                        help="""The part of the YouTube url
                        after the \"list=\" part""")
    parser.add_argument('album', help="The title of the album")
    parser.add_argument('artist', help="The name of the artist")
    parser.add_argument('--nodownload', default=False,
                        action="store_true",
                        help="This is mostly a debug option")

    args = parser.parse_args()

    download_playlist(f"https://www.youtube.com/playlist?list={args.list_id}",
                      args.album, args.artist, args.nodownload)
