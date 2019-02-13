#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import os
from gimpfu import *
import os.path

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

export_type = ".png"
baseLayerName = "base"
transitions_prefix = "trans-"
transitions_layer = "transitions-layer"
#tileW = 128
#tileH = 64

def get_lle_selection(tileW, tileH): return [0, tileH + tileH/2, tileW/2, tileH, tileW, tileH + tileH/2, tileW/2, 2* tileH ]
def get_le_selection(tileW, tileH): return [tileW/2, tileH, tileW, tileH/2, tileW + tileW/2, tileH, tileW, tileH + tileH/2 ]
def get_ule_selection(tileW, tileH): return [tileW, tileH/2, tileW + tileW/2, 0, 2 * tileW, tileH/2, tileW + tileW/2, tileH]
def get_ue_selection(tileW, tileH): return [tileW + tileW/2, tileH, 2 * tileW, tileH/2, 2 * tileW + tileW/2, tileH, 2 * tileW, tileH + tileH/2]
def get_ure_selection(tileW, tileH): return [2* tileW, tileH + tileH/2, 2 *tileW + tileW/2, tileH, 3 * tileW, tileH + tileH/2, 2 * tileW + tileW/2, 2 * tileH]
def get_re_selection(tileW, tileH): return [tileW + tileW/2, 2 * tileH, 2 * tileW, tileH + tileH/2, 2 * tileW + tileW/2, 2 * tileH, 2 * tileW, 2 * tileH + tileH/2]
def get_lre_selection(tileW, tileH): return [tileW, 2 * tileH + tileH/2, tileW + tileW/2, 2 * tileH, 2 * tileW, 2 * tileH + tileH/2, tileW + tileW/2, 3 * tileH]
def get_de_selection(tileW, tileH): return [tileW/2, 2 * tileH, tileW, tileH + tileH/2, tileW + tileW/2, 2 * tileH, tileW, 2 * tileH + tileH/2 ]
###########################################################
#
#
###########################################################
def split_transitions(image, drawable,tileW, tileH, output_path=""):
    for l in image.layers:
        if l.name.startswith(transitions_layer):
            export_transition(output_path, image, l, "lle", export_type, get_lle_selection(tileW, tileH))
            export_transition(output_path, image, l, "le",  export_type, get_le_selection(tileW, tileH))
            export_transition(output_path, image, l, "ule", export_type, get_ule_selection(tileW, tileH))
            export_transition(output_path, image, l, "ue",  export_type, get_ue_selection(tileW, tileH))
            export_transition(output_path, image, l, "ure", export_type, get_ure_selection(tileW, tileH))
            export_transition(output_path, image, l, "re",  export_type, get_re_selection(tileW, tileH))
            export_transition(output_path, image, l, "lre", export_type, get_lre_selection(tileW, tileH))
            export_transition(output_path, image, l, "de", export_type, get_de_selection(tileW, tileH))

###########################################################
#
#
###########################################################
def merge_transitions(img):
    for l in img.layers:
        if l.name.startswith(transitions_prefix):
            pdb.gimp_drawable_set_visible(l, True)
        else:
            pdb.gimp_drawable_set_visible(l, False)
    allTrans = pdb.gimp_image_merge_visible_layers(img, 0)
    allTrans.name = transitions_layer


###########################################################
#
#
###########################################################
def export_transition(output_path, img, layer, name, ext, selection):
    img.active_layer = layer
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(selection),selection)
    pdb.gimp_selection_grow(img,1)
    pdb.gimp_edit_copy(layer)
    fsel = pdb.gimp_edit_paste(layer, False)
    new = pdb.gimp_floating_sel_to_layer(fsel)
    theNewLayer = img.active_layer
    export_layers(img, theNewLayer, output_path, name, ext)
    img.remove_layer(theNewLayer)
    img.active_layer = layer

###########################################################
#
#
###########################################################
def export_layers(imgInput, drw, path, name, ext):
    img = pdb.gimp_image_duplicate(imgInput)

    for layer in img.layers:
        layer.visible = False

    for idx, layer in enumerate(img.layers):
        layer.visible = True
        filename = name % [ idx, layer.name ]
        fullpath = os.path.join(path, filename) + ext

        layer_img = img.duplicate()
        layer_img.flatten()
        pdb.gimp_file_save(layer_img, drw, fullpath, filename)
        img.remove_layer(layer)
        pdb.gimp_image_delete(layer_img)
    pdb.gimp_image_delete(img)

###########################################################
#
#
###########################################################
def create_tile(img, name, x , y):
    base = next(x for x in img.layers if x.name == baseLayerName )
    layer = base.copy()
    layer.name = name
    layer.set_offsets(x, y)
    img.add_layer(layer, 0)
    
###########################################################
#
#
###########################################################
def prepareImage(img, tileW, tileH):
    img.resize(tileW*3, tileH*3,tileW, tileH)
    #left corner
    create_tile(img, transitions_prefix + "lle", 0, tileH)
    #right corner
    create_tile(img, transitions_prefix + "ure", 2*tileW, tileH)
    #up edge
    create_tile(img, transitions_prefix + "ue", tileW+tileW/2, tileH/2)
    #right edge
    create_tile(img, transitions_prefix + "re", tileW+tileW/2, tileH + tileH/2)
    #left edge
    create_tile(img, transitions_prefix + "le", tileW/2, tileH/2)
    #down edge
    create_tile(img, transitions_prefix + "de", tileW/2, tileH + tileH/2)
    #lower right corner
    create_tile(img, transitions_prefix + "lre", tileW, 2 * tileH)
    #upper left corner
    create_tile(img, transitions_prefix + "ule", tileW, 0)
    merge_transitions(img)

###########################################################
#
#
###########################################################
def make_seamless_internal(img, layer, tileName, tileW, tileH, dir):
    sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    #pdb.gimp_selection_grow(img,0)
    pdb.gimp_edit_copy(layer)
    
    top_half = pdb.gimp_edit_paste(layer, False)
    pdb.gimp_floating_sel_to_layer(top_half)
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    bottom_half = pdb.gimp_edit_paste(layer, False)
    pdb.gimp_floating_sel_to_layer(bottom_half)

    if dir == "tldr":
        pdb.gimp_drawable_offset(top_half, False, 1, tileW/4, tileH/4)
        pdb.gimp_drawable_offset(bottom_half, False, 1, -tileW/4, -tileH/4)
    else:
        pdb.gimp_drawable_offset(top_half, False, 1, -tileW/4, tileH/4)
        pdb.gimp_drawable_offset(bottom_half, False, 1, tileW/4, -tileH/4)

    combined_layer = pdb.gimp_image_merge_down(img, top_half, 2)
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    pdb.gimp_selection_invert(img)
    pdb.gimp_edit_cut(combined_layer)
    return combined_layer

###########################################################
#
#
###########################################################
def select_transition(img, layer, tileName, tileW, tileH, grow=0):
    sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    pdb.gimp_selection_grow(img,grow)

###########################################################
#
#
###########################################################
def get_slice(img, layer, tileName, sliceType, tileW, tileH, grow=0):
    dx=int(tileW/2*0.8)
    dy=int(tileH/2*0.8)
    sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
    if sliceType == "nw":
        sel[4] -= dx; sel[6] -= dx
        sel[5] -= dy; sel[7] -= dy
    if sliceType == "ne":
        sel[0] += dx; sel[6] += dx
        sel[1] -= dy; sel[7] -= dy
    if sliceType == "sw":
        sel[2] -= dx; sel[4] -= dx
        sel[3] += dy; sel[5] += dy
    if sliceType == "se":
        sel[0] += dx; sel[2] += dx
        sel[1] += dy; sel[3] += dy
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    pdb.gimp_selection_grow(img,grow)

###########################################################
#
#
###########################################################
def create_outside_corner(img, layer, cornerType, tileW, tileH):
    if cornerType=="lle": edges=["le","de"]; sliceType=["ne","se"]
    if cornerType=="ule": edges=["le","ue"]; sliceType=["sw","se"]
    if cornerType=="ure": edges=["ue","re"]; sliceType=["nw","sw"]
    if cornerType=="lre": edges=["re","de"]; sliceType=["ne","nw"]

    #Hide the tile where the corner is supposed to be created
    select_transition(img, layer, cornerType, tileW, tileH)
    pdb.gimp_edit_cut(layer)

    for index in range(len(edges)):
        #select and copy slice
        get_slice(img, layer, edges[index], sliceType[index], tileW, tileH)
        pdb.gimp_edit_copy(layer)
        #select and paste slice
        get_slice(img, layer,cornerType, sliceType[index], tileW, tileH)
        selId= pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_anchor(selId)
        
###########################################################
#
#
###########################################################    
def create_outside_corners(img, layer, tileW, tileH):
    #create_outside_corner(img, layer, "lle", tileW, tileH)
    #create_outside_corner(img, layer, "ule", tileW, tileH)
    create_outside_corner(img, layer, "ure", tileW, tileH)
    #create_outside_corner(img, layer, "lre", tileW, tileH)

###########################################################
#
#
###########################################################
def make_seamless(img, layer, tileW, tileH):
    l1=make_seamless_internal(img, layer, "le" , tileW, tileH, "")
    l2=make_seamless_internal(img, layer, "ue" , tileW, tileH, "tldr")
    l3=make_seamless_internal(img, layer, "re" , tileW, tileH, "")
    l4=make_seamless_internal(img, layer, "de" , tileW, tileH, "tldr")
    pdb.gimp_image_merge_down(img, l4, 2)
    pdb.gimp_image_merge_down(img, l3, 2)
    pdb.gimp_image_merge_down(img, l2, 2)
    layer=pdb.gimp_image_merge_down(img, l1, 2)
    create_outside_corners(img,layer,tileW,tileH)

###########################################################
# execfile('/Users/alexjecu/Desktop/Workspace/dinsight/xamarin/assets/tiles/scripts/gimp-grid.py')
#image= gimp.image_list()[0]
#outputFolder = "/Users/alexjecu/Desktop/Workspace/dinsight/xamarin/assets/tiles/Gimp"
###########################################################
register(
         "python_fu_create_outside_corners",
         N_("Create Outside Corners"),
         """Create Outside Corners""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_Create Outside Corners..."),
         "*",
         [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "layer", "Input layer", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         create_outside_corners,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_select_tile",
         N_("Select Tile"),
         """Select Tile""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_Select Tile..."),
         "*",
         [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "layer", "Input layer", None),
          (PF_STRING, "transitionName", "Tile Name (lle,le,ule,ue,ure,re,lre,de)", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         select_transition,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_make_seamlesss",
         N_("Make Seamless Transitions"),
         """Make Seamless Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_Make Seamless Transition..."),
         "*",
         [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "layer", "Input layer", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         make_seamless,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_transitions",
         N_("Creates Tile Transitions"),
         """Creates Tile Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_Export Transitions..."),
         "*",
         [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
            (PF_INT, "tileW", "Tile Width", 128),
            (PF_INT, "tileH", "Tile Height", 64),
            (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd())
         ],
         [],
         split_transitions,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_prep_transitions",
         N_("ArrangeTile Transitions"),
         """Arrange Tile Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_Arrange Transitions..."),
         "*",
         [
          (PF_IMAGE, "img", "Input image", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         prepareImage,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

main()
