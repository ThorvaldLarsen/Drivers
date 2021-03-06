#!/usr/bin/env python3
import numpy as np

class Readout(object):
    """This class is used to generate multi-tone qubit readout pulses

    """

    def __init__(self, max_qubit=9):
        # define variables
        self.max_qubit = max_qubit
        self.n_readout = max_qubit
        self.frequencies = np.zeros(self.max_qubit)
        self.amplitudes = np.zeros(self.max_qubit)
        self.duration = 0.0
        self.sample_rate = 1E9
        self.match_main_size = False
        self.distribute_phases = False
        # predistortion
        self.predistort = False
        self.measured_rise = np.zeros(self.max_qubit)
        self.target_rise = np.zeros(self.max_qubit)
        # quasi-random phases
        # self.phases = 2 * np.pi * np.random.rand(max_qubit)
        self.phases = 2 * np.pi * np.array([0.8847060, 0.2043214, 0.9426104,
            0.6947334, 0.8752361, 0.2246747, 0.6503154, 0.7305004, 0.1309068])


    def set_parameters(self, config={}):
        """Set base parameters using config from from Labber driver

        Parameters
        ----------
        config : dict
            Configuration as defined by Labber driver configuration window

        """
        # get frequencies and amplitudes
        for n in range(self.max_qubit):
            self.frequencies[n] = config.get('Readout frequency #%d' % (n + 1))
            # amplitudes are currently same for all
            self.amplitudes[n] = config.get('Readout amplitude')
        # get other parameters
        self.duration = config.get('Readout duration')
        self.sample_rate = config.get('Sample rate')
        self.n_readout = int(config.get('Number of readout tones'))
        self.match_main_size = config.get('Match main sequence waveform size')
        self.distribute_phases = config.get('Distribute readout phases')
        # predistortion
        self.predistort = config.get('Predistort readout waveform')
        if self.predistort:
            for n in range(self.max_qubit):
                # pre-distortion settings are currently same for all qubits
                linewidth = config.get('Resonator linewidth')
                self.measured_rise[n] = 1.0 / (2 * np.pi * linewidth)
                self.target_rise[n] = config.get('Target rise time')


    def create_waveform(self, t_start=0.0):
        """Generate readout waveform

        Parameters
        ----------
        t_start : float
            Start time for readout waveform, relative to start of sequence

        Returns
        -------
        waveform : complex numpy array
            Complex waveforms with I/Q signal for qubit reaodut

        """
        # ignore time stamp
        t_start = 0.0
        # create time and output waveform
        n_pts = int(self.duration * self.sample_rate)
        t = t_start + np.arange(n_pts, dtype=float) / self.sample_rate
        waveform = np.zeros_like(t, dtype=complex)

        # add readout for all waveforms
        for n in range(self.n_readout):
            # get parameters
            a = self.amplitudes[n]
            omega = 2 * np.pi * self.frequencies[n]
            if self.distribute_phases:
                # phi = 2 * np.pi * n / self.n_readout
                # phi = 2 * np.pi * np.random.rand()
                phi = self.phases[n]
            else:
                phi = 0.0
            # create square baseband waveform
            y = np.ones_like(t, dtype=complex)
            # apply pre-distortion
            if self.predistort:
                # add inverted exponential
                y += ((self.measured_rise[n] / self.target_rise[n] - 1) * 
                      np.exp(-(t - t[1]) / self.target_rise[n]))
            y[0] = 0.0
            y[-1] = 0.0

            # apply SSBM transform
            waveform += a * (y.real * np.cos(omega * t - phi) +
                             -y.imag * np.cos(omega * t - phi + np.pi / 2))
            waveform += a * 1j * (-y.real * np.sin(omega * t - phi) +
                                  y.imag * np.sin(omega * t - phi + np.pi / 2))

        return waveform



if __name__ == '__main__':
    pass
