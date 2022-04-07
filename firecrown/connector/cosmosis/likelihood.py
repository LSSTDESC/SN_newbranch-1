from cosmosis.datablock import option_section
from cosmosis.datablock import names as section_names
import numpy as np
import pyccl as ccl
import firecrown

from firecrown.connector.mapping import mapping_builder
from firecrown.likelihood.likelihood import load_likelihood
from firecrown.parameters import ParamsMap

likes = section_names.likelihoods


def extract_section(sample, section):
    sec_dict = {name: sample[section, name] for _, name in sample.keys(section=section)}
    return sec_dict


class FirecrownLikelihood:
    """CosmoSIS likelihood module for calculating Firecrown likelihood.

    In this simplest implementation, we have only a single module. This module
    is responsible for calling CCL to perform theory calculations, based on the
    output of CAMB, and also for calculating the data likelihood baesd on this
    theory.
    """

    def __init__(self, config):
        firecrownIni = config[option_section, "firecrown_config"]

        self.likelihood = load_likelihood(firecrownIni)
        self.map = mapping_builder(input_style="CosmoSIS")

    def __str__(self):
        """Return the human-readabe representation of this object."""
        return f"Firecrown object with keys: {list(self.data.keys())}"

    def execute(self, sample):
        """This is the method called for each sample generated by the sampler."""

        cosmological_params = extract_section(sample, "cosmological_parameters")
        cosmological_params_for_ccl = self.map.set_params_from_cosmosis(
            cosmological_params
        )

        ccl_args = {}

        if sample.has_section("matter_power_lin"):
            k = self.map.transform_k_h_to_k(sample["matter_power_lin", "k_h"])
            z_mpl = sample["matter_power_lin", "z"]
            scale_mpl = self.map.redshift_to_scale_factor(z_mpl)
            p_k = self.map.transform_p_k_h3_to_p_k(sample["matter_power_lin", "p_k"])
            p_k = self.map.redshift_to_scale_factor_p_k(p_k)

            ccl_args["pk_linear"] = {
                "a": scale_mpl,
                "k": k,
                "delta_matter:delta_matter": p_k,
            }
            ccl_args["nonlinear_model"] = "halofit"

        # TODO: We should have several configurable modes for this module.
        # In all cases, an exception will be raised (causing a program shutdown) if something
        # that is to be read from the DataBlock is not present in the DataBlock.
        #
        # background: read only background information from the DataBlock; it will generate
        #    a runtime error if the configured likelihood attempts to use anything else.
        # linear: read also the linear power spectrum from the DataBlock. Any non-linear
        #    power spectrum present will be ignored. It will generate a runtime error if the
        #    configured likelihood attempts to make use of a non-linear spectrum.
        #  nonlinear: read also the nonlinear power spectrum from the DataBlock.
        #  halofit, halomodel, emu: use CCL to calculate the nonlinear power spectrum according
        #     to the named technique. In all cases, the linear power spectrum read from the
        #     DataBlock is used as input. In all cases, it is an error if the DataBlock also
        #     contains a nonlinear power spectrum.

        chi = np.flip(sample["distances", "d_m"])
        scale_distances = self.map.redshift_to_scale_factor(sample["distances", "z"])
        h0 = sample["cosmological_parameters", "h0"]

        # NOTE: The first value of the h_over_h0 array is non-zero because of the way
        # CAMB does it calculation. We do not modify this, because we want consistency.

        # hubble_radius_today = (ccl.physical_constants.CLIGHT * 1e-5) / h0
        # h_over_h0 = np.flip(sample["distances", "h"]) * hubble_radius_today
        h_over_h0 = self.map.transform_h_to_h_over_h0(sample["distances", "h"])

        ccl_args["background"] = {
            "a": scale_distances,
            "chi": chi,
            "h_over_h0": h_over_h0,
        }

        cosmo = ccl.CosmologyCalculator(**self.map.asdict(), **ccl_args)

        # TODO: Future development will need to capture elements that get put into the datablock.
        # This probably will be in a different "physics module" and not in the likelihood module.
        # And it requires updates to Firecrown to split the calculations.
        # e.g., data_vector/firecrown_theory  data_vector/firecrown_data

        firecrown_params = ParamsMap()

        for section in sample.sections():
            if "firecrown" in section:
                sec_dict = extract_section(sample, section)
                firecrown_params = ParamsMap({**firecrown_params, **sec_dict})

        lnlike = self.likelihood.compute_loglike(cosmo, firecrown_params)

        sample.put_double(section_names.likelihoods, "firecrown_like", lnlike)

        return 0

    def cleanup(self):
        """There is nothing to do in the cleanup function for this module."""
        return 0


def setup(config):
    return FirecrownLikelihood(config)


def execute(sample, instance):
    return instance.execute(sample)


def cleanup(instance):
    return instance.cleanup()
