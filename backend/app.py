from flask import Flask, jsonify, request, send_file,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging,pymysql
from io import BytesIO
import base64
from datetime import datetime
import imghdr
app = Flask(__name__)
from sqlalchemy import desc

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@192.168.242.106:32230/imagesdb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/imagesdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

#app.logger.setLevel(logging.INFO)
#file_handler = logging.FileHandler('app.log')
#file_handler.setLevel(logging.INFO)
#app.logger.addHandler(file_handler)

log_name="app.log"
log_path = os.path.join('logs', log_name)
log_save_path = os.path.join(os.path.dirname(__file__), '.', 'logs')
if not os.path.exists(log_save_path):
    os.makedirs(log_save_path)
#log_file.save=os.path.join(log_save_path,log_name)
log_file_path=os.path.join(log_save_path,log_name)

app.logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_time=db.Column(db.DateTime, default=datetime.now)
    image_path = db.Column(db.String(255))
    state = db.Column(db.Integer)

    def __init__(self, image_path, state):
        self.image_path = image_path
        self.state = state

    def serialize(self):
        return {'id': self.id, 'image_path': self.image_path, 'upload_time': self.upload_time.strftime("%Y-%m-%d %H:%M:%S%f"),'state': self.state}

with app.app_context():
    db.create_all()
is_upload = False

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['POST'])
def upload_image():
    global is_upload
    is_upload = True  
    app.logger.info(f'{datetime.now()}-Image upload requested')
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            filename = f"{current_time}.{image_file.filename.rsplit('.', 1)[1].lower()}"
            image_path = os.path.join('images', filename)
            save_path = os.path.join(os.path.dirname(__file__), '.', 'images')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            image_file.save(os.path.join(save_path, filename))

            img = Images(image_path=image_path, state=1)
            db.session.add(img)
            db.session.commit()
            app.logger.info(f'{datetime.now()}-Image upload: {image_path}')
            return 'Image uploaded successfully', 201

        else:
            app.logger.info(f'{datetime.now()}-Image upload failed for invalid type ')
            return 'Invalid file type. Only JPEG and PNG are allowed.', 406

    else:
        return 'No image provided', 400

@app.route('/', methods=['GET'])
def get_images():
    images = Images.query.filter(Images.state==1).order_by(desc(Images.upload_time))
    serialized_images = [image.serialize() for image in images]
    return jsonify(serialized_images)

@app.route('/<int:id>', methods=['GET'])
def download_image(id):
    global is_upload
    if (is_upload != True):
        app.logger.info(f'{datetime.now()}-Image download requested')
    img = Images.query.get(id)
    if img and img.image_path:  # 检查 image_path 是否存在
        image_path = os.path.join(os.path.dirname(__file__), '.', img.image_path)  # 构建完整的图像文件路径
        print(os.path.dirname(__file__))
        print(image_path)
        image_type = imghdr.what(image_path)  # 获取图像文件的类型
        if image_type in ['jpeg', 'jpg']:
            response = make_response(send_file(image_path, mimetype='image/jpeg'))
            response.headers.set('Content-Disposition', f'attachment; filename=image_{id}.jpeg')
            if (is_upload != True):
                app.logger.info(f'{datetime.now()}-Image download {image_path}')
            is_upload = False
            return response
        elif image_type == 'png':
            response = make_response(send_file(image_path, mimetype='image/png'))
            response.headers.set('Content-Disposition', f'attachment; filename=image_{id}.png')
            if (is_upload != True):
                app.logger.info(f'{datetime.now()}-Image download {image_path}')
            is_upload = False
            return response
        else:
            return 'Unknown image format', 400
    else:
        return 'Image not found', 404

@app.route('/<int:id>', methods=['DELETE'])
def delete_image(id):
    image = Images.query.get(id)
    if image:
        image.state=0
        # db.session.delete(image)
        db.session.commit()
        app.logger.info(f'{datetime.now()}-Image delete {image.image_path}')
        return 'deleted', 200

    else:
        return 'image not found', 404
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=int("5001"),debug=True)
