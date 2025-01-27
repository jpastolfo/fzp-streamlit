import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import units
from fzp import FZP, Material, WaveFront

st.set_page_config(
    page_title="OPT FZP Calculator",
    layout="wide",
)


st.title("FZP Calculations")


with st.sidebar:

    st.text("FZP Parameters")

    energy_input = st.number_input(
        "Energy (eV)",value=8000,placeholder="Insert the energy...",step=1000
    )

    material_symbol = st.text_input(
        "Material Symbol",value="Au",placeholder="Insert the material symbol..."
    )

    focal_length = st.number_input(
        "Focal Length (mm)",value=40,placeholder="Insert the focal length...",step=1
    )

    resolution = st.number_input(
        "Resolution (nm)",value=100,placeholder="Insert the resolution...",step=10
    )

    st.divider()
    st.text("Efficiency Plot Parameters")

    energy_min = st.number_input(
        "Minimum Energy (eV)",value=200,placeholder="Insert the energy...",step=1000
    )

    energy_max = st.number_input(
        "Maximum Energy (eV)",value=20000,placeholder="Insert the energy...",step=1000
    )

    points = int(st.number_input(
        "Points",value=101,placeholder="Insert the energy points...",step=10
    ))

    do_plot = st.button("Generate Efficiency Curve",type="primary")

    st.divider()
    st.text("Efficiency Map Parameters")

    thickness_min = st.number_input(
        "Minimum Thickness (nm)",value=200,placeholder="Insert minimum thickness...",step=100
    )

    thickness_max = st.number_input(
        "Maximum Thickness (nm)",value=5000,placeholder="Insert maximum thickness...",step=100
    )

    e_points = int(st.number_input(
        "Energy Points",value=201,placeholder="Insert the energy points...",step=10
    ))

    t_points = int(st.number_input(
        "Thickness Points",value=201,placeholder="Insert the thickness points...",step=10
    ))

    do_map = st.button("Generate Efficiency Map",type="primary")

col1,col2 = st.columns(2)

with col1:
    st.header("Efficiency Curve")

    if do_plot or do_map:
        beam = WaveFront(energy=energy_input)
        material = Material(material=material_symbol)

        fzp = FZP(
            f = focal_length*units.mm,
            resolution = resolution*units.nm,
            material = material,
            wavefront= beam,
        )

        thickness = fzp.thickness

        energies = np.linspace(energy_min,energy_max,points)
        efficiencies = []
        for energy in energies:

            beam = WaveFront(energy=energy)

            fzp = FZP(
                f = focal_length*units.mm,
                resolution=resolution*units.nm,
                material=material,
                wavefront=beam,
                thickness = thickness
            )

            efficiency = fzp.calculate_efficiency(beam)

            efficiencies.append(efficiency)

        efficiencies = np.array(efficiencies)

        fig,ax = plt.subplots(figsize=(10,10))
        ax.set_title("Efficiency x Energy")
        ax.plot(energies,efficiencies*1e2)
        ax.set_xlabel("Energy [eV]")
        ax.set_ylabel("Efficiency %")

        st.pyplot(fig)

        st.caption(f"Efficiency curve, for FZP made of {material.material} and thickness of {thickness*1e6:.1f} µm.")


with col2:
    st.header("Efficiency Map")

    if do_plot or do_map:

        material = Material("Au")

        energies = np.linspace(energy_min, energy_max, e_points)
        thicknesses = np.linspace(thickness_min, thickness_max, t_points) * 1e-9

        efficiencies = []

        for energy in energies:

            beam = WaveFront(energy=energy)

            for thickness in thicknesses:
                fzp = FZP(
                    f = focal_length*units.mm,
                    resolution=resolution*units.nm,
                    material=material,
                    wavefront=beam,
                    thickness=thickness
                )

                efficiency = fzp.calculate_efficiency(beam)

                efficiencies.append(efficiency)

        eff = np.array(efficiencies)
        eff = eff.reshape((e_points,t_points))

        energy,thickness = np.meshgrid(energies,thicknesses)
        efficiency = eff.transpose()

        fig,ax = plt.subplots(figsize=(10,10))
        ax.contourf(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.bone)
        contour = ax.contour(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.rainbow,linewidths=1)

        ax.clabel(contour)

        ax.set_xscale("log")
        ax.set_yscale("log")

        ax.set_xlabel("Energy [keV]")
        ax.set_ylabel("Thickness [nm]")

        st.pyplot(fig)
        st.caption(f"Efficiency map for FZP made of {material.material}.")


st.header("FZP Properties")

if do_plot or do_map:

    beam = WaveFront(energy=energy_input)
    material = Material("Au")

    fzp = FZP(
        f = focal_length*units.mm,
        resolution = resolution*units.nm,
        material = material,
        wavefront= beam,
    )

    df = pd.DataFrame(
        data = np.array([
            [focal_length],
            [fzp.diameter*1e6],
            [fzp.numerical_aperture],
            [fzp.n_zones],
            [fzp.outer_zone_thickness*1e9],
            [0.0*1e9],
            [fzp.dof*1e6],
            [fzp.thickness*1e6],
            [fzp.aspect_ratio]
        ]).transpose(),
        columns = [
            "Focal Distance (mm)",
            "Diameter (µm)",
            "N.A.",
            "Number of zones",
            "Outer zone width (nm)",
            "Inner zone width (nm)",
            "DOF (µm)",
            "Optimal Thickness (µm)",
            "Aspect Ratio",
        ]
    )

    st.table(df)
