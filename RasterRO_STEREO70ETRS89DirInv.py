# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterCAT_ED50ETRS89DirInv.py
    ---------------------
    Date                 : July 2015
    Copyright            : (C) 2015 by Carlos L�pez (PSIG)
    Email                : carlos dot lopez at psig dot es
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

Edited by Nicu Tofan <nicu.tofan@gmail.com> for Romania's Stereo 70.
"""

__author__ = 'Nicu Tofan'
__date__ = 'June 2017'
__copyright__ = '(C) 2017, Nicu Tofan'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import inspect
import os

from PyQt4.QtGui import *

from qgis.core import *

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

proj_def = '+proj=sterea +lat_0=46 +lon_0=25 +k=0.99975 +x_0=500000 +y_0=500000 +ellps=krass +nadgrids=' + os.path.dirname(__file__) + '/grids/stereo70_etrs89A.gsb +units=m +no_defs '

class RasterRO_STEREO70ETRS89DirInv(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    TRANSF = 'TRANSF'
    TRANSF_OPTIONS = ['Direct: Old Data -> ETRS89 [EPSG:4258]',
                      'Inverse: ETRS89 [EPSG:4258] -> Old Data']
    CRS = 'CRS'
    CRS_OPTIONS = ['Pulkovo 1942(58) / Stereo70 [EPSG:3844]']
    GRID = 'GRID'
    GRID_OPTIONS = ['stereo70_etrs89A']

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/ro.png')

    def help(self):
        name = self.commandLineName().split(':')[1].lower()
        filename = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'help', name + '.rst')
        try:
          html = getHtmlFromRstFile(filename)
          return True, html
        except:
          return False, None

    def defineCharacteristics(self):
        self.name = '[RO] Direct and inverse Raster tranformation'
        self.group = '[RO] Romania'
        self.addParameter(ParameterRaster(self.INPUT, 'Input raster', False))
        self.addParameter(ParameterSelection(self.TRANSF, 'Transformation',
                          self.TRANSF_OPTIONS))
        self.addParameter(ParameterSelection(self.CRS, 'Old Datum',
                          self.CRS_OPTIONS))
        self.addParameter(ParameterSelection(self.GRID, 'NTv2 Grid',
                          self.GRID_OPTIONS))
        self.addOutput(OutputRaster(self.OUTPUT, 'Output'))

    def processAlgorithm(self, progress):

        if self.getParameterValue(self.TRANSF) == 0:
            # Direct transformation
            arguments = ['-s_srs']
            if self.getParameterValue(self.CRS) == 0:
                # Stereo70
                if self.getParameterValue(self.GRID) == 0:
                    # stereo70_etrs89A
                    arguments.append(proj_def)
            arguments.append('-t_srs')
            arguments.append('EPSG:4258')
        else:
            # Inverse transformation
            arguments = ['-s_srs']
            arguments.append('EPSG:4258')
            arguments.append('-t_srs')
            if self.getParameterValue(self.CRS) == 0:
                # Stereo 70
                if self.getParameterValue(self.GRID) == 0:
                    # stereo70_etrs89A
                    arguments.append(proj_def)

        arguments.append('-multi')
        arguments.append('-of')
        out = self.getOutputValue(self.OUTPUT)
        arguments.append(GdalUtils.getFormatShortNameFromFilename(out))
        arguments.append(self.getParameterValue(self.INPUT))
        arguments.append(out)

        if os.path.isfile(os.path.dirname(__file__) + '/grids/stereo70_etrs89A.gsb') is False:
           import urllib
           urllib.urlretrieve ("https://github.com/tudorbarascu/stereo70-etrs89/raw/master/grids/stereo70_etrs89A.gsb", os.path.dirname(__file__) + "/grids/stereo70_etrs89A.gsb")

        GdalUtils.runGdal(['gdalwarp', GdalUtils.escapeAndJoin(arguments)],
                          progress)
