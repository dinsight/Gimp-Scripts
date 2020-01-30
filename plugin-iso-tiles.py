#!/usr/bin/env python
from gimpfu import *
import gimpenums
import collections
import math

gettext.install("resynthesizer", gimp.locale_directory, unicode=True)
Tile = collections.namedtuple("Tile",["inset_type", "x_index", "y_index", "show"])
Settings = collections.namedtuple("Settings",["width", "height", "inset", "map_weight", "autism", "neighbourhood", "trys"])

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

ts_oc = { 
      "rol": Tile(ROUND_OUTSIDE_LEFT, 0,2, True),
      "rot": Tile(ROUND_OUTSIDE_TOP, 1,1, True),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 1,3, True),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 2,2, True),
    }
ts_side1 = { 
      "rol": Tile(ROUND_OUTSIDE_LEFT, 0,5, False),
      "itl": Tile(INSET_TOP_LEFT, 1,4, True),
      "rot": Tile(ROUND_OUTSIDE_TOP, 2,3, False),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 1,6, False),
      "ibr": Tile(INSET_BOTTOM_RIGHT, 2,5, True),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 3,4, False),
    }
ts_side2 = { 
      "rol": Tile(ROUND_OUTSIDE_LEFT, 0,7, False),
      "rot": Tile(ROUND_OUTSIDE_TOP, 1,6, False),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 2,9, False),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 3,8, False),
      "itr": Tile(INSET_TOP_RIGHT, 2,7, True),
      "ibl": Tile(INSET_BOTTOM_LEFT, 1,8, True),
    }

full_tile = { 
      "itl": Tile(INSET_TOP_LEFT, 0,0, False),
      "itr": Tile(INSET_TOP_RIGHT, 2,0, False),
      "ibl": Tile(INSET_BOTTOM_LEFT, 0,2, False),
      "ibr": Tile(INSET_BOTTOM_RIGHT, 2,2, False),
      "full": Tile(BLANK, 1,1, True),
      "rol": Tile(ROUND_OUTSIDE_LEFT, -1,1, False),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 3,1, False),
      "rot": Tile(ROUND_OUTSIDE_TOP, 1,-1, False),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 1,3, False),
    }

settings = None
#----------------------------------------------------------------------
# Utils
#----------------------------------------------------------------------
def get_settings(tileSize):
    w = tileSize
    h = tileSize/2
    settings = Settings(w, h, 41.0, 0.5, 0.12, 30, 200)
    return settings
def filter_tileset(tile_set, arr_names):
    res = []
    for key, value in tile_set.items():
      if key in arr_names:
        res.append(value)
    return res
def select_diamond_shape(img, w, h, dx, dy):
    selection = [0+dx, h/2+dy, w/2+dx, dy, w+dx, h/2+dy, w/2+dx, h+dy]
    pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)
    return selection
def select_tile(img, tile):
    w = settings.width
    h = settings.height
    inset_size = settings.inset
    (dx, dy) = (tile.x_index * w/2, tile.y_index * h/2)
    selection = select_diamond_shape(img, w, h, dx, dy)
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
    
def copy_tile(img, srcLayer, src_tile, destLayer, dest_tile):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  select_tile(img, src_tile)
  pdb.gimp_edit_copy(srcLayer)
  select_tile(img, dest_tile)
  fsel = pdb.gimp_edit_paste(destLayer, False)
  pdb.gimp_floating_sel_anchor(fsel)
  pdb.gimp_context_set_antialias(antialias)

def place_tiles(img, ts, layer):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  for tile in ts.values():
    if tile.show == True:
      select_tile(img, tile)
      pdb.gimp_edit_fill(layer, gimpenums.FOREGROUND_FILL)
  pdb.gimp_context_set_antialias(antialias)

def synth_tileset(img, layer, source, mask, arr_tiles=None):
  if arr_tiles is None:
    foreground = pdb.gimp_context_get_foreground()
    pdb.gimp_image_select_color(img, gimpenums.CHANNEL_OP_REPLACE, layer, foreground)
  else:
    sel_channels = []
    for item in arr_tiles:
      select_tile(img, item)
      sel_channels.append(pdb.gimp_selection_save(img))
    pdb.gimp_selection_clear(img)
    for s in sel_channels:
      pdb.gimp_image_select_item(img, gimpenums.CHANNEL_OP_ADD, s)

  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(True)
  pdb.gimp_selection_grow(img, 3)
  pdb.plug_in_resynthesizer(img, layer, 
                            int(True),
                            int(True),
                            1,
                            source.ID,
                            mask.ID,
                            layer.ID,
                            settings.map_weight,
                            settings.autism,
                            settings.neighbourhood,
                            settings.trys)
  pdb.gimp_context_set_antialias(antialias)                            
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------

def python_iso_select_tiles(image, drawable, x, y, tileSize=128):
    global settings 
    settings = get_settings(tileSize)
    select_tile(image, Tile(BLANK, x, y, True))

def iso_tiles(image, drawable, source, mask, tileSize=128):
    global settings
    settings = get_settings(tileSize)
    
    img = gimp.Image(8*settings.width,8*settings.height,gimpenums.RGB)
    oc_layer = gimp.Layer(img, "OutsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(oc_layer)

    #Outside Corners
    place_tiles(img, ts_oc, oc_layer)
    synth_tileset(img, oc_layer, source, mask)

    sides1_layer = gimp.Layer(img, "Sides1", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides1_layer)

    #Side1
    place_tiles(img, ts_side1, sides1_layer)
    copy_tile(img, oc_layer, ts_oc["rol"], sides1_layer, ts_side1["rol"])
    copy_tile(img, oc_layer, ts_oc["rot"], sides1_layer, ts_side1["rot"])
    copy_tile(img, oc_layer, ts_oc["rob"], sides1_layer, ts_side1["rob"])
    copy_tile(img, oc_layer, ts_oc["ror"], sides1_layer, ts_side1["ror"])
    synth_tileset(img, sides1_layer, source, mask, filter_tileset(ts_side1, ["itl", "ibr"]))

    sides2_layer = gimp.Layer(img, "Sides2", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides2_layer)

    #Side2
    place_tiles(img, ts_side2, sides2_layer)
    copy_tile(img, oc_layer, ts_oc["rol"], sides2_layer, ts_side2["rol"])
    copy_tile(img, oc_layer, ts_oc["rot"], sides2_layer, ts_side2["rot"])
    copy_tile(img, oc_layer, ts_oc["rob"], sides2_layer, ts_side2["rob"])
    copy_tile(img, oc_layer, ts_oc["ror"], sides2_layer, ts_side2["ror"])
    synth_tileset(img, sides2_layer, source, mask, filter_tileset(ts_side2, ["itr", "ibl"]))

    #Full tile
    full_tile_layer = gimp.Layer(img, "FullTile", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(full_tile_layer)
    place_tiles(img, full_tile, full_tile_layer)
    copy_tile(img, sides1_layer, ts_side1["itl"], full_tile_layer, full_tile["itl"])
    copy_tile(img, sides1_layer, ts_side1["ibr"], full_tile_layer, full_tile["ibr"])
    copy_tile(img, sides2_layer, ts_side2["itr"], full_tile_layer, full_tile["itr"])
    copy_tile(img, sides2_layer, ts_side2["ibl"], full_tile_layer, full_tile["ibl"])
    copy_tile(img, oc_layer, ts_oc["rol"], full_tile_layer, full_tile["rol"])
    copy_tile(img, oc_layer, ts_oc["ror"], full_tile_layer, full_tile["ror"])
    copy_tile(img, oc_layer, ts_oc["rot"], full_tile_layer, full_tile["rot"])
    copy_tile(img, oc_layer, ts_oc["rob"], full_tile_layer, full_tile["rob"])
    synth_tileset(img, full_tile_layer, source, mask, filter_tileset(full_tile, ["full"]))

    # Check tiling
    check_layer = gimp.Layer(img, "Check Tiling", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(check_layer)

    check_tiles = {
      "t5": Tile(BLANK, 1,2, True),
      "t6": Tile(BLANK, 2,1, True),
      "t1": Tile(BLANK, 2,3, True),
      "t3": Tile(BLANK, 3,2, True),
      "t2": Tile(BLANK, 3,4, True),
      "t4": Tile(BLANK, 4,3, True),
      "t7": Tile(BLANK, 3,0, True),
      "t8": Tile(BLANK, 4,1, True),
      "t9": Tile(BLANK, 5,2, True),
    }
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t1"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t2"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t3"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t4"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t5"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t6"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t7"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t8"])
    copy_tile(img, full_tile_layer, full_tile["full"], check_layer, check_tiles["t9"])

    d = gimp.Display(img)

register(
  "python_iso_tiles",
  N_("Create Iso Tiles from pattern"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Create Isometric tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_DRAWABLE, "source", "Source image", None),
    (PF_DRAWABLE, "mask", "Source mask", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 128),
  ],
  [],
  iso_tiles,
  menu="<Image>/Filters/Tiles",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "python_iso_select_tiles",
  N_("Select Iso Tiles at Index"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Select tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "x", "X Index", 0),
    (PF_INT, "y", "Y Index", 0),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 128),
  ],
  [],
  python_iso_select_tiles,
  menu="<Image>/Filters/Tiles",
  domain=("resynthesizer", gimp.locale_directory)
  )

main()
