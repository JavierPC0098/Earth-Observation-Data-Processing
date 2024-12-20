from json import JSONDecoder
from math import pi

from numpy.ma.core import sctype
from scipy.stats import cosine

from config.ismConfig import ismConfig
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.special import j1
from numpy.matlib import repmat
from common.io.readMat import writeMat
from common.io.mkdirOutputdir import mkdirOutputdir
from common.plot.plotMat2D import plotMat2D
from scipy.interpolate import interp2d
from numpy.fft import fftshift, ifft2
import os
from netCDF4 import Dataset

def writeArray(outputdir, name, array):

    # Check output directory
    mkdirOutputdir(outputdir)

    # TOA filename
    savetostr = os.path.join(outputdir, name + '.nc')

    # open a netCDF file to write
    ncout = Dataset(savetostr, 'w', format='NETCDF4')

    # define axis size
    ncout.createDimension('alt_lines', array.shape[0])  # unlimited
    #ncout.createDimension('act_columns', mat.shape[1])

    # create variable array
    floris_toa_scene = ncout.createVariable('array', 'float32',
                                            ('alt_lines'))

    # Assign data
    floris_toa_scene[:]         = array[:]

    # close files
    ncout.close()

    print("Finished writting: " + savetostr)

class mtf:
    """
    Class MTF. Collects the analytical modelling of the different contributions
    for the system MTF
    """
    def __init__(self, logger, outdir):
        self.ismConfig = ismConfig()
        self.logger = logger
        self.outdir = outdir

    def system_mtf(self, nlines, ncolumns, D, lambd, focal, pix_size,
                   kLF, wLF, kHF, wHF, defocus, ksmear, kmotion, directory, band):
        """
        System MTF
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param pix_size: pixel size in meters [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :param directory: output directory
        :return: mtf
        """

        self.logger.info("Calculation of the System MTF")

        # Calculate the 2D relative frequencies
        self.logger.debug("Calculation of 2D relative frequencies")
        fn2D, fr2D, fnAct, fnAlt = self.freq2d(nlines, ncolumns, D, lambd, focal, pix_size)

        # Diffraction MTF
        self.logger.debug("Calculation of the diffraction MTF")
        Hdiff = self.mtfDiffract(fr2D)

        # Defocus
        Hdefoc = self.mtfDefocus(fr2D, defocus, focal, D)

        # WFE Aberrations
        Hwfe = self.mtfWfeAberrations(fr2D, lambd, kLF, wLF, kHF, wHF)

        # Detector
        Hdet  = self. mtfDetector(fn2D)

        # Smearing MTF
        Hsmear = self.mtfSmearing(fnAlt, ncolumns, ksmear)

        # Motion blur MTF
        Hmotion = self.mtfMotion(fn2D, kmotion)

        # Calculate the System MTF
        self.logger.debug("Calculation of the Sysmtem MTF by multiplying the different contributors")
        # Hsys = 1 # dummy
        Hsys = Hdiff * Hdefoc * Hwfe * Hdet * Hsmear * Hmotion

        # Plot cuts ACT/ALT of the MTF
        self.plotMtf(Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band)

        writeMat(self.outdir, 'Hdiff_' + band, Hdiff)
        writeMat(self.outdir, 'Hdefoc_' + band, Hdefoc)
        writeMat(self.outdir, 'Hwfe_' + band, Hwfe)
        writeMat(self.outdir, 'Hdet_' + band, Hdet)
        writeMat(self.outdir, 'Hsmear_' + band, Hsmear)
        writeMat(self.outdir, 'Hmotion_' + band, Hmotion)
        writeMat(self.outdir, 'Hsys_' + band, Hsys)
        writeArray(self.outdir, 'fnAct_' + band, fnAct)
        writeArray(self.outdir, 'fnAlt_' + band, fnAlt)

        return Hsys

    def freq2d(self,nlines, ncolumns, D, lambd, focal, w):
        """
        Calculate the relative frequencies 2D (for the diffraction MTF)
        :param nlines: Lines of the TOA
        :param ncolumns: Columns of the TOA
        :param D: Telescope diameter [m]
        :param lambd: central wavelength of the band [m]
        :param focal: focal length [m]
        :param w: pixel size in meters [m]
        :return fn2D: normalised frequencies 2D (f/(1/w))
        :return fr2D: relative frequencies 2D (f/(1/fc))
        :return fnAct: 1D normalised frequencies 2D ACT (f/(1/w))
        :return fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        """
        #TODO

        eps = 10**(-8)
        fstepAlt = 1 / nlines / w
        fstepAct = 1 / ncolumns / w
        fAlt = np.arange(-1 / (2 * w), 1 / (2 * w) - eps, fstepAlt)
        fAct = np.arange(-1 / (2 * w), 1 / (2 * w) - eps, fstepAct)

        # We work with nomralized frequencies
        # compute the cut of freq
        fco = D / (lambd * focal)

        # compute teh realtive freqnecies
        fr_Alt = fAlt / fco
        fr_Act = fAct / fco
        fn_Alt = fAlt / (1/w)
        fn_Act = fAct / (1/w)

        [fnAltxx, fnActxx] = np.meshgrid(fn_Alt, fn_Act,indexing='ij')  # Please use ‘ij’ indexing or you will get the transpose
        fn2D = np.sqrt(fnAltxx * fnAltxx + fnActxx * fnActxx)

        [frAltxx, frActxx] = np.meshgrid(fr_Alt, fr_Act,indexing='ij')  # Please use ‘ij’ indexing or you will get the transpose
        fr2D = np.sqrt(frAltxx * frAltxx + frActxx * frActxx)

        return fn2D, fr2D, fn_Act, fn_Alt

    def mtfDiffract(self,fr2D):
        """
        Optics Diffraction MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :return: diffraction MTF
        """
        #TODO

        Hdiff = np.zeros((fr2D.shape[0], fr2D.shape[1]))
        for i in range(fr2D.shape[0]):
            for j in range(fr2D.shape[1]):
                if fr2D[i, j] < 1:
                    Hdiff[i, j] = 2 / np.pi * (
                                np.arccos(fr2D[i, j]) - fr2D[i, j] * np.sqrt((1 - (fr2D[i, j]) * fr2D[i, j])))
                else:
                    Hdiff[i,j]=0.
        return Hdiff


    def mtfDefocus(self, fr2D, defocus, focal, D):
        """
        Defocus MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param defocus: Defocus coefficient (defocus/(f/N)). 0-2 low defocusing
        :param focal: focal length [m]
        :param D: Telescope diameter [m]
        :return: Defocus MTF
        """
        #TODO

        x = np.pi *  defocus * fr2D * (1 - fr2D)
        Hdefoc = 2 * j1(x) /x

        return Hdefoc

    def mtfWfeAberrations(self, fr2D, lambd, kLF, wLF, kHF, wHF):
        """
        Wavefront Error Aberrations MTF
        :param fr2D: 2D relative frequencies (f/fc), where fc is the optics cut-off frequency
        :param lambd: central wavelength of the band [m]
        :param kLF: Empirical coefficient for the aberrations MTF for low-frequency wavefront errors [-]
        :param wLF: RMS of low-frequency wavefront errors [m]
        :param kHF: Empirical coefficient for the aberrations MTF for high-frequency wavefront errors [-]
        :param wHF: RMS of high-frequency wavefront errors [m]
        :return: WFE Aberrations MTF
        """
        #TODO

        Hwfe = np.exp(-fr2D * (1-fr2D) * (kLF*(wLF/lambd)**2 + kHF*(wHF/lambd)**2))

        return Hwfe

    def mtfDetector(self,fn2D):
        """
        Detector MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :return: detector MTF
        """
        #TODO

        Hdet = np.abs(np.sinc(fn2D))

        return Hdet

    def mtfSmearing(self, fnAlt, ncolumns, ksmear):
        """
        Smearing MTF
        :param ncolumns: Size of the image ACT
        :param fnAlt: 1D normalised frequencies 2D ALT (f/(1/w))
        :param ksmear: Amplitude of low-frequency component for the motion smear MTF in ALT [pixels]
        :return: Smearing MTF
        """
        #TODO

        Hsmear_1 = np.sinc(ksmear * fnAlt)
        Hsmear = np.tile(Hsmear_1.reshape(-1, 1),  ncolumns)  # usar reshape con 1 y -1 o el traspose

        return Hsmear

    def mtfMotion(self, fn2D, kmotion):
        """
        Motion blur MTF
        :param fnD: 2D normalised frequencies (f/(1/w))), where w is the pixel width
        :param kmotion: Amplitude of high-frequency component for the motion smear MTF in ALT and ACT
        :return: detector MTF
        """
        #TODO

        Hmotion = np.sinc(kmotion * fn2D)

        return Hmotion

    def plotMtf(self,Hdiff, Hdefoc, Hwfe, Hdet, Hsmear, Hmotion, Hsys, nlines, ncolumns, fnAct, fnAlt, directory, band):
        """
        Plotting the system MTF and all of its contributors
        :param Hdiff: Diffraction MTF
        :param Hdefoc: Defocusing MTF
        :param Hwfe: Wavefront electronics MTF
        :param Hdet: Detector MTF
        :param Hsmear: Smearing MTF
        :param Hmotion: Motion blur MTF
        :param Hsys: System MTF
        :param nlines: Number of lines in the TOA
        :param ncolumns: Number of columns in the TOA
        :param fnAct: normalised frequencies in the ACT direction (f/(1/w))
        :param fnAlt: normalised frequencies in the ALT direction (f/(1/w))
        :param directory: output directory
        :param band: band
        :return: N/A
        """
        #TODO

        halfAct = int(np.floor(fnAct.shape[0] / 2))
        halfAlt = int(np.floor(fnAlt.shape[0] / 2))
        fig, ax = plt.subplots()
        plt.suptitle('Alt = ' + str(halfAlt) + ' for ' + band)
        x_1 = fnAct[halfAct:]
        y_1 = Hdiff[halfAlt, halfAct:]
        y_2 = Hdefoc[halfAlt, halfAct:]
        y_3 = Hwfe[halfAlt, halfAct:]
        y_4 = Hdet[halfAlt, halfAct:]
        y_5 = Hsmear[halfAlt, halfAct:]
        y_6 = Hmotion[halfAlt, halfAct:]
        y_7 = Hsys[halfAlt, halfAct:]
        ax.plot(x_1, y_1, 'r', label='Hdiff')
        ax.plot(x_1, y_2, 'g', label='Hdefoc')
        ax.plot(x_1, y_3, 'b', label='Hwfe')
        ax.plot(x_1, y_4, 'k', label='Hdet')
        ax.plot(x_1, y_5, 'y', label='Hsmear')
        ax.plot(x_1, y_6, 'r', label='Hmotion')
        ax.plot(x_1, y_7, 'g', label='Hsys')
        plt.legend(loc='lower left')
        plt.xlabel('Spatial Frequencies [-]')
        plt.ylabel('MTF')
        plt.grid(True)
        # plt.show()
        fig.savefig(self.outdir + '/graph_mtf_alt_' + band + '_graph.png')

        fig2, ax2 = plt.subplots()
        x_2 = fnAlt[halfAlt:]
        y_1 = Hdiff[halfAlt:, halfAct]
        y_2 = Hdefoc[halfAlt:, halfAct]
        y_3 = Hwfe[halfAlt:, halfAct]
        y_4 = Hdet[halfAlt:, halfAct]
        y_5 = Hsmear[halfAlt:, halfAct]
        y_6 = Hmotion[halfAlt:, halfAct]
        y_7 = Hsys[halfAlt:, halfAct]

        a = 'Act = ' + str(halfAct) + ' for ' + band
        plt.suptitle(a)
        plt.grid(True)
        plt.xlabel('Spatial Frequencies [-]')
        plt.ylabel('MTF')
        ax2.plot(x_2, y_1, 'r', label='Hdiff')
        ax2.plot(x_2, y_2, 'g', label='Hdefoc')
        ax2.plot(x_2, y_3, 'b', label='Hwfe')
        ax2.plot(x_2, y_4, 'k', label='Hdet')
        ax2.plot(x_2, y_5, 'y', label='Hsmear')
        ax2.plot(x_2, y_6, 'r', label='Hmotion')
        ax2.plot(x_2, y_7, 'g', label='Hsys')
        plt.legend(loc='lower left')
        # plt.show()
        fig2.savefig(self.outdir + '/graph_mtf_act_' + band + '_graph.png')