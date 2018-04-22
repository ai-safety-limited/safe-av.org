from vapory import *
import numpy as np, PIL, PIL.ImageFont, PIL.Image


def letter_pixels(letter):

    font =  PIL.ImageFont.load_default()
    (width, height) = font.getsize(letter)
    txt_image = np.array(font.getmask(letter)).reshape((height, width))
    xx,yy = np.logical_not(np.pad(txt_image, 1, 'constant')).nonzero()[::-1]
    return zip([width + 2.0] * len(xx), [height + 2.0] * len(yy), xx, yy)

# Spec the cube
#  >>> "  ".join(["L R U D F B M E L' R' U' D' F' B' M' E'".split()[int(d, 16)] for d in "".join([str(hex(ord(c)))[2:] for c in ("AI SAFETY")])])
# "F  R  F  R'  U  L  B  D  F  R  F  M  F  B  B  F  B  R'"


spec = \
   [(i % 3, 2 - i // 3, 0, (0.05, 0.95), (0.05, 0.95), (0.05, 0.01), 'RGWYBWGYG'[i]) for i in range(9)] \
 + [(0, 2 - i // 3, 2 - i % 3, (0.05, 0.01), (0.05, 0.95), (0.05, 0.95), 'ROYWYBRBW'[i]) for i in range(9)] \
 + [(2 - i // 3, 2, 2 - i % 3, (0.05, 0.95), (0.95, 0.98), (0.05, 0.95), 'BYORROYBG'[i]) for i in range(9)] \


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


cubes = [([x + 0.03,y + 0.03,z + 0.03], [x + 0.97,y + 0.97,z + 0.97], textures['0']) for x,y,z,dx,dy,dz,c in spec]


stickers = [([x + dx[0], y + dy[0], z + dz[0]], [x + dx[1],y + dy[1],z + dz[1]], textures[c]) for x,y,z,dx,dy,dz,c in spec][-9:]

text = []


for letter, (x,y,z,dx,dy,dz,c) in zip('dexle./avharamporg', spec):
    for width, height, i, j in letter_pixels(letter):
        if dz == (0.05, 0.01): xx, yy, zz = i, height - j, width - 3
        elif dx == (0.05, 0.01): xx, yy, zz = width / 2, height - j, width - i
        text.append(([   x + dx[0] + (dx[1] - dx[0]) * xx / width, 
                         y + dy[0] + (dy[1] - dy[0]) * yy / height, 
                         z + dz[0] + (dz[1] - dz[0]) * zz / width ],
                         [x + dx[0] + (dx[1] - dx[0]) * (xx + 1) / width,
                          y + dy[0] + (dy[1] - dy[0]) * (yy - 1) / height,
                          z + dz[0] + (dz[1] - dz[0]) * (zz - 1) / width],
                         textures[c]
                         ))

boxes = cubes + stickers + text

scale = 0.5
boxes = [Box([x0 * scale, y0 * scale, z0 * scale],[x1 * scale, y1 * scale, z1 * scale], c, Interior('ior', 4)) for ((x0, y0, z0),(x1, y1, z1), c) in boxes]

lights = LightSource([-20, 50, -20], 'color', 1)
camera = Camera( 'location', [-10, 10, -4], 'look_at', [1.5 * scale, 1.5 * scale, 1.5 * scale], 'angle', 10)

ground = Plane( [0, 1, 0], 0,
                Texture( Pigment( 'color', [1, 1, 1]),
                Finish( 'phong', 0.1, 'reflection',0.0,                                         'metallic', 0.3)))

scene = Scene(camera, [lights, Background("White"), ground] + boxes,
        included=["colors.inc", "textures.inc", "glass.inc"])

#scene.render("brick.png", width=2000, height=2000, antialiasing=0.1)


img = PIL.Image.open("brick.png")
width, height = img.size


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

scale = 2000 / 640.0
pa = [(0, 0), (width, 0), (width, height), (0, height)]
pb = [(0, 0), (640 * scale, 0), (595 * scale, 2500 * scale), (50 * scale, 2500 * scale)]
print pa, pb
coeffs = find_coeffs(pa, pb)
img.transform((width, height), PIL.Image.PERSPECTIVE, coeffs,
                PIL.Image.BICUBIC).save("brick-perspective.png")
