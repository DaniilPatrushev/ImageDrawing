# ImageDrawing
API to detect faces on image using [Face++](https://www.faceplusplus.com)

## Example
<img width="716" alt="Снимок экрана 2023-03-02 в 02 18 23" src="https://user-images.githubusercontent.com/48191103/222230898-05c61fbb-fd7b-4840-8496-303eca420808.png">

## Docs
http://127.0.0.1:8000/docs

- **POST** `/image`
It takes a picture, runs it through the [FacePlusPlus](https://www.faceplusplus.com/) API, and puts the result into the MongoDB. Image file size should be less than 2MB, format : JPG (JPEG) or PNG.
Returns JSON `{'id': <id>}`

- **GET** `/image/<id>?color=<red/green/blue>`
It takes an id and a color parameter - a color, with this color it draws faces in the picture that were found using FacePlusPlus and returns the rendered picture in response

- **PUT** `/image/<id>`
Accepts a picture, changes it for recording with the corresponding id and drives it through FacePlusPlus

- **DELETE** `/image/<id>`
Deletes the picture and post with the corresponding id

## How to run?
- Fill env.txt

Using local enviroment:
```
sudo apt install python3-pip
pip install —upgrade pip
pip install virtualenv
python3 -m venv venv
source venv/bin/activate
pip install requirements.txt
mkdir images
cd ./app
export LOCAL_STORAGE_IMAGE_PATH=/my/path/to/images
uvicorn main:app —reload
```

Using docker container
```
docker build . -t imagedrawing:latest
docker run -p 127.0.0.1:8000:8000 --env-file=env.txt --name=PROD -d imagedrawing:latest
```

## TODO
- [X] Add multiface recognition.
- [ ] Add volume option to container to save all downloaded pictures.
- [ ] Deploy.
