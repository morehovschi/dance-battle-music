from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
import os
import soundfile as sf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chunk_processor import ChunkProcessor  # Make sure to import your class

# Dejavu configuration
config = {
    "database": {
        "host": "localhost",
        "user": "root",
        "password": "password",
        "database": "dejavu",
    },
    "database_type": "mysql",
}

if __name__ == '__main__':
    # Initialize Dejavu
    djv = Dejavu(config)

    # Initialize ChunkProcessor
    meta_csv_path = os.path.join(os.getcwd(), "Fingerprinting data annotation - Master.csv")
    audio_data_path = os.path.join(os.getcwd(), "data-out")
    sampling_rate = 48000  
    processor = ChunkProcessor(meta_csv_path, audio_data_path, sampling_rate)

    # ---------------------- FINGERPRINTING REFERENCE AUDIO ----------------------
    for row in range(len(processor.meta_df)):
        row_data = processor.meta_df.iloc[row]
        
        # Extract reference chunk
        _, ref_audio = processor.query_and_reference_chunk_audio(row)
        
        # Generate correct name for the reference chunk
        ref_song_name = "{}-{}-{}".format(
            row_data.get("reference's YouTube ID", "unknown"),
            row_data.get("start time in reference", "0"),
            row_data.get("end time in reference", "0")
        )
        
        # Save temporary file
        ref_audio_path = f"{ref_song_name}.mp3"
        sf.write(ref_audio_path, ref_audio, sampling_rate)
        
        # Fingerprint the reference chunk
        print(f"Fingerprinting: {ref_song_name}")
        djv.fingerprint_file(ref_audio_path, ref_song_name)
        
        # Remove temporary file
        os.remove(ref_audio_path)
    
    print(f"Total fingerprints in DB after saving: {djv.db.get_num_fingerprints()}")

 