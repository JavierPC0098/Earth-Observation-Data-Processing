
from ism.src.initIsm import initIsm
from math import pi
from ism.src.mtf import mtf
from numpy.fft import fftshift, ifft2, fft2
import numpy as np
from common.io.writeToa import writeToa
from common.io.readIsrf import readIsrf
from scipy.interpolate import interp1d, interp2d
from common.plot.plotMat2D import plotMat2D
from common.plot.plotF import plotF
from scipy.signal import convolve2d
from common.src.auxFunc import getIndexBand
from l1b.test.l1b_test import alt_toa_extractor


class opticalPhase(initIsm):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def compute(self, sgm_toa, sgm_wv, band):
        """
        The optical phase is in charge of simulating the radiance
        to irradiance conversion, the spatial filter (PSF)
        and the spectral filter (ISRF).
        :return: TOA image in irradiances [mW/m2/nm],
                    with spatial and spectral filter
        """
        self.logger.info("EODP-ALG-ISM-1000: Optical stage") # name of the algorith to be used

        # Calculation and application of the ISRF
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-1010: Spectral modelling. ISRF")
        toa = self.spectralIntegration(sgm_toa, sgm_wv, band)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

        if self.ismConfig.save_after_isrf:
            saveas_str = self.globalConfig.ism_toa_isrf + band
            writeToa(self.outdir, saveas_str, toa)

        # Radiance to Irradiance conversion
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-1020: Radiances to Irradiances")
        toa = self.rad2Irrad(toa,
                             self.ismConfig.D,
                             self.ismConfig.f,
                             self.ismConfig.Tr)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

        # Spatial filter
        # -------------------------------------------------------------------------------
        # Calculation and application of the system MTF
        self.logger.info("EODP-ALG-ISM-1030: Spatial modelling. PSF/MTF")
        myMtf = mtf(self.logger, self.outdir)
        Hsys = myMtf.system_mtf(toa.shape[0], toa.shape[1],
                                self.ismConfig.D, self.ismConfig.wv[getIndexBand(band)], self.ismConfig.f, self.ismConfig.pix_size,
                                self.ismConfig.kLF, self.ismConfig.wLF, self.ismConfig.kHF, self.ismConfig.wHF,
                                self.ismConfig.defocus, self.ismConfig.ksmear, self.ismConfig.kmotion,
                                self.outdir, band)

        # Apply system MTF
        toa = self.applySysMtf(toa, Hsys) # always calculated
        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")



        # Write output TOA & plots
        # -------------------------------------------------------------------------------
        if self.ismConfig.save_optical_stage:
            saveas_str = self.globalConfig.ism_toa_optical + band

            writeToa(self.outdir, saveas_str, toa)

            title_str = 'TOA after the optical phase [mW/sr/m2]'
            xlabel_str='ACT'
            ylabel_str='ALT'
            plotMat2D(toa, title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

            idalt = int(toa.shape[0]/2)
            saveas_str = saveas_str + '_alt' + str(idalt)
            plotF([], toa[idalt,:], title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

        return toa

    def rad2Irrad(self, toa, D, f, Tr):
        """
        Radiance to Irradiance conversion
        :param toa: Input TOA image in radiances [mW/sr/m2]
        :param D: Pupil diameter [m]
        :param f: Focal length [m]
        :param Tr: Optical transmittance [-]
        :return: TOA image in irradiances [mW/m2]
        """
        # TODO
        # pag 34.
        # here we integrate all the energy commint to the telescope

        toa_irradiance = Tr * toa * ( D / f )**4 * np.pi/4
        irradiance_conv_factor = Tr * ( D / f )**4 * np.pi/4
        print(f" -+-+- Irradiance Conversion factor: {irradiance_conv_factor:.10f}")

        return toa_irradiance


    def applySysMtf(self, toa, Hsys):
        """
        Application of the system MTF to the TOA
        :param toa: Input TOA image in irradiances [mW/m2]
        :param Hsys: System MTF
        :return: TOA image in irradiances [mW/m2]
        """
        # TODO

        GE = fft2(toa) # image in the frequency domain
        # fftshift(Hsys) # frequency shifted. Reorders the frequencies to put the value 1 in the first pixel (top left corner)

        toa_ft = np.real(ifft2( GE * fftshift(Hsys)))

        return toa_ft

    def spectralIntegration(self, sgm_toa, sgm_wv, band):
        """
        Integration with the ISRF to retrieve one band
        :param sgm_toa: Spectrally oversampled TOA cube 3D in irradiances [mW/m2]
        :param sgm_wv: wavelengths of the input TOA cube
        :param band: band
        :return: TOA image 2D in radiances [mW/m2]
        """
        # TODO
        isrf, wv_isrf = readIsrf(self.auxdir + self.ismConfig.isrffile, band)
        wv_isrf = wv_isrf * 1000 # we want to work in nm
        nrow_alt, ncol_act, nwvs = sgm_toa.shape
        isrf_step = wv_isrf[1] - wv_isrf[0] # 0.001  # compute the delta wv from here sgm_wv
        toa_filtered = np.zeros((nrow_alt, ncol_act))


        # Appliying the filter. We normalize it first. Eq. pag 33
        isfr_int = np.sum(isrf) * isrf_step
        isfr_norm = isrf / isfr_int

        for ialt in range(nrow_alt) :
            for iact in range(ncol_act):
                # We compute the TOA Eq. pag 32
                cs = interp1d(sgm_wv, sgm_toa[ialt, iact, :], fill_value=(0, 0), bounds_error=False)
                toa_interpolated = cs(wv_isrf) # to do the unit conversion from microns to nanometers

                # Apply the filter. Pag 32
                toa_filtered[ialt, iact] = np.sum(toa_interpolated * isfr_norm * isrf_step)

        return toa_filtered


