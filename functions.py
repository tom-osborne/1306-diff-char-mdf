import numpy as np
from itertools import tee, islice, chain
import config

def smooth(x, window_len, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
    Source: SciPy Cookbook -  https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len:0:-1], x, x[-2:-window_len:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[int((window_len/2-1)):-int((window_len/2)+1)]


def set_axis(plots, axis, label, start, end, major, minor=None):
    """
    Function for setting plot label, axis major
    and minor ticks and formats the gridlines
    """
    for plot in plots:
        if major:
            major_ticks = np.arange(start, end + 1, major)
            if axis == 'x':
                plot.set_xlabel(label)
                plot.set_xlim([start, end])
                plot.set_xticks(major_ticks)
            elif axis == 'y':
                plot.set_ylabel(label)
                plot.set_ylim([start, end])
                plot.set_yticks(major_ticks)

        if minor:
            minor_ticks = np.arange(start, end + 1, minor)
            if axis == 'x':
                plot.set_xticks(minor_ticks, minor=True)
            elif axis == 'y':
                plot.set_yticks(minor_ticks, minor=True)

        if major and minor:
            plot.grid(which='both')
        plot.grid(which='minor', alpha=0.4)
        plot.grid(which='major', alpha=0.8)


def get_gear(channel):
    gears = config.Gears
    ratios = config.Ratios
    actualGear = np.argmax(np.bincount(channel))
    gear_hr = gears[actualGear]
    ratio = ratios[actualGear]
    return actualGear, gear_hr, ratio


def get_sample_rate(channel):
    deltas = np.diff(channel, n=1)
    return int(1 / (sum(deltas) / len(deltas)))


def prev_and_next(iterable):
    prevs, items, nexts = tee(iterable, 3)
    prevs = chain([0.0], prevs)
    nexts = chain(islice(nexts, 1, None), [0.0])
    return zip(prevs, items, nexts)


def SplitData(df):
    # Group Data
    # First we loop through the filtered data, using time channel and find "gaps"
    # We then build a list of indices where these gaps occur, which we can use to split to dataframe up
    group_idxs = []

    for idx, _ in df.iterrows():
        if idx == len(df.index)-1:
            break

        cur = df.iloc[idx]
        nxt = df.iloc[idx + 1]
        diff = nxt['time'] - cur['time']

        if diff > 0.5:        
            group_idxs.append(idx + 1)

    # # We also need the last index to capture the final group
    group_idxs.append(len(df))


    # Split dataframe using the id's created above
    l_mod = [0] + group_idxs + [max(group_idxs) + 1]
    list_of_dfs = [df.iloc[l_mod[n]:l_mod[n + 1]] for n in range(len(l_mod) - 1)]

    return list_of_dfs