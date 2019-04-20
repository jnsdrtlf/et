from os import path
import random
import secrets
from PIL import Image, ImageFont, ImageDraw

from app import create_app
from app.models.user import User

from app.utils.tasks import huey

width = 480
height = 480
font_size = 260
colors = [
    [
        (23, 126, 137, 255),
        (255, 255, 255, 140)
    ],
    [
        (8, 76, 97, 255),
        (255, 255, 255, 140)
    ],
    [
        (219, 58, 52, 255),
        (255, 255, 255, 140)
    ],
    [
        (255, 200, 87, 255),
        (31, 45, 61, 178)
    ],
    [
        (50, 48, 49, 255),
        (255, 255, 255, 140)
    ]
]


@huey.task()
def create_user_image(user_id):
    app, db = create_app(None, minimal=True)

    with app.app_context():
        user = db.session.query(User).filter(User.id.is_(user_id)).one()

        color = random.choice(colors)
        image = Image.new('RGBA', (width, height), color[0])
        initials_image = Image.new('RGBA', image.size, (0, 0, 0, 0))

        initials = user.get_initials()

        font = ImageFont.truetype(path.join(app.static_folder, 'css', 'Roboto-Light.ttf'), font_size)
        draw = ImageDraw.Draw(initials_image)
        _w, _h = draw.textsize(initials, font=font)
        draw.text(((width - _w) / 2, (height - font_size) / 2.4), initials, fill=color[1], font=font)

        image_name = f'{user.id}-{secrets.token_hex(16)}'
        image_path = path.join(app.static_folder, 'images', 'profile', f'{image_name}.png')
        image = Image.alpha_composite(image, initials_image)
        image = image.convert('RGB')
        image.save(image_path)
        del image

        user.set_picture(image_name)
        db.session.merge(user)
        db.session.commit()
