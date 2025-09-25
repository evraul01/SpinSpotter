#!/usr/bin/env python
# encoding: utf-8

import astropy.io.fits
import numpy

import sys

def main():
    """
    csv-to-fits.py  INPUT.csv  OUTPUT.fits

    Convert a CSV file to a FITS bintable

    - In the first line of the CSV are described names of columns.
        - A column named "id" is treated as 64bit integer.
        - A column named "starnotgal" is treated as boolean (0/1).
        - Columns named "ra" and "dec" are treated as double precision float.
        - Other columns are treated as single precision float.
    """

    if len(sys.argv) != 3:
        raise Exception(
            "commandline: {}  INPUT.csv  OUTPUT.fits"
            .format(sys.argv[0]))

    recarray = loadCsvAsNumpy(sys.argv[1])
    bintable = convertNumpyToFitsBinTable(recarray)
    saveFitsBinTable(bintable, sys.argv[2])


def loadCsvAsNumpy(filename):
    dtypes = {
        "Time (BJD-2457000)" : numpy.float64,
        "Flux" : numpy.float64,
        "Flattened Flux" : numpy.float64,
        "id" : numpy.int64,
        "starnotgal" : numpy.bool,
        "RA" : numpy.float64,
        "DEC" : numpy.float64,
    }

    def nameFilter(name):
        uname = name.upper()
        if uname == "RA" or uname == "DEC":
            return uname
        elif uname == "RA_ERR":
            return "RA_err"
        elif uname == "DEC_ERR":
            return "DEC_err"
        elif uname == "ID" or uname == "STARNOTGAL":
            return name.lower()
        else:
            return name

    with open(filename) as f:
        headers = map(nameFilter, f.readline().strip().split(','))

    dtype = [ (name, dtypes[name] if name in dtypes else numpy.float32)
        for name in headers ]

    return numpy.loadtxt(filename,
        dtype = dtype, delimiter = ',', skiprows = 1)


def convertNumpyToFitsBinTable(recarray):
    return astropy.io.fits.FITS_rec.from_columns(astropy.io.fits.ColDefs(recarray))


def saveFitsBinTable(bintable, filename):
    primaryHDU = astropy.io.fits.PrimaryHDU()
    binTableHDU = astropy.io.fits.BinTableHDU(bintable)
    astropy.io.fits.HDUList([primaryHDU, binTableHDU]).writeto(filename)


if __name__ == "__main__":
    main()
