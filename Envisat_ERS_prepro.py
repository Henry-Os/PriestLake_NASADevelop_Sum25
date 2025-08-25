from esa_snappy import ProductIO, GPF, HashMap
import os
from glob import glob

# Parameters for subsetting and terrain correction
WKT = 'POLYGON((-116.9817 48.4477,-116.7727 48.4477,-116.7727 48.8248,-116.9817 48.8248,-116.9817 48.4477))'
PROJ = '''PROJCS["UTM Zone 11N / World Geodetic System 1984", GEOGCS["World Geodetic System 1984",
    DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],
    AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],
    UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], AXIS["Geodetic latitude", NORTH]],
    PROJECTION["Transverse_Mercator"], PARAMETER["central_meridian", -117.0],
    PARAMETER["latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996],
    PARAMETER["false_easting", 500000.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0],
    AXIS["Easting", EAST], AXIS["Northing", NORTH]]'''

def read_product(file):
    return ProductIO.readProduct(file)

def apply_orbit(product):
    params = HashMap()
    params.put('continueOnFail', True)
    params.put('Apply-Orbit-File', True)
    return GPF.createProduct('Apply-Orbit-File', params, product)

def apply_calibration(product):
    params = HashMap()
    params.put('outputImageScaleInDb', True)
    return GPF.createProduct('Calibration', params, product)

def apply_terrain_correction(product):
    params = HashMap()
    params.put('demName', 'SRTM 1Sec HGT')
    params.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    params.put('pixelSpacingInMeter', 12.5)
    params.put('mapProjection', PROJ)
    params.put('nodataValueAtSea', False)
    params.put('saveSelectedSourceBand', True)
    return GPF.createProduct('Terrain-Correction', params, product)

def apply_subset(product):
    params = HashMap()
    params.put('geoRegion', WKT)
    params.put('copyMetadata', True)
    return GPF.createProduct('Subset', params, product)

def satellite_subfolder(filename):
    if filename.endswith('.E1'):
        return 'ERS-1'
    elif filename.endswith('.E2'):
        return 'ERS-2'
    elif filename.endswith('.N1'):
        return 'Envisat'
    else:
        return 'Unknown'

def process_files(files, output_dir):
    for file in files:
        read = read_product(file)
        product = apply_orbit(read)
        product = apply_calibration(product)
        product = apply_terrain_correction(product)
        product = apply_subset(product)

        satellite = satellite_subfolder(file)
        satellite_dir = os.path.join(output_dir, satellite)
        os.makedirs(satellite_dir, exist_ok=True)

        output_path = os.path.join(mission_dir, product.getName())
        ProductIO.writeProduct(product, output_path, 'GeoTIFF')
        print(f'{read.getName()} successfully preprocessed into {output_path}')

# Set paths and run
os.chdir("C:/Users/henry/Documents/DEVSum25/SAR_raw")
files = glob('*.E1') + glob('*.E2') + glob('*.N1')
out_dir = "C:/Users/henry/Documents/DEVSum25/SAR_preprocessed"
process_files(files, out_dir)