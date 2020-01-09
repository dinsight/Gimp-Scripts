#!/usr/bin/env python
from gimpfu import *
import gimpenums
import collections
import math

gettext.install("resynthesizer", gimp.locale_directory, unicode=True)
Tile = collections.namedtuple("Tile",['name', "inset_type"])

BLANK                 = int('0000000000000000',2)
ROUND_INSIDE_TOP      = int('0000000000000001',2)
ROUND_INSIDE_BOTTOM   = int('0000000000000010',2)
ROUND_INSIDE_LEFT     = int('0000000000000100',2)
ROUND_INSIDE_RIGHT    = int('0000000000001000',2)
ROUND_OUTSIDE_BOTTOM  = int('0000000000010000',2)
ROUND_OUTSIDE_TOP     = int('0000000000100000',2)
ROUND_OUTSIDE_RIGHT   = int('0000000001000000',2)
ROUND_OUTSIDE_LEFT    = int('0000000010000000',2)
INSET_TOP_LEFT        = int('0000000100000000',2)
INSET_TOP_RIGHT       = int('0000001000000000',2)
INSET_BOTTOM_LEFT     = int('0000010000000000',2)
INSET_BOTTOM_RIGHT    = int('0000100000000000',2)

inside_corners_with_edges = {
    Tile("a00", INSET_TOP_RIGHT):         (1,0),
    Tile("a01", ROUND_INSIDE_TOP):        (2,1),
    Tile("a02", INSET_TOP_LEFT):          (3,0),
    Tile("a06", INSET_BOTTOM_RIGHT):      (4,1),
    Tile("a07", ROUND_INSIDE_RIGHT):      (3,2),
    Tile("a08", INSET_TOP_RIGHT):         (4,3),
    Tile("a09", INSET_BOTTOM_LEFT):       (0,1),
    Tile("a10", ROUND_INSIDE_LEFT):       (1,2),
    Tile("a11", INSET_TOP_LEFT):          (0,3),
    Tile("a12", INSET_BOTTOM_RIGHT):      (1,4),
    Tile("a13", ROUND_INSIDE_BOTTOM):     (2,3),
    Tile("a14", INSET_BOTTOM_LEFT):       (3,4),
}

inside_corners_with_edges_plane = {
    Tile("b01", ROUND_INSIDE_LEFT):       (0,2),
    Tile("b02", BLANK):                   (1,1),
    Tile("b03", ROUND_INSIDE_TOP):        (2,0),
    Tile("b04", BLANK):                   (1,3),
    Tile("b05", BLANK):                   (2,2),
    Tile("b06", BLANK):                   (3,1),
    Tile("b07", BLANK):                   (2,4),
    Tile("b08", BLANK):                   (3,3),
    Tile("b09", BLANK):                   (4,2),
    Tile("b10", ROUND_INSIDE_BOTTOM):     (3,5),
    Tile("b11", BLANK):                   (4,4),
    Tile("b12", ROUND_INSIDE_RIGHT):      (5,3),
}

outside_corners_with_edges = {
    Tile("c01", ROUND_OUTSIDE_LEFT):     (0,2),
    Tile("c02", INSET_TOP_LEFT):         (1,1),
    Tile("c03", ROUND_OUTSIDE_TOP):      (2,0),
    Tile("c04", INSET_BOTTOM_LEFT):      (1,3),
    Tile("c05", BLANK):                  (2,2),
    Tile("c06", INSET_TOP_RIGHT):        (3,1),
    Tile("c07", INSET_BOTTOM_LEFT):      (2,4),
    Tile("c08", BLANK):                  (3,3),
    Tile("c09", INSET_TOP_RIGHT):        (4,2),
    Tile("c10", ROUND_OUTSIDE_BOTTOM):   (3,5),
    Tile("c11", INSET_BOTTOM_RIGHT):     (4,4),
    Tile("c12", ROUND_OUTSIDE_RIGHT):    (5,3),
    }

#----------------------------------------------------------------------
# Utils
#----------------------------------------------------------------------
def select_tile(img, w, h, dx, dy):
    selection = [0+dx, h/2+dy, w/2+dx, dy, w+dx, h/2+dy, w/2+dx, h+dy]
    pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)
    return selection
def calc_tile_pos(tile_set, tile, w, h, off_x=0, off_y=0):
    dx = (tile_set[tile][0]) * w/2 + off_x
    dy = (tile_set[tile][1]) * h/2 + off_y
    return (dx, dy)
def select_tile_inset(img, tile_set, w, h, tile, inset_size):
    pos = calc_tile_pos(tile_set, tile, w, h)
    (dx, dy) = (pos[0], pos[1])
    selection = select_tile(img, w, h, dx, dy)
    d=math.sqrt(w/2.0*w/2.0+h/2.0*h/2.0)
    def to_sel_index(diamond_index):
      return (2*diamond_index, 1+2*diamond_index)
    def get_sel_value(diamond_index):
      return (selection[2*diamond_index], selection[1+2*diamond_index])
    def add_to_sel(diamond_index, (dx, dy)):
      selection[2*diamond_index] = selection[2*diamond_index] + dx
      selection[1+2*diamond_index] = selection[1+2*diamond_index] + dy
    def cut_ellipse_outside(diamond_index,pct_w=1,pct_h=1, op=gimpenums.CHANNEL_OP_SUBTRACT, off_x=0, off_y=0):
      (x_index,y_index) = to_sel_index(diamond_index)
      ellipsis_w = 2*(d - inset_size) * pct_w
      ellipsis_h = 2*(d - inset_size) * pct_h
      (x,y) = (selection[x_index]-ellipsis_w/2+off_x, selection[y_index]-ellipsis_h/2+off_y)
      pdb.gimp_image_select_ellipse(img, op, x, y, ellipsis_w, ellipsis_h)
    def cut_ellipse_inside(diamond_index,pct_w=1,pct_h=1, op=gimpenums.CHANNEL_OP_SUBTRACT, off_x=0, off_y=0):
      (x_index,y_index) = to_sel_index(diamond_index)
      ellipsis_w = 2*(inset_size) * pct_w
      ellipsis_h = 2*(inset_size) * pct_h
      (x,y) = (selection[x_index]-ellipsis_w/2+off_x, selection[y_index]-ellipsis_h/2+off_y)
      pdb.gimp_image_select_ellipse(img, op, x, y, ellipsis_w, ellipsis_h)      
    def cut_poly( vec1_index, vec2_index ):
      start1 = get_sel_value(vec1_index[0])
      end1   = get_sel_value(vec1_index[1])
      start2 = get_sel_value(vec2_index[0])
      end2   = get_sel_value(vec2_index[1])
      m      = inset_size/d
      (dx1, dy1) = (m*(end1[0]-start1[0]), m*(end1[1]-start1[1]))
      (dx2, dy2) = (m*(end2[0]-start2[0]), m*(end2[1]-start2[1]))
      add_to_sel(vec1_index[0], (dx1, dy1))
      add_to_sel(vec2_index[0], (dx2, dy2))
      pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)

    if tile.inset_type & ROUND_INSIDE_LEFT>0:    cut_ellipse_inside (0)
    if tile.inset_type & ROUND_INSIDE_RIGHT>0:   cut_ellipse_inside (2)
    if tile.inset_type & ROUND_INSIDE_TOP>0:     cut_ellipse_inside (1, 1.20, 0.65,  off_x=1, off_y=1)
    if tile.inset_type & ROUND_INSIDE_BOTTOM>0:  cut_ellipse_inside (3, 1.20, 0.65,  off_x=1, off_y=1)
    if tile.inset_type & ROUND_OUTSIDE_RIGHT>0:  cut_ellipse_outside(0, 1.42, 0.57,  op=gimpenums.CHANNEL_OP_INTERSECT, off_x=1, off_y=1)
    if tile.inset_type & ROUND_OUTSIDE_LEFT>0:   cut_ellipse_outside(2, 1.42, 0.565, op=gimpenums.CHANNEL_OP_INTERSECT, off_y=1)
    if tile.inset_type & ROUND_OUTSIDE_BOTTOM>0: cut_ellipse_outside(1, 1.51, 0.55,  op=gimpenums.CHANNEL_OP_INTERSECT, off_y=1)
    if tile.inset_type & ROUND_OUTSIDE_TOP>0:    cut_ellipse_outside(3, 1.51, 0.55,  op=gimpenums.CHANNEL_OP_INTERSECT)
    if tile.inset_type & INSET_TOP_LEFT>0:       cut_poly((0, 3), (1, 2))
    if tile.inset_type & INSET_TOP_RIGHT>0:      cut_poly((1, 0), (2, 3))
    if tile.inset_type & INSET_BOTTOM_LEFT>0:    cut_poly((0, 1), (3, 2))
    if tile.inset_type & INSET_BOTTOM_RIGHT>0:   cut_poly((3, 0), (2, 1))
        
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def iso_tiles(image, drawable, tileSize=128):
    w = tileSize
    h = tileSize/2
    img = gimp.Image(7*w,8*h,gimpenums.RGB)
    l = gimp.Layer(img, "Base", img.width,img.height,gimpenums.RGBA_IMAGE,100,
                   gimpenums.NORMAL_MODE)
    img.add_layer(l)

    inset_size = 41.0
    ts = inside_corners_with_edges 
    for tile in ts.keys():
        select_tile_inset(img, ts, w, h, tile, inset_size)
        pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)

    #pdb.gimp_selection_none(img)
    d = gimp.Display(img)

register(
  "python_iso_tiles",
  N_("Create Iso Tiles from pattern"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Isometric tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 128),
  ],
  [],
  iso_tiles,
  menu="<Image>/Filters/Enhance",
  domain=("resynthesizer", gimp.locale_directory)
  )

main()