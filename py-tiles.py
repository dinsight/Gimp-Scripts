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
inside_corners_layer = "inside-corners-layer"

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
def export_transitions(image, layer_name,tileW, tileH, output_path=""):
    for l in image.layers:
        if l.name.startswith(layer_name):
            #print("exporting layer : " + layer_name)
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
def make_tile(img, name, x , y):
    base = next(x for x in img.layers if x.name == baseLayerName )
    layer = base.copy()
    layer.name = name
    layer.set_offsets(x, y)
    img.add_layer(layer, 0)

###########################################################
#
#
###########################################################
def merge_transitions(img, withPrefix, destLayer):
    for l in img.layers:
        if l.name.startswith(withPrefix):
            pdb.gimp_drawable_set_visible(l, True)
        else:
            pdb.gimp_drawable_set_visible(l, False)
    allTrans = pdb.gimp_image_merge_visible_layers(img, 0)
    allTrans.name = destLayer

###########################################################
#
#
###########################################################
def translate_selection(sel,dx,dy):
    for index in range(len(sel)):
        if index%2==0:
            sel[index] += dx
        else:
            sel[index] += dy

###########################################################
#
#
###########################################################
def get_slice(img, layer, tileName, sliceType, tileW, tileH, grow, translate):
    dx=int(tileW/2*0.8)
    dy=int(tileH/2*0.8)
    sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
    if sliceType == "nw":
        sel[4] -= dx; sel[6] -= dx
        sel[5] -= dy; sel[7] -= dy
        translate_selection(sel,-translate,-translate)
    if sliceType == "ne":
        sel[0] += dx; sel[6] += dx
        sel[1] -= dy; sel[7] -= dy
        translate_selection(sel,translate,-translate)
    if sliceType == "sw":
        sel[2] -= dx; sel[4] -= dx
        sel[3] += dy; sel[5] += dy
        translate_selection(sel,-translate,translate)
    if sliceType == "se":
        sel[0] += dx; sel[2] += dx
        sel[1] += dy; sel[3] += dy
        translate_selection(sel,translate,translate)
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    pdb.gimp_selection_grow(img,grow)

###########################################################
#
#
###########################################################
def make_seamless_corner(img, layer, cornerType, tileW, tileH, dictionary):
    edges = dictionary[cornerType][0]
    sliceType = dictionary[cornerType][1]

    #Hide the tile where the corner is supposed to be created
    select_transition(img, layer, cornerType, tileW, tileH)
    pdb.gimp_edit_cut(layer)

    for index in range(len(edges)):
        #select and copy slice
        get_slice(img, layer, edges[index], sliceType[index], tileW, tileH, 0, 0)
        pdb.gimp_edit_copy(layer)
        #select and paste slice
        get_slice(img, layer,cornerType, sliceType[index], tileW, tileH, 0, 1)
        selId= pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_anchor(selId)
        
###########################################################
#
#
###########################################################    
def make_outside_corners(img, layer, tileW, tileH):
    dictionary = {
        "lle" : ( ["le","de"], ["ne","se"] ),
        "ule" : ( ["le","ue"], ["sw","se"] ),
        "ure" : ( ["ue","re"], ["nw","sw"] ),
        "lre" : ( ["re","de"], ["ne","nw"] )
    }
    make_seamless_corner(img, layer, "lle", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "ule", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "ure", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "lre", tileW, tileH, dictionary)

###########################################################
#
#
###########################################################    
def make_inside_corners(img, layer, tileW, tileH):
    dictionary = {
        "lle" : ( ["le","de"], ["ne","se"] ),
        "ule" : ( ["le","ue"], ["sw","se"] ),
        "ure" : ( ["ue","re"], ["nw","sw"] ),
        "lre" : ( ["re","de"], ["ne","nw"] )
    }
    make_seamless_corner(img, layer, "lle", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "ule", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "ure", tileW, tileH, dictionary)
    make_seamless_corner(img, layer, "lre", tileW, tileH, dictionary)
    
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
def make_seamless(img, layer, tileW, tileH):
    l1=make_seamless_internal(img, layer, "le" , tileW, tileH, "")
    l2=make_seamless_internal(img, layer, "ue" , tileW, tileH, "tldr")
    l3=make_seamless_internal(img, layer, "re" , tileW, tileH, "")
    l4=make_seamless_internal(img, layer, "de" , tileW, tileH, "tldr")
    pdb.gimp_image_merge_down(img, l4, 2)
    pdb.gimp_image_merge_down(img, l3, 2)
    pdb.gimp_image_merge_down(img, l2, 2)
    layer=pdb.gimp_image_merge_down(img, l1, 2)
    make_outside_corners(img,layer,tileW,tileH)
    #make_inside_corners(img,layer,tileW,tileH)

###########################################################
#
#
###########################################################
def make_transitions_from_base_tile(img, layer, tileW, tileH):
    img.resize(tileW*3, tileH*3,tileW, tileH)
    #left corner
    make_tile(img, transitions_prefix + "lle", 0, tileH)
    #right corner
    make_tile(img, transitions_prefix + "ure", 2*tileW, tileH)
    #up edge
    make_tile(img, transitions_prefix + "ue", tileW+tileW/2, tileH/2)
    #right edge
    make_tile(img, transitions_prefix + "re", tileW+tileW/2, tileH + tileH/2)
    #left edge
    make_tile(img, transitions_prefix + "le", tileW/2, tileH/2)
    #down edge
    make_tile(img, transitions_prefix + "de", tileW/2, tileH + tileH/2)
    #lower right corner
    make_tile(img, transitions_prefix + "lre", tileW, 2 * tileH)
    #upper left corner
    make_tile(img, transitions_prefix + "ule", tileW, 0)
    merge_transitions(img, transitions_prefix, transitions_layer)
    #inside corner nw
    make_tile(img, transitions_prefix + "ic-n", tileW/2, 0)
    #inside corner ne
    make_tile(img, transitions_prefix + "ic-s", tileW/2, tileH)
    #inside corner sw
    make_tile(img, transitions_prefix + "ic-e", tileW, tileH/2)
    #inside corner se
    make_tile(img, transitions_prefix + "ic-w", 0, tileH/2)
    merge_transitions(img, transitions_prefix, inside_corners_layer)

###########################################################
#
#
###########################################################
def select_transition(img, layer, tileName, tileW, tileH, grow=0):
    sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
    pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
    pdb.gimp_selection_grow(img,grow)

###########################################################
#image= gimp.image_list()[0]
###########################################################

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
         "python_fu_make_transitions",
         N_("Create Transitions from Base Tile"),
         """Create Transitions from Base Tile""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_1. Make Transitions from Base Tile..."),
         "*",
         [
          (PF_IMAGE, "img", "Input image", None),
          (PF_DRAWABLE, "layer", "Input layer", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         make_transitions_from_base_tile,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_make_seamlesss",
         N_("Make Seamless Transitions"),
         """Make Seamless Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_2. Make Seamless Transition..."),
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
         "python_fu_export_transitions",
         N_("Export Tile Transitions"),
         """Export Tile Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_3. Export Transitions..."),
         "*",
         [
            (PF_IMAGE, "image", "Input image", None),
            (PF_STRING, "layer_name", "Prefx of the layer to Export", transitions_layer),
            (PF_INT, "tileW", "Tile Width", 128),
            (PF_INT, "tileH", "Tile Height", 64),
            (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd())
         ],
         [],
         export_transitions,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

main()
