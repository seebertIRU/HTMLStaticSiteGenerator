import base64
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(script_dir, 'static', 'images')

png_data = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)

with open(os.path.join(img_dir, 'glorfindel.png'), 'wb') as f:
    f.write(png_data)

with open(os.path.join(img_dir, 'tom.png'), 'wb') as f:
    f.write(png_data)

with open(os.path.join(img_dir, 'rivendell.png'), 'wb') as f:
    f.write(png_data)

print('Images created successfully')
