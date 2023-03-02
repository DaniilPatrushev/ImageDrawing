import re
import os
from random import choice
from string import ascii_letters

import PIL.ImageDraw
import pymongo

from database import get_database
from settings import LOCAL_STORAGE_IMAGE_PATH


def get_image_path(image_id: str, image_format: str) -> str:
    """
    Returns the path to the image with the specified id
    """

    return LOCAL_STORAGE_IMAGE_PATH + image_id + '.' + image_format


def image_draw(current_part_of_contour: str, image_coordinates: dict, color: str,
               draw: PIL.ImageDraw.ImageDraw) -> dict:
    """Drawing contour of the face

    Args:
        current_part_of_contour (str): Accepts the right/left half of the face for rendering
        image_coordinates (dict): Accepts a dictionary with the coordinates of the contour of the face
        color (str): Color to draw
        draw (Pil.ImageDraw.Image.Draw): An instance of the pillow for drawing a contour on image

    Returns:
        coordinates (dict): Returns the last point of one half of the face
    """

    # Draw the contour of the face by coordinates from the database
    number_of_point = 1
    coordinates = image_coordinates[current_part_of_contour + str(number_of_point)]
    while True:
        number_of_point += 1
        try:
            next_coordinates = image_coordinates[current_part_of_contour + str(number_of_point)]
        except KeyError:
            return coordinates
        draw.line([
            (coordinates['x'], coordinates['y']),
            (next_coordinates['x'], next_coordinates['y'])
            ],
            width=5, fill=color)
        coordinates = next_coordinates


def image_contour(response: dict) -> dict:
    """
    Returns the coordinates of the face contour
    
    Args:
        response (dict): Response from Face++ API
        
    Returns:
        face_contour (dict): Return only face contour coordinates
    """

    face_contour = {}
    for i in response['faces']:
        image_coordinates = i['landmark']
        key = i['face_token']
        pattern = r'contour_((left)|(right))\d+'
        face_coordinates = {}
        for j in image_coordinates:
            if re.match(pattern, j):
                face_coordinates[j] = image_coordinates[j]
        face_contour[key] = face_coordinates
    return face_contour


def deleting_images(image_id: str) -> pymongo.collection:
    """
    Delete the image from the database and the file system

    Args:
        image_id (str): Unique image id

    Returns:
        collection (pymongo.collection): Return MongoDB collection
    """

    collection = get_database()
    try:
        image_format = collection.find_one({'_id': image_id})
        os.remove(get_image_path(image_id=image_id, image_format=image_format['format']))
        collection.delete_one({'_id': image_id})
        return collection
    except TypeError:
        return None


def random_id() -> str:
    """
        Return random image id, length = 15
    """

    return ''.join(choice(ascii_letters) for i in range(15))
