from project import app


def allowed_img(imgname):
    if not '.' in imgname:
        return False
    ext = imgname.split('.')
    if ext[-1].upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    return False

