from vapory import *
import numpy as np, PIL, PIL.ImageFont, PIL.Image


def letter_pixels(letter):

    font =  PIL.ImageFont.load_default()
    (width, height) = font.getsize(letter)
    txt_image = np.array(font.getmask(letter)).reshape((height, width))
    #xx,yy = np.logical_not(np.pad(txt_image, 1, 'constant')).nonzero()[::-1]
    xx,yy = np.pad(txt_image, 1, 'constant').nonzero()[::-1]
    return zip([width + 2.0] * len(xx), [height + 2.0] * len(yy), xx, yy)

textures = {
 '0' : Texture(Pigment('color', [0.01, 0.01, 0.01])),
 '1' : Texture(Pigment('color', [1, 1, 1])),
 'G' : Texture("Jade"),
 'R' : Texture("Red_Marble"),
 'W' : Texture("White_Marble"),
 'B' : Texture("Blue_Agate"),
 'Y' : Texture("Yellow_Pine"),
 'O' : Texture("Tom_Wood"),
 'Gold' : Texture("Gold_Texture"),

}

text = []
dx,dy,dz = 4,5,4

for width, height, i, j in letter_pixels("SafeAV"):
    yy, zz = height - j, width - i
    text.append(([   0, 
                     dy * yy / height, 
                     dz * zz / width ],
                 [   dx / height,
                     dy * (yy - 1) / height,
                     dz * (zz - 1) / width],
                 Texture("Jade")
                 ))

boxes = text

scale = 0.6
boxes = [Box([x0 * scale, y0 * scale, z0 * scale],[x1 * scale, y1 * scale, z1 * scale], c, Interior('ior', 4)) for ((x0, y0, z0),(x1, y1, z1), c) in boxes]

lights = LightSource([-20, 50, -20], 'color', 1)
camera = Camera( 'location', [-10, 10, -4], 'look_at', [1.5 * scale, 1.0 * scale, 2.5 * scale], 'angle', 10)

ground = Plane( [0, 1, 0], 0,
                Texture( Pigment( 'color', [1, 1, 1]),
                Finish( 'phong', 0.1, 'reflection',0.0,                                         'metallic', 0.3)))

scene = Scene(camera, [lights, Background("White"), ground] + boxes,
        included=["colors.inc", "textures.inc", "glass.inc"])

for i in [32, 64, 128, 256, 512]:
    scene.render("logo-%d" % i , width=i, height=i, antialiasing=0.01)
