""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
import datetime as dt
import os
import image_lib
import inspect
import sys
import sqlite3
import apod_api
import hashlib
import re

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    
    earliest_date = dt.date(1995, 6, 16)
    current_date = dt.date.today()
    num_params = len(sys.argv) -1
    if num_params >= 1:
        check_date = sys.argv[1]
        try:
            date_obj = dt.datetime.strptime(check_date, '%Y-%m-%d').date()
            
            if earliest_date <= date_obj <= current_date:                
                apod_date = date_obj 
            else:
                print('Error: ', end='')
                if date_obj > current_date:
                    print('APOD date cannot be in the future')
                elif earliest_date > date_obj:
                    print('APOD date cannot be earlier than 1995-06-16')

                print('Script execution aborted')
                sys.exit()

        except ValueError:
            print(f'Error: Invalid date format; ', end='')

            print(f'Invalid isoformat string: {check_date}')
            
            print('Script execution aborted')
            sys.exit()
    else:
        apod_date = dt.date.today().isoformat()
    return apod_date
        #day is out of range for month
        #Invalid isoformat string:{'check_date'}

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir 
    global image_cache_db
    # TODO: Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, 'image_cache')

    # TODO: Create the image cache directory if it does not already exist
    print(f'Image cache directory: {image_cache_dir}')
    if not os.path.exists(image_cache_dir):
        os.mkdir(image_cache_dir)
        print('Image cache directory created.')
    else:
        print('Image cache directory already exists.')
    
    # TODO: Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'image_chache.db')
    print(f'Image chache database: {image_cache_db}')
    
    # TODO: Create the DB if it does not already exist
    if not os.path.exists(image_cache_db):
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        create_apod_query ="""
        CREATE TABLE IF NOT EXISTS apod
        (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        explanation TEXT NOT NULL,
        file_path TEXT NOT NULL,    
        sha256 TEXT NOT NULL
        );
        """
        cur.execute(create_apod_query)
        con.commit()
        con.close()
        print('Image cache database created.') 
    else:
        print('Image cache database already exists.')

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date)

    # TODO: Download the APOD information from the NASA API
    apod_info = apod_api.get_apod_info(apod_date)
    title = apod_info['title']
    print(f'APOD title: {title}')
    explanation = apod_info['explanation']
    apod_img_url = apod_api.get_apod_image_url(apod_info)
    print(f'APOD URL: {apod_img_url}')
    image_path = determine_apod_file_path(title, apod_img_url)
    
    # TODO: Download the APOD image
    file_content = image_lib.download_image(apod_img_url)
    sha256 = hashlib.sha256(file_content).hexdigest()
    print(f'APOD SHA-256: {sha256}')
    sha_match = get_apod_id_from_db(sha256)


    # TODO: Check whether the APOD already exists in the image cache
    if sha_match != 0:
        print('APOD image is already in cache.')
        return sha_match
    # TODO: Save the APOD file to the image cache directory
    elif sha_match == 0:
        print('APOD image is not already in cache.')
        print(f'APOD file path: {image_path}')
        image_lib.save_image_file(file_content, image_path)
    # TODO: Add the APOD information to the DB
        apod_id = add_apod_to_db(title, explanation, image_path, sha256)
        return apod_id
    else:
        return 0

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    
    # TODO: Complete function body
    print(f'Adding APOD to image database...', end='')
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    apod_query = """INSERT INTO apod (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?);"""
    apod_values = (title, explanation, file_path, sha256)
    cur.execute(apod_query, apod_values)
    con.commit()
    created_id = cur.lastrowid
    con.close()
    if created_id > 0: 
        print('success')
        return created_id
    else:
        print('failure')
        return 0
    
def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    
    # TODO: Complete function body
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    id_query = """SELECT id, sha256 FROM apod WHERE sha256 = ?"""
    cur.execute(id_query, (image_sha256,))
    query_result = cur.fetchone()
    con.close()

    try:
        db_sha = query_result[1]
    except:
        return 0
    
    if image_sha256 == db_sha:
        id = query_result[0]
        return id
    else:
        return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """

    # TODO: Complete function body
    apod_img_exe = '.' + image_url.split('.')[-1]
    image_title = image_title.strip()
    image_title = re.sub(r'\s+', '_', image_title)
    image_title = re.sub(r'[^\w\d_]', '', image_title)
    file_path = os.path.join(image_cache_dir, image_title + apod_img_exe)
    
    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
   
    # TODO: Query DB for image info
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    get_info_query = """SELECT title, explanation, file_path FROM apod WHERE id = ?"""
    cur.execute(get_info_query, (image_id,)) #THIS WAS WORKING AS NOT A TUPLE THEN STOPPED
    query_result = cur.fetchone() 
    con.close()

    # TODO: Put information into a dictionary
    apod_info = {
        'title': query_result[0], 
        'explanation': query_result[1],
        'file_path': query_result[2]
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """

    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    get_title_query = """SELECT title FROM apod"""
    cur.execute(get_title_query)
    query_result = [row[0] for row in cur.fetchall()] 
    con.close()

    return query_result

if __name__ == '__main__':
    main()