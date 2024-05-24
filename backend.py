import numpy as np
import colorspacious
colorspace = 'CAM02-LCD'

def set_ab_rot(Jab, ar, br, rot):
    '''
    sets the [:,:,1] and [:,:,2] axes of a Jab colormap to ar and br
    then rotates the ab color plane according to the angle rot

    Args:
        Jab: (l,l,3) colormap
        ar: 1d array, typically made by np.linspace()
        br: 1d array, typically made by np.linspace()
        rot: angle in degrees
    returns:
        None (but Jab changed in-place)
    '''

    if rot==0:
        Jab[:,:,1] = ar[:,np.newaxis]
        Jab[:,:,2] = br[np.newaxis,:]
    else:
        ab = np.sqrt(ar[:,np.newaxis]**2+br[np.newaxis,:]**2)
        Jab[:,:,1] = ar[:,np.newaxis]
        Jab[:,:,2] = br[np.newaxis,:]
        phi = np.arctan2(Jab[:,:,1],Jab[:,:,2])+rot*np.pi/180
        Jab[:,:,2] = ab*np.cos(phi)
        Jab[:,:,1] = ab*np.sin(phi)

def get_var_J(J = [95,128.5], a = (-1,1), b = (-1,1), r = 33.0, l=256, rot = 0,
             gamma = 1):
    '''
    Generates am rgb colormap of (l,l,3) that attempts to keep a constant lightness in the CAM02-LCD colorspace
    The colormap is based on the a-b plane of the Jab colorspace for a constant J.

    Args:
        J: (lighness) tuple of 2 floats, default [95,128.5] defining the range of lightness for the colormap, default 95,
            max range of J approximately 1 to 128.5
        a: tuple of 2 floats, default (-1,1). The limit along the a-axis will be (a[0]*r,a[1]*r)
        b: tuple of 2 floats, default (-1,1). The limit along the b-axis will be (b[0]*r,b[1]*r)
        r: float, default 33.0. The saturation where a or b is 1. (named 'r' for radius in the a-b plane)
        l: int, default 256. Size of the colormap.
        mask: string, default 'no_mask'.
                If 'circle' makes a circular mask, and everything outside will be np.nan
                If 'unavailable' makes a colors that "should" have rgb<0 or rgb>1 when transformed to sRGB will be np.nan
        rot: rotation of the hues on the a-b plane, in degrees

    returns:
        a (l,l,3) numpy array of rgb values
    '''

    Jab = np.zeros((l,l,3))
    ar = np.linspace(r*a[0], r*a[1],l)
    br = np.linspace(r*b[0], r*b[1],l)
    set_ab_rot(Jab, ar, br, rot)
    ab = np.sqrt(ar[:,np.newaxis]**2+br[np.newaxis,:]**2)

    a_1 = np.linspace(a[0], a[1],l)
    b_1 = np.linspace(b[0], b[1],l)

    Jab[:,:,0] = J[1] -(J[1]-J[0])*(np.sqrt(a_1[:,np.newaxis]**2+b_1[np.newaxis,:]**2))**(gamma)
    Jab[Jab[:,:,0]<1,0] = 1
    Jab[Jab[:,:,0]>128,0] = 128
    rgb = colorspacious.cspace_convert(Jab, colorspace, "sRGB1")


    rgb[rgb[:,:,:]<0] = 0
    rgb[rgb[:,:,:]>1] = 1

    #print(r)
    return rgb