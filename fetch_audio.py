#!/usr/bin/env python
import os
import json
import yt_dlp
import sys

def get_video_metadata(video_url):
    """
    Just get metadata
    """
    ydl_opts = {
        'quiet': True,
        'writeinfojson': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info

def download_audio(video_url, output_name):
    """
    Just get the video's audio
    """
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"downloads/{output_name}.%(ext)s",
        'quiet': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def fetch_metadata_and_download(video_url, output_name):
    """
    Get both metadata and audio for the video
    
    output_name (str): path to write the output mp3 to
    """
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"{output_name}.%(ext)s",
        'quiet': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)  # Extracts metadata & downloads audio
        return info  # Returns metadata for further processing

if __name__ == "__main__":
    if len( sys.argv ) < 2:
        print( f"Usage: python3 {sys.argv[0]} <path to collection of YouTube IDs> "
               f"<output path>" )
        exit( 0 )

    src_data_path = sys.argv[ 1 ]
    data_out_path = sys.argv[ 2 ] if len( sys.argv ) > 2 else "data-out"
    
    if os.path.isdir( data_out_path ):
        print( "There already is a {data_out_path} and I don't want to overwrite "
               "it. Please just indicate a new output path." )
        print( f"Usage: python3 {sys.argv[0]} <path to collection of YouTube IDs> "
               f"<output path>" )
        exit( 0 )
    
    os.mkdir( data_out_path )

    titles = {}
    id_collection = {}
    with open( src_data_path, "r" ) as f:
        id_collection = json.load( f )

    print( "Downloading audio for:" )
    for i, eye_dee in enumerate( id_collection ):

        video_dir_path = f"{data_out_path}/" + f"{i}".zfill( 3 ) + f"[{eye_dee}]"
        os.mkdir( video_dir_path )

        video_md = get_video_metadata( "https://youtube.com/watch?v=" + eye_dee )
        video_md = fetch_metadata_and_download(
            "https://youtube.com/watch?v=" + eye_dee,
             video_dir_path + "/full" )

        video_title = video_md[ "title" ] + f" [ID: {eye_dee}]"
        titles[ video_title ] = []
        print( f"{i+1}.{video_title}" )
        
        for song_id in id_collection[ eye_dee ]:
            song_md = fetch_metadata_and_download(
                        "https://youtube.com/watch?v=" + song_id,
                        f"{video_dir_path}/reference[{song_id}]" )
            titles[ video_title ].append( f"{song_md['title']} [ID:{song_id}]" )

    with open( f"{data_out_path}/titles.json", "w" ) as f:
        json.dump( titles, f )
