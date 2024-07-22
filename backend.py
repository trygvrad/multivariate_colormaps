import numpy as np
import colorspacious
import matplotlib.pyplot as plt
colorspace = 'CAM02-LCD'

def set_ab_rot(Jab, ar, br, rot, sat_gamma):
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

    ab = np.sqrt(ar[:,np.newaxis]**2 + br[np.newaxis,:]**2)**sat_gamma
    Jab[:,:,1] = ar[:,np.newaxis]
    Jab[:,:,2] = br[np.newaxis,:]
    phi = np.arctan2(Jab[:,:,1], Jab[:,:,2]) + rot*np.pi/180
    Jab[:,:,2] = ab*np.cos(phi)
    Jab[:,:,1] = ab*np.sin(phi)

def get_var_J(J = [95,128.5], a = (-1,1), b = (-1,1), r = 33.0, l=256, rot = 0,
             gamma = 1, sat_gamma = 1):
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
    ar = np.linspace(a[0], a[1],l)
    br = np.linspace(b[0], b[1],l)
    set_ab_rot(Jab, ar, br, rot, sat_gamma)
    Jab *= r
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

def eval(cmap, axes = None):
    '''
    plots the colormap overlaid with contour plots of J, hue and sat and simulated partial colorblindness
    (partial deuteranomaly appears to be the most common kind https://en.wikipedia.org/wiki/Color_blindness)

    Args:
        axes: default None, alternatively a list of 5 matplotlib axes
            if None, a fig with 5 axes will be created
    returns:
        fig, axes if axes are not declared as input, otherwise None
    '''

    if axes is None:
        fig, axes = plt.subplots(1,5, figsize = (10,2))
    axes = axes.ravel()
    for ax in axes:
            ax.set_xticks([])
            ax.set_yticks([])

    axes[0].imshow(cmap, origin = 'lower')


    rgb = np.nan_to_num(cmap)
    Jab = colorspacious.cspace_convert(rgb, "sRGB1", colorspace)
    phi = np.arctan2(Jab[:,:,1],Jab[:,:,2])
    sat = np.sqrt(Jab[:,:,1]**2 + Jab[:,:,2]**2)


    for ax in axes[1:4]:
        ax.imshow(cmap, origin = 'lower', alpha = 0.5)
    lw = 0.5
    axes[1].contour(Jab[:,:,0], levels = 21, colors = [[0,0,0]], linewidths = lw)
    axes[1].set_title('J')
    #axes[4].contour(Jab[:,:,1], levels = 21, colors = [[0,0,0]], linewidths = lw)
    #axes[4].set_title('a')
    #axes[5].contour(Jab[:,:,2], levels = 21, colors = [[0,0,0]], linewidths = lw)
    #axes[5].set_title('b')

    axes[2].contour(phi, levels = 21, colors = [[0,0,0]], linewidths = lw)
    axes[2].set_title('hue')
    axes[3].contour(sat, levels = 21, colors = [[0,0,0]], linewidths = lw)
    axes[3].set_title('saturation')

    cvd_space = {"name": "sRGB1+CVD",
                "cvd_type": "deuteranomaly",
                "severity": 100}
    deuteranomaly = colorspacious.cspace_convert(cmap, cvd_space, "sRGB1")
    deuteranomaly[deuteranomaly<0] = 0
    deuteranomaly[deuteranomaly>1] = 1

    axes[4].imshow(deuteranomaly, origin = 'lower')
    axes[4].set_title('100% Deuteranomaly')

    if 'fig' in locals():
        fig.patch.set_facecolor('white')
        return fig, axes