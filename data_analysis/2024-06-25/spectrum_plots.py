import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

p = Path("/home/tomi/Documents/academicos/facultad/tesis/tesis/data_analysis/2024-06-25")
data_path = p / 'data' / 'full_spectrums'
figures_path = p / 'figures'

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError

def plot(df, label="", color='C0'):
    int_time = df.attrs["integration_time"]
    plt.plot(df.wavelength, df.counts / int_time, '-', label=label, color=color)
    plt.xlabel("Longitud de onda (nm)")
    plt.ylabel("Cuentas por segundo (1/s)")
    plt.grid(True)

optical_powers = []
data = pd.DataFrame(columns=["optical_power", "path"])
for i, df_path in enumerate(data_path.glob('*.pickle')):
    df = pd.read_pickle(df_path)
    #plot(df)

    optical_power = df.attrs["optical_power"]
    
    data.loc[len(data)] = dict(optical_power=optical_power, path=df_path)

    #plt.title(f"Optical power {optical_power:.4f} W")
    #plt.savefig(figures_path / f"{df.attrs["optical_power"]:.4f}.png", dpi=300)
    #plt.show()

data = data.sort_values(by="optical_power")
data.drop([9, 8, 3], inplace=True)
print(data)
cmap = plt.get_cmap("OrRd")
#currents = [0.05, 0.1, 0.15, 0.2, 0.25, 0.25, 0.3, 0.3, 0.4, 0.4]
currents = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]
ranges = {
    "G":(500, 535),
    "R":(630, 690),
    "Y":(535,570),
    "UVA":(372,390),
    "B":(397, 525)
}
colors = {
    "G":"green",
    "R":"red",
    "Y":"yellow",
    "UVA":"violet",
    "B":"blue"
}
#fig, axs = plt.subplots(5, 1, sharex=True)
for i, (name, rng) in enumerate(ranges.items()):
    lower, upper = rng
    intensities409 = []
    for current, optical_power, df_path in zip(currents, data.optical_power, data.path):
        df = pd.read_pickle(df_path)
        color = cmap(optical_power / data.optical_power.max())
        #plot(df, label=f"{current:.4f} W", color=color)
        #plt.legend()
        int_time = df.attrs["integration_time"]
        counts = df[(df.wavelength >= lower ) & (df.wavelength <= upper)].counts.mean()
        intensities409.append(counts/int_time)

    #plt.show()
#plt.savefig(figures_path / "all_spectrums.png", dpi=300)
    #axs[i].loglog(data.optical_power, intensities409, 'o', label=name, color=colors[name])
    #axs[i].legend()
    plt.loglog(data.optical_power, intensities409, 'o', label=name, color=colors[name])
plt.xlabel("Power (W)")
plt.ylabel("Counts per sec")
plt.tight_layout()
plt.show()
