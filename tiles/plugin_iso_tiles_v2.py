#!/usr/bin/env python
from gimpfu import *
import gimpenums
import collections
import math
import re
import os

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)
Settings = collections.namedtuple("Settings",["width", "inset"])
Tile = collections.namedtuple("Tile",["inset_type", "x_index", "y_index", "show"])

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

#----------------------------------------------------------------------
# Globals
#----------------------------------------------------------------------

settings = None
#----------------------------------------------------------------------
# Utils
#----------------------------------------------------------------------
def select_diamond_shape(img, w, h, dx, dy):
    selection = [0+dx, h/2+dy, w/2+dx, dy, w+dx, h/2+dy, w/2+dx, h+dy]
    pdb.gimp_image_select_polygon(img, gimpenums.CHANNEL_OP_REPLACE,len(selection),selection)
    return selection

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def to_iso_tile(img, layer, grow=0):
  #pdb.gimp_context_set_interpolation(gimpenums.INTERPOLATION_NONE)
  item = pdb.gimp_item_transform_rotate(layer, math.pi/4, True, 0, 0)
  dw = settings.width * 2
  dh = settings.width
  return pdb.gimp_item_transform_scale(item, 0, 0, dw+2*grow, dh+2*grow)

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def merge_layers(image, layer1, layer2):
      for L in image.layers: 
        if L == layer1 or L == layer2: 
          pdb.gimp_drawable_set_visible(L, True) 
        else:
          pdb.gimp_drawable_set_visible(L, False) 
      return pdb.gimp_image_merge_visible_layers(image, 0)
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def get_layer(image, name):
      for l in image.layers:
        if l.name.startswith(name):
          return l
      return None
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def select_tile(img, tile, select_full=False, sel_type=gimpenums.CHANNEL_OP_REPLACE):
    h = w = settings.width
    inset_size = settings.inset
    (dx, dy) = (tile.x_index * w, tile.y_index * h)
    def select_circle(cx,cy,cr, op=sel_type):
      (x,y) = (cx-cr, cy-cr)
      pdb.gimp_image_select_ellipse(img, op, x, y, 2*cr ,2*cr )

    selection = pdb.gimp_image_select_rectangle (img, sel_type, dx, dy, w ,w)
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

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def place_tiles(img, ts, layer, showall=False, grow=0):
  antialias = pdb.gimp_context_get_antialias()
  pdb.gimp_context_set_antialias(False)
  for tile in ts.values():
    if tile.show == True or showall==True:
      select_tile(img, tile)
      if grow > 0 : pdb.gimp_selection_grow(img, grow)
      if grow < 0 : pdb.gimp_selection_shrink(img, -grow)
      pdb.gimp_edit_fill(layer, gimpenums.FOREGROUND_FILL)
  pdb.gimp_context_set_antialias(antialias)

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def copy_tile(img, source_tile, dest_tile, source_layer, dest_layer, select_full=False):
  antialias = pdb.gimp_context_get_antialias()
  select_tile(img, source_tile, select_full=select_full) 
  pdb.gimp_edit_copy(source_layer)
  select_tile(img, dest_tile, select_full=select_full) 
  fsel = pdb.gimp_edit_paste(dest_layer, False)
  pdb.gimp_floating_sel_anchor(fsel)
  pdb.gimp_context_set_antialias(False)
  pdb.gimp_context_set_antialias(antialias)

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def make_transition_layer(image, tile, mask, background, tileSize, mask_pos_x, mask_pos_y, name, pad=1):
  bk = pdb.gimp_layer_new_from_drawable(background, image)
  transition = pdb.gimp_layer_new_from_drawable(tile, image)
  transition.name = name
  image.add_layer(bk)
  image.add_layer(transition)
      
  do_select_tile(mask.image, mask, mask_pos_x, mask_pos_y, tileSize)
  pdb.gimp_edit_copy(mask)
  theMask = pdb.gimp_layer_create_mask(transition, gimpenums.ADD_BLACK_MASK)
  pdb.gimp_layer_add_mask(transition, theMask)
  fsel = pdb.gimp_edit_paste(theMask, False)

  s = select_diamond_shape(image, tileSize * 2, tileSize, 0, 0)
  fsel = pdb.gimp_item_transform_scale(fsel, s[0]-pad, s[3]-pad, s[4]+pad, s[7]+pad)

  pdb.gimp_floating_sel_anchor(fsel)
  merged_layer = merge_layers(image, transition, bk)
  merged_layer.name = name
  return merged_layer
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_select_tile(image, drawable, x, y, tileSize=64, select_diamond=True ):
    w = tileSize
    h = tileSize
    grow = 0
    (dx, dy) = (x * w, y * h)

    if select_diamond:
      isox = (x - y) * w  + image.width/2.0 + grow
      isoy = (x + y) * h / 2 + grow
      return select_diamond_shape(image, w * 2, h, isox, isoy)
    return  pdb.gimp_image_select_rectangle (image, gimpenums.CHANNEL_OP_REPLACE, dx, dy, w ,w)
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_iso_tiles(image, drawable, source_layer, tileSize=64):
    global settings
    settings =  Settings(tileSize, 41.0)
    
    img = gimp.Image(settings.width*2,settings.width,gimpenums.RGB)
    orig = gimp.Layer(img, "Orig", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(orig)

    pdb.gimp_edit_copy(source_layer)
    fsel = pdb.gimp_edit_paste(orig, False)
    pdb.gimp_floating_sel_anchor(fsel)
    pdb.gimp_drawable_offset(orig, True, gimpenums.OFFSET_WRAP_AROUND, img.width/2,img.height/2)
    fsel = pdb.gimp_edit_paste(orig, False)
    pdb.gimp_floating_sel_anchor(fsel)
    
    #there is a bug in gimp_drawable_offset - if one of the offsets is zero, the function does nothing
    #we add 1 on the x and y then we substract it to simulate (offset_x = 0 , offset_y=img.height/2)
    pdb.gimp_drawable_offset(orig, True, gimpenums.OFFSET_WRAP_AROUND, 1,img.height/2+1)
    pdb.gimp_drawable_offset(orig, True, gimpenums.OFFSET_WRAP_AROUND, -1,-1)

    pdb.gimp_edit_copy(source_layer)
    fsel = pdb.gimp_edit_paste(orig, True)
    pdb.gimp_floating_sel_to_layer(fsel)
    tile_layer = img.active_layer
    tile_layer.name = "tile"
    img.lower_layer(tile_layer)

    select_diamond_shape(img, tileSize * 2, tileSize, 0, 0)
    pdb.gimp_selection_invert(img)
    img.active_layer = orig
    pdb.gimp_edit_clear(orig)
    pdb.gimp_selection_invert(img)

    merge_layers(img, orig, tile_layer)
    gimp.Display(img)

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_create_corners(image, drawable, tileSize=64):
    global settings
    settings =  Settings(tileSize, 41.0)
    
    img = gimp.Image(settings.width*5,settings.width*5,gimpenums.RGB)
    orig = gimp.Layer(img, "OutsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(orig)
    #save alias settings
    antialias = pdb.gimp_context_get_antialias()
    pdb.gimp_context_set_antialias(False)
    #fill out the tiles
    select_tile(img, Tile(ROUND_OUTSIDE_LEFT, 0, 1, True))   ;pdb.gimp_edit_fill(orig, gimpenums.FOREGROUND_FILL)
    select_tile(img, Tile(ROUND_OUTSIDE_RIGHT, 1, 0, True))  ;pdb.gimp_edit_fill(orig, gimpenums.FOREGROUND_FILL)
    select_tile(img, Tile(ROUND_OUTSIDE_TOP, 0, 0, True))    ;pdb.gimp_edit_fill(orig, gimpenums.FOREGROUND_FILL)
    select_tile(img, Tile(ROUND_OUTSIDE_BOTTOM, 1,1, True))  ;pdb.gimp_edit_fill(orig, gimpenums.FOREGROUND_FILL)
    
    #restore alias settings
    pdb.gimp_context_set_antialias(antialias)
    gimp.Display(img)

#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_create_sides(img, drawable, tileSize=64):
    global settings
    settings =  Settings(tileSize, 41.0)
    sides = gimp.Layer(img, "Sides", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(sides)
    #save alias settings
    antialias = pdb.gimp_context_get_antialias()
    pdb.gimp_context_set_antialias(False)
    oc = get_layer(img, "OutsideCorners")
    #fill out the tiles
    copy_tile(img, Tile(ROUND_OUTSIDE_TOP, 0, 0, True),    Tile(ROUND_OUTSIDE_TOP, 0, 0, True), oc, sides)
    copy_tile(img, Tile(ROUND_OUTSIDE_LEFT, 0, 1, True),   Tile(ROUND_OUTSIDE_LEFT, 0, 2, True), oc, sides)
    copy_tile(img, Tile(ROUND_OUTSIDE_RIGHT, 1, 0, True),  Tile(ROUND_OUTSIDE_RIGHT, 2, 0, True), oc, sides)
    copy_tile(img, Tile(ROUND_OUTSIDE_BOTTOM, 1, 1, True), Tile(ROUND_OUTSIDE_BOTTOM, 2, 2, True), oc, sides)

    select_tile(img, Tile(INSET_TOP_LEFT, 0, 1, True), select_full=True, sel_type=gimpenums.CHANNEL_OP_REPLACE) 
    select_tile(img, Tile(INSET_BOTTOM_LEFT, 1, 2, True), select_full=True, sel_type=gimpenums.CHANNEL_OP_ADD)  
    select_tile(img, Tile(INSET_TOP_RIGHT, 1, 0, True), select_full=True, sel_type=gimpenums.CHANNEL_OP_ADD) 
    select_tile(img, Tile(INSET_BOTTOM_RIGHT, 2,1, True), select_full=True, sel_type=gimpenums.CHANNEL_OP_ADD)  

    pdb.gimp_edit_fill(sides, gimpenums.FOREGROUND_FILL)
    
    #restore alias settings
    pdb.gimp_context_set_antialias(antialias)
    #gimp.Display(img)
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_create_inside_corners(img, drawable, tileSize=64):
    global settings
    settings =  Settings(tileSize, 41.0)
    ic = gimp.Layer(img, "InsideCorners", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(ic)
    #save alias settings
    antialias = pdb.gimp_context_get_antialias()
    pdb.gimp_context_set_antialias(False)
    sides = get_layer(img, "Sides")
    #fill out the tiles
    copy_tile(img, Tile(INSET_TOP_LEFT, 0, 1, True),     Tile(INSET_TOP_LEFT, 1, 0, True), sides, ic, select_full=True)
    copy_tile(img, Tile(INSET_BOTTOM_RIGHT, 2, 1, True),    Tile(INSET_BOTTOM_RIGHT, 2, 0, True), sides, ic, select_full=True)
    copy_tile(img, Tile(INSET_TOP_LEFT, 0, 1, True),     Tile(INSET_TOP_LEFT, 1, 3, True), sides, ic, select_full=True)
    copy_tile(img, Tile(INSET_BOTTOM_RIGHT, 2, 1, True),    Tile(INSET_BOTTOM_RIGHT, 2, 3, True), sides, ic, select_full=True)

    copy_tile(img, Tile(INSET_TOP_RIGHT, 1, 0, True),  Tile(INSET_TOP_RIGHT, 0, 1, True), sides, ic)
    copy_tile(img, Tile(INSET_BOTTOM_LEFT, 1, 2, True), Tile(INSET_BOTTOM_LEFT, 0, 2, True), sides, ic)
    copy_tile(img, Tile(INSET_TOP_RIGHT, 1, 0, True),  Tile(INSET_TOP_RIGHT, 3, 1, True), sides, ic)
    copy_tile(img, Tile(INSET_BOTTOM_LEFT, 1, 2, True), Tile(INSET_BOTTOM_LEFT, 3, 2, True), sides, ic)

    w = tileSize
    pdb.gimp_image_select_rectangle (img, gimpenums.CHANNEL_OP_REPLACE, w, w, 2*w ,2*w)
    pdb.gimp_edit_fill(ic, gimpenums.FOREGROUND_FILL)
    
    #restore alias settings
    pdb.gimp_context_set_antialias(antialias)

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_transitions_to_iso(img, drawable, tileSize=64):
  global settings
  settings =  Settings(tileSize, 41.0)
  sides = get_layer(img, "Sides")
  oc = get_layer(img, "OutsideCorners")
  ic = get_layer(img, "InsideCorners")
  iso = gimp.Layer(img, "Iso", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
  img.add_layer(iso)

  def transform_tile(srcLayer, src_tile, destLayer, dest_tile):
    w = h = tileSize
    (dx, dy) = (dest_tile.x_index , dest_tile.y_index )
    select_tile(img, src_tile, True)
    grow = 0
    pdb.gimp_selection_grow(img, grow)
    pdb.gimp_edit_copy(srcLayer)
    select_tile(img, dest_tile, True)
    pdb.gimp_selection_grow(img, grow)
    fsel = pdb.gimp_edit_paste(destLayer, False)
    fsel = to_iso_tile(img, fsel, grow)
    isox = (dx - dy) *w  + img.width/2.0 + grow
    isoy = (dx + dy) *h / 2 + grow

    pdb.gimp_layer_translate(fsel, isox, isoy)
    pdb.gimp_floating_sel_anchor(fsel)

  transform_tile(oc, Tile(ROUND_OUTSIDE_TOP, 0, 0, True),iso,  Tile(ROUND_OUTSIDE_TOP, 0, 0, True))
  transform_tile(oc, Tile(ROUND_OUTSIDE_LEFT, 0, 1, True),iso, Tile(ROUND_OUTSIDE_LEFT, 0, 1, True))
  transform_tile(oc, Tile(ROUND_OUTSIDE_RIGHT, 1, 0, True),iso, Tile(ROUND_OUTSIDE_RIGHT, 0, 2, True))
  transform_tile(oc, Tile(ROUND_OUTSIDE_BOTTOM, 1, 1, True),iso, Tile(ROUND_OUTSIDE_BOTTOM, 1, 1, True))

  transform_tile(sides, Tile(INSET_TOP_LEFT, 0, 1, True),iso, Tile(INSET_TOP_LEFT, 1, 2, True))
  transform_tile(sides, Tile(INSET_BOTTOM_LEFT, 1, 2, True),iso, Tile(INSET_BOTTOM_LEFT, 1, 3, True))
  transform_tile(sides, Tile(INSET_TOP_RIGHT, 1, 0, True),iso, Tile(INSET_TOP_RIGHT, 2, 2, True))
  transform_tile(sides, Tile(INSET_BOTTOM_RIGHT, 2, 1, True),iso, Tile(INSET_BOTTOM_RIGHT, 2, 3, True))

  transform_tile(ic, Tile(ROUND_INSIDE_TOP, 1, 1, True),iso, Tile(ROUND_INSIDE_TOP, 2, 4, True))
  transform_tile(ic, Tile(ROUND_INSIDE_BOTTOM, 2, 2, True),iso, Tile(ROUND_INSIDE_BOTTOM, 3, 3, True))
  transform_tile(ic, Tile(ROUND_INSIDE_LEFT, 1, 2, True),iso, Tile(ROUND_INSIDE_LEFT, 3, 4, True))
  transform_tile(ic, Tile(ROUND_INSIDE_RIGHT, 2, 1, True),iso, Tile(ROUND_INSIDE_RIGHT, 4, 4, True))

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_export_transitions(image, output_path, tile, mask=None, background=None, tileSize=64):
    pad = 1
    def save_transition(mask_pos_x, mask_pos_y, name):
      layer = make_transition_layer(image, tile, mask, background, tileSize, mask_pos_x, mask_pos_y, name)
      fullpath = os.path.join(output_path, name) + ".png"
      layer = pdb.gimp_item_transform_scale(layer, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
      pdb.gimp_file_save(image, layer, fullpath, name)
      layer = pdb.gimp_item_transform_scale(layer, 0, 0, 2 * tileSize, tileSize)
      image.remove_layer(layer)
    def save_layer(layer):
      fullpath = os.path.join(output_path, layer.name) + ".png"
      layer = pdb.gimp_item_transform_scale(layer, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
      pdb.gimp_file_save(image, layer, fullpath, layer.name)
      layer = pdb.gimp_item_transform_scale(layer, 0, 0, 2 * tileSize, tileSize)

    save_transition(0,0, "OutsideTop")
    save_transition(0,1, "OutsideLeft")
    save_transition(0,2, "OutsideRight")
    save_transition(1,1, "OutsideBottom")
    save_transition(1,2, "InsetTopLeft")
    save_transition(1,3, "InsetBottomLeft")
    save_transition(2,2, "InsetTopRight")
    save_transition(2,3, "InsetBottomRight")

    save_transition(2,4, "InsideTop")
    save_transition(3,3, "InsideBottom")
    save_transition(3,4, "InsideLeft")
    save_transition(4,4, "InsideRight")
    save_layer(tile)

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_export_tile(image, drawable, output_path, tileSize=64):
  pad = 1
  def save_layer(layer):
      fullpath = os.path.join(output_path, layer.name) + ".png"
      layer = pdb.gimp_item_transform_scale(layer, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
      pdb.gimp_file_save(image, layer, fullpath, layer.name)
      layer = pdb.gimp_item_transform_scale(layer, 0, 0, 2 * tileSize, tileSize)
  save_layer(drawable)

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_demo_tiles(image, tile, mask, background, tileSize=64):
  pad = 1
  w = h = tileSize
  global settings
  settings =  Settings(tileSize, 41.0)
  img = gimp.Image(settings.width*20,settings.width*10,gimpenums.RGB)
  demo = gimp.Layer(img, "Demo", image.width,image.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
  img.add_layer(demo)

  def move(img, layer, dest):
    (dx, dy) = (dest[1] , dest[0] )      
    isox = (dx - dy) *w  + img.width/2.0
    isoy = (dx + dy) *h / 2
    pdb.gimp_layer_translate(layer, isox, isoy)
    return layer

  def place_tile(img, layer, destinations):
    for dest in destinations:
      copy = pdb.gimp_layer_new_from_drawable(layer, img)
      img.add_layer(copy)
      copy = pdb.gimp_item_transform_scale(copy, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
      move(img, copy, dest)

  def place_transition(img, mask_pos_x, mask_pos_y, name, destinations):
    layer = make_transition_layer(img, tile, mask, background, tileSize, mask_pos_x, mask_pos_y, name)
    layer = pdb.gimp_item_transform_scale(layer, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
    for dest in destinations:
      copy = pdb.gimp_layer_new_from_drawable(layer, img)
      img.add_layer(copy)
      move(img, copy, dest)
    img.remove_layer(layer)

  #place_transition( 0,0, "OutsideTop", [[0,0], [0,1], [0,2]])
  place_transition(img, 0, 0, "OutsideTop", [[0,0], [-2,3]])
  place_transition(img, 0, 2, "OutsideRight", [[-2,4], [0,5]])
  place_transition(img, 2, 2, "InsetTopRight", [[0,1], [0,2]])
  place_transition(img, 1, 2, "InsetTopLeft", [[-1,3], [1,0], [2,0], [3,0], [5, 3]])
  place_transition(img, 2, 4, "InsideTop", [[0, 3]])
  place_transition(img, 1, 3, "InsetBottomLeft", [[4, 1], [4,2]]) 
  place_transition(img, 2, 3, "InsetBottomRight", [[5,4], [4,4], [-1,4], [1,5],[2,5]])
  place_transition(img, 3, 4, "InsideLeft", [[4,3]])
  place_transition(img, 0, 1, "OutsideLeft", [[4,0],[6, 3]])
  place_transition(img, 1, 1, "OutsideBottom", [[6,4],[3,5]])
  place_transition(img, 3, 3, "InsideBottom", [[3,4]])
  place_transition(img, 4, 4, "InsideRight", [[0,4]])
  #place_transition(img, 4, 4, "InsideRight", [[]])
  place_tile(img, tile, [[1,1],[2,1], [3,1],
    [1,2],[2,2], [3,2],
    [1,3],[2,3], [3,3],
    [1,4],[2,4]
  ])

  for l in img.layers:
    pdb.gimp_drawable_set_visible(l, True) 
  pdb.gimp_image_flatten(img)
  gimp.Display(img)

#----------------------------------------------------------------------
# Registration
#----------------------------------------------------------------------
register(
  "do_select_tile",
  N_("Select Iso Tiles at Index"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Select Tile..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "x", "X Index", 0),
    (PF_INT, "y", "Y Index", 0),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64),
    (PF_BOOL,  "select_diamond", "Is Diamond Sel", True)
  ],
  [],
  do_select_tile,
  menu="<Image>/Filters/Tiles/Tools"
)

register(
  "do_iso_tiles",
  N_("Create Iso Tiles from pattern"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Create ISO Tile From Pattern..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_DRAWABLE, "source_layer", "Source image", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_iso_tiles,
  menu="<Image>/Filters/Tiles/Tools",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_create_corners",
  N_("1. Create Corner Tiles"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("1. _Create Corner Tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_create_corners,
  menu="<Image>/Filters/Tiles/Tools/Transitions",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_create_sides",
  N_("2. Create Side Tiles"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("2. _Create Side Tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "img",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_create_sides,
  menu="<Image>/Filters/Tiles/Tools/Transitions",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_create_inside_corners",
  N_("3.Create Inside Corners"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("3. _Create Inside Corners..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "img",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_create_inside_corners,
  menu="<Image>/Filters/Tiles/Tools/Transitions",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_transitions_to_iso",
  N_("4.Transitions to ISO"),
  "Requires separate resynthesizer plugin.",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("4. _Transitions to ISO..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "img",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_transitions_to_iso,
  menu="<Image>/Filters/Tiles/Tools/Transitions",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_export_transitions",
  N_("Export All Tiles"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Export All Tiles..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd()),
    (PF_DRAWABLE, "tile", _("Tile"), None),
    (PF_DRAWABLE, "mask", _("Tile masks"), None),
    (PF_DRAWABLE, "background", _("Tile background"), None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_export_transitions,
  menu="<Image>/Filters/Tiles/Tools/Export",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_export_tile",
  N_("Export Single Tile"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Export Single Tile..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd()),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_export_tile,
  menu="<Image>/Filters/Tiles/Tools/Export",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_demo_tiles",
  N_("Test Tile Layout"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Test Layout..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "tile", _("Tile"), None),
    (PF_DRAWABLE, "mask", _("Masks"), None),
    (PF_DRAWABLE, "background", _("Tile background"), None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_demo_tiles,
  menu="<Image>/Filters/Tiles/Tools",
  domain=("resynthesizer", gimp.locale_directory)
  )

main()
