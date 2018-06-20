"""
This script downloads selected data files from the NHANES repository,
extracts selected columns, and merges across files to create one integrated
csv file per wave.
"""

import pandas
import os
from os import path
import pandas as pd
import numpy as np

# The base URL for all NHANES data
base = "https://wwwn.cdc.gov/Nchs/Nhanes"

# Demographics files
demo = [
    ("2003-2004", "DEMO_C.XPT"),
    ("2011-2012", "DEMO_G.XPT"),
    ("2015-2016", "DEMO_I.XPT"),
]

# Blood pressure files
bpx = [
    ("2003-2004", "BPX_C.XPT"),
    ("2011-2012", "BPX_G.XPT"),
    ("2015-2016", "BPX_I.XPT"),
]

# Body measures files
bmx = [
    ("2003-2004", "BMX_C.XPT"),
    ("2011-2012", "BMX_G.XPT"),
    ("2015-2016", "BMX_I.XPT"),
]

# Alcohol use
alq = [
    ("2003-2004", "ALQ_C.XPT"),
    ("2011-2012", "ALQ_G.XPT"),
    ("2015-2016", "ALQ_I.XPT"),
]

# Smoking
smq = [
    ("2003-2004", "SMQ_C.XPT"),
    ("2011-2012", "SMQ_G.XPT"),
    ("2015-2016", "SMQ_I.XPT"),
]

# Insurance
hiq = [
    ("2003-2004", "HIQ_C.XPT"),
    ("2011-2012", "HIQ_G.XPT"),
    ("2015-2016", "HIQ_I.XPT"),
]

# Variables to keep
kvar = ["SEQN", "RIAGENDR", "RIDAGEYR", "RIDRETH1", "DMDMARTL",
        "INDFMPIR", "DMDEDUC2", "DMDCITZN", "DMDHHSIZ",
        "BPXSY1", "BPXSY2", "BPXDI1", "BPXDI2", "BMXWT",
        "BMXHT", "BMXBMI", "BMXWAIST", "BMXARMC", "BMXARML",
        "BMXLEG", "ALQ101", "ALQ110", "ALQ130", "SMQ020",
        "SMQ030", "SMD040", "HID010", "HID030A", "HIQ210",
        "HIQ220"]
kvar = set(kvar)

waves = [x[0] for x in demo]

# Create the directory structure
for di in "raw", "csv", "merged":
    try:
        os.mkdir(di)
    except FileExistsError:
        pass

    if di == "merged":
        continue

    for wave in waves:
        try:
            os.mkdir(path.join(di, wave))
        except FileExistsError:
            pass

# Download from the NHANES site
for fb in demo, bpx, bmx, alq, smq, hiq:
    for fi in fb:

        # Download if we don't already have it
        cmd = "wget -N -P %s %s" % (path.join("raw", fi[0]), path.join(base, *fi))
        os.system(cmd)

        # Extract columns of interest and save as csv.
        fname = path.join("raw", *fi)
        data = pd.read_sas(fname)
        cols = [x for x in data.columns if x in kvar]
        da = data.loc[:, cols]
        da.SEQN = da.SEQN.astype(np.int)
        out = path.join("csv", fi[0], fi[1].replace(".XPT", ".csv.gz"))
        da.to_csv(out, index=None, compression="gzip")

# Merge the files within each wave
for wave in waves:

    dfiles = os.listdir(path.join("csv", wave))
    dfiles = [f for f in dfiles if f.endswith(".csv.gz")]
    dfiles = [path.join("csv", wave, f) for f in dfiles]

    data = [pd.read_csv(f) for f in dfiles]

    da = data.pop(0)
    while len(data) > 0:
        da = pd.merge(da, data.pop(0), left_on="SEQN", right_on="SEQN", how="left")

    fname = path.join("merged", "nhanes_" +
    wave.replace("-", "_") + ".csv")
    da.to_csv(fname, index=False)
