# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterCH_LV95ETRS89DirInv.py
    ---------------------
    Date                 : March 2015
    Copyright            : (C) 2015 by Giovanni Manghi
    Email                : giovanni dot manghi at naturalgis dot pt
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giovanni Manghi'
__date__ = 'March 2015'
__copyright__ = '(C) 2015, Giovanni Manghi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import inspect
import os

from PyQt4.QtGui import QIcon

from processing.gui.Help2Html import getHtmlFromRstFile

try:
    from processing.parameters.ParameterRaster import ParameterRaster
    from processing.parameters.ParameterSelection import ParameterSelection
    from processing.outputs.OutputRaster import OutputRaster
except:
    from processing.core.parameters import ParameterRaster
    from processing.core.parameters import ParameterSelection
    from processing.core.outputs import OutputRaster

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class RasterCH_LV95ETRS89DirInv(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    TRANSF = 'TRANSF'
    TRANSF_OPTIONS = ['Direct: CH1903/LV03 [EPSG:21781] -> New Data]',
                      'Inverse: New Data -> CH1903/LV03 [EPSG:21781]']
    CRS = 'CRS'
    CRS_OPTIONS = ['ETRS89 [EPSG:4258]',
                  'CH1903+ [EPSG:2056]']

    GRID = 'GRID'
    GRID_OPTIONS = ['CHENyx06']

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/ch.png')

    def help(self):
        name = self.commandLineName().split(':')[1].lower()
        filename = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'help', name + '.rst')
        try:
          html = getHtmlFromRstFile(filename)
          return True, html
        except:
          return False, None

    def defineCharacteristics(self):
        self.name = '[CH] Direct and inverse Raster transformation'
        self.group = '[CH] Switzerland'
        self.addParameter(ParameterRaster(self.INPUT, 'Input raster', False))
        self.addParameter(ParameterSelection(self.TRANSF, 'Transformation',
                          self.TRANSF_OPTIONS))
        self.addParameter(ParameterSelection(self.CRS, 'New Datum',
                          self.CRS_OPTIONS))
        self.addParameter(ParameterSelection(self.GRID, 'NTv2 Grid',
                          self.GRID_OPTIONS))
        self.addOutput(OutputRaster(self.OUTPUT, 'Output'))

    def processAlgorithm(self, progress):

        if self.getParameterValue(self.TRANSF) == 0:
            # Direct transformation
            arguments = ['-t_srs']
            if self.getParameterValue(self.CRS) == 0:
                # CH1903+/LV95
                if self.getParameterValue(self.GRID) == 0:
                    # CHENyx06
                    arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +nadgrids=@null +wktext +units=m')
                    gridname = 'CHENYX06a.gsb'
            else:
                # ETRS89
                if self.getParameterValue(self.GRID) == 0:
                    # CHENyx06
                    arguments.append('EPSG:4258')
                    gridname = 'chenyx06etrs.gsb'
            arguments.append('-s_srs')
            arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids=' + os.path.dirname(__file__) + '/grids/' + gridname + ' +wktext +units=m +no_defs')
        else:
            # Inverse transformation
            arguments = ['-s_srs']
            if self.getParameterValue(self.CRS) == 0:
                # CH1903+/LV95
                if self.getParameterValue(self.GRID) == 0:
                    # CHENyx06
                    arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +nadgrids=@null +wktext +units=m')
                    gridname = 'CHENYX06a.gsb'
            else:
                # ETRS89
                if self.getParameterValue(self.GRID) == 0:
                    # CHENyx06
                    arguments.append('EPSG:4258')
                    gridname = 'chenyx06etrs.gsb'
            arguments.append('-t_srs')
            arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids=' + os.path.dirname(__file__) + '/grids/' + gridname + ' +wktext +units=m +no_defs')

        arguments.append('-multi')
        arguments.append('-of')
        out = self.getOutputValue(self.OUTPUT)
        arguments.append(GdalUtils.getFormatShortNameFromFilename(out))
        arguments.append(self.getParameterValue(self.INPUT))
        arguments.append(out)

        if os.path.isfile(os.path.dirname(__file__) + '/grids/CHENYX06a.gsb') is False:
            try:
                from urllib import urlretrieve
            except ImportError:
                from urllib.request import urlretrieve
            urlretrieve ("https://github.com/NaturalGIS/ntv2_transformations_grids_and_sample_data/raw/master/ch/CHENYX06a.gsb", os.path.dirname(__file__) + "/grids/CHENYX06a.gsb")
            urlretrieve ("https://github.com/NaturalGIS/ntv2_transformations_grids_and_sample_data/raw/master/ch/chenyx06etrs.gsb", os.path.dirname(__file__) + "/grids/chenyx06etrs.gsb")

        GdalUtils.runGdal(['gdalwarp', GdalUtils.escapeAndJoin(arguments)],
                          progress)
