from typing import List, Union
import numpy as np


def get_sat(acc: List[float], time: List[float], period: Union[float, np.array], damping: float = 0.02) -> float:
    """Get the pseudo spectral acceleration (Sa(period, damping)) of a ground motion

    Parameters
    ----------
    acc : List[float]
        Acceleration time history in [g]
    time : List[float]
        Time history [s]
    period : Union[float, np.array]
        Period[s] at which we calculate Spectral Acceleration e.g.Sa(T1) - Sa(0.7)
    damping : float, optional
        Damping ratio, by default 0.02

    Returns
    -------
    float
        Spectral accelerations at Periods (Sa(T)) in g, Sa(T=0) = PGA
    """
    dt = time[2] - time[1]

    if isinstance(period, int):
        period = float(period)

    if dt == 0 and isinstance(period, float) and period == 0.0:
        dt = 1e-20

    if dt == 0 and isinstance(period, float) and period != 0.0:
        raise ValueError("Time step must not be zero!")

    if isinstance(period, float):
        if period == 0.0:
            period = 1e-20
    else:
        period[period == 0.0] = 1e-20

    power = 1
    while np.power(2, power) < len(acc):
        power = power + 1

    n_points = np.power(2, power)
    fas = np.fft.fft(acc, n_points)
    d_freq = 1 / (dt * (n_points - 1))
    freq = d_freq * np.array(range(n_points))
    if n_points % 2 != 0:
        sym_idx = int(np.ceil(n_points / 2))
    else:
        sym_idx = int(1 + n_points / 2)

    nat_freq = 1 / period

    if isinstance(period, float):
        h = np.ones(len(fas), 'complex')
    else:
        h = np.ones((len(fas), len(period)), 'complex')

    h[np.int_(np.arange(1, sym_idx))] = np.array([nat_freq ** 2 * 1 / ((nat_freq ** 2 - i ** 2) + 2 * 1j
                                                                       * damping * i * nat_freq) for i in freq[1: sym_idx]])

    if n_points % 2 != 0:
        h[np.int_(np.arange(len(h) - sym_idx + 1, len(h)))
          ] = np.flipud(np.conj(h[np.int_(np.arange(1, sym_idx))]))
    else:
        h[np.int_(np.arange(len(h) - sym_idx + 2, len(h)))
          ] = np.flipud(np.conj(h[np.int_(np.arange(1, sym_idx - 1))]))

    if isinstance(period, float) or isinstance(period, int):
        sa = np.max(abs(np.real(np.fft.ifft(np.multiply(h, fas)))))
    else:
        sa = np.max(
            abs(np.real(np.fft.ifft(np.multiply(h, fas[:, np.newaxis]), axis=0))), axis=0)
        
    return sa
