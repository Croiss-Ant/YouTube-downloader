# Ant's YouTube Downloader Tool

**Simple CLI python script making downloading YouTube videos very easy**

## Features :
- Simple and intuitive command line interface
- Support for both YouTube and YouTube Music urls
- Playlist handling
- Export as mp3 and mp4
- Experimental thumbnail cropping for music covers

## Download
You can find the latest release [here](github.com/Croiss-Ant/YouTube-downloader/releases) *(Not available yet)*

## Building the app from source
1. Download the source code
2. Open it in a python capable IDE
3. Make sure Python and Pip are up to date
4. Run `pip install -r requirements.txt`
5. Install PyInstaller `pip install pyinstaller` then run `pyinstaller --onefile main.py`
6. Once done, the executable should be located in the `dist` folder

You are now free to move and rename the exec file however you please

### Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)