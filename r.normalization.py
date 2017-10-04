#!/usr/bin/env python
#
##############################################################################
#
# MODULE:       Normalization
#
# AUTHOR(S):    Steven Pawley
#
# PURPOSE:      Simple script that provides quick access to several normalization,
#               standardization and raster inversion methods
#
# COPYRIGHT:    (C) 2015 Steven Pawley, and by the GRASS Development Team
#
# DATE:         September 15 2017
#
##############################################################################

#%module
#% description: Raster normalization, standardization and inversion
#% keyword: raster
#% keyword: inversion
#% keyword: normalization
#% keyword: standardization
#%end

#%option G_OPT_R_INPUT
#% description: Input raster
#% key: input
#% required : yes
#%end

#%option
#% key: method
#% type: string
#% description: Transformation method
#% required: yes
#% answer: standardization
#% options: normalization,standardization,inversion,invert_nodata,percentile_stretch
#%end

#%option
#% key: percentiles
#% type: string
#% description: Percentiles for linear stretch
#% required: no
#% answer: 2,98
#%end

#%option G_OPT_R_OUTPUT
#% description: Output raster
#% key: output
#% required : yes
#%end

import sys
from subprocess import PIPE
import grass.script as gs
from grass.pygrass.modules.shortcuts import raster as r
from grass.script.utils import parse_key_val


def main():
    raster = options['input']
    output = options['output']
    percentiles = options['percentiles']
    method = options['method']
    
    # remove mapset from output name in case of overwriting existing map
    output = output.split('@')[0]

    # get univariate raster statistics
    gs.message("Retrieving univariate statistics...")
    stats = parse_key_val(
        r.univar(map=raster, flags='g', stdout_=PIPE).outputs.stdout, sep='=')
    
    # transformation methods
    if method == 'normalization':
        gs.message("Normalizing the input raster...")
        r.mapcalc(
            '{x} = float(({raster} - {minval}) / ({maxval} - {minval}))'.format(
                    x=output, raster=raster,
                    maxval=stats['max'], minval=stats['min']))

    elif method == 'standardization':
        gs.message("Standardizing the input raster...")
        r.mapcalc(
            '{x} = float(({raster} - {mean}) / {std})'.format(
                    x=output, raster=raster,
                    mean=stats['mean'], std=stats['stddev']))
        
    elif method == 'inversion':
        gs.message("Inverting the input raster...")
        r.mapcalc(
            '{x} = (({raster} - {maxval}) * -1) + {minval}'.format(
                x=output, raster=raster, maxval=stats['max'], minval=stats['min']))

    elif method == 'invert_nodata':
        gs.message("Inverting data/no-data...")
        r.mapcalc(
            '{x} = if(isnull({y}), 1, null())'.format(x=output, y=raster))

    elif method == 'percentile_stretch':
        
        # split string and convert to float or integer
        percentiles = percentiles.split(',')
        percentiles = list(map(float, percentiles))
    
        if len(percentiles) != 2:
            gs.fatal('Need to specify lower and upper percentiles for linear stretch  (comma separated)')

        gs.message("Performing linear percentile stretch...")
        p = r.quantile(
            input=raster, percentiles=percentiles, quiet=True, 
            stdout_=PIPE).outputs.stdout
        
        pmin = float(p.splitlines()[0].split(':')[2])
        pmax = float(p.splitlines()[1].split(':')[2])
        
        r.mapcalc(
            '{x} = if({Pin}<{c},{a}, if({Pin}>{d}, {b}, ({Pin}-{c}) * ({b}-{a}) / ({d}-{c}) + {a}))'.format(
                x=output, Pin=raster,
                a=stats['min'], b=stats['max'],
                c=pmin, d=pmax))

    return 0

if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
