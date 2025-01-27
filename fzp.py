import matplotlib.pyplot as plt
import numpy as np
import xraylib

import units
from constants import *


class WaveFront(object):
    def __init__(self, energy: float):
        self.energy = energy
        self.wavelength = h_eV * c / energy

        self.k = 2 * pi / self.wavelength


class Material(object):
    def __init__(self, material: str):
        self.material = material

        self.Z = xraylib.SymbolToAtomicNumber(self.material)
        self.density = xraylib.ElementDensity(self.Z)

    def get_refraction_index_for_wavefront(self, wavefront: WaveFront):
        energy_keV = wavefront.energy * 1e-3

        self.delta = 1 - xraylib.Refractive_Index_Re(
            compound=self.material, E=energy_keV, density=self.density
        )

        self.beta = xraylib.Refractive_Index_Im(
            compound=self.material, E=energy_keV, density=self.density
        )

        self.mu = 4 * pi * self.beta / wavefront.wavelength
        self.attenuation_length = 1 / self.mu

    def calculate_optimal_thickness(self, wavefront: WaveFront):
        self.get_refraction_index_for_wavefront(wavefront)
        a = wavefront.wavelength / (2 * self.delta)
        b = 1 - (2 * self.beta) / (pi * self.delta)
        return a * b


class FZP(object):
    def __init__(
        self,
        f: float,
        resolution: float,
        material: Material,
        wavefront: WaveFront,
        thickness: float = None,
    ):
        self.f = f
        self.resolution = resolution
        self.material = material

        self.outer_zone_thickness = self.resolution / 1.22
        self.n_zones = wavefront.wavelength * self.f / (4 * self.outer_zone_thickness ** 2)

        self.diameter = 4 * self.n_zones * self.outer_zone_thickness
        self.numerical_aperture = wavefront.wavelength / (2 * self.outer_zone_thickness)
        self.dof = wavefront.wavelength/self.numerical_aperture**2

        self.thickness = (
            self.material.calculate_optimal_thickness(wavefront)
            if thickness is None
            else thickness
        )

        self.aspect_ratio = self.thickness / self.resolution

    def calculate_efficiency(self, wavefront: WaveFront, order: int = 1):
        self.material.get_refraction_index_for_wavefront(wavefront)
        eta = self.material.beta / self.material.delta
        phi = wavefront.k * self.material.delta * self.thickness

        first_term = 1 / (order ** 2 * pi ** 2)
        exponential_term = (
            1 + np.exp(-2 * eta * phi) - 2 * np.exp(-2 * eta * phi) * np.cos(phi)
        )

        efficiency = first_term * exponential_term
        return efficiency




if __name__ == "__main__":

    beam = WaveFront(energy=100 * units.keV)

    material = Material("Au")

    fzp = FZP(
        f=10 * units.mm,
        resolution=100 * units.nm,
        material=material,
        wavefront=beam,
        thickness=3e-6,
    )

    energies = np.linspace(200, 20000, 1001)
    thicknesses = np.linspace(10, 5000, 1001) * 1e-9

    efficiencies = []

    for energy in energies:

        beam = WaveFront(energy=energy)

        for thickness in thicknesses:
            fzp = FZP(
                f = 10*units.mm,
                resolution=100*units.nm,
                material=material,
                wavefront=beam,
                thickness=thickness)

            efficiency = fzp.calculate_efficiency(beam)

            efficiencies.append(efficiency)

    eff = np.array(efficiencies)
    eff = eff.reshape((1001,1001))

    energy,thickness = np.meshgrid(energies,thicknesses)
    efficiency = eff.transpose()

    plt.figure()
    plt.contourf(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.bone)
    contour = plt.contour(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.rainbow,linewidths=1)

    plt.clabel(contour)

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Energy [keV]")
    plt.ylabel("Thickness [nm]")

    plt.show()
