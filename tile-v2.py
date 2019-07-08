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

def sign(n): return (n > 0) - (n < 0);

def get_lle_selection(tileW, tileH): return [0, tileH + tileH/2, tileW/2, tileH, tileW, tileH + tileH/2, tileW/2, 2* tileH ]
def get_le_selection(tileW, tileH): return [tileW/2, tileH, tileW, tileH/2, tileW + tileW/2, tileH, tileW, tileH + tileH/2 ]
def get_ule_selection(tileW, tileH): return [tileW, tileH/2, tileW + tileW/2, 0, 2 * tileW, tileH/2, tileW + tileW/2, tileH]
def get_ue_selection(tileW, tileH): return [tileW + tileW/2, tileH, 2 * tileW, tileH/2, 2 * tileW + tileW/2, tileH, 2 * tileW, tileH + tileH/2]
def get_ure_selection(tileW, tileH): return [2* tileW, tileH + tileH/2, 2 *tileW + tileW/2, tileH, 3 * tileW, tileH + tileH/2, 2 * tileW + tileW/2, 2 * tileH]
def get_re_selection(tileW, tileH): return [tileW + tileW/2, 2 * tileH, 2 * tileW, tileH + tileH/2, 2 * tileW + tileW/2, 2 * tileH, 2 * tileW, 2 * tileH + tileH/2]
def get_lre_selection(tileW, tileH): return [tileW, 2 * tileH + tileH/2, tileW + tileW/2, 2 * tileH, 2 * tileW, 2 * tileH + tileH/2, tileW + tileW/2, 3 * tileH]
def get_de_selection(tileW, tileH): return [tileW/2, 2 * tileH, tileW, tileH + tileH/2, tileW + tileW/2, 2 * tileH, tileW, 2 * tileH + tileH/2 ]
def get_ic_n_selection(tileW, tileH): return Util.offset_selection([tileW/2, tileH/2, tileW, 0, tileW/2+tileW, tileH/2, tileW, tileH], 2*tileW, 2*tileH+tileH/2)
def get_ic_s_selection(tileW, tileH): return Util.offset_selection([tileW/2, tileH/2+tileH, tileW, tileH, tileW+tileW/2, tileH+tileH/2, tileW, 2*tileH], 2*tileW, 2*tileH+tileH/2)
def get_ic_e_selection(tileW, tileH): return Util.offset_selection([tileW, tileH, tileW+tileW/2, tileH/2, 2*tileW, tileH, tileW+tileW/2, tileH+tileH/2], 2*tileW, 2*tileH+tileH/2)
def get_ic_w_selection(tileW, tileH): return Util.offset_selection([0, tileH, tileW/2, tileH/2, tileW, tileH, tileW/2, tileH + tileH/2], 2*tileW, 2*tileH+tileH/2)
def get_base_selection(tileW, tileH): return Util.offset_selection([0, tileH, tileW/2, tileH/2, tileW, tileH, tileW/2, tileH + tileH/2], 0, 0)

def get_ic_selection(tileW, tileH): return Util.offset_selection([0,tileH,tileW,0,2*tileW,tileH,tileW,2*tileH], 2*tileW, 2*tileH+tileH/2)
    
###########################################################
#
#
###########################################################
class Util:

    @staticmethod
    def get_layer(image,name):
            for l in image.layers:
                if l.name == name:
                    return l
            return None

    @staticmethod
    def merge_layers(img, layer_list):
        if len(layer_list)>1:
            img.active_layer = layer_list[0]
            last_layer = None
            for index in range(len(layer_list)):
                if index < len(layer_list)-1:
                    l = layer_list[index]
                    last_layer = pdb.gimp_image_merge_down(img, l, 0)
                    layer_list[index+1]=last_layer
            return last_layer
        return layer_list[0] if len(layer_list)==1 else None

    @staticmethod
    def offset_selection(sel, dx, dy ):
        for index in range(len(sel)):
            if index%2==0:
                sel[index] += dx
            else:
                sel[index] += dy
        return sel
            
class Export:
        
###########################################################
#
#
###########################################################
    @staticmethod
    def export_transitions(image, layer_name, tileW, tileH, output_path=""):
        for l in image.layers:
            if l.name.startswith(layer_name):
                Export.export_transition(output_path, image, l, "lle", export_type, get_lle_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "le",  export_type, get_le_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ule", export_type, get_ule_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ue",  export_type, get_ue_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ure", export_type, get_ure_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "re",  export_type, get_re_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "lre", export_type, get_lre_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "de", export_type, get_de_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ic_n", export_type, get_ic_n_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ic_s", export_type, get_ic_s_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ic_e", export_type, get_ic_e_selection(tileW, tileH))
                Export.export_transition(output_path, image, l, "ic_w", export_type, get_ic_w_selection(tileW, tileH))

    @staticmethod            
    def export_transition(output_path, img, layer, name, ext, selection):
        img.active_layer = layer
        pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(selection),selection)
        pdb.gimp_selection_sharpen(img)
        pdb.gimp_selection_flood(img)
        pdb.gimp_edit_copy(layer)
        fsel = pdb.gimp_edit_paste(layer, False)
        new = pdb.gimp_floating_sel_to_layer(fsel)
        theNewLayer = img.active_layer
        Export.export_layers(img, theNewLayer, output_path, name, ext)
        img.remove_layer(theNewLayer)
        img.active_layer = layer

    @staticmethod
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
class Transitions:

    @staticmethod
    def make_transitions_from_base_tile(img, layer, tileW, tileH):
        src = layer.name
        img.resize(tileW*4, tileH*4+tileH/2,tileW, tileH)
        #left corner
        Transitions.make_tile(img, src, transitions_prefix + "lle", 0, tileH)
        #right corner
        Transitions.make_tile(img, src, transitions_prefix + "ure", 2*tileW, tileH)
        #up edge
        Transitions.make_tile(img, src, transitions_prefix + "ue", tileW+tileW/2, tileH/2)
        #right edge
        Transitions.make_tile(img, src, transitions_prefix + "re", tileW+tileW/2, tileH + tileH/2)
        #left edge
        Transitions.make_tile(img, src, transitions_prefix + "le", tileW/2, tileH/2)
        #down edge
        Transitions.make_tile(img, src, transitions_prefix + "de", tileW/2, tileH + tileH/2)
        #lower right corner
        Transitions.make_tile(img, src, transitions_prefix + "lre", tileW, 2 * tileH)
        #upper left corner
        Transitions.make_tile(img, src, transitions_prefix + "ule", tileW, 0)
        Transitions.merge_transitions(img, transitions_prefix, transitions_layer)        

    @staticmethod
    def make_tile(img, src, name, x , y):
        base = next(z for z in img.layers if z.name == src )
        layer = base.copy()
        layer.name = name
        layer.set_offsets(x, y)
        img.add_layer(layer, 0)
        return layer

    @staticmethod
    def merge_transitions(img, withPrefix, destLayer):
        for l in img.layers:
            if l.name.startswith(withPrefix):
                pdb.gimp_drawable_set_visible(l, True)
            else:
                pdb.gimp_drawable_set_visible(l, False)
        allTrans = pdb.gimp_image_merge_visible_layers(img, 0)
        allTrans.name = destLayer
        pdb.gimp_layer_resize_to_image_size(allTrans)

    @staticmethod       
    def select_transition(img, layer, tileName, tileW, tileH, grow=0):
        sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
        pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
        pdb.gimp_selection_grow(img,grow)
        
###########################################################
#
#
###########################################################
class Tiles:

    @staticmethod
    def get_tile_slice(img, tileName, sliceType, tileW, tileH):
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
        return sel

    @staticmethod
    def make_seamless_corner(img, sourceLayer, destLayer, cornerType, tileW, tileH, dictionary):
        edges = dictionary[cornerType][0]
        sliceType = dictionary[cornerType][1]
        corner_layers = []

        #Hide the tile where the corner is supposed to be created
        Transitions.select_transition(img, destLayer, cornerType, tileW, tileH)
        #pdb.gimp_selection_sharpen(img)

        for index in range(len(edges)):
            #select and copy slice
            ss = Tiles.get_tile_slice(img, edges[index], sliceType[index], tileW, tileH)
            pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(ss),ss)
            pdb.gimp_selection_sharpen(img)
            pdb.gimp_selection_flood(img)
            pdb.gimp_edit_copy(sourceLayer)

            #paste slice
            selId= pdb.gimp_edit_paste(destLayer, False)
            pdb.gimp_floating_sel_to_layer(selId)
            pos = pdb.gimp_drawable_offsets(selId)
            #move it 
            ds = Tiles.get_tile_slice(img, cornerType, sliceType[index], tileW, tileH)

            pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(ds),ds)
            pdb.gimp_selection_sharpen(img)
            pdb.gimp_selection_flood(img)
            #pdb.gimp_selection_grow(img,1)
            pdb.gimp_edit_cut(destLayer)
            
            dx = ds[0]-ss[0]
            dy = ds[1]-ss[1]

            #if sliceType[index] == "sw":
            #    dx -= 1
            #    dy += 1
            #if sliceType[index] == "ne":
            #    dy -= 1
            #if sliceType[index] == "nw":
            #    dy -= 1                
            
            pdb.gimp_layer_set_offsets(selId, pos[0]+dx, pos[1]+dy)
            corner_layers.append(selId)

        layer = Util.merge_layers(img,corner_layers)
        layer.name = cornerType
        return layer

    @staticmethod
    def make_seamless_tile(img, layer, tileName, tileW, tileH, dir):
        sel = eval("get_" + tileName+ "_selection(tileW, tileH)")
        pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
        pdb.gimp_selection_sharpen(img)
        pdb.gimp_edit_copy(layer)    
        top_half = pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_to_layer(top_half)
        
        #pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
        bottom_half = pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_to_layer(bottom_half)

        if dir == "tldr":
            pdb.gimp_drawable_offset(top_half, False, 1, +tileW/4, +tileH/4)
            pdb.gimp_drawable_offset(bottom_half, False, 1, -tileW/4, -tileH/4)
        else:
            pdb.gimp_drawable_offset(top_half, False, 1, -tileW/4, +tileH/4)
            pdb.gimp_drawable_offset(bottom_half, False, 1, tileW/4, -tileH/4)

        combined_layer = pdb.gimp_image_merge_down(img, top_half, 2)
        pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE,len(sel),sel)
        pdb.gimp_selection_sharpen(img)
        pdb.gimp_selection_flood(img)
        pdb.gimp_selection_invert(img)
        pdb.gimp_edit_cut(combined_layer)
        return combined_layer
    
    @staticmethod
    def make_outside_corners(img, sourceLayer, destLayer, tileW, tileH):
        corners = []
        dictionary = {
            "lle" : ( ["le","de"], ["ne","se"] ),
            "ule" : ( ["le","ue"], ["sw","se"] ),
            "ure" : ( ["ue","re"], ["nw","sw"] ),
            "lre" : ( ["re","de"], ["ne","nw"] )
        }
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "lle", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ule", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ure", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "lre", tileW, tileH, dictionary))
        return Util.merge_layers(img,corners)

    @staticmethod
    def make_inside_corners(img, sourceLayer, destLayer, tileW, tileH):
        corners = []
        dictionary = {
            "ic_n" : ( ["ue","le"], ["nw","ne"] ),
            "ic_s" : ( ["re","de"], ["sw","se"] ),
            "ic_e" : ( ["re","ue"], ["ne","se"] ),
            "ic_w" : ( ["de","le"], ["nw","sw"] )
        }
                
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ic_n", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ic_s", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ic_e", tileW, tileH, dictionary))
        corners.append(Tiles.make_seamless_corner(img, sourceLayer, destLayer, "ic_w", tileW, tileH, dictionary))
        return Util.merge_layers(img,corners)

    @staticmethod
    def make_seamless(img, layer, tileW, tileH):
        corners = []
        corners.append(Tiles.make_seamless_tile(img, layer, "le" , tileW, tileH, ""))
        corners.append(Tiles.make_seamless_tile(img, layer, "ue" , tileW, tileH, "tldr"))
        corners.append(Tiles.make_seamless_tile(img, layer, "re" , tileW, tileH, ""))
        corners.append(Tiles.make_seamless_tile(img, layer, "de" , tileW, tileH, "tldr"))
        dest_layer = Util.merge_layers(img,corners)
        pdb.gimp_layer_resize_to_image_size(dest_layer)
        
        outside_corners = Tiles.make_outside_corners(img,dest_layer,dest_layer,tileW,tileH)
        pdb.gimp_layer_resize_to_image_size(outside_corners)
        dest_layer = Util.merge_layers(img,[outside_corners, dest_layer])
        img.active_layer = dest_layer
        

    @staticmethod
    def make_seamless_inside_corners(img, layer, tileW, tileH):
        src = 'base'
        icn = Transitions.make_tile(img, src, transitions_prefix + "ic_n", 2*tileW+tileW/2, 2*tileH+tileH/2)
        ics = Transitions.make_tile(img, src, transitions_prefix + "ic_s", 2*tileW+tileW/2, 3*tileH+tileH/2)
        ice = Transitions.make_tile(img, src, transitions_prefix + "ic_e", 3*tileW, 3*tileH)
        icw = Transitions.make_tile(img, src, transitions_prefix + "ic_w", 2*tileW, 3*tileH)
        
        pdb.gimp_drawable_set_visible(icn, True)
        pdb.gimp_drawable_set_visible(ics, True)
        pdb.gimp_drawable_set_visible(ice, True)
        pdb.gimp_drawable_set_visible(icw, True)
        Util.merge_layers(img,[icw, ice, ics, icn])
        
        work_layer = img.active_layer
        pdb.gimp_layer_resize_to_image_size(work_layer)
        
        inside_corners = Tiles.make_inside_corners(img,layer, work_layer,tileW,tileH)
        pdb.gimp_layer_resize_to_image_size(inside_corners)
        dest_layer = Util.merge_layers(img,[inside_corners, work_layer])

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
         Transitions.select_transition,
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
         Transitions.make_transitions_from_base_tile,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_make_seamless",
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
         Tiles.make_seamless,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_make_seamless_inside_corners",
         N_("Make Seamless Inside Corners"),
         """Make Seamless Inside Corners""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_3. Make Seamless Inside Corners..."),
         "*",
         [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "layer", "Input layer", None),
          (PF_INT, "tileW", "Tile Width", 128),
          (PF_INT, "tileH", "Tile Height", 64)
          ],
         [],
         Tiles.make_seamless_inside_corners,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

register(
         "python_fu_export_transitions",
         N_("Export Tile Transitions"),
         """Export Tile Transitions""",
         "Alex Cotoman",
         "Alex Cotoman",
         "2019",
         _("_4. Export Transitions..."),
         "*",
         [
            (PF_IMAGE, "image", "Input image", None),
            (PF_STRING, "layer_name", "Prefx of the layer to Export", transitions_layer),
            (PF_INT, "tileW", "Tile Width", 128),
            (PF_INT, "tileH", "Tile Height", 64),
            (PF_DIRNAME, "output_path", _("Output Path"), os.getcwd())
         ],
         [],
         Export.export_transitions,
         menu="<Image>/Filters/Alex's/Tile Library",
         domain=("gimp20-python", gimp.locale_directory))

main()
