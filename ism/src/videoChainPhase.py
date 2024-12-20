
from ism.src.initIsm import initIsm
import numpy as np
from common.plot.plotMat2D import plotMat2D
from common.plot.plotF import plotF

class videoChainPhase(initIsm):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def compute(self, toa, band):
        self.logger.info("EODP-ALG-ISM-3000: Video Chain")

        # Electrons to Voltage - read-out & amplification
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-3010: Electrons to Voltage – Read-out and Amplification")
        toa = self.electr2Volt(toa,
                         self.ismConfig.OCF,
                         self.ismConfig.ADC_gain)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [V]")

        # Digitisation
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-3020: Voltage to Digital Numbers – Digitisation")
        toa = self.digitisation(toa,
                          self.ismConfig.bit_depth,
                          self.ismConfig.min_voltage,
                          self.ismConfig.max_voltage)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [DN]")

        # Plot
        if self.ismConfig.save_vcu_stage:
            saveas_str = self.globalConfig.ism_toa_vcu + band
            title_str = 'TOA after the VCU phase [DN]'
            xlabel_str='ACT'
            ylabel_str='ALT'
            plotMat2D(toa, title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

            idalt = int(toa.shape[0]/2)
            saveas_str = saveas_str + '_alt' + str(idalt)
            plotF([], toa[idalt,:], title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

        return toa

    def electr2Volt(self, toa, OCF, gain_adc):
        """
        Electron to Volts conversion.
        Simulates the read-out and the amplification
        (multiplication times the gain).
        :param toa: input toa in [e-]
        :param OCF: Output Conversion factor [V/e-]
        :param gain_adc: Gain of the Analog-to-digital conversion [-]
        :return: output toa in [V]
        """
        #TODO

        toa = toa * OCF * gain_adc

        print("----------------------------------------------------------------------------------------------")
        print(f"Electrons to Volts: {OCF * gain_adc:.8f}")

        return toa

    def digitisation(self, toa, bit_depth, min_voltage, max_voltage):
        """
        Digitisation - conversion from Volts to Digital counts
        :param toa: input toa in [V]
        :param bit_depth: bit depth
        :param min_voltage: minimum voltage
        :param max_voltage: maximum voltage
        :return: toa in digital counts
        """
        #TODO

        # Calculate the maximum possible digital value based on bit depth
        max_digital_value = 2 ** bit_depth - 1

        # Apply the digitization formula
        toa_dn = np.round((toa / (max_voltage - min_voltage))*(2**bit_depth - 1))

        v2dig = np.round((1 / (max_voltage - min_voltage)) * (2 ** bit_depth - 1))
        print("----------------------------------------------------------------------------------------------")
        print(f"Volts to digital: {v2dig:.8f}")

        # Saturate the value to ensure it's within the valid range
        toa_dn = np.clip(toa_dn, 0, max_digital_value)

        # Calculate the number of pixels that are saturated
        saturated_pixels = np.sum(toa_dn == max_digital_value)

        # Calculate the total number of pixels in the matrix
        total_pixels = toa_dn.size

        # Calculate the percentage of saturated pixels
        saturated_percentage = (saturated_pixels / total_pixels) * 100

        print(f" -+-+-+- Percentage of saturated pixels: {saturated_percentage:.2f}%")

        return toa_dn

