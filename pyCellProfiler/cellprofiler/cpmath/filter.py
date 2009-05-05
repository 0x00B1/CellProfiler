'''filter.py - functions for applying filters to images

CellProfiler is distributed under the GNU General Public License.
See the accompanying file LICENSE for details.

Developed by the Broad Institute
Copyright 2003-2009

Please see the AUTHORS file for credits.

Website: http://www.cellprofiler.org
'''
__version__="$Revision: 1 "

import numpy as np
import _filter
from rankorder import rank_order

def stretch(image, mask=None):
    '''Normalize an image to make the minimum zero and maximum one
    
    image - pixel data to be normalized
    mask  - optional mask of relevant pixels. None = don't mask
    
    returns the stretched image
    '''
    if np.product(image.shape) == 0:
        return image
    if mask is None:
        minval = np.min(image)
        maxval = np.max(image)
        if minval == maxval:
            return image
        else:
            return (image - minval) / (maxval - minval)
    else:
        significant_pixels = image[mask]
        minval = np.min(significant_pixels)
        maxval = np.max(significant_pixels)
        if minval == maxval:
            transformed_image = minval
        else:
            transformed_image = ((significant_pixels - minval) /
                                 (maxval - minval))
        result = image.copy()
        image[mask] = transformed_image
        return image

def median_filter(data, mask, radius, percent=50):
    '''Masked median filter with octagonal shape
    
    data - array of data to be median filtered.
    mask - mask of significant pixels in data
    radius - the radius of a circle inscribed into the filtering octagon
    percent - conceptually, order the significant pixels in the octagon,
              count them and choose the pixel indexed by the percent
              times the count divided by 100. More simply, 50 = median
    returns a filtered array
    '''
    #
    # Normalize the ranked data to 0-255
    #
    if (not np.issubdtype(data.dtype, np.int) or
        np.min(data) < 0 or np.max(data) > 255):
        ranked_data,translation = rank_order(data[mask])
        max_ranked_data = np.max(ranked_data)
        if max_ranked_data == 0:
            return data
        if max_ranked_data > 255:
            ranked_data = ranked_data * 255 / max_ranked_data
        was_ranked = True
    else:
        ranked_data = data[mask]
        was_ranked = False
    input = np.zeros(data.shape, np.uint8 )
    input[mask] = ranked_data
    
    mmask = np.ascontiguousarray(mask, np.uint8)
    
    output = np.zeros(data.shape, np.uint8)
    
    _filter.median_filter(input, mmask, output, radius, percent)
    if was_ranked:
        #
        # The translation gives the original value at each ranking.
        # We rescale the output to the original ranking and then
        # use the translation to look up the original value in the data.
        #
        if max_ranked_data > 255:
            result = translation[output.astype(np.uint32) * max_ranked_data / 255]
        else:
            result = translation[output]
    else:
        result = output
    not_mask = np.logical_not(mask)
    result[not_mask] = data[not_mask] 
    return result
    