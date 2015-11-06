import hashlib, datetime, md5, time, random
from time import localtime, strftime

# sets a dictionary with allowed upload extentions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def hash_filename(fname):
    m = md5.new()
    millis = int(round(time.time() * 1000))
    m.update(str(millis)+fname+str(random.randrange(992838239, 290385928893)))
    return m.hexdigest()