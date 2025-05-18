import tkinter as tk                #tkinter include for UI
from PIL import Image, ImageTk      #Pillow required for place/resize image

#key values/defines
bg_color =              '#636363'   #dark grey-ish color for background
lbl_fg_color =          '#00FF00'   #normal label foreground color
lbl_otln_color =        '#00FF00'   #normal outline color
ind_on_color =          '#00FF00'   #indicator "on" color
ind_off_color =         bg_color    #indicator "off" color
alert_lbl_fg_color =    '#000000'   #label foreground color when alterting an out of bounds value
warn_color =            '#FFFF00'   #yellow color for warning
dngr_color =            '#FF0000'   #red color for danger/error

default_font_sz =       45                              #default font size (pt not px)
small_font_sz =         36                              #small font size
tiny_font_sz =          24                              #tiny font size
default_font =          ("Helvetica",default_font_sz, "bold")   #default font and size
default_font_sm =       ("Helvetica",small_font_sz, "bold")     #small font and size
sniffer_font =          ("Helvetica",tiny_font_sz, "bold")      #font for CAN sniffer window
noPad_height =          default_font_sz*16/12-10        #label height with no vertical padding
noPad_height_sm =       small_font_sz*16/12-6           #label height with no vertical padding

class draw_funcs:
    def __init__(self):
        #TODO: any init things
        pass

    ''' @brief: draw rounded edge rectangle
        @param: canv    - canvas object rectangle is being placed on
                x0, y0  - initial anchor points (*of the top-left corner)
                w,h     - width and height
                r       - corner radius
        @notes: default kwargs set to standard values
        @retrn: rounded rectangle object  
    '''
    def draw_round_rect(self, canv, x0, y0, w, h, r=20, **kwargs):
        #special thanks to SneakyTurtle on stackoverflow for this
        #remeber with **kwargs any of the default options works
        x1=x0+w; y1=y0+h
        points = [  x0+r, y0, x0+r, y0,
                    x1-r, y0, x1-r, y0,
                    x1, y0,
                    x1, y0+r, x1, y0+r,
                    x1, y1-r, x1, y1-r,
                    x1, y1,
                    x1-r, y1, x1-r, y1,
                    x0+r, y1, x0+r, y1,
                    x0, y1,
                    x0, y1-r, x0, y1-r,
                    x0, y0+r, x0, y0+r,
                    x0, y0]
        
        #do some default appearance assignments via kwargs
        kwargs.setdefault("width", 3)
        kwargs.setdefault("fill", bg_color)

        return canv.create_polygon(points, smooth = True, **kwargs) #return created polygon
    
    ''' @brief: draw cicle
        @param: canv    - canvas object rectangle is being placed on
                x0, y0  - initial anchor points (*of the top-left corner)
                scale   - x/y size scale (in pixels) to get to x1, y1
        @notes: modified from the draw elipse to just have a square scale
        @retrn: circle canvas object 
    '''
    def draw_circle(self, canv, x0, y0, scale, **kwargs):
        #default kwarg assignments
        kwargs.setdefault("width", 3)
        kwargs.setdefault("fill", bg_color)
        kwargs.setdefault("outline", lbl_otln_color)
        return canv.create_oval(x0,y0,x0+scale, y0+scale, **kwargs) #return circle object
    
    ''' @brief: draw text label
        @param: scope   - window or scope the tkinter object is being created in
                txt     - text to be hard-fixed to the label (if its a static label)
                strvar  - stringVar to be assigned to the label (for dynamic labels)
        @notes: modified from the draw elipse to just have a square scale
        @retrn: label object 
    '''
    def draw_txt_lbl(self, scope, txt=None, strvar=None, **kwargs):
        tmp_lbl = tk.Label(scope)                                   #create temp label

        #do some default appearance assignments via kwargs
        kwargs.setdefault("font", default_font) 
        kwargs.setdefault("fg", lbl_fg_color)    
        kwargs.setdefault("bg", bg_color)       
        kwargs.setdefault("anchor", "w")

        tmp_lbl.config(**kwargs)                                    #apply configuration
        if txt is not None: tmp_lbl.config(text=txt.upper())        #assign text if passed
        if strvar is not None: tmp_lbl.config(textvariable=strvar)  #and/or bind label to if passed
        return tmp_lbl
    
    ''' @brief: place image
        @param: canv    - canvas object rectangle is being placed on
                x, y    - anchor points (*of the top-left corner)
                h_scale - height scale of desired output
        @notes: the height scale is passed and then for non-square images
                the width-scale is calculated. It's not exact but is 
                "rounded" via truncation to the closest value.
        @retrn: image canvas object 
    '''
    def make_image(self, img, h_scale=None):
        self.i_img = i_img = Image.open(img)                        #open passed image
        if h_scale is not None:                                     #rescale image
            w_scale = int(i_img.width*h_scale / i_img.height)       #get width scale
            self.r_img = r_img = i_img.resize((w_scale,h_scale))    #and resize
        else: self.r_img = r_img = i_img                            #otherwise leave native size
        self.tmp_img = tmp_img = ImageTk.PhotoImage(r_img)          #create tk Image after any modification
        return ImageTk.PhotoImage(r_img)                            #return image object
    
drw_func = draw_funcs()
