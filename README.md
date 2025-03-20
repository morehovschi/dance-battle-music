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
