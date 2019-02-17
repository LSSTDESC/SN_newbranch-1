import pyccl as ccl

from ..core import Systematic

__all__ = ['MultiplicativeShearBias', 'LinearAlignmentSystematic']

# constant from KEB16, near eqn 7
C1RHOC = 0.0134


class MultiplicativeShearBias(Systematic):
    """Multiplicative shear bias systematic.

    This systematic adjusts the `scale_` of a source by `(1 + m)`.

    Parameters
    ----------
    m : str
        The name of the multiplicative bias parameter.

    Methods
    -------
    apply : appaly the systematic to a source
    """
    def __init__(self, m):
        self.m = m

    def apply(self, cosmo, params, source):
        """Apply multiplicative shear bias to a source. The `scale_` of the
        source is multiplied by `(1 + m)`.

        Parameters
        ----------
        cosmo : pyccl.Cosmology
            A pyccl.Cosmology object.
        params : dict
            A dictionary mapping parameter names to their current values.
        source : a source object
            The source to which apply the shear bias.
        """
        source.scale_ *= (1.0 + params[self.m])


class LinearAlignmentSystematic(Systematic):
    """Linear alignment systematic.

    This systematic adds a linear intrinsic alignment model systematic
    which varies with redshift and the growth function.

    Parameters
    ----------
    alphaz : str
        The mame of redshift dependence parameter of the intrinsic alignment
        signal.
    alphag : str
        The name of the growth dependence parameter of the intrinsic alignment
        signal.
    z_piv : str
        The name of the pivot redshift parameter for the intrinsic alignment
        parameter.
    Omega_b : str
        The name of the parameter for the baryon density at z = 0.
    Omega_c : str
        The name of the patameter for the cold dark matter density at z = 0.

    Methods
    -------
    apply : apply the systematic to a source
    """
    def __init__(self, alphaz, alphag, z_piv, Omega_b, Omega_c):
        self.alphaz = alphaz
        self.alphag = alphag
        self.z_piv = z_piv
        self.Omega_b = Omega_b
        self.Omega_c = Omega_c

    def apply(self, cosmo, params, source):
        """Apply a linear alignment systematic.

        Parameters
        ----------
        cosmo : pyccl.Cosmology
            A pyccl.Cosmology object.
        params : dict
            A dictionary mapping parameter names to their current values.
        source : a source object
            The source to which apply the shear bias.
        """
        pref = (params[self.Omega_b] + params[self.Omega_c]) * C1RHOC * (
            ((1.0 + source.z_) / (1.0 + params[self.z_piv])) **
            params[self.alphaz])
        pref *= ccl.growth_factor(
                cosmo, 1.0 / (1.0 + source.z_)) ** params[self.alphag]
        source.ia_bias_ *= pref
