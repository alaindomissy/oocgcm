#!/usr/bin/env python
#
"""oocgcm.core.grids.
Define classes that give acces to model grid metrics and operators.

"""

import numpy as np
import xarray as xr
import xarray.ufuncs as xu # ufuncs like np.sin for xarray


#======================== Working with DataArray ===============================
#
def finalize_dataarray_attributes(arr,**kwargs):
    """Update the dictionary of attibutes of a xarray dataarray.
    """
    if isinstance(arr, xr.DataArray):
        arr.attrs.update(kwargs)
    if arr.attrs.has_key('short_name'):
        arr.name = arr.attrs['short_name']
    return arr

def convert_dataarray_attributes_xderivative(attrs,grid_location=None):
    """Return the dictionary of attributes corresponding to spatial derivative
    in the x-direction
    """
    new_attrs = attrs.copy()
    if attrs.has_key('long_name'):
        new_attrs['long_name'] = 'x-derivative of ' + attrs['long_name']
    if attrs.has_key('short_name'):
        new_attrs['short_name'] = 'd_' + attrs['short_name'] + '_dx'
    if attrs.has_key('units'):
        new_attrs['units'] = attrs['units'] + '/m'
    if grid_location is not None:
        new_attrs['grid_location'] = grid_location
    return new_attrs

def convert_dataarray_attributes_yderivative(attrs,grid_location=None):
    """Return the dictionary of attributes corresponding to spatial derivative
    in the y-direction
    """
    new_attrs = attrs.copy()
    if attrs.has_key('long_name'):
        new_attrs['long_name'] = 'y-derivative of ' + attrs['long_name']
    if attrs.has_key('short_name'):
        new_attrs['short_name'] = 'd_' + attrs['short_name'] + '_dy'
    if attrs.has_key('units'):
        new_attrs['units'] = attrs['units'] + '/m'
    if grid_location is not None:
        new_attrs['grid_location'] = grid_location
    return new_attrs

def convert_dataarray_attributes_laplacian(attrs,grid_location='t'):
    """Return the dictionary of attributes corresponding to horiz. laplacian
    """
    new_attrs = attrs.copy()
    if attrs.has_key('long_name'):
        new_attrs['long_name'] = 'horizontal laplacian of ' + attrs['long_name']
    if attrs.has_key('short_name'):
        new_attrs['short_name'] = 'hlap_' + attrs['short_name']
    if attrs.has_key('units'):
        new_attrs['units'] = attrs['units'] + '/m2'
    if grid_location is not None:
        new_attrs['grid_location'] = grid_location
    return new_attrs

def convert_dataarray_attributes_divergence(attrs1,attrs2,grid_location='t'):
    """Return the dictionary of attributes corresponding to divergence of a
    vector field.
    """
    new_attrs = attrs1.copy()
    if attrs1.has_key('long_name') and attrs2.has_key('long_name'):
        new_attrs['long_name'] = \
           'horizontal divergence of ('\
           + attrs1['long_name'] + ','\
           + attrs2['long_name'] + ')'
    if attrs1.has_key('short_name') and attrs2.has_key('short_name'):
            new_attrs['short_name'] = 'div_()' + attrs1['short_name'] + ','\
                                               + attrs1['short_name'] + ')'
    if attrs1.has_key('units'):
            new_attrs['units'] = attrs1['units'] + '/m'
    if grid_location is not None:
        new_attrs['grid_location'] = grid_location
    return new_attrs

def assert_chunks_are_compatible(chunks1=None,chunks2=None,ndims=None):
    """Return True when two chunks are aligned over their common dimensions.
    """
    test = True
    if (chunks1 is None) or (chunks2 is None):
        if (chunks1 is None) and (chunks2 is None):
            return True
        else:
            return False
    for idim in range(ndims):
        test *= chunks1[-idim-1] == chunks2[-idim-1]
    return test

def assert_grid_location(xarr,grid_location=None):
    """Return True when the xarr grid_location attribute is grid_location
    """
    test = True
    if xarr.attrs.has_key('grid_location'):
        test *= (xarr.attrs['grid_location']==grid_location)
    return test

def check_input_array(xarr,shape=None,chunks=None,\
                      grid_location=None,ndims=None):
    """Returns true if arr is a dataarray with expected shape, chunks at
    grid_location attribute. Otherwise raise errors.
    """
    if hasattr(xarr,'name'):
       arrayname = xarr.name
    else:
       arrayname = 'array'
    if not(isinstance(xarr,xr.DataArray)):
        raise TypeError(arrayname + 'is expected to be a xarray.DataArray')
        return False
    if not(assert_chunks_are_compatible(xarr.chunks,chunks,ndims=ndims)):
        raise ChunkError()
        return False
    if not(assert_grid_location(xarr,grid_location)):
        raise GridLocationError()
        return False
    return True

#========================== Data structures ====================================
#

# a data structure for vector field.
#
from collections import namedtuple


def assert_and_set_grid_location_attribute(xarr,grid_location=None):
    """Assert whether xarr holds an extra attribute 'grid_location' that
    equals grid_location. If xarr does not have such extra-attribute, create
    one with value grid_location.

    Parameters
    ----------
    xarr : xarray.DataArray
        xarray dataarray that should be associated with a grid location
    grid_location : str
        string describing the grid location : eg 'u','v','t','f'...
    """
    if xarr.attrs.has_key('grid_location'):
        assert ( xarr.attrs['grid_location'] == grid_location )
    else:
        xarr.attrs['grid_location'] = grid_location

def VectorField2d(vx,vy,\
                  x_component_grid_location=None,\
                  y_component_grid_location=None):
    """Minimal data structure for manupulating 2d vector fields on a grid.

    Parameters
    ----------
    vx : xarray.DataArray
        x-component of the vector fields
    vy : xarray.DataArray
        y-component of the vector fields
    x_component_grid_location : str
        string describing the grid location of the x-component
    y_component_grid_location : str
        string describing the grid location of the y-component

    Returns
    -------
    o : namedtuple
       namedtuple containing the vector field.
    """
    v = namedtuple('VectorField2d',['x_component','y_component',\
                                    'x_component_grid_location',\
                                    'y_component_grid_location'])
    #
    assert_and_set_grid_location_attribute(vx,x_component_grid_location)
    assert_and_set_grid_location_attribute(vy,y_component_grid_location)
    #
    o = v(vx,vy,x_component_grid_location,y_component_grid_location)
    return o

def VectorField3d(vx,vy,vz,\
                  x_component_grid_location=None,\
                  y_component_grid_location=None,\
                  z_component_grid_location=None):
    """Minimal data structure for manupulating 3d vector fields on a grid.

    Parameters
    ----------
    vx : xarray.DataArray
        x-component of the vector fields
    vy : xarray.DataArray
        y-component of the vector fields
    vz : xarray.DataArray
        z-component of the vector fields
    x_component_grid_location : str
        string describing the grid location of the x-component
    y_component_grid_location : str
        string describing the grid location of the y-component
    z_component_grid_location : str
        string describing the grid location of the z-component

    Returns
    -------
    o : namedtuple
           namedtuple containing the vector field.
    """
    v = namedtuple('VectorField3d',['x_component','y_component','z_component',\
                                    'x_component_grid_location',\
                                    'y_component_grid_location',\
                                    'z_component_grid_location'])
    #
    assert_and_set_grid_location_attribute(vx,x_component_grid_location)
    assert_and_set_grid_location_attribute(vy,y_component_grid_location)
    assert_and_set_grid_location_attribute(vz,z_component_grid_location)
    #
    o = v(vx,vy,vz,\
          x_component_grid_location,\
          y_component_grid_location,\
          z_component_grid_location)
    return o

def Tensor2d(axx,axy,ayx,ayy,\
             xx_component_grid_location=None,\
             xy_component_grid_location=None,\
             yx_component_grid_location=None,\
             yy_component_grid_location=None):
    """Minimal data structure for manupulating 2d tensors on a grid.

    use the following notations :
                | axx   axy|
            T = |          |
                | ayx   ayy|
    Parameters
    ----------
    axx : xarray.DataArray
        xx-component of the tensor
    axy : xarray.DataArray
        xy-component of the tensor
    ayx : xarray.DataArray
        yx-component of the tensor
    ayy : xarray.DataArray
        yy-component of the tensor
    xx_component_grid_location : str
        string describing the grid location of the xx-component
    xy_component_grid_location : str
        string describing the grid location of the xy-component
    yx_component_grid_location : str
        string describing the grid location of the yx-component
    yy_component_grid_location : str
        string describing the grid location of the yy-component

    Returns
    -------
    o : namedtuple
           namedtuple containing the tensor field.
    """
    t = namedtuple('Tensor2d',['xx_component','xy_component',\
                               'yx_component','yy_component',\
                               'xx_component_grid_location',\
                               'xy_component_grid_location',\
                               'yx_component_grid_location',\
                               'yy_component_grid_location'])
    #
    if axx.attrs.has_key('grid_location'):
        assert (axx.attrs['grid_location'] == xx_component_grid_location )
    else:
        axx.attrs['grid_location'] = xx_component_grid_location
    #
    assert_and_set_grid_location_attribute(axx,xx_component_grid_location)
    assert_and_set_grid_location_attribute(axy,xy_component_grid_location)
    assert_and_set_grid_location_attribute(ayx,yx_component_grid_location)
    assert_and_set_grid_location_attribute(ayy,yy_component_grid_location)
    #
    o = t(axx,axy,ayx,ayy,\
          xx_component_grid_location,xy_component_grid_location,\
          yx_component_grid_location,yy_component_grid_location)
    return o

#========================== Minimal exceptions =================================
# TODO : should probably move to a dedicated file oocgcm.core.exceptions.py
#
class ChunkError(Exception):
    def __init__(self):
        Exception.__init__(self,"incompatible chunk size")

class GridLocationError(Exception):
    def __init__(self):
        Exception.__init__(self,"incompatible grid_location")

#======================== Generic 2D Grid Class ================================
class generic_2d_grid:
    """Model agnostic grid object, two dimensional version.

    This class holds the arrays that describe the grid and
    implements grid related methods including :
        - vector calculus
        - differential operators (gradient, divergence, etc...)
        - spatial integration

    Methods expect and return xarray dataarrays.

    Assume that dimension names ar 'x' and 'y'.
    """
    # TODO : keep _variables and _methods up to date.
    _required_variables = [\
       ]
    _available_methods = [\
         "rechunk", "__getitem__"\
        ,"d_i","d_j"\
       ]
    def __init__(self,variables=None,parameters=None):
        """Initialize grid from dictionary of variables.
        """
        self.arrays = variables
        self.parameters = parameters
        self._define_aliases_for_arrays()
        self.chunks = self.arrays["sea_binary_mask_at_t_location"].chunks
        # TODO : what chunk should we use ?
        self.shape  = self.arrays["sea_binary_mask_at_t_location"].shape
        self.dims   = self.arrays["sea_binary_mask_at_t_location"].dims
        self.ndims = len(self.dims)

#--------------------- Aliases for DataArrays ----------------------------------
    def _define_aliases_for_arrays(self):
        """Define alias for frequently used variables.
        This mostly follows nemo name conventions and will evolve in the future.
        """
        # coordinates
        self.array_navlon = self.arrays["projection_x_coordinate_at_t_location"]
        self.array_navlat = self.arrays["projection_y_coordinate_at_t_location"]
        # metrics
        self.array_e1t = self.arrays["cell_x_size_at_t_location"]
        self.array_e1u = self.arrays["cell_x_size_at_u_location"]
        self.array_e1v = self.arrays["cell_x_size_at_v_location"]
        self.array_e2t = self.arrays["cell_y_size_at_t_location"]
        self.array_e2u = self.arrays["cell_y_size_at_u_location"]
        self.array_e2v = self.arrays["cell_y_size_at_v_location"]

        # masks
        self.array_tmask = self.arrays["sea_binary_mask_at_t_location"]
        self.array_umask = self.arrays["sea_binary_mask_at_u_location"]
        self.array_vmask = self.arrays["sea_binary_mask_at_v_location"]
        self.array_fmask = self.arrays["sea_binary_mask_at_f_location"]

#--------------------- Chunking and Slicing ------------------------------------
    def rechunk(self,chunks=None):
        """Rechunk all the variables defining the grid.
        """
        for dataname in self.arrays:
            data = self.arrays[dataname]
            if isinstance(data, xr.DataArray):
                self.arrays[dataname] = data.chunk(chunks)
        self.chunks = self.array_tmask.chunks

    def __getitem__(self,item):
        """Return a grid object restricted to a subdomain.
        """
        sliced_arrays = {}
        for dataname in self.arrays:
            sliced_arrays[dataname] = self.arrays[dataname][item]
        return generic_2d_grid(variables=sliced_arrays,\
                             parameters=self.parameters)

#---------------------------- Grid Swapping ------------------------------------
#- Core swapping utilities
    def _grid_i_to_ip1(self,var,weights=None):
        """
        """
        pass

#---------------------------- Vector Operators ---------------------------------
    def norm_of_vector_field(self,a):
        """Return the norm of a vector field a at t-point.
        """
        return xu.sqrt(self.scalar_product(a,a))

    def scalar_product(self,a,b):
        """Return the scalar product of two vector fields a and b at t-point.
        """
        pass

    def scalar_outer_product(self,q,a):
        """Return the outer product of a scalar q with the vector a at t-point.
        """
        pass

    def vertical_component_of_vector_cross_product(self,a,b):
        """Return the cross product of two vector fields a and b.
        """
        pass

#-------------------- Differences and Averages ---------------------------------
    def d_i(self,q):
        """Return the difference q(i+1) - q(i)
        """
        di = q.shift(x=-1) - q
        return di

    def d_j(self,q):
        """Return the difference q(j+1) - q(j)
        """
        dj = q.shift(y=-1) - q
        return dj


    def m_i(self,q):
        """Return the average of q(i+1) and q(i)
        """
        pass

    def m_j(self,q):
        """Return the average of q(j+1) and q(j)
        """
        pass

#-------------------- Differential Operators------------------------------------
    def horizontal_gradient(self,q):
        """
        Return the horizontal gradient of a scalar field at t-points.
        """
        # check
        check_input_array(q,\
                          chunks=self.chunks,grid_location='t',ndims=self.ndims)
        # define
        gx = self.d_i(q) / self.array_e1u
        gy = self.d_j(q) / self.array_e2v
        # finalize attributes
        gxatts = \
            convert_dataarray_attributes_xderivative(q.attrs,grid_location='u')
        gyatts = \
            convert_dataarray_attributes_yderivative(q.attrs,grid_location='v')
        #
        gx = finalize_dataarray_attributes(gx,**gxatts)
        gy = finalize_dataarray_attributes(gy,**gyatts)
        #
        return VectorField2d(gx,gy,\
                             'x_component_grid_location' = 'u',\
                             'y_component_grid_location' = 'v')

    def horizontal_laplacian(self,q):
        """
        Return the horizontal laplacian of a scalar field at t-points.
        """
        # check
        check_input_array(q,\
                          chunks=self.chunks,grid_location='t',ndims=self.ndims)
        # define
        lap = self.horizontal_divergence(self.horizontal_gradient(q))
        # finalize
        lapatts = \
            convert_dataarray_attributes_laplacian(q.attrs,grid_location='t')
        lap = finalize_dataarray_attributes(lap,**lapatts)
        return lap

    def vertical_component_of_curl(self,a):
        """Return the vertical component of the curl of a vector field.
        """
        pass

    def horizontal_divergence(self,vectorfield):
        """
        Return the horizontal divergence of a vector field at u,v-points.
        """
        a1 = vectorfield.x_component
        a2 = vectorfield.y_component
        # check
        check_input_array(a1,\
                          chunks=self.chunks,grid_location='u',ndims=self.ndims)
        check_input_array(a2,\
                          chunks=self.chunks,grid_location='v',ndims=self.ndims)
        # define
        div  = self.d_i(a1 / self.array_e2u)
        div += self.d_j(a2 / self.array_e1v)
        div /= self.array_e1t * self.array_e2t
        # finalize
        divatts = \
            convert_dataarray_attributes_divergence(a1.attrs,a2.attrs)
        div = finalize_dataarray_attributes(div,**divatts)
        return div

#----------------------- Specific operators ------------------------------------
    def geostrophic_current_from_sea_surface_height(self,ssh):
        """Return the geostrophic current on u,v-grids.
        """
        pass
