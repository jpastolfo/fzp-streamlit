import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import units
from fzp import FZP, Material, WaveFront

st.title("FZP Calculations")

with st.sidebar:
    energy = st.number_input(
        "Energy (eV)",value=8000,placeholder="Insert the energy...",step=1000
    )

    material = st.text_input(
        "Material Symbol",value="Au",placeholder="Insert the material symbol..."
    )

    focal_length = st.number_input(
        "Focal Length (mm)",value=40,placeholder="Insert the focal length...",step=1
    )

    resolution = st.number_input(
        "Resolution (nm)",value=100,placeholder="Insert the resolution...",step=10
    )

    energy_min = st.number_input(
        "Minimum Energy (eV)",value=1000,placeholder="Insert the energy...",step=1000
    )

    energy_max = st.number_input(
        "Maximum Energy (eV)",value=20000,placeholder="Insert the energy...",step=1000
    )

    points = int(st.number_input(
        "Points",value=0,placeholder="Insert the energy points...",step=10
    ))


    do_calculation = st.button("Calculate",type="primary")

if do_calculation:
    beam = WaveFront(energy=energy)
    material = Material(material=material)

    fzp = FZP(
        f = focal_length*units.mm,
        resolution = resolution*units.nm,
        material = material,
        wavefront= beam,
    )

    thickness = fzp.thickness
    st.write("Thickness: ", fzp.thickness)


    st.divider()


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


    fig,ax = plt.subplots()
    ax.set_title("Efficiency x Energy")
    ax.plot(energies,efficiencies*1e2)
    ax.set_xlabel("Energy [eV]")
    ax.set_ylabel("Efficiency %")


    st.pyplot(fig)