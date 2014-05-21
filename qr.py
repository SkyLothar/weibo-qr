# -*- coding: utf8 -*-

__author__ = 'Shi Wei'
__email__ = 'shiwei@mobvoi.com'
__copyright__ = 'Copyright 2014, Mobvoi Inc.'
__date__ = '2014/05/21'
__version__ = '0.0.1'
__maintainer__ = 'Shi Wei'
__status__ = 'prototype'


from cStringIO import StringIO
from urllib import unquote
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED

from flask import Flask
from flask import Response
from flask import request

from PIL import ImageDraw

from qrcode import QRCode
from qrcode import ERROR_CORRECT_H


BARS = (
    (80, 0, 84, 164),  # H_BAR
    (0, 80, 164, 84),  # V_BAR
)
IMG_BOXES = {
    'left-up':      (0, 0, 79, 79),      'right-up':     (85, 0, 164, 79),
    'left-bottom':  (0, 85, 79, 164),    'right-bottom': (85, 85, 164, 164),
}
WEIBO_THUMB_SIZE = 165
WHITE = 1
ZIP_NAME = 'qr-code/{0}.png'


app = Flask(__name__)


def gen_thumbnail_qr(data):
    qr = QRCode(
        version=2,
        error_correction=ERROR_CORRECT_H,
        border=0
    )
    qr.add_data(data)
    qr.make()
    img = qr.make_image()
    return img.resize((WEIBO_THUMB_SIZE, WEIBO_THUMB_SIZE))


def draw_white_bars(img):
    draw = ImageDraw.Draw(img)
    for bar_box in BARS:
        draw.rectangle(bar_box, WHITE)


def cut_and_pack(img):
    png_zip = StringIO()
    with ZipFile(png_zip, mode='w', compression=ZIP_DEFLATED) as zf:
        for part_name, part_box in IMG_BOXES.items():
            part_img = img.crop(part_box)
            zip_name = ZIP_NAME.format(part_name)
            part_data = StringIO()
            part_img.save(part_data, 'png')
            part_data.seek(0, 0)
            zf.writestr(zip_name, part_data.read())
    return png_zip.getvalue()


@app.route('/qr-code-img')
def full_image():
    img = gen_thumbnail_qr(unquote(request.args['data']))
    draw_white_bars(img)
    png_data = StringIO()
    img.save(png_data, 'png')
    png_data.seek(0)
    return Response(
        png_data,
        headers={
            'content-type': 'image/png',
            'content-disposition': 'attachment; filename="qr-code.png"'
        }
    )


@app.route('/qr-code-zip')
def zip_image():
    img = gen_thumbnail_qr(unquote(request.args['data']))
    zip_file = cut_and_pack(img)
    return Response(
        zip_file,
        headers={
            'content-type': 'application/zip',
            'content-disposition': 'attachment; filename="qr-code.zip"'
        }
    )


if __name__ == '__main__':
    app.run(debug=True)
