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

    # ---------------------- MATCH SEARCH ----------------------
    results_data = []
    meta_df = processor.meta_df
    annotation_df = pd.read_csv(meta_csv_path)  # Load annotation file
    for row in range(len(meta_df)):
        row_data = meta_df.iloc[row]
        
        # Extract query chunk
        query_audio, _ = processor.query_and_reference_chunk_audio(row)
        
        # Generate correct name for the query chunk
        query_song_name = "{}-{}-{}".format(
            row_data.get("query YouTubeID", "unknown"),
            row_data.get("start time in query", "0"),
            row_data.get("end time in query", "0")
        )
        
        # Save temporary file with the generated name
        query_audio_path = f"{query_song_name}.mp3"
        sf.write(query_audio_path, query_audio, sampling_rate)
        
        print(f"Searching for matches for: {query_song_name}")
        result = djv.recognize(FileRecognizer, query_audio_path)
        
        # Process results
        if result["results"]:
            for match in result["results"]:
                match_ratio = match["hashes_matched_in_input"] / match["fingerprinted_hashes_in_db"] if match["fingerprinted_hashes_in_db"] > 0 else 0
                
                query_parts = query_song_name.split('-')
                query_youtube_id = '-'.join(query_parts[:-2])
                start_time_query = query_parts[-2]
                end_time_query = query_parts[-1]
                query_duration = int(end_time_query) - int(start_time_query)
                
                # Find the corresponding row in the annotation file
                matched_row = annotation_df[
                    (annotation_df["query YouTubeID"] == query_youtube_id) &
                    (annotation_df["start time in query"] == float(start_time_query)) &
                    (annotation_df["end time in query"] == float(end_time_query))
                ]
                
                if not matched_row.empty:
                    # Extract values from the reference file name
                    ref_song_name = match["song_name"].decode("utf-8")
                    ref_parts = ref_song_name.split('-')
                    ref_youtube_id = '-'.join(ref_parts[:-2])
                    start_time_ref = ref_parts[-2]
                    end_time_ref = ref_parts[-1]

                    # Compare values
                    if (matched_row["reference's YouTube ID"].values[0] == ref_youtube_id and
                        matched_row["start time in reference"].values[0] == float(start_time_ref) and
                        matched_row["end time in reference"].values[0] == float(end_time_ref)):
                        
                        success = "YES"
                    else:
                        success = "NO"
                else:
                    success = "NO"
                
                # Calculate match ratio
                match_ratio = match["hashes_matched_in_input"] / match["fingerprinted_hashes_in_db"] if match["fingerprinted_hashes_in_db"] > 0 else 0
                
                results_data.append([
                    query_song_name, match["song_name"].decode("utf-8"), 
                    match["input_confidence"], match["input_total_hashes"], 
                    match["fingerprinted_hashes_in_db"], match["hashes_matched_in_input"],
                    match["offset_seconds"], result["total_time"], result["fingerprint_time"], 
                    result["query_time"], result["align_time"], success, match_ratio, query_duration, "NO", "NO"
                ])
        else:
            results_data.append([
                query_song_name, "Not identified", 0, 0, 0, 0, 0, 0, 0, 0, 0, "NO", 0, 0
            ])
        
        os.remove(query_audio_path)
    
    df = pd.DataFrame(results_data, columns=[
        "Query", "Identified as", "Confidence", "Total Hashes", 
        "Hashes in DB", "Matching Hashes", "Offset (s)", "Total Time (s)", 
        "Fingerprint Time (s)", "Query Time (s)", "Align Time (s)", "Success", "Match Ratio", "Query Duration", "Partial Success", "Total Success"
    ])
    
    # ---------------------- TOTAL SUCCESS ----------------------
    df["Total Success"] = "NO"
    df["Partial Success"] = "NO"
    # Update the columns for each query
    for query in df["Query"].unique():
        subset = df[df["Query"] == query]
        if len(subset) == 2:
            # Check if any of the rows for the same query have "YES" in "Success" for Partial Success
            if "YES" in subset["Success"].values:
                df.loc[df["Query"] == query, "Partial Success"] = "YES"
            
            # Determine if the maximum match ratio corresponds to a successful query for "Total Success"
            max_ratio_index = subset["Match Ratio"].idxmax()
            if df.loc[max_ratio_index, "Success"] == "YES":
                df.loc[df["Query"] == query, "Total Success"] = "YES"
                
    
    # Save results to CSV
    output_csv_path = os.path.join(os.getcwd(), "results.csv")
    df.to_csv(output_csv_path, index=False)
    print(f"Table saved to '{output_csv_path}'.")