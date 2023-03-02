import requests
import io
import imghdr

from pymongo.errors import DuplicateKeyError
from fastapi import FastAPI, File, Response, HTTPException
from fastapi.responses import JSONResponse
from PIL import ImageDraw, Image

from database import get_database
from settings import params, FACEPP_URL
from utils import get_image_path, image_draw, image_contour, deleting_images, random_id


URL = FACEPP_URL
app = FastAPI()


@app.post('/image')
async def get_image(image: bytes = File(...)):
    """Takes an image, runs it through Face++ API and saves the image in local store, data about image in database

        Args:\n
            image (str): Accept image in .png or .jpg(.jpeg) format

        Returns:\n
            image_id (JSONResponse): Return image id
        """

    if image.__sizeof__() >= 2097152:
        raise HTTPException(status_code=400, detail='Image file too large. Image file size should be less than 2MB')
    response = requests.post(url=URL, params=params, files={'image_file': image}).json()
    if 'error_message' in response:
        raise HTTPException(status_code=400, detail=response['error_message'])
    print(response)
    if not len(response['faces']):
        raise HTTPException(status_code=406, detail='NO FACE ON IMAGE')
    image_id = response['image_id']
    image_format = imghdr.what('', h=image)

    face_contour = image_contour(response)
    collection = get_database()
    face_contour['_id'] = image_id
    face_contour['format'] = image_format
    try:
        collection.insert_one(face_contour)
    except DuplicateKeyError:
        image_id = random_id()
        face_contour['_id'] = image_id
        collection.insert_one(face_contour)

    image_path = get_image_path(image_id, image_format)
    with open(image_path, 'wb') as img:
        img.write(image)
    return JSONResponse({'id': image_id})


@app.get('/image/{image_id}')
async def image_color(image_id: str, color: str = 'red'):
    """Accepts an image and returns it with the outline of the face

    Args:\n
        image_id (str): Unique image id

        color (str, optional): Accepts a color for rendering. Should be red/green/blue. Defaults to 'red'.

    Returns:\n

        image (Response): Return rendered image
    """

    # Connect to MongoDB and find image id
    collection = get_database()
    try:
        image_from_database = collection.find_one({'_id': image_id})
        image_path = get_image_path(image_id=image_id, image_format=image_from_database['format'])
        image = Image.open(image_path)
    except TypeError:
        raise HTTPException(status_code=412, detail='ID IS NOT EXISTS')

    # Outlines the contour of the face
    draw = ImageDraw.Draw(image)
    for i in image_from_database:
        if (i != '_id') and (i != 'format'):
            try:
                last_left = image_draw(current_part_of_contour='contour_left',
                                       image_coordinates=image_from_database[i], color=color, draw=draw)
                last_right = image_draw(current_part_of_contour='contour_right',
                                        image_coordinates=image_from_database[i], color=color, draw=draw)
                draw.line([(last_left['x'], last_left['y']), (last_right['x'], last_right['y'])], width=5, fill=color)
            except ValueError:
                raise HTTPException(status_code=412, detail='COLOR SHOULD BE RED/GREEN/BLUE')

    # Return image
    buf = io.BytesIO()
    image.save(buf, format=image_from_database['format'].upper())
    byte_image = buf.getvalue()
    return Response(content=byte_image, media_type='image/jpeg')


@app.put('/image/{image_id}')
async def replace_image(image_id: str, image: bytes = File(...)):
    """Replaces the image with a new one by the specified id

    Args:\n
        image_id (str): Unique image id

        image (bytes, optional): Accept a new image to replace. Defaults to File(...).

    Returns:\n
        message (JSONResponse): Returns a message about successful replacement
    """

    collection = deleting_images(image_id)
    if collection is None:
        raise HTTPException(status_code=412, detail='ID IS NOT EXISTS')

    response = requests.post(url=URL, params=params, files={'image_file': image}).json()
    if 'error_message' in response:
        raise HTTPException(status_code=400, detail=response['error_message'])
    image_format = imghdr.what('', h=image)

    face_contour = image_contour(response)
    face_contour['_id'] = image_id
    face_contour['format'] = image_format
    collection.insert_one(face_contour)

    image_path = get_image_path(image_id, image_format=image_format.upper())
    with open(image_path, 'wb') as img:
        img.write(image)
    return JSONResponse({'id': 'Image is successfully updated'})


@app.delete('/image/{image_id}')
def delete_image(image_id: str):
    """Delete image from database and local storage

    Args:\n
        image_id (str): Unique image id

    Returns:\n
        message (JSONResponse): Returns a message about successful deleting
    """

    if deleting_images(image_id) is None:
        raise HTTPException(status_code=412, detail='ID IS NOT EXISTS')
    return JSONResponse({'id': 'Image is successfully deleted'})
