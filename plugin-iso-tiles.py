#!/usr/bin/env python
from gimpfu import *
import gimpenums
import collections
import math
import re
import os

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

ts_inside = {
    "full1": Tile(BLANK, 1,1, False),
    "full2": Tile(BLANK, 2,2, False),
    "full3": Tile(BLANK, 3,3, False),
    "full4": Tile(BLANK, 4,4, False),
    "full5": Tile(BLANK, 5,5, False),
    "full6": Tile(BLANK, 1,5, False),
    "full7": Tile(BLANK, 2,4, False),
    "full8": Tile(BLANK, 4,2, False),
    "full9": Tile(BLANK, 5,1, False),
    "ibl1":  Tile(INSET_BOTTOM_LEFT, 0,2, False),
    "ibl2":  Tile(INSET_BOTTOM_LEFT, 4,6, False),
    "itr1":  Tile(INSET_TOP_RIGHT, 2,0, False),
    "itr2":  Tile(INSET_TOP_RIGHT, 6,4, False),
    "itl1":  Tile(INSET_TOP_LEFT, 0,4, False),
    "itl2":  Tile(INSET_TOP_LEFT, 4,0, False),
    "ibr1":  Tile(INSET_BOTTOM_RIGHT, 2,6, False),
    "ibr2":  Tile(INSET_BOTTOM_RIGHT, 6,2, False),

    "ril": Tile(ROUND_INSIDE_LEFT, 1,3, True),
    "rir": Tile(ROUND_INSIDE_RIGHT, 5,3, True),
    "rit": Tile(ROUND_INSIDE_TOP, 3,1, True),
    "rib": Tile(ROUND_INSIDE_BOTTOM, 3,5, True),
}

full_tile = { 
      "itl":  Tile(INSET_TOP_LEFT, 0,0, False),
      "itr":  Tile(INSET_TOP_RIGHT, 2,0, False),
      "ibl":  Tile(INSET_BOTTOM_LEFT, 0,2, False),
      "ibr":  Tile(INSET_BOTTOM_RIGHT, 2,2, False),
      "full": Tile(BLANK, 1,1, True),
      "rol":  Tile(ROUND_OUTSIDE_LEFT, -1,1, False),
      "ror":  Tile(ROUND_OUTSIDE_RIGHT, 3,1, False),
      "rot":  Tile(ROUND_OUTSIDE_TOP, 1,-1, False),
      "rob":  Tile(ROUND_OUTSIDE_BOTTOM, 1,3, False),
    }

check_tiles = {
      "rol1": Tile(ROUND_OUTSIDE_LEFT, 0,6, True),
      "rol2": Tile(ROUND_OUTSIDE_LEFT, 4,10, True),
      "rot1": Tile(ROUND_OUTSIDE_TOP, 3,3, True),
      "rot2": Tile(ROUND_OUTSIDE_TOP, 8,2, True),
      "ror1": Tile(ROUND_OUTSIDE_RIGHT, 11,5, True),
      "ror2": Tile(ROUND_OUTSIDE_RIGHT, 12,10, True),
      "rob1": Tile(ROUND_OUTSIDE_BOTTOM, 1,7, True),
      "rob2": Tile(ROUND_OUTSIDE_BOTTOM, 7,13, True),
      "rob3": Tile(ROUND_OUTSIDE_BOTTOM, 9,13, True),
      "rit1": Tile(ROUND_INSIDE_TOP, 5,5, True),
      "rib1": Tile(ROUND_INSIDE_BOTTOM, 2,6, True),
      "rib2": Tile(ROUND_INSIDE_BOTTOM, 8,12, True),
      "ril1": Tile(ROUND_INSIDE_LEFT, 5,9, True),
      "rir1": Tile(ROUND_INSIDE_RIGHT, 9,7, True),
      "itl1": Tile(INSET_TOP_LEFT, 1,5, True),
      "itl2": Tile(INSET_TOP_LEFT, 2,4, True),
      "itl3": Tile(INSET_TOP_LEFT, 6,4, True),
      "itl4": Tile(INSET_TOP_LEFT, 7,3, True),
      "itr1": Tile(INSET_TOP_RIGHT, 4,4, True),
      "itr2": Tile(INSET_TOP_RIGHT, 9,3, True),
      "itr3": Tile(INSET_TOP_RIGHT, 10,4, True),
      "itr4": Tile(INSET_TOP_RIGHT, 10,8, True),
      "itr5": Tile(INSET_TOP_RIGHT, 11,9, True),
      "ibl1": Tile(INSET_BOTTOM_LEFT, 3,7, True),
      "ibl2": Tile(INSET_BOTTOM_LEFT, 4,8, True),
      "ibl3": Tile(INSET_BOTTOM_LEFT, 5,11, True),
      "ibl4": Tile(INSET_BOTTOM_LEFT, 6,12, True),
      "ibr1": Tile(INSET_BOTTOM_RIGHT, 10,6, True),
      "ibr2": Tile(INSET_BOTTOM_RIGHT, 10,12, True),
      "ibr3": Tile(INSET_BOTTOM_RIGHT, 11,11, True),
      "full1":  Tile(BLANK, 3,5, True),
      "full2":  Tile(BLANK, 4,6, True),
      "full3":  Tile(BLANK, 5,7, True),
      "full4":  Tile(BLANK, 6,6, True),
      "full5":  Tile(BLANK, 7,5, True),
      "full6":  Tile(BLANK, 8,4, True),
      "full7":  Tile(BLANK, 6,8, True),
      "full8":  Tile(BLANK, 7,7, True),
      "full9":  Tile(BLANK, 8,6, True),
      "full10": Tile(BLANK, 9,5, True),
      "full11": Tile(BLANK, 6,10, True),
      "full12": Tile(BLANK, 7,9, True),
      "full13": Tile(BLANK, 8,8, True),
      "full14": Tile(BLANK, 7,11, True),
      "full15": Tile(BLANK, 8,10, True),
      "full16": Tile(BLANK, 9,9, True),
      "full17": Tile(BLANK, 9,11, True),
      "full18": Tile(BLANK, 10,10, True),
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

def copy_tiles_with_prefix(img, srcLayer, src_tile, destLayer, dest_tile, prefixes=[]):
  def remove_digits(name): 
    pattern = '[0-9]'
    return re.sub(pattern, '', name)
  for dest_key in dest_tile.keys():
    key = remove_digits(dest_key)
    if key in src_tile and key in prefixes:
      copy_tile(img, srcLayer, src_tile[key], destLayer, dest_tile[dest_key])

def place_tiles(img, ts, layer):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  for tile in ts.values():
    if tile.show == True:
      select_tile(img, tile)
      pdb.gimp_edit_fill(layer, gimpenums.FOREGROUND_FILL)
  pdb.gimp_context_set_antialias(antialias)

def synth_tileset(img, layer, source, mask, arr_tiles=None, surrounds=3):
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
  pdb.gimp_selection_grow(img, surrounds)
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
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def python_iso_export_transitions(image, output_path, tileSize=128, background=None):
    global settings 
    settings = get_settings(tileSize)
    def merge_layers(layer1, layer2):
      for L in image.layers: 
        if L == layer1 or L == layer2: 
          pdb.gimp_drawable_set_visible(L, True) 
        else:
          pdb.gimp_drawable_set_visible(L, False) 
      return pdb.gimp_image_merge_visible_layers(image, 0)
    def get_layer(name):
      for l in image.layers:
        if l.name.startswith(name):
          return l
      return None
    layer = get_layer("Check Tiling")
    image.active_layer = layer
    exp_list = { 
      "rol1", "ror1", "rot1", "rob1", "rit1", "rib1", 
      "ril1", "rir1", "itl1", "itr1", "ibl1", "ibr1", "full1"
    }
    for name in exp_list:
      bk_layer = None
      select_tile(image, Tile(BLANK, check_tiles[name].x_index, check_tiles[name].y_index, True))
      pdb.gimp_selection_grow(image, 1)
      pdb.gimp_edit_copy(layer)
      fsel = pdb.gimp_edit_paste(layer, False)
      new = pdb.gimp_floating_sel_to_layer(fsel)
      theNewLayer = image.active_layer

      if background is not None:
        select_tile(image, Tile(BLANK, check_tiles[name].x_index, check_tiles[name].y_index, True))
        pdb.gimp_selection_layer_alpha(background)
        pdb.gimp_edit_copy(background)
        fsel = pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_to_layer(fsel)
        bk_layer = image.active_layer
        
      if bk_layer is not None:
        theNewLayer = merge_layers(bk_layer, theNewLayer)
      
      fullpath = os.path.join(output_path, name) + ".png"
      pdb.gimp_file_save(image, theNewLayer, fullpath, name)
      image.remove_layer(theNewLayer)
      image.active_layer = layer

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def iso_tiles(image, drawable, source, mask, tileSize=128):
    global settings
    settings = get_settings(tileSize)
    
    img = gimp.Image(8*settings.width,8*settings.height,gimpenums.RGB)
    oc_layer = gimp.Layer(img, "OutsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(oc_layer)

    #----------------------------------------Outside Corners----------------------------------------
    place_tiles(img, ts_oc, oc_layer)
    synth_tileset(img, oc_layer, source, mask)

    sides1_layer = gimp.Layer(img, "Sides1", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides1_layer)

    #----------------------------------------Side1----------------------------------------
    place_tiles(img, ts_side1, sides1_layer)
    copy_tiles_with_prefix(img, oc_layer, ts_oc, sides1_layer, ts_side1, ["rol", "rot", "rob", "ror"])
    synth_tileset(img, sides1_layer, source, mask, filter_tileset(ts_side1, ["itl", "ibr"]), surrounds=1)

    sides2_layer = gimp.Layer(img, "Sides2", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides2_layer)

    #----------------------------------------Side2----------------------------------------
    place_tiles(img, ts_side2, sides2_layer)
    copy_tiles_with_prefix(img, oc_layer, ts_oc, sides2_layer, ts_side2, ["rol", "rot", "rob", "ror"])
    synth_tileset(img, sides2_layer, source, mask, filter_tileset(ts_side2, ["itr", "ibl"]), surrounds=1)

    #----------------------------------------Full tile----------------------------------------
    full_tile_layer = gimp.Layer(img, "FullTile", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(full_tile_layer)
    place_tiles(img, full_tile, full_tile_layer)
    
    copy_tiles_with_prefix(img, oc_layer, ts_oc, full_tile_layer, full_tile, ["rol", "rot", "rob", "ror"])
    copy_tiles_with_prefix(img, sides1_layer, ts_side1, full_tile_layer, full_tile, ["itl", "ibr" ])
    copy_tiles_with_prefix(img, sides2_layer, ts_side2, full_tile_layer, full_tile, ["itr", "ibl" ])
    synth_tileset(img, full_tile_layer, source, mask, filter_tileset(full_tile, ["full"]), surrounds=1)

    #----------------------------------------Inside Corners----------------------------------------
    ic_layer = gimp.Layer(img, "InsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(ic_layer)
    place_tiles(img, ts_inside, ic_layer)
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["itl", "ibr"])
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["itr", "ibl"])
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["full"])
    synth_tileset(img, ic_layer, source, mask, filter_tileset(ts_inside, ["ril", "rir", "rit", "rib"]), surrounds=1)

    #---------------------------------------- Check tiling ----------------------------------------
    check_layer = gimp.Layer(img, "Check Tiling", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(check_layer)

    copy_tiles_with_prefix(img, full_tile_layer, full_tile, check_layer, check_tiles, ["itl","itr","ibl","ibr","rol","ror","rot","rob","full"])
    copy_tiles_with_prefix(img, ic_layer, ts_inside, check_layer, check_tiles, ["ril","rir","rit","rib"])

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

register(
  "python_iso_export_transitions",
  N_("Export Tiles"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Export tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd()),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 128),
    (PF_DRAWABLE, "background", _("Tile background"), None),
  ],
  [],
  python_iso_export_transitions,
  menu="<Image>/Filters/Tiles",
  domain=("resynthesizer", gimp.locale_directory)
  )

main()
