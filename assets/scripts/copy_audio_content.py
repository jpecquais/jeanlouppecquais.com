import shutil
from pathlib import Path

def copy_folder(src_folder: Path,target_folder: Path):
    # if not target_folder.is_dir(): target_folder.mkdir(parents=False,exist_ok=True)
    if not target_folder.is_dir(): Path(target_folder).mkdir()
    content = [item for item in src_folder.iterdir()]
    for item in content:
        if item.is_file():
            # print(item)
            # print(target_folder)
            shutil.copy(item,target_folder)
        elif item.is_dir():
            copy_folder(item,Path(target_folder,item.name))

# Main function.
if __name__ == "__main__":
    # Get the project root directory (assuming script is in project root)
    quarto_music_path = Path(Path(__file__).parent,"../../music")
    on_site_music_path = Path(Path(__file__).parent,"../../_site/music")
    
    release_folders = [folder for folder in quarto_music_path.iterdir() if folder.is_dir()]
    for folder in release_folders:
        audio_folder = Path(folder,"audio")
        if audio_folder.is_dir():
            dest_path = Path(on_site_music_path,folder.name,"audio")
            copy_folder(audio_folder,dest_path)
            # print(dest_path)