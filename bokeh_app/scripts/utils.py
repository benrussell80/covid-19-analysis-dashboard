from pyproj import Transformer
import os
from functools import partial
from typing import Callable, Tuple
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp


DATA_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    'data'
)

join_to_data_folder = partial(os.path.join, DATA_FOLDER)

def longitude_latitude_to_web_mercator(latitude, longitude):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    web_merc_x, web_merc_y = transformer.transform(latitude, longitude)
    
    return web_merc_x, web_merc_y


# SIR Modeling
class Model:
    """
    Model for fitting system of differential equations to data.
    """
    def __init__(self, ode_system_func: Callable, t_span: Tuple[float, float], z: np.ndarray):
        """
        Parameters
        ----------
        ode_system_func : Callable
            Callable defining the system of differential equations.
            Signature should be `func(t, z, ...)` with parameters to fit placed after `z`.
            Parameters should be positional arguments with no defaults. There must be
            at least 1 parameter.

        t_span : Iterable[float]
            Bounds of integration for `scipy.integrate.solve_ivp`.

        z : np.ndarray
            Numpy array of size (n, m) where n is the number of equations in the system,
            and m is the number of data points. Avoid having NaN values in the arrays.
        """
        self.ode_system_func = ode_system_func
        self.t_span = np.asarray(t_span)
        self.z = np.asarray(z)
        
    def fit(self, fitting_idx: int = 0, num_params: int = 0, **kwargs):
        """
        Fit system of ODEs to data.
        
        Parameters
        ----------
        fitting_param_idx : int
            0 <= Integer < n where n is the number of equations in the system.
            This index specifies which subarray of `z` to fit to.
            
        num_params : int
            Verbose way of spcifying the number of parameters to solve for.
            If no value is supplied (default 0) then introspection on `self.ode_system_func`
            is performed instead.
            
        kwargs : Any
            Additional parameters passed to `scipy.optimize.curve_fit`
        """
        def fitting_func(xdata, *args):
            z0 = self.z[:, 0]
            sol = solve_ivp(self.ode_system_func, self.t_span, z0, args=args, dense_output=True)
            return sol.sol(xdata)[fitting_idx]
        
        num_params = num_params or (
            self.ode_system_func.__code__.co_argcount
            - self.ode_system_func.__code__.co_kwonlyargcount
            - 2
        )
        
        popt, _ = curve_fit(
            fitting_func,
            np.linspace(*self.t_span, self.z.shape[1]),
            self.z[fitting_idx],
            p0=[1]*num_params,
            **kwargs
        )
        
        return popt
