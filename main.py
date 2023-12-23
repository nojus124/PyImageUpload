import random
import shutil
import datetime

import configparser
from fastapi import FastAPI, UploadFile, File
from starlette.responses import HTMLResponse

class Config:
    def __init__(self, config_file="settings.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get(self, section, option):
        return self.config.get(section, option)

class Images:
    def __init__(self):
        self.config = Config()
        print("Loading images from file....")
        self.images_list = self.load_images_from_file()
        if len(self.images_list) > 0:
            for image in self.images_list:
                print(f"{image.ImageID} {image.ImagePath} {image.ImageName}")
            print("Pictures loaded successfully.")
        else:
            print("There are no images :(")

    def add_image(self, image_name: str):
        new_image = Image(ImageName=image_name)
        self.images_list.append(new_image)
        return new_image
    def load_images_from_file(self):
        FileName = self.config.get("FileSystem", "SaveFile")
        images = []
        try:
            with open(FileName, "r") as f:
                for line in f:
                    image_info = line.strip().split()
                    if len(image_info) == 3:
                        image = Image(ImageName=image_info[2])
                        image.ImageID = int(image_info[0])
                        image.ImagePath = image_info[1]
                        images.append(image)
        except FileNotFoundError:
            pass  # Ignore if the file is not found
        return images

class Image:
    ImagePath: str
    ImageName: str
    def __init__(self, ImageName: str):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")  # Replace colons with hyphens
        self.ImageID = random.randint(0, 999999)
        self.ImageName = ImageName
        self.ImagePath = fr"images\{formatted_datetime}{self.ImageID}.png"

class Main:
    def __init__(self):
        self.app = FastAPI()
        self.config = Config()  # Import the Config class
        self.image_list = Images()

        @self.app.post("/upload-image")
        async def upload_image(file: UploadFile = File(...)):
            FileName = self.config.get("FileSystem", "SaveFile")
            image_instance = self.image_list.add_image(image_name=file.filename)
            f = open(FileName, "a")
            f.write(f"{image_instance.ImageID} {image_instance.ImagePath} {image_instance.ImageName}\n")
            f.close()
            # Save the uploaded file to the "images" folder
            with open(image_instance.ImagePath, "wb") as f:
                shutil.copyfileobj(file.file, f)
            print("Picture succesfully uploaded")

            # Return file information
            return HTMLResponse(content=f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                            <title></title>
                        </head>
                        <body class="bg-gray-200 h-screen flex items-center justify-center">
                        <script>
                        window.location.href = '/';
                        </script>

                        </body>
                        </html>
                        """)

        @self.app.api_route("/", methods=["GET"])
        async def main_page():
            titlename = self.config.get("Settings", "title_name")

            # Display the list of uploaded images
            images_info = ""
            for image in reversed(self.image_list.images_list):
                images_info += f"""
                <div class="bg-gray-100 p-4 my-2 rounded-md shadow-md w-full">
                    <div>ID: {image.ImageID}</div>
                    <div>Name: {image.ImageName}</div>
                    <div>Path: {image.ImagePath}</div>
                </div>
                """

            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                <title>{titlename}</title>
            </head>
            <body class="bg-gray-200">

                <div class="min-h-screen flex flex-col items-center justify-center">

                    <div class="bg-white p-8 rounded-lg shadow-md w-96">
                        <form action="/upload-image" method="post" enctype="multipart/form-data" class="text-center">
                            <label for="image" class="block text-sm font-medium text-gray-700">Choose an image</label>
                            <input type="file" id="image" name="file" accept="image/*" class="mt-1 p-2 border border-gray-300 rounded-md">
                            <button type="submit" class="mt-4 p-2 bg-blue-500 text-white rounded-md">Upload</button>
                        </form>

                        <div>
                            <h3>Uploaded Images:</h3>
                            {images_info}
                        </div>
                    </div>

                </div>

            </body>
            </html>
            """)


# Run the FastAPI app using uvicorn
if __name__ == "__main__":
    import uvicorn
    config = Config()
    Host = config.get("Settings", "host")
    Port = int(config.get("Settings", "port"))
    main_instance = Main()
    uvicorn.run(main_instance.app, host=Host, port=Port)
