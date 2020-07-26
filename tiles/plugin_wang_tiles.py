#!/usr/bin/env python
from gimpfu import *
from random import *
import gimpenums
import collections
import math
import re
import os

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)
Settings = collections.namedtuple("Settings",["width", "inset"])
#----------------------------------------------------------------------
# Globals
#----------------------------------------------------------------------
settings = None
layout_size = 4
number = [4,6,14,12,5,7,15,13,1,3,11,9,0,2,10,8]

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
def merge_layers(image, layer1, layer2):
      for L in image.layers: 
        if L == layer1 or L == layer2: 
          pdb.gimp_drawable_set_visible(L, True) 
        else:
          pdb.gimp_drawable_set_visible(L, False) 
      return pdb.gimp_image_merge_visible_layers(image, 0)
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
def do_select_tile(drawable, x, y, tileSize=64, select_diamond=True ):
    w = tileSize
    h = tileSize
    grow = 0
    (dx, dy) = (x * w, y * h)

    if select_diamond:
      isox = (x - y) * w  + drawable.image.width/2.0 + grow
      isoy = (x + y) * h / 2 + grow
      return select_diamond_shape(drawable.image, w * 2, h, isox, isoy)
    return  pdb.gimp_image_select_rectangle (drawable.image, gimpenums.CHANNEL_OP_REPLACE, dx, dy, w ,w)
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def to_iso_tile(layer, tileSize, grow=0):
  #pdb.gimp_context_set_interpolation(gimpenums.INTERPOLATION_NONE)
  item = pdb.gimp_item_transform_rotate(layer, math.pi/4, True, 0, 0)
  dw = tileSize * 2
  dh = tileSize
  return pdb.gimp_item_transform_scale(item, 0, 0, dw+2*grow, dh+2*grow)
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def make_transition_layer(image, tile, mask, background, tileSize, mask_pos_x, mask_pos_y, name, pad=1):
  tile_bkgn = pdb.gimp_layer_new_from_drawable(background, image)
  tile_copy = pdb.gimp_layer_new_from_drawable(tile, image)
  tile_copy.name = name
  image.add_layer(tile_bkgn)
  image.add_layer(tile_copy)
  pdb.gimp_layer_set_offsets(tile_bkgn, 0, 0)
  pdb.gimp_layer_set_offsets(tile_copy, -1, -1)
      
  do_select_tile(mask, mask_pos_x, mask_pos_y, tileSize)
  pdb.gimp_edit_copy(mask)
  theMask = pdb.gimp_layer_create_mask(tile_copy, gimpenums.ADD_BLACK_MASK)
  pdb.gimp_layer_add_mask(tile_copy, theMask)
  fsel = pdb.gimp_edit_paste(theMask, False)

  s = select_diamond_shape(image, tileSize * 2, tileSize, 0, 0)
  fsel = pdb.gimp_item_transform_scale(fsel, s[0]-pad, s[3]-pad, s[4]+pad, s[7]+pad)

  pdb.gimp_floating_sel_anchor(fsel)
  merged_layer = merge_layers(image, tile_copy, tile_bkgn)
  merged_layer.name = name
  return merged_layer
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def save_layer(output_path, tileSize, layer):
  pad = 1
  fullpath = os.path.join(output_path, layer.name) + ".png"
  pdb.gimp_file_save(layer.image, layer, fullpath, layer.name)
  layer = pdb.gimp_item_transform_scale(layer, 0, 0, 2 * tileSize, tileSize)
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def seed_tiles(tiles, canvas_size):
  gap = randint(3, 7) 
  for row in range(canvas_size/2-2, canvas_size/2 +2):
    for col in range(canvas_size/2-2, canvas_size/2 +2):
      tiles[row][col] = 15
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def prapare_mask(layer, index, tileSize):
  tile_val = number[index]
  pdb.gimp_selection_clear(layer.image)
  if tile_val==0:
    return
  if tile_val & int('0001',2) > 0: #top edge
    p =[0,0,tileSize,0,tileSize/2,tileSize/2]
    pdb.gimp_image_select_polygon(layer.image, gimpenums.CHANNEL_OP_ADD, len(p), p)
  if tile_val & int('0010',2) > 0: #right edge
    p =[tileSize,0,tileSize,tileSize,tileSize/2,tileSize/2]
    pdb.gimp_image_select_polygon(layer.image, gimpenums.CHANNEL_OP_ADD, len(p), p)
  if tile_val & int('0100',2) > 0: #bottom edge
    p =[0,tileSize,tileSize/2,tileSize/2,tileSize,tileSize]
    pdb.gimp_image_select_polygon(layer.image, gimpenums.CHANNEL_OP_ADD, len(p), p)
  if tile_val & int('1000',2) > 0: #left edge
    p =[0,0,tileSize/2,tileSize/2,0,tileSize]
    pdb.gimp_image_select_polygon(layer.image, gimpenums.CHANNEL_OP_ADD, len(p), p)

  pdb.gimp_edit_fill(layer, gimpenums.FOREGROUND_FILL)
  pdb.gimp_selection_clear(layer.image)

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def select_tile(img, layer, index, tileSize=64):
    image_index = number.index(index)
    row = image_index / layout_size
    col = image_index - (row * layout_size)
    pdb.gimp_image_select_rectangle (img, gimpenums.CHANNEL_OP_REPLACE, col * tileSize, row * tileSize, tileSize, tileSize)
    pdb.gimp_edit_copy(layer)

#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_make_square_seamless_tile(image, source_layer, tileSize):
    img = gimp.Image(tileSize,tileSize,gimpenums.RGB)
    orig = gimp.Layer(img, "Orig", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
    img.add_layer(orig)
    pdb.gimp_edit_copy(source_layer)
    fsel = pdb.gimp_edit_paste(orig, False)
    pdb.gimp_floating_sel_anchor(fsel)
    pdb.gimp_drawable_offset(orig, True, gimpenums.OFFSET_WRAP_AROUND, img.width/2,img.height/2)
    pdb.gimp_image_select_rectangle (image, gimpenums.CHANNEL_OP_REPLACE, 0, 0, tileSize, tileSize)
    gimp.Display(img)
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_create_wang_layout(image, drawable, foreground_tile, background_tile, tileSize):
  global settings
  settings =  Settings(tileSize, 41.0)
  pad = 0
  w = tileSize
  h = tileSize
  img = gimp.Image(tileSize*layout_size,tileSize*layout_size,gimpenums.RGB)
  wang_layer = gimp.Layer(img, "WangBackground", image.width,image.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
  img.add_layer(wang_layer)
  
  #tile the background first
  for y in range(layout_size):
   for x in range(layout_size):
    copy = pdb.gimp_layer_new_from_drawable(background_tile, img)
    pdb.gimp_drawable_set_visible(copy, True) 
    img.add_layer(copy)
    pdb.gimp_layer_set_offsets(copy, 0, 0)
    pdb.gimp_layer_translate(copy, w*x, h*y)
  pdb.gimp_image_merge_visible_layers(img, gimpenums.EXPAND_AS_NECESSARY)
  #tile the foreground
  index = 0
  for y in range(layout_size):
   for x in range(layout_size):
    copy = pdb.gimp_layer_new_from_drawable(foreground_tile, img)
    pdb.gimp_drawable_set_visible(copy, True) 
    img.add_layer(copy)
    pdb.gimp_layer_set_offsets(copy, 0, 0)
    theMask = pdb.gimp_layer_create_mask(copy, gimpenums.ADD_BLACK_MASK)
    pdb.gimp_layer_add_mask(copy, theMask)
    prapare_mask(theMask,index,tileSize)
    pdb.gimp_layer_translate(copy, w*x, h*y)
    copy.name = str(number[index])
    index = index + 1 
  gimp.Display(img)
#----------------------------------------------------------------------
# 
#----------------------------------------------------------------------
def do_render_wang(image, drawable, tileSize):
  canvas_size = 15
  seed(9)
  def pick_tiles():
    tiles = [[None for i in range(canvas_size)] for j in range(canvas_size)]
    seed_tiles(tiles, canvas_size)
    for row in range(canvas_size):
      for col in range(canvas_size):
        north = 0 if row==0 else tiles[row-1][col]
        west  = 0 if col==0 else tiles[row][col-1]
        east  = 0 if col+1 >= canvas_size else tiles[row][col+1]
        south = 0 if row+1 >= canvas_size else tiles[row+1][col]

        east  = randrange(0,2)<<3 if east  is None else east
        south = randrange(0,2)<<0 if south is None else south
        north = randrange(0,2)<<2 if north is None else north
        west  = randrange(0,2)<<1 if west  is None else west

        north_part = ((north & int('0100',2))>>2)
        west_part  = ((west  & int('0010',2))<<2)
        east_part  = ((east  & int('1000',2))>>2)
        south_part = ((south & int('0001',2))<<2)
        tiles[row][col] = north_part | west_part | east_part | south_part
    return tiles

  def paste_tile(img, layer, row, col):
    fsel = pdb.gimp_edit_paste(layer, False)
    pdb.gimp_layer_set_offsets(fsel, 0, 0)
    pdb.gimp_layer_translate(fsel, col*tileSize, row*tileSize)
    pdb.gimp_floating_sel_anchor(fsel)
  
  img = gimp.Image(tileSize*canvas_size,tileSize*canvas_size,gimpenums.RGB)
  demo = gimp.Layer(img, "Demo", img.width,img.height,gimpenums.RGBA_IMAGE,100, gimpenums.NORMAL_MODE)
  img.add_layer(demo)

  tiles = pick_tiles()
  pdb.gimp_message(tiles)
  for row in range(canvas_size):
      for col in range(canvas_size):
        index = tiles[row][col]
        select_tile(drawable.image, drawable, index)
        paste_tile(img,demo,row, col)

  gimp.Display(img)
#----------------------------------------------------------------------
#
#----------------------------------------------------------------------
def do_export(image, drawable, output_path, mask=None, background=None, tileSize=64):
  pad = 1
  def save_wang_transition(tile, bk, mask_pos_x, mask_pos_y, name):
    layer = make_transition_layer(image, tile, mask, bk, tileSize, mask_pos_x, mask_pos_y, name)
    fullpath = os.path.join(output_path, name) + ".png"
    layer = pdb.gimp_item_transform_scale(layer, -pad, -pad, 2 * tileSize + pad, tileSize+pad)
    pdb.gimp_file_save(image, layer, fullpath, name)
    layer = pdb.gimp_item_transform_scale(layer, 0, 0, 2 * tileSize, tileSize)
    image.remove_layer(layer)
  
  def save_wang_tile(layer, tileIndex):
    select_tile(image, layer, tileIndex)
    copy = pdb.gimp_edit_paste(layer, False)
    copy = to_iso_tile(copy, tileSize, 1)
    copy.name = "wang_{}".format(tileIndex)
    return copy
  
  for index in range(0,16):
    copy = save_wang_tile(drawable, index)
    save_layer(output_path,tileSize, copy)
    image.remove_layer(copy)

  #create transitions using the mask
  if mask is not None and background is not None:
    select_tile(image, drawable, 0)
    copy = pdb.gimp_edit_paste(drawable, False)
    pdb.gimp_floating_sel_to_layer(copy)
    to_iso_tile(copy, tileSize, 1)
    
    #copy the mask
    save_wang_transition(copy, background, 0,0, "OutsideTop")
    save_wang_transition(copy, background, 0,1, "OutsideLeft")
    save_wang_transition(copy, background, 0,2, "OutsideRight")
    save_wang_transition(copy, background, 1,1, "OutsideBottom")
    save_wang_transition(copy, background, 1,2, "InsetTopLeft")
    save_wang_transition(copy, background, 1,3, "InsetBottomLeft")
    save_wang_transition(copy, background, 2,2, "InsetTopRight")
    save_wang_transition(copy, background, 2,3, "InsetBottomRight")
    save_wang_transition(copy, background, 2,4, "InsideTop")
    save_wang_transition(copy, background, 3,3, "InsideBottom")
    save_wang_transition(copy, background, 3,4, "InsideLeft")
    save_wang_transition(copy, background, 4,4, "InsideRight")
    image.remove_layer(copy)

#----------------------------------------------------------------------
# Registration
#----------------------------------------------------------------------
register(
  "do_create_wang_layout",
  N_("Create Wang Layout"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Create Layout..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_DRAWABLE, "foreground_tile", _("Tile foreground"), None),
    (PF_DRAWABLE, "background_tile", _("Tile background"), None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_create_wang_layout,
  menu="<Image>/Filters/Tiles/Wang",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_make_square_seamless_tile",
  N_("Make Seamless"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Make Seamless..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "source_layer", _("Source"), None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_make_square_seamless_tile,
  menu="<Image>/Filters/Tiles/Wang",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_render_wang",
  N_("Render Wang Tiles"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Render Wang..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_render_wang,
  menu="<Image>/Filters/Tiles/Wang",
  domain=("resynthesizer", gimp.locale_directory)
  )

register(
  "do_export",
  N_("Export Wang Tiles"),
  "",
  "Alex Cotoman",
  "2020 Alex Cotoman",  # Copyright 
  "2020",
  N_("_Export..."),
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image", "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd()),
    (PF_DRAWABLE, "mask", "Transitions Mask", None),
    (PF_DRAWABLE, "background", "Background", None),
    (PF_INT, "tileSize", _("Tile width (pixels):"), 64)
  ],
  [],
  do_export,
  menu="<Image>/Filters/Tiles/Wang",
  domain=("resynthesizer", gimp.locale_directory)
  )

main()
