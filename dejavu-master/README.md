# Dance Battle Audio Fingerprinting and Matching

This project is based on the peak detection method implemented in **Dejavu** for audio fingerprinting. You can find the original implementation of Dejavu [here](https://github.com/worldveil/dejavu/tree/master?tab=readme-ov-file). Several modifications have been made to adapt the code to work with **MySQL databases**.

## Changes and Additions

- **MySQL Database Support**: Minor modifications to ensure compatibility with MySQL databases.
- **Data**: The folder `data-out` contains 15 YouTube dance battle videos that have been annotated.
- **Annotations**: The file `Fingerprinting data annotation - Master.csv` contains annotations for the videos.

## Programs Included

The project includes the following Python scripts:

1. **chunk_processor.py**: This script returns reference and query chunks for each of the annotations in the dataset.
2. **dance_fingerprint.py**: This script generates the audio fingerprints for the reference chunks using the `ChunkProcessor` class.
3. **dance_match.py**: This script searches for two matches for each query chunk retrieved by the `ChunkProcessor` class, and generates a `results.csv` file with the results.
4. **dance_statistics.py**: This script calculates accuracy percentages and generates plots based on the `results.csv` file for drawing conclusions.
5. **dance_delete_db.py**: This script is used to delete the database entries, useful for cleaning up or resetting the database.

## Results

The project also includes the generated **results.csv** file and various plots that were used to extract conclusions from the data.

## Dependencies

The following libraries are required to run the project:
pydub==0.23.1 PyAudio==0.2.11 numpy==1.17.2 scipy==1.3.1 matplotlib==3.1.1 mysql-connector-python==8.0.17 psycopg2==2.8.3 librosa==0.8.1 seaborn==0.11.2 soundfile==0.10.3.post1 dejavu==1.1.0

To install the required dependencies, run: pip install -r requirements.txt

## Running the Scripts

1. **Fingerprinting the reference chunks**:  
   Use `dance_fingerprint.py` to fingerprint the reference chunks stored in `data-out`.

2. **Matching query chunks**:  
   Use `dance_match.py` to search for matches between query and reference chunks and generate the `results.csv`.

3. **Generating statistics and plots**:  
   Use `dance_statistics.py` to calculate accuracy and generate visualizations based on the results.

4. **Cleaning the database**:  
   If needed, use `dance_delete_db.py` to clean the database.


