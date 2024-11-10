import os
import shutil

# Define the paths to the directories
images_folder = r'C:\Users\jacfo\Downloads\web gfs data model folder\public\images'
grib_folder = r'C:\Users\jacfo\Downloads\web gfs data model folder\public\grib'
rainpng_folder = r'C:\Users\jacfo\Downloads\web gfs data model folder\public\rainpng'  # Path to the rainpng folder
exclude_file = 'index.html'

# Function to delete contents of a folder, skipping an excluded file
def clear_folder(folder_path, exclude_file=None):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all files and directories in the specified folder
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # Check if the item is the excluded file
            if exclude_file and item == exclude_file:
                print(f"Skipping deletion of: {item_path}")
                continue  # Skip the exclusion file
            
            # Check if it's a file or directory
            if os.path.isfile(item_path):
                os.remove(item_path)  # Delete the file
                print(f"Deleted file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete the directory and its contents
                print(f"Deleted directory: {item_path}")
    else:
        print(f"The specified folder does not exist: {folder_path}")

# Clear the public/images folder excluding index.html
clear_folder(images_folder, exclude_file)

# Clear the public/grib folder (no exclusions)
clear_folder(grib_folder)

# Clear the public/rainpng folder (no exclusions)
clear_folder(rainpng_folder)
