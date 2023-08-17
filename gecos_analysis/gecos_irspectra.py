import glob
import os.path
from collections import defaultdict
import numpy as np
import pandas as pd
import scipy


class GecosIRSpectra:

    """
    This class is use to get IR spectra from QM calculations.
    """

    # =========================================================================
    def __init__(self, nspectra, freqs, iractivity, temperature, deltag=None,
                 scale=None, start=0.0, end=4000.0, npoints=500, width=10.0,
                 function="lorentzian", similarity=True, logger=None):

        """
        Initialize the instance

        :param nspectra
        :param freqs
        :param iractivity
        :param temperature
        :param deltag
        :param scale
        :param start
        :param end
        :param npoints
        :param width
        :param function
        :param logger: Logger to write results
        """

        self._logger = logger
        self._nspectra = nspectra
        self._freqs_dict = freqs
        self._iractiivity_dict = iractivity
        self._temperature = temperature
        self._deltag = deltag
        self._start = start
        self._end = end
        self._npoints = npoints
        self._width = width
        self._function = function
        self._similarity = similarity
        self._isscaled = False
        self._nspectra = len(self._freqs_dict)
        self._scale = scale
        self._spectrum = defaultdict()
        self._xvalues = None
        self._scaled_boltz_spectrum = None
        self._scaled_simple_spectrum = None
        self._similarity_matrix_pearson = None
        self._similarity_matrix_spearman = None

        # Scale frequencies
        if scale is not None:
            self._scale_frequencies()

    # =========================================================================
    def _scale_frequencies(self):

        """
        Scale frequency positions.

        :return:
        """

        for ikey, ivalue in self._freqs_dict.items():
            self._freqs_dict[ikey] = ivalue * self._scale
        self._isscaled = True

    # =========================================================================
    def calculate_spectrum(self, avg=None):

        """
        Calculate spectrum

        :return:
        """

        # Zip in a list the freq and intensity for each spectra
        peaks = defaultdict()
        for ikey, freqvalue in self._freqs_dict.items():
            irvalue = self._iractiivity_dict[ikey]
            peaks[ikey] = list(zip(freqvalue, irvalue))

        # Create the spectrum and save the data
        for ikey, ivalue in self._freqs_dict.items():
            self._spectrum[ikey] = np.zeros(self._npoints)
            if self._function.upper() == "LORENTZIAN":
                self._xvalues = np.arange(self._npoints)*float(self._end-self._start)/(self._npoints-1)+self._start
            elif self._function.upper() == "LORENTZIAN_GAUSSIAN":
                self._xvalues = np.arange(self._npoints)*float(self._end-self._start)/self._npoints+self._start
            for i in range(self._npoints):
                x = self._xvalues[i]
                for (pos, height) in peaks[ikey]:
                    self._spectrum[ikey][i] = self._spectrum[ikey][i] + \
                                           self._formula(self._function, x, pos, height, self._width)

            filename = os.path.splitext(os.path.split(ikey)[-1])[0]+"_spectrum.dat"
            with open(filename, 'w') as fdat:
                line = ""
                max_intensity = np.max(self._spectrum[ikey])
                range_freq = float(self._end-self._start)
                for i in range(self._npoints):
                    if self._function.upper() == "LORENTZIAN":
                        realx = range_freq*(i+1)/self._npoints+self._start
                    elif self._function.upper() == "LORENTZIAN_GAUSSIAN":
                        realx = self._xvalues[i]
                    line += "{} {} {}\n".format(realx, self._spectrum[ikey][i], self._spectrum[ikey][i]/max_intensity)
                fdat.writelines(line)

        # GNUPLOT templates
        self._gnuplot_template()

        # Average spectrum
        self._avg_spectrum(avg)

        # Similary of the spectra
        # The spectra with lowest energy is used as template
        self._calculate_similarity()

    # =========================================================================
    def _calculate_similarity(self):

        """
        Assesment of the similarity of the calculated QM spectra using the
        method discussed in https://dx.doi.org/10.1021/acs.jctc.0c00126

        :return:
        """

        nspectra = len(self._freqs_dict)
        self._similarity_matrix_pearson = np.zeros([nspectra, nspectra], dtype=np.float32)
        self._similarity_matrix_spearman = np.zeros([nspectra, nspectra], dtype=np.float32)
        xidx = 0
        for xkey, xvalue in self._freqs_dict.items():
            yidx = 0
            for ykey, yvalue in self._freqs_dict.items():
                pearson = scipy.stats.pearsonr(xvalue, yvalue)
                spearman = scipy.stats.spearmanr(xvalue, yvalue)
                self._similarity_matrix_pearson[xidx, yidx] = pearson.statistic
                self._similarity_matrix_spearman[xidx, yidx] = spearman.correlation
                yidx += 1
            xidx += 1

    # =========================================================================
    def _formula(self, name, x, peak, height, width):
        """The lorentzian curve.

        f(x) = a/(1+a)

        where a is FWHM**2/4
        """

        if name.upper() == "LORENTZIAN":
            a = width**2./4.
            return float(height)*a/((peak-x)**2 + a)
        elif name.upper() == "LORENTZIAN_GAUSSIAN":
            """ See DOI: 10.13140/RG.2.1.4181.6160"""
            return float(2. / np.pi) * (100 / np.log(10)) * float(height) * (
                        width / ((4 * (peak - x) ** 2) + width ** 2))
        else:
            m = "\t\t ERROR: {} formula is not implemented".format(name)
            print(m) if self._logger is not None else self._logger.error(m)

    # =========================================================================
    def _gnuplot_template(self, nx=3, ny=3):

        max_intensity = 0
        for ikey, ir in self._spectrum.items():
            if np.max(ir) > max_intensity:
                max_intensity = np.max(ir)
        max_intensity += 10
        max_intensity = np.floor(max_intensity)

        linegnuplot = "reset\n"
        linegnuplot += 'set xlabel "Freq (cm^-1)"\n'
        linegnuplot += 'set ylabel "Intensity"\n'
        linegnuplot += 'set grid\n'
        linegnuplot += 'set xrange [{0:d}:{1:d}]\n'.format(int(self._start), int(self._end))
        linegnuplot += 'set yrange [{0:d}:{1:d}]\n'.format(0, int(max_intensity))
        linegnuplot += "# "+50*'*'+"\n"

        iwxt = 1
        iplot = 0
        for ikey, ir_values in self._spectrum.items():
            ifilename = os.path.splitext(os.path.split(ikey)[-1])[0]+"_spectrum.dat"
            if iplot % (nx*ny) == 0:
                linegnuplot += "unset multiplot\n"
                iheight = int(500 * ny)
                iwidth = int(300 * nx)
                linegnuplot += 'set term wxt {0:d} enhanced dashed size {1:d},{2:d} ' \
                               'font "Arial,8"\n'.format(iwxt, iheight, iwidth)
                linegnuplot += 'set multiplot layout {0:d},{1:d}\n'.format(nx, ny)
                iwxt += 1
            ititle = ifilename.replace("_", "-")
            linegnuplot += 'set title "{0:s}"\n'.format(ititle)
            linegnuplot += 'p "./{0:s}" u 1:2 w l notitle\n'.format(ifilename)
            iplot += 1

        with open("template_gnu.plot", "w") as fgnuplot:
            fgnuplot.writelines(linegnuplot)

    # =========================================================================
    def _avg_spectrum(self, avg):

        """
        Averaging spectra
        """

        # ===============================================
        def boltzmann_weight():

            """
            Calculate the boltzmann averaged spectrum
            :return:
            """

            nspectra = self._nspectra
            kb_t = 1.987204259/1000  # kcal/mol
            sum_weight = np.zeros(self._npoints)
            sum_bfactor = 0.0

            for ikey, ir_values in self._spectrum.items():
                boltzmann_factor = np.exp(-self._deltag[ikey] / (kb_t * self._temperature[ikey]))
                sum_weight += boltzmann_factor * self._spectrum[ikey]
                sum_bfactor += boltzmann_factor

            self._scaled_boltz_spectrum = sum_weight / sum_bfactor

            filename = "boltzmann_spectrum.dat"
            title = "# Boltzmann Averaged spectrum"

            with open(filename, 'w') as fdat:
                line = title
                for i in range(self._npoints):
                    line += "{} {}\n".format(self._xvalues[i], self._scaled_boltz_spectrum[i])
                fdat.writelines(line)

        # ===============================================
        def simple_weight():

            """
            Calculate the arithmethic averaged spectrum
            :return:
            """

            nspectra = self._nspectra
            sum_weight = np.zeros(self._npoints)

            for ikey, ir_values in self._spectrum.items():
                boltzmann_factor = 1.0
                sum_weight += boltzmann_factor * self._spectrum[ikey]

            self._scaled_simple_spectrum = sum_weight / nspectra

            filename = "averaged_spectrum.dat"
            title = "# Averaged spectrum (Non boltzmann)"

            with open(filename, 'w') as fdat:
                line = title
                for i in range(self._npoints):
                    line += "{} {}\n".format(self._xvalues[i], self._scaled_simple_spectrum[i])
                fdat.writelines(line)

        # ===============================================
        def gnu_template_avg(nx=1, ny=1):

            tmpdict = defaultdict(list)
            if avg == "boltzmann" and self._deltag is not None:
                tmpdict["boltzmann"] = self._scaled_boltz_spectrum
            elif avg == "simple":
                tmpdict["averaged"] = self._scaled_simple_spectrum
            else:
                tmpdict["boltzmann"] = self._scaled_boltz_spectrum
                tmpdict["averaged"] = self._scaled_simple_spectrum

            max_intensity = 0
            for ikey, ir in tmpdict.items():
                if np.max(ir) > max_intensity:
                    max_intensity = np.max(ir)
            max_intensity += 10
            max_intensity = np.floor(max_intensity)

            linegnuplot = "reset\n"
            linegnuplot += 'set xlabel "Freq (cm^-1)"\n'
            linegnuplot += 'set ylabel "Intensity"\n'
            linegnuplot += 'set grid\n'
            linegnuplot += 'set xrange [{0:d}:{1:d}]\n'.format(int(self._start), int(self._end))
            linegnuplot += 'set yrange [{0:d}:{1:d}]\n'.format(0, int(max_intensity))
            linegnuplot += "# "+50*'*'+"\n"

            iwxt = 1
            iplot = 0
            for ikey, ir_values in tmpdict.items():
                ifilename = os.path.splitext(os.path.split(ikey)[-1])[0]+"_spectrum.dat"
                if iplot % (nx*ny) == 0:
                    linegnuplot += "unset multiplot\n"
                    iheight = int(500 * ny)
                    iwidth = int(300 * nx)
                    linegnuplot += 'set term wxt {0:d} enhanced dashed size {1:d},{2:d} ' \
                                   'font "Arial,8"\n'.format(iwxt, iheight, iwidth)
                    linegnuplot += 'set multiplot layout {0:d},{1:d}\n'.format(nx, ny)
                    iwxt += 1
                ititle = ifilename.replace("_", "-")
                linegnuplot += 'set title "{0:s}"\n'.format(ititle)
                linegnuplot += 'p "./{0:s}" u 1:2 w l notitle\n'.format(ifilename)
                iplot += 1

            with open("template_avg_gnu.plot", "w") as fgnuplot:
                fgnuplot.writelines(linegnuplot)

        if avg == "boltzmann" and self._deltag is not None:
            boltzmann_weight()
        elif avg == "simple":
            simple_weight()
        else:
            boltzmann_weight()
            simple_weight()

        gnu_template_avg()
