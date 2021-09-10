import math
import numpy as np
import pyccl as ccl

from firecrown.connector.mapping import mapping_builder

from pprint import pprint

from cobaya.theory import Theory


class CCLConnector(Theory):
    """
    A class implementing cobaya.theory.Theory ...

    ...

    Attributes
    ----------
    ... : str
        ...

    Methods
    -------
    ...(...)
        ....
    """

    input_style: str = None

    def initialize(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """

        self.map = mapping_builder(input_style=self.input_style)

        self.a_bg = np.linspace(0.1, 1.0, 50)
        self.z_bg = 1.0 / self.a_bg - 1.0
        self.z_Pk = np.arange(0.2, 6.0, 1)
        self.Pk_kmax = 1.0
        pass

    def get_param(self, p):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        pass

    def initialize_with_params(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        pass

    def initialize_with_provider(self, provider):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        self.provider = provider

    def get_can_provide_params(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        return []

    def get_can_support_params(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        return self.map.get_names()

    def get_allow_agnostic(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        return False

    def get_requirements(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """

        ccl_calculator_requires = {
            "omk": None
        }  # {param: None for param in self.map.get_names()}

        ccl_calculator_requires["Pk_grid"] = {"k_max": self.Pk_kmax, "z": self.z_Pk}
        ccl_calculator_requires["comoving_radial_distance"] = {"z": self.z_bg}
        ccl_calculator_requires["Hubble"] = {"z": self.z_bg}

        return ccl_calculator_requires

    def must_provide(self, **requirements):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        pass

    def calculate(self, state, want_derived=True, **params_values):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """

        self.map.set_params_from_camb(**params_values)

        ccl_params_values = self.map.asdict()
        # This is the dictionary appropriate for CCL creation

        chi_arr = self.provider.get_comoving_radial_distance(self.z_bg)
        hoh0_arr = self.provider.get_Hubble(self.z_bg) / self.map.get_H0()
        k, z, pk = self.provider.get_Pk_grid()

        self.a_Pk = self.map.redshift_to_scale_factor(z)
        pk_a = self.map.redshift_to_scale_factor_p_k(pk)

        cosmo = ccl.CosmologyCalculator(
            **ccl_params_values,
            background={"a": self.a_bg, "chi": chi_arr, "h_over_h0": hoh0_arr},
            pk_linear={
                "a": self.a_Pk,
                "k": k,
                "delta_matter:delta_matter": pk_a,
            },
            nonlinear_model="halofit"
        )
        state["ccl"] = cosmo

    def get_ccl(self):
        """...
        ...
        Parameters
        ----------
        ... : str
            ...
        """
        return self.current_state["ccl"]
