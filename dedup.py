#!/usr/bin/env python
import os
import json
import pprint

from scrape import youtube_id, save_data_file

if __name__ == "__main__":
    collection = {}
    
    for fname in os.listdir( "data" ):
        if not fname.endswith( ".json" ):
            continue

        file_collection = {}
        with open( f"data/{fname}", "r" ) as json_file:
            file_collection = json.load( json_file )

        for video_url in file_collection:
            video_id = youtube_id( video_url )

            associated_song_ids = []
            for song_url in file_collection[ video_url ]:
                # due to a bug in an early version of the scraper, this
                # non-video-specific url got mixed up with actual song urls
                if song_url == "l/UC-9-kyTW":
                    continue
                
                # due to another bug, sometimes links from the "Chapters" section of
                # a video (which point to the video itself, with additional
                # timestamp information) get saved together with references to
                # music used within
                if youtube_id( song_url ) == video_id:
                    continue                

                associated_song_ids.append( youtube_id( song_url ) )    

            if video_id in collection:
                assert associated_song_ids == collection[ video_id ], \
                    ( fname, associated_song_ids, collection[ video_id ] )
            elif associated_song_ids:
                # only update with entry for video id if non-empty
                collection[ video_id ] = associated_song_ids
 
    print( f"There are {len(collection)} deduplicated items:" )
    pprint.pp( collection )

    fname = save_data_file( "data/music_links_dedup", collection )  
    print( f"Saved the deduplicated collection to {fname}." )
