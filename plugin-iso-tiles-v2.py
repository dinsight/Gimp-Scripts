#!/usr/bin/env python
from gimpfu import *
import gimpenums
import collections
import math
import re
import os

gettext.install("resynthesizer", gimp.locale_directory, unicode=True)
Tile = collections.namedtuple("Tile",["inset_type", "x_index", "y_index", "show"])
Settings = collections.namedtuple("Settings",["width", "inset", "map_weight", "autism", "neighbourhood", "trys"])

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
      "rol": Tile(ROUND_OUTSIDE_LEFT, 0,1, True),
      "rot": Tile(ROUND_OUTSIDE_TOP, 0,0, True),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 1,1, True),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 1,0, True),
    }

full_tile = { 
      "itl":  Tile(INSET_TOP_LEFT, 0,1, False),
      "itr":  Tile(INSET_TOP_RIGHT, 1,0, False),
      "ibl":  Tile(INSET_BOTTOM_LEFT, 1,2, False),
      "ibr":  Tile(INSET_BOTTOM_RIGHT, 2,1, False),
      "full": Tile(BLANK, 1,1, True),
      "rol":  Tile(ROUND_OUTSIDE_LEFT, 0,2, False),
      "ror":  Tile(ROUND_OUTSIDE_RIGHT, 2,0, False),
      "rot":  Tile(ROUND_OUTSIDE_TOP, 0,0, False),
      "rob":  Tile(ROUND_OUTSIDE_BOTTOM, 2,2, False),
    }

ts_side1 = {
    "rot": Tile(ROUND_OUTSIDE_TOP, 0,0, False),
    "ror": Tile(ROUND_OUTSIDE_RIGHT, 1,0, False),  
    "itl": Tile(INSET_TOP_LEFT, 0,1, True),
    "ibr": Tile(INSET_BOTTOM_RIGHT, 1,1, True),
    "rol": Tile(ROUND_OUTSIDE_LEFT, 0,2, False),
    "rob": Tile(ROUND_OUTSIDE_BOTTOM, 1,2, False),
}

ts_side2 = { 
      "rol": Tile(ROUND_OUTSIDE_LEFT, 0,1, False),
      "rot": Tile(ROUND_OUTSIDE_TOP, 0,0, False),
      "rob": Tile(ROUND_OUTSIDE_BOTTOM, 2,1, False),
      "ror": Tile(ROUND_OUTSIDE_RIGHT, 2,0, False),
      "itr": Tile(INSET_TOP_RIGHT, 1,0, True),
      "ibl": Tile(INSET_BOTTOM_LEFT, 1,1, True),
    }

ts_inside = {
    "full1": Tile(BLANK, 2,0, False),
    "full2": Tile(BLANK, 2,1, False),
    "full3": Tile(BLANK, 2,2, False),
    "full4": Tile(BLANK, 2,3, False),
    "full5": Tile(BLANK, 2,4, False),
    "full6": Tile(BLANK, 0,2, False),
    "full7": Tile(BLANK, 1,2, False),
    "full8": Tile(BLANK, 3,2, False),
    "full9": Tile(BLANK, 4,2, False),

    "itl1":  Tile(INSET_TOP_LEFT, 1,0, False),
    "itl2":  Tile(INSET_TOP_LEFT, 1,4, False),
    "ibr1":  Tile(INSET_BOTTOM_RIGHT, 3,0, False),
    "ibr2":  Tile(INSET_BOTTOM_RIGHT, 3,4, False),
    "ibl1":  Tile(INSET_BOTTOM_LEFT, 0,3, False),
    "ibl2":  Tile(INSET_BOTTOM_LEFT, 4,3, False),
    "itr1":  Tile(INSET_TOP_RIGHT, 0,1, False),
    "itr2":  Tile(INSET_TOP_RIGHT, 4,1, False),

    "ril": Tile(ROUND_INSIDE_LEFT, 1,3, True),
    "rir": Tile(ROUND_INSIDE_RIGHT, 3,1, True),
    "rit": Tile(ROUND_INSIDE_TOP, 1,1, True),
    "rib": Tile(ROUND_INSIDE_BOTTOM, 3,3, True),
}

check_tiles = {
  "full1": Tile(BLANK, 1,5, True),
  "full2": Tile(BLANK, 1,6, True),

  "full3": Tile(BLANK, 2,1, True),
  "full4": Tile(BLANK, 2,2, True),
  "full5": Tile(BLANK, 2,3, True),
  "full6": Tile(BLANK, 2,4, True),
  "full7": Tile(BLANK, 2,5, True),
  "full8": Tile(BLANK, 2,6, True),
  "full9": Tile(BLANK, 2,7, True),
  "full10": Tile(BLANK, 3,3, True),
  "full11": Tile(BLANK, 3,4, True),
  "full12": Tile(BLANK, 3,5, True),
  "full13": Tile(BLANK, 3,6, True),
  "full14": Tile(BLANK, 3,7, True),
  "full15": Tile(BLANK, 4,3, True),
  "full16": Tile(BLANK, 4,4, True),
  "full17": Tile(BLANK, 5,3, True),
  "full18": Tile(BLANK, 5,4, True),

  "itl1":  Tile(INSET_TOP_LEFT, 1,2, False),
  "itl2":  Tile(INSET_TOP_LEFT, 1,3, False),
  "itl3":  Tile(INSET_TOP_LEFT, 0,5, False),
  "itl4":  Tile(INSET_TOP_LEFT, 0,6, False),
  "itr1":  Tile(INSET_TOP_RIGHT, 1,0, False),
  "itr2":  Tile(INSET_TOP_RIGHT, 2,0, False),
  "itr3":  Tile(INSET_TOP_RIGHT, 4,2, False),
  "itr4":  Tile(INSET_TOP_RIGHT, 5,2, False),
  "ibr1":  Tile(INSET_BOTTOM_RIGHT, 3,1, False),
  "ibr2":  Tile(INSET_BOTTOM_RIGHT, 6,3, False),
  "ibr3":  Tile(INSET_BOTTOM_RIGHT, 6,4, False),
  "ibr4":  Tile(INSET_BOTTOM_RIGHT, 4,6, False),
  "ibr5":  Tile(INSET_BOTTOM_RIGHT, 4,7, False),
  "ibl1":  Tile(INSET_BOTTOM_LEFT, 5,5, False),
  "ibl2":  Tile(INSET_BOTTOM_LEFT, 2,8, False),
  "ibl3":  Tile(INSET_BOTTOM_LEFT, 3,8, False),

  "rot1": Tile(ROUND_OUTSIDE_TOP, 0,0, True),
  "rot2": Tile(ROUND_OUTSIDE_TOP, 0,4, True),
  "ror1": Tile(ROUND_OUTSIDE_RIGHT, 3,0, True),
  "ror2": Tile(ROUND_OUTSIDE_RIGHT, 6,2, True),
  "rob1": Tile(ROUND_OUTSIDE_BOTTOM, 6,5, True),
  "rob2": Tile(ROUND_OUTSIDE_BOTTOM, 4,8, True),
  "rol1": Tile(ROUND_OUTSIDE_LEFT, 0,1, True),
  "rol2": Tile(ROUND_OUTSIDE_LEFT, 0,7, True),
  "rol3": Tile(ROUND_OUTSIDE_LEFT, 1,8, True),

  "rit1": Tile(ROUND_INSIDE_TOP, 1,4, True),
  "rib1": Tile(ROUND_INSIDE_BOTTOM, 4,5, True),
  "ril1": Tile(ROUND_INSIDE_LEFT, 1,1, True),
  "ril2": Tile(ROUND_INSIDE_LEFT, 1,7, True),
  "rir1": Tile(ROUND_INSIDE_RIGHT, 3,2, True),
}
settings = None
#----------------------------------------------------------------------
# Utils
#----------------------------------------------------------------------
def get_settings(tileSize):
    w = tileSize
    settings = Settings(w, 41.0, 0.5, 0.12, 30, 200)
    return settings
def to_iso_tile(img, layer, grow=0):
  item = pdb.gimp_item_transform_rotate(layer, math.pi/4, True, 0, 0)
  dw = settings.width * 2
  dh = settings.width
  return pdb.gimp_item_transform_scale(item, 0, 0, dw+2*grow, dh+2*grow)
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
def select_tile(img, tile, select_full=False):
    h = w = settings.width
    inset_size = settings.inset
    (dx, dy) = (tile.x_index * w, tile.y_index * h)
    def select_circle(cx,cy,cr, op=gimpenums.CHANNEL_OP_REPLACE):
      (x,y) = (cx-cr, cy-cr)
      pdb.gimp_image_select_ellipse(img, op, x, y, 2*cr ,2*cr )

    selection = pdb.gimp_image_select_rectangle (img, gimpenums.CHANNEL_OP_REPLACE, dx, dy, w ,w)
    if not select_full:
      if tile.inset_type & ROUND_OUTSIDE_LEFT>0:    select_circle(dx+w, dy, inset_size, gimpenums.CHANNEL_OP_INTERSECT)
      if tile.inset_type & ROUND_OUTSIDE_RIGHT>0:   select_circle(dx, dy+h, inset_size, gimpenums.CHANNEL_OP_INTERSECT)
      if tile.inset_type & ROUND_OUTSIDE_BOTTOM>0:  select_circle(dx, dy, inset_size, gimpenums.CHANNEL_OP_INTERSECT)
      if tile.inset_type & ROUND_OUTSIDE_TOP>0:     select_circle(dx+w, dy+h, inset_size, gimpenums.CHANNEL_OP_INTERSECT)
      if tile.inset_type & ROUND_INSIDE_TOP>0:      select_circle(dx, dy, w-inset_size, gimpenums.CHANNEL_OP_SUBTRACT)
      if tile.inset_type & ROUND_INSIDE_RIGHT>0:    select_circle(dx+w, dy, w-inset_size, gimpenums.CHANNEL_OP_SUBTRACT)
      if tile.inset_type & ROUND_INSIDE_BOTTOM>0:   select_circle(dx+w, dy+h, w-inset_size, gimpenums.CHANNEL_OP_SUBTRACT)
      if tile.inset_type & ROUND_INSIDE_LEFT>0:     select_circle(dx, dy+h, w-inset_size, gimpenums.CHANNEL_OP_SUBTRACT)
      if tile.inset_type & INSET_TOP_LEFT>0:        pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_SUBTRACT, dx, dy, w-inset_size , h )
      if tile.inset_type & INSET_TOP_RIGHT>0:       pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_SUBTRACT, dx, dy, w, h-inset_size )
      if tile.inset_type & INSET_BOTTOM_RIGHT>0:    pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_SUBTRACT, dx+inset_size, dy, w-inset_size, h )
      if tile.inset_type & INSET_BOTTOM_LEFT>0:     pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_SUBTRACT, dx, dy+inset_size, w, h-inset_size )
        

def copy_tile(img, srcLayer, src_tile, destLayer, dest_tile, to_iso=False):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  
  if to_iso:
    w = settings.width
    (dx, dy) = (dest_tile.x_index , dest_tile.y_index )
    select_tile(img, src_tile, True)
    grow = 1
    pdb.gimp_selection_grow(img, grow)
    pdb.gimp_edit_copy(srcLayer)
    select_tile(img, dest_tile, True)
    pdb.gimp_selection_grow(img, grow)
    fsel = pdb.gimp_edit_paste(destLayer, False)
    fsel = to_iso_tile(img, fsel, grow)
    isox = (dx - dy) *w + img.width/2.0 + grow
    isoy = (dx + dy) *w/2.0 + grow
    pdb.gimp_message('dx={}, dy={}, isox={}, isoy={}'.format(dx, dy, isox, -isoy))
    pdb.gimp_layer_translate(fsel, isox, isoy)
    pdb.gimp_floating_sel_anchor(fsel)
  else:
    select_tile(img, src_tile)
    pdb.gimp_edit_copy(srcLayer)
    select_tile(img, dest_tile)
    fsel = pdb.gimp_edit_paste(destLayer, False)
    pdb.gimp_floating_sel_anchor(fsel)
  
  pdb.gimp_context_set_antialias(antialias)

def copy_tiles_with_prefix(img, srcLayer, src_tile, destLayer, dest_tile, prefixes=[], to_iso=False):
  def remove_digits(name): 
    pattern = '[0-9]'
    return re.sub(pattern, '', name)
  for dest_key in dest_tile.keys():
    key = remove_digits(dest_key)
    if key in src_tile and key in prefixes:
      copy_tile(img, srcLayer, src_tile[key], destLayer, dest_tile[dest_key], to_iso)

def place_tiles(img, ts, layer, showall=False, grow=0):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  for tile in ts.values():
    if tile.show == True or showall==True:
      select_tile(img, tile)
      if grow > 0 : pdb.gimp_selection_grow(img, grow)
      pdb.gimp_edit_fill(layer, gimpenums.FOREGROUND_FILL)
  pdb.gimp_context_set_antialias(antialias)

def synth_tileset(img, layer, source, mask, arr_tiles=None, surrounds=3):
  if arr_tiles is None:
    foreground = pdb.gimp_context_get_foreground()
    pdb.gimp_image_select_color(img, gimpenums.CHANNEL_OP_REPLACE, layer, foreground)
  else:
    sel_channels = []
    for item in arr_tiles:
      select_tile(img, item, True)
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
    w = settings.width
    h = w/2
    #select_tile(image, Tile(BLANK, x, y, True))
    (dx, dy) = (dx, dy) = (x * w/2, y * h/2)
    select_diamond_shape(image, w, h, dx, dy)
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
      trns = to_iso_tile(image, fsel)
      new = pdb.gimp_floating_sel_to_layer(trns)
      theNewLayer = image.active_layer

      # if background is not None:
      #   select_tile(image, Tile(BLANK, check_tiles[name].x_index, check_tiles[name].y_index, True))
      #   pdb.gimp_selection_layer_alpha(background)
      #   pdb.gimp_edit_copy(background)
      #   fsel = pdb.gimp_edit_paste(layer, True)
      #   pdb.gimp_floating_sel_to_layer(fsel)
      #   bk_layer = image.active_layer
        
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
    
    img = gimp.Image(8*settings.width*2,9*settings.width,gimpenums.RGB)
    #----------------------------------------Outside Corners----------------------------------------
    oc_layer = gimp.Layer(img, "OutsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(oc_layer)
    place_tiles(img, ts_oc, oc_layer)
    synth_tileset(img, oc_layer, source, mask, surrounds=4)
    #----------------------------------------Side1----------------------------------------
    sides1_layer = gimp.Layer(img, "Sides1", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides1_layer)
    copy_tiles_with_prefix(img, oc_layer, ts_oc, sides1_layer, ts_side1, ["rol", "rot", "rob", "ror"])
    place_tiles(img, ts_side1, sides1_layer)
    synth_tileset(img, sides1_layer, source, mask, filter_tileset(ts_side1, ["itl", "ibr"]), surrounds=1)
    #----------------------------------------Side2----------------------------------------
    sides2_layer = gimp.Layer(img, "Sides2", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides2_layer)
    copy_tiles_with_prefix(img, oc_layer, ts_oc, sides2_layer, ts_side2, ["rol", "rot", "rob", "ror"])
    place_tiles(img, ts_side2, sides2_layer)
    synth_tileset(img, sides2_layer, source, mask, filter_tileset(ts_side2, ["itr", "ibl"]), surrounds=1)

    #----------------------------------------Full tile----------------------------------------
    full_tile_layer = gimp.Layer(img, "FullTile", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(full_tile_layer)
    copy_tiles_with_prefix(img, oc_layer, ts_oc, full_tile_layer, full_tile, ["rol", "rot", "rob", "ror"])
    copy_tiles_with_prefix(img, sides1_layer, ts_side1, full_tile_layer, full_tile, ["itl", "ibr" ])
    copy_tiles_with_prefix(img, sides2_layer, ts_side2, full_tile_layer, full_tile, ["itr", "ibl" ])
    place_tiles(img, full_tile, full_tile_layer, grow=0)
    synth_tileset(img, full_tile_layer, source, mask, filter_tileset(full_tile, ["full"]), surrounds=0)
    
    # #----------------------------------------Inside Corners----------------------------------------
    ic_layer = gimp.Layer(img, "InsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(ic_layer)
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["itl", "ibr"])
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["itr", "ibl"])
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, ic_layer, ts_inside, ["full"])
    place_tiles(img, ts_inside, ic_layer)
    synth_tileset(img, ic_layer, source, mask, filter_tileset(ts_inside, ["ril", "rir", "rit", "rib"]), surrounds=1)

    #---------------------------------------- Check tiling ----------------------------------------
    check_layer = gimp.Layer(img, "Check Tiling", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(check_layer)
    copy_tiles_with_prefix(img, full_tile_layer, full_tile, check_layer, check_tiles, ["itl","itr","ibl","ibr","rol","ror","rot","rob","full"], True)
    copy_tiles_with_prefix(img, ic_layer, ts_inside, check_layer, check_tiles, ["ril","rir","rit","rib"], True)
    # place_tiles(img, check_tiles, check_layer, True)
    
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
