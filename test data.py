import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# URL for the form submission
filter_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_blend.pl"

# Form data to simulate the submission
form_data = {
    'dir': '/blend.20241107/15/core',    # Adjust directory as needed
    'var_ASNOW': 'on',                    # You can adjust the parameters here as well
    'lev_surface': 'on',
}

# Define the download directory
current_date = datetime.now().strftime('%Y%m%d')  # You can customize the folder naming
download_directory = os.path.join(os.getcwd(), current_date)

# Create the download folder if it doesn't exist
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Function to download the GRIB file
def download_file(file_url, file_name):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {file_name}")
    else:
        print(f"Failed to download file: {file_url}")

# Function to simulate the form submission and get the download link
def get_grib_file_url(forecast_hour):
    # Adjust the file parameter to the appropriate forecast hour (f000, f010, f020, ...)
    file_name = f"blend.t15z.core.{forecast_hour}.co.grib2"
    
    # Update the form data with the correct file
    form_data['file'] = file_name
    
    # Send POST request with the form data to the URL
    response = requests.post(filter_url, data=form_data, allow_redirects=True)
    
    if response.status_code != 200:
        print(f"Failed to access page: {response.status_code}")
        return None
    
    # Parse the page content to extract the actual file download URL
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the link to the .grib2 file in the HTML
    file_link = None
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.grib2'):
            file_link = link['href']
            break
    
    if file_link:
        full_url = "https://nomads.ncep.noaa.gov" + file_link
        return full_url
    else:
        print(f"GRIB file link not found for {file_name}")
        return None

# Main function to download the files for the forecast hours
def main():
    # Loop through the forecast hours you want to download (f000, f010, f020, ...)
    for hour in range(0, 240, 10):  # Starts at f000, ends at f230
        forecast_hour = f"f{hour:03d}"
        print(f"Fetching data for forecast hour: {forecast_hour}")
        
        # Get the GRIB file URL for the current forecast hour
        file_url = get_grib_file_url(forecast_hour)
        
        if file_url:
            # Extract the file name from the URL and set the download path
            file_name = file_url.split('/')[-1]
            file_path = os.path.join(download_directory, file_name)
            
            # Download the file
            download_file(file_url, file_path)

if __name__ == "__main__":
    main()
