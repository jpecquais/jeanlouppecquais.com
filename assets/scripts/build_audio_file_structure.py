# generate_audio_structure.py
import json
from typing import List, Dict
from pathlib import Path
from mutagen import oggopus
import librosa

# This script create json files in each audio folders include in an article in the music section.
# This json is used to generate the playlist of the audio player.
# The data structure of the playlist is a list of dict. The position in the list indicate the position of the track in the setlist, while the dict hold the track information.
# Only support Opus codec for now.

# Expand the table so that it can hold the new track
def expand_table(table: List,new_size: int):
    table_len = len(table)
    if table_len < new_size:
        for i in range(table_len,new_size,1):
            table.insert(i,None)

# Add the metadata in the data_structure
def append_audio_metadata(file: Path, structure: List):
    audio = None
    try :
        audio = oggopus.OggOpus(file)
    except:
        print(f'{file.name} is not an opus file')
        return

    path_to_store = file.relative_to(file.parent.parent.parent)
    
    tracknumber = int(audio['TRACKNUMBER'][0])
    position = tracknumber-1
    title = audio['TITLE'][0]
    albumartist = audio['ALBUMARTIST'][0]
    format = audio['COMMENT'][0] #Use comment filed to store audio stream type
    duration = audio.info.length

    expand_table(structure,tracknumber)
    if not structure[position]:
        structure[position] = {'tracknumber': tracknumber,
                               'titletrack': title,
                               'artist': albumartist,
                               'duration': duration}

    if not structure[position].get('format'):
        structure[position]['format'] = {
                str(format): str(path_to_store)
            }
    else:
        structure[position]['format'][str(format)] = str(path_to_store)

    if not structure[position].get('howl'):
        structure[position]['howl'] = None

# Recursive function to parse the content of the audio folder.
def scan_release_audio_folders(audio_path,structure):
    """Scan the audio directory structure for a specific release."""
    
    # Check if the audio directory exists
    if not audio_path.exists():
        print(f"Audio directory not found at {audio_path}")
        return structure
    
    files = [file for file in audio_path.iterdir() if file.is_file()]
    folders = [folder for folder in audio_path.iterdir() if folder.is_dir()]

    for file in files:
        append_audio_metadata(file,structure)

    for folder in folders:
        scan_release_audio_folders(folder,structure)
            
                
    return structure

#Process all the release
def process_all_releases(project_root):
    """Process all releases in the music directory."""
    # Path to the music directory
    music_path = project_root / "music"
    
    # Check if the music directory exists
    if not music_path.exists():
        print(f"Music directory not found at {music_path}")
        return
    
    # Get all release folders
    release_folders = [item for item in music_path.iterdir() if item.is_dir()]
    
    print(f"Found {len(release_folders)} releases")
    
    # Process each release
    for release_path in release_folders:
        release_name = release_path.name
        if release_name == "_template_files":
            continue
        
        # Create the structure.json file for this release
        audio_path = Path(release_path, "audio")
        if not audio_path:
            print(f"No audio founds in this {release_name}")
            return
        
        res = [None]
        res = scan_release_audio_folders(audio_path,res)
        if not res: return
        structure = [entry for entry in res if entry] #TODO: ugly, all of that should be handled algorithmically
        
        output_path = release_path / "audio" / "playlist.json"
        
        # Write the structure.json file
        with open(output_path, "w") as f:
            json.dump(structure, f, indent=2)
        
        
# Main function.
if __name__ == "__main__":
    # Get the project root directory (assuming script is in project root)
    project_root = Path(Path(__file__).parent,"../../")
    
    process_all_releases(project_root)