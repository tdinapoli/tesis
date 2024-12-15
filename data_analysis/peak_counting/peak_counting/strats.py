import pandas as pd
import numpy as np
import scipy.signal as ssig
from peak_counting import constants

def original(df: pd.DataFrame, threshold=0.5):
    return df.iloc[np.where(np.diff(df.ch1) > threshold)[0]]

def negative_original(df: pd.DataFrame, threshold=1.5):
    return df.iloc[np.where(np.diff(df.ch1) < -threshold)[0]]

def original_filter_close(df: pd.DataFrame, threshold=0.5, further: int = 3, sampling_rate: float = constants.SR):
    df = original(df, threshold=threshold)
    return 

def fpcwt(df: pd.DataFrame, widths=np.arange(2, 10, 1), min_snr=1):
    return df.iloc[ssig.find_peaks_cwt(-df.ch1, widths=widths, min_snr=min_snr)]

