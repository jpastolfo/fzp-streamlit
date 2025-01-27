import matplotlib.pyplot as plt
import numpy as np

from fzp import FZP, WaveFront, Material
import units

energies = np.linspace(0.5,20,1001)*1e3

material = Material("Au")

efficiencies = []

# for energy in energies:

#     beam = WaveFront(energy=energy)

#     for thickness in thicknesses:
#         fzp = FZP(
#             f = 10*units.mm,
#             resolution=100*units.nm,
#             material=material,
#             wavefront=beam,
#             thickness=thickness)

#         efficiency = fzp.calculate_efficiency(beam)

#         efficiencies.append(efficiency)

# eff = np.array(efficiencies)
# eff = eff.reshape((501,501))

# energy,thickness = np.meshgrid(energies,thicknesses)
# efficiency = eff.transpose()

# plt.figure()
# plt.contourf(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.bone)
# contour = plt.contour(energy*1e-3,thickness*1e9,efficiency,cmap=plt.cm.rainbow)

# plt.clabel(contour)

# plt.xscale("log")
# plt.yscale("log")

# plt.xlabel("Energy [keV]")
# plt.ylabel("Thickness [nm]")

# plt.show()

beam = WaveFront(energy=8000)

fzp = FZP(
    f = 10*units.mm,
    resolution=100*units.nm,
    material=material,
    wavefront=beam,
)

print(fzp.thickness)

for energy in energies:

    beam = WaveFront(energy=energy)

    fzp = FZP(
        f = 10*units.mm,
        resolution=100*units.nm,
        material=material,
        wavefront=beam,
        thickness=1527*units.nm
    )

    efficiency = fzp.calculate_efficiency(beam)

    efficiencies.append(efficiency)

efficiencies = np.array(efficiencies)


plt.figure()
plt.title("Efficiency x Energy")
plt.plot(energies,efficiencies*1e2)
plt.xlabel("Energy [eV]")
plt.ylabel("Efficiency %")
plt.show()