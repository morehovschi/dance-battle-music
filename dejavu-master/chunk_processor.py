"""
    Helper class that allows for easy navigation and retrieval of query and
    reference chunks. Check usage in view_chunks.ipynb
"""

#!/usr/bin/env python3
import librosa
import pandas as pd

class ChunkProcessor:
    def __init__( self, meta_path, audio_data_path, rate ):
        self.meta_path = meta_path
        self.meta_df = pd.read_csv( self.meta_path, dtype={ "Number": str } )
        
        self.audio_data_path = audio_data_path

        self.rate = rate
        
        self.cached_query_fpath = None
        self.cached_query_audio = None
        self.cached_reference_fpath = None
        self.cached_reference_audio = None

    def query_and_reference_chunk_audio( self, row ):
        number = self.meta_df.iloc[row]["Number"]
        query_id = self.meta_df.iloc[row]["query YouTubeID"]
        
        query_fpath = f"{self.audio_data_path}/{number}[{query_id}]/full.mp3"

        # use cached audio to cut chunk, to avoid unnecessarily repeating librosa.load
        if self.cached_query_fpath and self.cached_query_fpath == query_fpath:
            query_audio = self.cached_query_audio
        else:
            self.cached_query_fpath = query_fpath
            query_audio, sr = librosa.load( query_fpath, sr=self.rate )
            self.cached_query_audio = query_audio
        
        query_chunk_audio = query_audio[ self.meta_df.iloc[ row ][ "start time in query" ] * self.rate :
                                         self.meta_df.iloc[ row ][ "end time in query" ] * self.rate ]
        
        reference_id = self.meta_df.iloc[ row ][ "reference's YouTube ID" ]
        reference_fpath = f"{self.audio_data_path}/{number}[{query_id}]/reference[{reference_id}].mp3"
        
        if self.cached_reference_fpath and self.cached_reference_fpath == reference_fpath:
            reference_audio = self.cached_reference_audio
        else:
            self.cached_reference_fpath = reference_fpath
            reference_audio, sr = librosa.load( reference_fpath, sr=self.rate )
            self.cached_reference_audio = reference_audio
        
        reference_chunk_audio = reference_audio[ self.meta_df.iloc[ row ][ "start time in reference" ] * self.rate :
                                                 self.meta_df.iloc[ row ][ "end time in reference" ] * self.rate ]
        
        return query_chunk_audio, reference_chunk_audio
