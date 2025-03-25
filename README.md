### Hip Hop Dance Battle Music dataset

Currently this project just has a script scraping YouTube videos of hip hop
dance battles and collecting the links of any music listed in the "Music"
section for the video.

##### Setup
Run the commands in `setup.sh` to install playwright and yt-dlp.

#### Get the actual audios
a) `python3 fetch_audio.py music_links_dedup_0.json`

With the command above you will get a mini version of the dataset (N=15) where
audio is downloaded based on existing YouTube links.

b) If you'd like to run the script that queries YouTube for IDs of hip hop dance
battle videos and songs referenced within:<br>
`./fetch_links.py --n_results <n_results> --n_attempts <n_attempts>`<br>
`python3 fetch_audio.py <most recently produced file in data/> <output_path>`<br>

#### Dataset structure
Here is what the mini version of the dataset looks like after downloading with (a):
```
data-out/
├── 000[YzHOD9t1fKM]
│   ├── full.mp3
│   ├── reference[hTDb0ebFh8E].mp3
│   └── reference[voL5Zrs1-zk].mp3
├── 001[xVknxiEDy-s]
│   ├── full.mp3
│   └── reference[hTWKbfoikeg].mp3
├── 002[izixWy82qLs]
│   ├── full.mp3
│   ├── reference[56Byey6YD3Y].mp3
│   ├── reference[853G21eiTNs].mp3
│   ├── reference[e3T-KIiz4Jo].mp3
│   └── reference[ekCp0ujVjEI].mp3
[ ... ]
├── 014[eWh9NgFyaz0]
│   ├── full.mp3
│   ├── reference[6O8ij0TELJk].mp3
│   ├── reference[GK396YTm9Ek].mp3
│   ├── reference[GSoQDaXh144].mp3
│   └── reference[lkprxUbLPnM].mp3
└── titles.json
```

Each top level directory corresponds to a dance battle video with the
YouTube ID in square brackets. In each video's directory, there is an audio of the
full video and audios of all the songs referenced with links in the Music section
of the video. `titles.json` contains all the titles of the YouTube videos used
(dance videos and their corresponding songs).

---

**Setup Neural FP**
1. Run the ```setup_fingerprinting.sh``` to git clone the neural fp repo
2. Install neural-audio-fp requirements (If not already installed through the setup)

**Extract fingerprinting script**
- Run extract_chunks.py in order to extract fingerprints of the dataset in segments of 1 second with 0.5 second overlap. Run it with the following command 
```bash
python extract_chunks.py --meta path/to/annotations.csv --audio data-out --output fingerprints_chunks --config neural-audio-fp/config/default.yaml
```

---

### Peak Detection Method

This project is based on the peak detection method implemented in **Dejavu** for audio fingerprinting. You can find the original implementation of Dejavu [here](https://github.com/worldveil/dejavu/tree/master?tab=readme-ov-file). Several modifications have been made to adapt the code to work with **MySQL databases**.

#### Changes and Additions

- **MySQL Database Support**: Minor modifications to ensure compatibility with MySQL databases.
- **Data**: You need to download the dataset and place it in the data-out folder.
- **Annotations**: The file `Fingerprinting data annotation - Master.csv` contains annotations for the videos.

#### Programs Included

The project includes the following Python scripts:

1. **chunk_processor.py**: This script returns reference and query chunks for each of the annotations in the dataset.
2. **dance_fingerprint.py**: This script generates the audio fingerprints for the reference chunks using the `ChunkProcessor` class.
3. **dance_match.py**: This script searches for two matches for each query chunk retrieved by the `ChunkProcessor` class, and generates a `results.csv` file with the results.
4. **dance_statistics.py**: This script calculates accuracy percentages and generates plots based on the `results.csv` file for drawing conclusions.
5. **dance_delete_db.py**: This script is used to delete the database entries, useful for cleaning up or resetting the database.

#### Results

The project also includes the generated **results.csv** file and various plots that were used to extract conclusions from the data.

#### Dependencies

The following libraries are required to run the project:
pydub==0.23.1 PyAudio==0.2.11 numpy==1.17.2 scipy==1.3.1 matplotlib==3.1.1 mysql-connector-python==8.0.17 psycopg2==2.8.3 librosa==0.8.1 seaborn==0.11.2 soundfile==0.10.3.post1 dejavu==1.1.0

To install the required dependencies, run: pip install -r requirements.txt

#### Running the Scripts

1. **Fingerprinting the reference chunks**:  
   Use `dance_fingerprint.py` to fingerprint the reference chunks stored in `data-out`.

2. **Matching query chunks**:  
   Use `dance_match.py` to search for matches between query and reference chunks and generate the `results.csv`.

3. **Generating statistics and plots**:  
   Use `dance_statistics.py` to calculate accuracy and generate visualizations based on the results.

4. **Cleaning the database**:  
   If needed, use `dance_delete_db.py` to clean the database.

#### Dejavu Setup Guide

This guide provides step-by-step instructions to set up Dejavu for audio fingerprinting, including database configuration and necessary modifications to the `fingerprints` and `songs` tables.

##### 1. Install Dependencies
Ensure you have the required dependencies installed before proceeding:

- Python 3.x
- MySQL Server
- Required Python packages (install using `pip install -r requirements.txt`)

##### 2. Database Configuration

**2.1 Create and Configure the Database**

1. Log into MySQL:
   ```sh
   mysql -u root -p
   ```

2. Create the database:
   ```sql
   CREATE DATABASE dejavu;
   ```

3. Use the newly created database:
   ```sql
   USE dejavu;
   ```

4. Create the `songs` table:
   ```sql
   CREATE TABLE songs (
       song_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
       song_name VARCHAR(250) NOT NULL,
       fingerprinted TINYINT DEFAULT 0,
       file_sha1 BINARY(20) NOT NULL,
       total_hashes INT NOT NULL DEFAULT 0,
       date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       date_modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       PRIMARY KEY (song_id)
   );
   ```

5. Create the `fingerprints` table:
   ```sql
   CREATE TABLE fingerprints (
       hash BINARY(10) NOT NULL,
       song_id MEDIUMINT UNSIGNED NOT NULL,
       offset INT UNSIGNED NOT NULL,
       date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       date_modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       PRIMARY KEY (hash, song_id, offset)
   );
   ```

##### 3. Configure Dejavu

Modify the `dejavu.cnf` file (or your equivalent configuration file) to include the correct database credentials:

```json
{
    "database": {
        "host": "localhost",
        "user": "root",
        "password": "yourpassword",
        "database": "dejavu"
    },
    "database_type": "mysql"
}
```

##### 4. Run Dejavu

Once the database is set up and configured, you can start fingerprinting audio files:

```sh
python dejavu.py --fingerprint /path/to/audio/files
```

To recognize a song:

```sh
python dejavu.py --recognize file /path/to/query/audio.mp3
```



