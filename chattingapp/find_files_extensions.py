import base64, binascii, magic

def get_file_type(file_data):
    file_type = magic.from_buffer(file_data, mime=True)
    if file_type.startswith("image/"):
    # File is an image
        return file_type
    elif file_type.startswith("video/"):
        # File is a video
        return file_type
    elif file_type.startswith("audio/"):
        # File is an audio file
        return file_type
    else:
    # File is some other type of file
        return None
