#!/usr/bin/env python3
"""
Extract neural fingerprints from query and reference audio chunks
with timestamps for audio matching evaluation.
"""
import os
import sys
import json
import numpy as np
import tensorflow as tf
import librosa
from tqdm import tqdm
import argparse
import yaml
import re

# Add the necessary paths
script_dir = os.path.dirname(os.path.abspath(__file__))
neural_fp_path = os.path.join(script_dir, 'lib/neural-audio-fp')
if neural_fp_path not in sys.path:
    sys.path.insert(0, neural_fp_path)

# Import from neural-audio-fp
from run import load_config
from model.fp.melspec.melspectrogram import get_melspec_layer
from model.fp.nnfp import get_fingerprinter

# Import local ChunkProcessor
from chunk_processor import ChunkProcessor


def numpy_converter(o):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def load_model(config_path='default'):
    """Load the fingerprinting model"""

    if not os.path.dirname(config_path):
        neural_fp_config_path = os.path.join(neural_fp_path, 'config', f"{config_path}.yaml")
        if os.path.exists(neural_fp_config_path):
            print(f"Loading configuration from: {neural_fp_config_path}")
            config_path = neural_fp_config_path
            
    if not config_path.endswith('.yaml'):
        config_path += '.yaml'
        
    if os.path.exists(config_path):
        print(f'Loading configuration from {config_path}')
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
    else:
        sys.exit(f'Configuration file {config_path} is missing')
    
    # Create model components
    m_pre = get_melspec_layer(cfg, trainable=False)
    m_fp = get_fingerprinter(cfg, trainable=False)
    return m_pre, m_fp, cfg


def extract_fingerprint(audio, m_pre, m_fp, start_time=0, sr=22050):
    """Extract fingerprints from audio chunk as 1-second segments with 0.5s overlap"""
    original_duration = len(audio) / sr  # Store original duration
    
    # Resample to 8kHz
    if sr != 8000:
        audio = librosa.resample(y=audio, orig_sr=sr, target_sr=8000)
        sr = 8000
    
    # Process in one-second windows with 0.5s overlap
    window_size = 8000  # 1 second at 8kHz
    hop_length = 4000   # 0.5 second hop
    
    # Initialize list to store individual segment fingerprints
    segment_fingerprints = []
    
    for i in range(0, len(audio) - window_size + 1, hop_length):
        window = audio[i:i + window_size]
        
        # Skip windows that are too short (should not happen with our range check)
        if len(window) < window_size:
            continue
            
        segment_tensor = tf.convert_to_tensor(window, dtype=tf.float32)
        segment_tensor = tf.reshape(segment_tensor, (1, 1, 8000))
        feat = m_pre(segment_tensor)
        emb = m_fp(feat)
        
        # Calculate segment timestamps relative to the original audio
        segment_start_time = start_time + (i / sr)
        segment_end_time = segment_start_time + (window_size / sr)
        
        # Store individual fingerprint with timing info
        segment_fingerprints.append({
            'start_time': segment_start_time,
            'end_time': segment_end_time,
            'fingerprint': emb.numpy().flatten().tolist()
        })
    
    # Handle case of short audio (< 1 second)
    if len(audio) > 0 and not segment_fingerprints:
        # Pad to 1 second
        padded_audio = np.pad(audio, (0, window_size - len(audio)), 'constant')
        segment_tensor = tf.convert_to_tensor(padded_audio, dtype=tf.float32)
        segment_tensor = tf.reshape(segment_tensor, (1, 1, 8000))
        feat = m_pre(segment_tensor)
        emb = m_fp(feat)
        
        segment_fingerprints.append({
            'start_time': start_time,
            'end_time': start_time + (len(audio) / sr),
            'fingerprint': emb.numpy().flatten().tolist(),
            'padded': True 
        })
    
    # Return a result object with all segment fingerprints
    result = {
        'chunk_start_time': start_time,
        'chunk_end_time': start_time + original_duration,
        'chunk_duration': original_duration,
        'num_segments': len(segment_fingerprints),
        'segment_fingerprints': segment_fingerprints,
        'overlap': 0.5 
    }
    
    return result


def process_dataset(meta_path, audio_data_path, output_dir, config_path=None, rate=22050):
    # Create main output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create separate folders for query and reference fingerprints
    query_dir = os.path.join(output_dir, "query")
    reference_dir = os.path.join(output_dir, "reference")
    os.makedirs(query_dir, exist_ok=True)
    os.makedirs(reference_dir, exist_ok=True)
    
    print("Loading neural fingerprinting model...")
    m_pre, m_fp, cfg = load_model(config_path)
    processor = ChunkProcessor(meta_path, audio_data_path, rate)
    num_chunks = len(processor.meta_df)
    print(f"Processing {num_chunks} audio chunks...")
    fingerprint_db = {}

    # Load video titles from titles.json
    with open(os.path.join(script_dir, 'data-out/titles.json'), 'r') as f:
        titles_data = json.load(f)

    for idx in tqdm(range(num_chunks)):
        try:
            row = processor.meta_df.iloc[idx]
            number = row['Number']
            formatted_number = f"{int(number):03d}"
            query_id = row["query YouTubeID"]
            reference_id = row["reference's YouTube ID"]

            query_start = row["start time in query"]
            query_end = row["end time in query"]
            ref_start = row["start time in reference"]
            ref_end = row["end time in reference"]

            print(f"Processing chunk {idx}: Video {formatted_number}[{query_id}], Reference [{reference_id}]")
            print(f"  Query time: {query_start}s - {query_end}s")
            print(f"  Reference time: {ref_start}s - {ref_end}s")

            query_audio, ref_audio = processor.query_and_reference_chunk_audio(idx)
            query_audio_id = f"{idx}_query"
            ref_audio_id = f"{idx}_reference_{reference_id}" 
            
            # Use separate folders for query and reference fingerprints
            query_fp_file = os.path.join(query_dir, f"{formatted_number}[{query_id}]_{query_audio_id}_fp.json")
            ref_fp_file = os.path.join(reference_dir, f"{formatted_number}[{query_id}]_{ref_audio_id}_fp.json")

            query_fp = extract_fingerprint(query_audio, m_pre, m_fp, start_time=query_start, sr=rate)
            ref_fp = extract_fingerprint(ref_audio, m_pre, m_fp, start_time=ref_start, sr=rate)

            with open(query_fp_file, 'w') as f:
                json.dump(query_fp, f, indent=2, default=numpy_converter)

            with open(ref_fp_file, 'w') as f:
                json.dump(ref_fp, f, indent=2, default=numpy_converter)

            with open(os.path.join(script_dir, 'data-out/titles.json'), 'r') as f:
                titles_data = json.load(f)

            print(f"  Saved fingerprints to separate query/reference folders")

            # Store relative paths in the database
            query_db_key = f"{idx}_query_{query_id}"
            ref_db_key = f"{idx}_reference_{reference_id}"

            # Initialize with default values
            query_title_clean = f"Chunk {idx} from video {formatted_number}"
            ref_title_clean = f"Reference for chunk {idx}"

            # Find actual titles from titles.json
            for query_title, references in titles_data.items():
                if f"[ID: {query_id}]" in query_title or f"[ID:{query_id}]" in query_title:
                    query_title_clean = re.sub(r'\s*\[ID:.*?\]', '', query_title).strip()
                    
                    # Find matching reference in the list of references
                    for ref in references:
                        if f"[ID:{reference_id}]" in ref or f"[ID: {reference_id}]" in ref:
                            ref_title_clean = re.sub(r'\s*\[ID:.*?\]', '', ref).strip()
                            break
                    break

            # Create fingerprint database entries with actual video titles
            fingerprint_db[query_db_key] = {
                "source": f"{formatted_number}[{query_id}]/full.mp3",
                "fingerprint_file": os.path.relpath(query_fp_file, output_dir),
                "video_id": query_id,
                "video_title": query_title_clean,        
                "chunk_description": f"Chunk {idx} from video {formatted_number}",
                "n_segments": query_fp["num_segments"],
                "start_time": query_start,
                "end_time": query_end,
                "chunk_duration": query_end - query_start,
                "chunk_index": idx,
                "is_query": True
            }

            fingerprint_db[ref_db_key] = {
                "source": f"{formatted_number}[{query_id}]/reference_{reference_id}.mp3",
                "fingerprint_file": os.path.relpath(ref_fp_file, output_dir),
                "video_id": reference_id,
                "video_title": ref_title_clean,           
                "chunk_description": f"Reference for chunk {idx}",
                "n_segments": ref_fp["num_segments"],
                "start_time": ref_start,
                "end_time": ref_end,
                "chunk_duration": ref_end - ref_start,
                "chunk_index": idx,
                "is_reference": True
            }

        except Exception as e:
            print(f"Error processing chunk {idx}: {e}")
            import traceback
            traceback.print_exc()

    # Save the fingerprint database in the main output directory
    db_path = os.path.join(output_dir, "fingerprint_db.json")
    with open(db_path, 'w') as f:
        json.dump(fingerprint_db, f, indent=2, default=numpy_converter)

    print(f"Saved fingerprint database to {db_path}")
    print(f"Organized {len(fingerprint_db) // 2} chunks into query and reference folders")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract neural fingerprints from audio chunks")
    parser.add_argument("--meta", required=True, help="Path to metadata CSV file")
    parser.add_argument("--audio", required=True, help="Path to audio data directory")
    parser.add_argument("--output", required=True, help="Path to output directory")
    parser.add_argument("--config", default="default", help="Path to model config file")
    parser.add_argument("--rate", type=int, default=22050, help="Audio sample rate (default: 22050)")
    args = parser.parse_args()
    process_dataset(args.meta, args.audio, args.output, args.config, args.rate)
