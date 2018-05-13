"""
mosaique.py.
python mosaique.py reborn_from_ashes_by_nanomortis-dah4pk0.png --rec -g 9 -m 1 -b 1.1 --holes
python mosaique.py reborn_from_ashes_by_nanomortis-dah4pk0.png --tri -g 6 -m 0 -b 1.1 --holes
python mosaique.py reborn_from_ashes_by_nanomortis-dah4pk0.png --hex -g 9 -m 0 -b 1.1 --holes
python mosaique.py reborn_from_ashes_by_nanomortis-dah4pk0.png --los -g 6 -m 2 -b 1.1 --holes

Usage:
  mosaique.py <filename> (--hex|--tri|--rec|--los) [options]
  mosaique.py -h | --help
  mosaique.py --version

Options:
  -h --help     Show this screen.
  --holes  \o/
  -b=<value>, --background=<value>  background darker level [default: 1].
  -g=<step>, --grid=<step>  grid step [default: 18].
  -m=<margin>, --margin=<margin>  grid step [default: 0].
  -s=<tuple>, --size=<tuple>  output size  [default: 1920,1080].
  -f=<filter>, --filter=<filter>  filter size  [default: 0].
  -o=<output>, --output=<output>  prefix.

"""

import cv2
import numpy as np
from docopt import docopt
from random import randint
from path import Path

class Geometry(object):
  def __init__(self, step, margin):
    self._stepx = 0
    self._stepy = 0
    self._radius = 0
    self.offsetx = 0
    self.offsety = 0

  @property
  def radius(self):
    return int(self._radius)

  @property
  def step(self):
    return [self._stepx, self._stepy]

  def get_properties(self, x, y):
    # X, Y, PTS
    return [int(0), int(0), np.array([[int(0), int(0)]], np.int32).reshape((-1, 1, 2))]


class Rectangle(Geometry):
  def __init__(self, step, margin):
    self._stepx = int(step)
    self._stepy = int(self._stepx)
    # dimension caractéristiques du polygone
    self._radius = self._stepx/2. - margin
    self.sx = self._radius
    self.sy = self._radius

    # parametre d'offset
    self.offsetx = 0  # step/3. + step/5.
    self.offsety = 0  # step/3. + step/5.

  def get_properties(self, x, y):
    # calcul de la position
    cx = self.offsetx + x * self._stepx
    cy = self.offsety + y * self._stepy

    pts = np.array([[int(cx-self.sx), int(cy+self.sy)],
                    [int(cx-self.sx), int(cy-self.sy)],
                    [int(cx+self.sx), int(cy-self.sy)],
                    [int(cx+self.sx), int(cy+self.sy)]], np.int32).reshape((-1, 1, 2))
    return [int(cx), int(cy), pts]


class Losange(Geometry):
  def __init__(self, step, margin):
    self._stepx = int(step)
    self._stepy = int(self._stepx * 2.)
    # dimension caractéristiques du polygone
    self._radius = self._stepx - margin
    self.sx = self._radius
    self.sy = self._radius
    # parametre d'offset
    self.offsetx = 0  # step/3. + step/5.
    self.offsety = 0  # step/3. + step/5.

  def get_properties(self, x, y):
    # calcul de la position
    cx = self.offsetx + x * self._stepx
    if x % 2 == 0:
      cy = self.offsety + y * self._stepy
    else:
      cy = self.offsety + y * self._stepy + self._stepy/2.

    pts = np.array([[int(cx-self.sx), int(cy)],
                    [int(cx), int(cy-self.sy)],
                    [int(cx+self.sx), int(cy)],
                    [int(cx), int(cy+self.sy)]], np.int32).reshape((-1, 1, 2))
    return [int(cx), int(cy), pts]


class Hexagon(Geometry):
  def __init__(self, step, margin):
    self._stepx = int(step)
    self._stepy = int(self._stepx * 2/3. * np.sqrt(3)/2. * 2.)
    # dimension caractéristiques du polygone
    self._radius = self._stepx * 2/3. - margin
    self.sx = np.sqrt(3)/2. * self._radius
    self.sy = 1/2. * self._radius
    self.sz = self._radius
    # parametre d'offset
    self.offsetx = 0  # step/3. + step/5.
    self.offsety = 0  # step/3. + step/5.

  def get_properties(self, x, y):
    # calcul de la position
    cx = self.offsetx + x * self._stepx
    if x % 2 == 0:
      cy = self.offsety + y * self._stepy
    else:
      cy = self.offsety + y * self._stepy + self._stepy/2.

    pts = np.array([[int(cx-self.sz), int(cy)],
                     [int(cx-self.sy), int(cy-self.sx)],
                     [int(cx+self.sy), int(cy-self.sx)],
                     [int(cx+self.sz), int(cy)],
                     [int(cx+self.sy), int(cy+self.sx)],
                     [int(cx-self.sy), int(cy+self.sx)]], np.int32).reshape((-1, 1, 2))
    return [int(cx), int(cy), pts]


class Triangle(Geometry):
  def __init__(self, step, margin):
    self._stepx = int(step)
    self._stepy = int(self._stepx * 2. * np.sqrt(3)/2.)
    # dimension caractéristiques du polygone
    self.su = self._stepx * 2. * 1/3. * np.sqrt(3)/4.
    self._radius = self._stepx * 2. - margin

    self.sx = self._radius / 2.
    self.sy = self._radius * 2/3. * np.sqrt(3)/2.
    self.sz = self._radius * 1/3. * np.sqrt(3)/2.

    # parametre d'offset
    self.offsetx = 0  # step/3. + step/5.
    self.offsety = 0  # step/3. + step/5.

  def get_properties(self, x, y):
    # calcul de la position
    cx = self.offsetx + x * self._stepx
    if (x+y) % 2 == 0:
      cy = self.offsety + y * self._stepy + self.su
      pts = np.array([[int(cx), int(cy-self.sy)],
                      [int(cx-self.sx), int(cy+self.sz)],
                      [int(cx+self.sx), int(cy+self.sz)]], np.int32).reshape((-1, 1, 2))
    else:
      cy = self.offsety + y * self._stepy - self.su
      pts = np.array([[int(cx-self.sx), int(cy-self.sz)],
                      [int(cx), int(cy+self.sy)],
                      [int(cx+self.sx), int(cy-self.sz)]], np.int32).reshape((-1, 1, 2))
    return [int(cx), int(cy), pts]


if __name__ == '__main__':
  arguments = docopt(__doc__, version='0.1')
  print(arguments)

  img = cv2.imread(Path(arguments["<filename>"]))

  # choix du motif
  if arguments["--hex"]:
    geometry = Hexagon(int(float(arguments["--grid"])), int(float(arguments["--margin"])))
  elif arguments["--tri"]:
    geometry = Triangle(int(float(arguments["--grid"])), int(float(arguments["--margin"])))
  elif arguments["--rec"]:
    geometry = Rectangle(int(float(arguments["--grid"])), int(float(arguments["--margin"])))
  elif arguments["--los"]:
    geometry = Losange(int(float(arguments["--grid"])), int(float(arguments["--margin"])))
  else:
    raise IOError("Geometry not known")

  stepx, stepy = geometry.step
  dst_size = list(map(int, arguments["--size"].split(",")))

  # crop to keep the same proportion after resize
  max_factor = max(dst_size[0]/img.shape[1], dst_size[1]/img.shape[0])
  h = int(dst_size[1]/max_factor)
  w = int(dst_size[0]/max_factor)
  x = int((img.shape[1] - w)/2.)
  y = int((img.shape[0] - h)/2.)
  img = img[y:y+h, x:x+w]

  img = cv2.resize(img, (dst_size[0]*2, dst_size[1]*2), interpolation=cv2.INTER_CUBIC)

  if int(arguments["--filter"]) > 0:
    img = cv2.blur(img, (int(arguments["--filter"]), int(arguments["--filter"])))

  img = img / 255.
  output = img * float(arguments["--background"])

  for x in range(int(img.shape[1]/(stepx))+2):
    for y in range(int(img.shape[0]/(stepy))+2):
      if randint(1, 10) > 3 if arguments["--holes"] else True:
        cx, cy, pts = geometry.get_properties(x, y)
        color = ((img[max(0,min(img.shape[0]-1, cy)), max(0,min(img.shape[1]-1, cx))][0]),
                 (img[max(0,min(img.shape[0]-1, cy)), max(0,min(img.shape[1]-1, cx))][1]),
                 (img[max(0,min(img.shape[0]-1, cy)), max(0,min(img.shape[1]-1, cx))][2]))
        cv2.fillPoly(output, [pts], color=color, lineType=cv2.LINE_AA)

  output = cv2.resize(output, (dst_size[0], dst_size[1]), interpolation=cv2.INTER_CUBIC)

  if arguments["--output"]:
    print(arguments["--output"] + Path(arguments["<filename>"]).basename())
    cv2.imwrite(arguments["--output"] + Path(arguments["<filename>"]).basename(), output * 255)
  cv2.imshow("Test", output)
  cv2.waitKey(0)

