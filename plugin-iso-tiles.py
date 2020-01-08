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
ROUND_OUTSIDE_TOP     = int('0000000000010000',2)
ROUND_OUTSIDE_BOTTOM  = int('0000000000100000',2)
ROUND_OUTSIDE_LEFT    = int('0000000001000000',2)
ROUND_OUTSIDE_RIGHT   = int('0000000010000000',2)
INSET_TOP_LEFT        = int('0000000100000000',2)
INSET_TOP_RIGHT       = int('0000001000000000',2)
INSET_BOTTOM_LEFT     = int('0000010000000000',2)
INSET_BOTTOM_RIGHT    = int('0000100000000000',2)

tiles = {
    # Tile("a0", ROUND_INSIDE_LEFT):     (0,2),
    # Tile("a1", BLANK):                 (1,1),
    # Tile("a2", ROUND_INSIDE_TOP):      (2,0),
    # Tile("b0", BLANK):                 (1,3),
    # Tile("b1", BLANK):                 (2,2),
    # Tile("b2", BLANK):                 (3,1),
    # Tile("c0", BLANK):                 (2,4),
    # Tile("c1", BLANK):                 (3,3),
    # Tile("c2", BLANK):                 (4,2),
    # Tile("d0", ROUND_INSIDE_BOTTOM):   (3,5),
    # Tile("d1", BLANK):                 (4,4),
    # Tile("d2", ROUND_INSIDE_RIGHT):    (5,3),

    Tile("a0", ROUND_OUTSIDE_RIGHT):    (0,2),
    Tile("a1", INSET_TOP_LEFT):         (1,1),
    Tile("a2", ROUND_OUTSIDE_BOTTOM):   (2,0),
    Tile("b0", BLANK):                  (1,3),
    Tile("b1", BLANK):                  (2,2),
    Tile("b2", BLANK):                  (3,1),
    Tile("c0", BLANK):                  (2,4),
    Tile("c1", BLANK):                  (3,3),
    Tile("c2", BLANK):                  (4,2),
    Tile("d0", ROUND_OUTSIDE_TOP):      (3,5),
    Tile("d1", BLANK):                  (4,4),
    Tile("d2", ROUND_OUTSIDE_LEFT):     (5,3),
    }

#----------------------------------------------------------------------
# Utils
#----------------------------------------------------------------------
def select_tile(img, w, h, dx, dy):
    selection = [0+dx, h/2+dy, w/2+dx, dy, w+dx, h/2+dy, w/2+dx, h+dy]
    pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)
    return selection
def select_tile_inset(img, w, h, tile, inset_size):
    dx = (tiles[tile][0]) * w/2
    dy = (tiles[tile][1]) * h/2
    selection = select_tile(img, w, h, dx, dy)
    d=math.sqrt(w/2.0*w/2.0+h/2.0*h/2.0)
    def cut_ellipse(x_index,y_index,pct_w=1,pct_h=1, op=gimpenums.CHANNEL_OP_SUBTRACT):
      ellipsis_w = 2*(d - inset_size) * pct_w
      ellipsis_h = 2*(d - inset_size) * pct_h
      (x,y) = (selection[x_index]-ellipsis_w/2, selection[y_index]-ellipsis_h/2)
      pdb.gimp_image_select_ellipse(img, op, x, y, ellipsis_w, ellipsis_h)
    def calc_proportional_point(node_end_index, node_start_index):
      f = inset_size/d
      node_start = (0+2*node_start_index, 1+2*node_start_index)
      node_end   = (0+2*node_end_index, 1+2*node_end_index)
      return (f*(node_end[0]-node_start[0]), f*(node_end[1]-node_start[1]))
    def cut_poly(node1_end_index, node1_start_index, node2_end_index, node2_start_index):
      pt1 = calc_proportional_point(node1_end_index, node1_start_index)
      pt2 = calc_proportional_point(node2_end_index, node2_start_index)
      selection[2*node1_end_index]   = pt1[0]
      selection[1+2*node1_end_index] = pt1[1]
      selection[2*node2_end_index]   = pt2[0]
      selection[1+2*node2_end_index] = pt2[1]
      pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)

    if tile.inset_type & ROUND_INSIDE_LEFT>0:    cut_ellipse(0, 1)
    if tile.inset_type & ROUND_INSIDE_RIGHT>0:   cut_ellipse(4, 5)
    if tile.inset_type & ROUND_INSIDE_TOP>0:     cut_ellipse(2, 3, 1, 0.5)
    if tile.inset_type & ROUND_INSIDE_BOTTOM>0:  cut_ellipse(6, 7, 1, 0.5)
    if tile.inset_type & ROUND_OUTSIDE_LEFT>0:   cut_ellipse(0, 1, op=gimpenums.CHANNEL_OP_INTERSECT)
    if tile.inset_type & ROUND_OUTSIDE_RIGHT>0:  cut_ellipse(4, 5, op=gimpenums.CHANNEL_OP_INTERSECT)
    if tile.inset_type & ROUND_OUTSIDE_TOP>0:    cut_ellipse(2, 3, 1, 0.5, op=gimpenums.CHANNEL_OP_INTERSECT)
    if tile.inset_type & ROUND_OUTSIDE_BOTTOM>0: cut_ellipse(6, 7, 1, 0.5, op=gimpenums.CHANNEL_OP_INTERSECT)
    if tile.inset_type & INSET_TOP_LEFT>0:       cut_poly(3, 0, 2, 1)
    if tile.inset_type & INSET_TOP_RIGHT>0:      cut_poly(0, 1, 3, 2)
    if tile.inset_type & INSET_BOTTOM_LEFT>0:    cut_poly(1, 0, 2, 3)
    if tile.inset_type & INSET_BOTTOM_RIGHT>0:   cut_poly(0, 3, 1, 2)
        
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def iso_tiles(image, drawable, tileSize=128):
    w = tileSize
    h = tileSize/2
    img = gimp.Image(4*w,4*h,gimpenums.RGB)
    l = gimp.Layer(img, "Base", img.width,img.height,gimpenums.RGBA_IMAGE,100,
                   gimpenums.NORMAL_MODE)
    img.add_layer(l)

    inset_size = 25
    for tile in tiles.keys():
        select_tile_inset(img, w, h, tile, inset_size)
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
