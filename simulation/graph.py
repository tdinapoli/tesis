import matplotlib.pyplot as plt


model_params_diff_ev_etu = {
    "sigma0":1.2e1,
    "sigma1":6.0e-2,
    "ketu":6.593e6,
    "k1":2.060e6,
    "k2":8.001e6
    }

model_params_diff_ev_esa = {
    "sigma0":8e0,
    "sigma1":6.0e-2,
    "ketu":4.898e6,
    "k1":1977e6,
    "k2":1.2e7
    }

model_params_bujjamer_etu = {
    "sigma0":1,
    "sigma1":5E-1,
    "ketu":2,
    "k1":2,
    "k2":2
}

model_params_bujjamer_esa = {
    "sigma0":1,
    "sigma1":1e-4,
    "ketu":1,
    "k1":2,
    "k2":2
}
keys = list(model_params_bujjamer_esa.keys())
buj_params = []
fit_params = []
for i, key in enumerate(keys):
    buj_params.append(model_params_bujjamer_etu[key]/model_params_bujjamer_esa[key]) 
    fit_params.append(model_params_diff_ev_etu[key]/model_params_diff_ev_esa[key]) 
print(len(buj_params), len(keys))
fig, ax = plt.subplots()
ax.bar(keys, buj_params, label="bujjamer etu/esa")
keys = [key+"fit" for key in keys]
ax.bar(keys, fit_params, label="fit etu/esa")
ax.legend()
plt.yscale("log")
plt.show()