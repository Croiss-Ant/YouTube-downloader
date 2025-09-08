# -----------------------------------
# ---- VARIABLES & MODULES INIT -----
# -----------------------------------
from yt_dlp import YoutubeDL, postprocessor as Pp
from pathlib import Path
import inquirer
run = True

# CLI colours
OKBLUE = '\033[34m'
OKCYAN = '\033[36m'
OKGREEN = '\033[32m'
WARNING = '\033[33m'
FAIL = '\033[31m'
ENDC = '\033[0m'

# -----------------------------------
# -------- INQUIRER PROMPTS ---------
# -----------------------------------
# Format
format_prompt = [
    inquirer.List("format", message="Select the output format", 
        choices=[
            "mp3 - Audio only", 
            "mp4 - Video & Audio"
        ]
    )
]

# Cropping
crop_prompt = [
    inquirer.Confirm("crop", message="Crop the thumbnail into a 1:1 square ? (Perfect for music covers)")
]

# Close program
continue_prompt = [
    inquirer.Confirm("continue", message="Download more videos ?")
]

# -----------------------------------
# ---------- YT-DLP CONFIG ----------
# -----------------------------------
# Base options
base_opts = {
    # Output configuration
    "outtmpl": None,

    # Download behavior
    "ignoreerrors": True,
    "nooverwrites": True,
    "continuedl": True,
    "retries": 3,
    "fragment_retries": 3,
    "skip_unavailable_fragments": True,

    # Metadata and info
    #"writeinfojson": True,
    "writethumbnail": True,

    # Network and performance
    "socket_timeout": 30,
    "http_chunk_size": 10485760,  # 10MB chunks
    "concurrent_fragment_downloads": 4,
}

# Testing options
test_opts = { 
        "quiet": True,
        "playlist_items": "0",
        #"writeinfojson": True,
    }

# mp3 specific options
mp3_opts = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3"
    },
    {
        "key": "FFmpegMetadata",
        "add_metadata": True,
    },
    {
        # Parse track number (only really works for playlists and only visible on music libraries)
        "key": "MetadataParser",
        "actions": [(Pp.metadataparser.MetadataParserPP.interpretter, "playlist_index", "%(track_number)s")],
        "when": "pre_process"
    },
    {
        "key": "EmbedThumbnail"
    }],
}

# mp4 specific options
mp4_opts = {
    "format": "bestvideo[height<=1080]+bestaudio/best",
    "merge_output_format": "mp4",
    "postprocessors": [{
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mp4",
    }, 
    {
        "key": "FFmpegMetadata",
        "add_metadata": True,
    },
    {
        "key": "EmbedThumbnail"
    }],
}

# Crops the thumbnail into a 1:1 square (messy but works)
crop_thumbnail = {
    "postprocessor_args": {
        "thumbnailsconvertor+ffmpeg_o": [
            "-c:v",
            "png",
            "-vf",
            "crop=ih"
        ]
    },
}

# -----------------------------------
# ------------ FUNCTIONS ------------
# -----------------------------------
def download(url, format, crop=False, output_dir="Downloads"):
    # Sets the save path
    save_path = Path.home() / output_dir
    # Sets the download options
    opts = dict(base_opts | eval(format + "_opts"))

    # Adds thumbnail cropping options if enabled
    if crop:
        opts = opts | crop_thumbnail

    # Sets the output path for both playlists and videos
    if "list" in url:
        opts["outtmpl"] = str(save_path / "%(playlist)s" / "%(playlist_index)03d - %(title)s.%(ext)s")
    else:
        opts["outtmpl"] = str(save_path / "%(title)s.%(ext)s")

    # Check if the link is valid + extract some video info
    try:
        with YoutubeDL(test_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Extract useful info
            title = info.get("title")
            uploader = info.get("uploader")
            item_count = info.get("playlist_count")
            #print(info)
    except:
        print(FAIL + "ERROR: " + ENDC + "Make sure the provided URL is correct then try again", "\n")
        return None
    
    print("[info] Attempting to download \"" + OKBLUE + title + ENDC + "\" in " + WARNING + format + ENDC)
    # Automatically and independently downloads playlists and videos one by one
    with YoutubeDL(opts) as ydl:
        ydl.download([url])

    # Summary of everything that has just been downloaded (messy but works, trust)
    print(OKGREEN + "[success] " + ENDC + "Download complete !")
    print("[summary] Downloaded " + OKBLUE + title + ENDC, end="")
    if item_count == None: 
        print("") 
    else: 
        print(" (" + str(item_count) + " items)")
    if uploader == None:
        print("", end="")
    else:
        print("[summary] By " + OKCYAN + uploader + ENDC)
    print("[summary] In format " + WARNING + format + ENDC)
    if format == "mp3":
        print("[summary] With thumbnail cropping ", end="")
        if crop:
            print(OKGREEN + "enabled" + ENDC) 
        else: 
            print(FAIL + "disabled" + ENDC)
    if not "list" in url:
        title = title + "." + format
    print("[summary] Saved into :")
    print(str(save_path / title), end="\n\n")

# -----------------------------------
# ------------- PROGRAM -------------
# -----------------------------------
print(OKGREEN + "-----------------------------------")
print("---- Ant's YouTube Downloader -----")
print("-----------------------------------" + ENDC, "\n")
while run:
    # Disable thumbnail cropping at the start of each loop
    crop = False

    try:
        # Prompt URL and conversion format
        url = input("[" + WARNING + "?" + ENDC +"] Paste the link here (Supports playlists): ")
        answers = inquirer.prompt(format_prompt)

        # Reformat the conversion format for readability
        format = str(answers["format"]).split(" - ")[0]

        if format == "mp3":
            # Prompt to enable cropping
            answers = inquirer.prompt(crop_prompt)
            crop = answers["crop"]

        # Download using the provided url, format
        download(url, format, crop)

        # Ask to continue
        answers = inquirer.prompt(continue_prompt)
        if not answers["continue"]:
            # Stop program
            run = False
            print("\n[system] Have a fantastic day !", "\n")
    except:
        # Fail stop when doing ctrl-C
        run = False
        print("\n[system] User prompted force-quit !", "\n")