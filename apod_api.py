'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
from apod_desktop import get_apod_date
#from apod_desktop import get_apod_date
API_APOD_URL = 'https://api.nasa.gov/planetary/apod'
API_KEY = 'zDZBpCmZcQyKzskgCae1cZJLyq3edLtEAK9e7mIO'

def main():   
    # TODO: Add code to test the functions in this module
    #apod_date = '2023-03-27'
    apod_date = get_apod_date()
    apod_info_dict = get_apod_info(apod_date)
    apod_image_url = get_apod_image_url(apod_info_dict)
    print(apod_image_url)
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    apod_date_url =  API_APOD_URL +'?api_key=' + API_KEY + '&date=' + apod_date
    print(f'Getting {apod_date} APOD information from NASA...', end='')
    resp_msg = requests.get(apod_date_url)
    
    if resp_msg.ok:
        print('success')
        apod_info_dict = resp_msg.json()
        return apod_info_dict
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')
        return

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    media_type = apod_info_dict['media_type']
    if media_type == 'image':
        image_url = apod_info_dict['hdurl']
        return image_url
    elif media_type == 'video':
        video_url = apod_info_dict['url']
        return video_url 
    else:
        print('invalid media type')
    return

if __name__ == '__main__':
    main()