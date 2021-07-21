"""The module mapping provides facilities for mapping the cosmological constants
used by one body of code to another. This is done by defining one of the codes
(pyccl) as being the 'standard', and for all other supported code, providing
functions from_ccl and to_ccl.

The supported codes include:
    pyccl
    CAMB (Fortran convention)
    pycamb (similar but not identical to the CAMB Fortran convention)
    CLASS
    Cobaya
    CosmoSIS
"""


def require_type(val, typ, typename):
    """If val is of type typ, return it; else raise a TypeError with a message
    '{typename} value is required'
    """
    if type(val) is typ:
        return val
    raise TypeError(f"{typename} value is required")


def require_float(val):
    return require_type(val, float, "float")


def require_string(val):
    return require_type(val, str, "string")


class PyCCLCosmologyConstants:
    def __init__(
        self,
        *,
        Omega_c,
        Omega_b,
        h,
        A_s=None,
        sigma_8=None,
        n_s,
        Omega_k,
        Omega_g=None,
        Neff,
        m_nu,
        m_nu_type,
        w0,
        wa,
    ):
        """Construct an object suitable for use in constructing a pyccl.core.CosmologyCalculator. See the
        documentation of that class for an explanation of the choices and meanings of default values of
        None.
        """

        # We typecheck arguments to avoid very confusing error messages at a later time in case
        # of error.
        self.Omega_c = require_float(Omega_c)
        self.Omega_b = require_float(Omega_b)
        self.h = require_float(h)

        if A_s is not None and sigma_8 is not None:
            raise ValueError("Exactly one of A_s and sigma_8 must be supplied")
        if sigma_8 is None:
            self.A_s = require_float(A_s)
        else:
            self.sigma_8 = require_float(sigma_8)

        self.n_s = require_float(n_s)
        self.Omega_k = require_float(Omega_k)
        self.Omega_g = Omega_g
        self.Neff = require_float(Neff)
        self.m_nu = require_float(m_nu)
        self.m_nu_type = require_string(m_nu_type)
        self.w0 = require_float(w0)
        self.wa = require_float(wa)
        self.T_CMB = None


def from_cosmosis_camb(cosmosis_params: dict):
    """Return a PyCCLCosmologyConstants object with parameters equivalent to
    those read from CosmoSIS when using CAMB."""
    # TODO: Verify that CosmoSIS/CAMB does not use Omega_g
    # TODO: Verify that CosmoSIS/CAMB uses delta_neff, not N_eff
    # TODO: Get the right value of m_nu from CosmoSIS/CAMB. This might
    #       depend on which of the CAMB versions are used, or whether
    #       one of the modified CAMBs is in use. m_nu_type almost certain
    #       also needs to be altered.
    Omega_c = cosmosis_params["omega_c"]
    Omega_b = cosmosis_params["omega_b"]
    h = cosmosis_params["h0"]  # Not 'hubble' !
    sigma_8 = cosmosis_params["sigma_8"]
    n_s = cosmosis_params["n_s"]
    Omega_k = cosmosis_params["omega_k"]
    Omega_g = None
    Neff = cosmosis_params.get("delta_neff", 0.0) + 3.0
    m_nu = 0.0
    m_nu_type = "normal"
    w0 = cosmosis_params["w"]
    wa = cosmosis_params["wa"]
    return PyCCLCosmologyConstants(
        Omega_c=Omega_c,
        Omega_b=Omega_b,
        h=h,
        sigma_8=sigma_8,
        n_s=n_s,
        Omega_k=Omega_k,
        Omega_g=Omega_g,
        Neff=Neff,
        m_nu=m_nu,
        m_nu_type=m_nu_type,
        w0=w0,
        wa=-wa,
    )
