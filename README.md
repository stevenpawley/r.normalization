# r.normalization
Simple script for various normalization and transformations in GRASS GIS 7

<h2>DESCRIPTION</h2>

<i>r.normalization</i> is a simple script that allows rasters, often represented by digital elevation models, to be normalized (scaled to 0-1), standardized or inverted. Options are also provided to invert data/no-data values, and perform linear percentile stretching.

<h2>EXAMPLE</h2>

<div class="code"><pre>
r.normalization input=DEM method=inversion output=inverted.dem
</pre></div>

<h2>AUTHOR</h2>

Steven Pawley
