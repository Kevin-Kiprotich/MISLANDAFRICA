<?xml version="1.0" ?>
<qgis>
    <pipe>
        <rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
            <rasterTransparency/>
            <rastershader>
                <colorrampshader colorRampType="INTERPOLATED">
                    <item alpha="255" value="-250" label="Enhanced Regrowth" color="#acbe4d"/>
                    <item alpha="255" value="-100" label="unburned" color="#0ae042"/>
                    <item alpha="255" value="100" label="Low" color="#fff70b"/>
                    <item alpha="255" value="270" label="Moderate Severity" color="#ffaf38"/>
                    <item alpha="255" value="660" label="High Severity" color="#a41fd6"/>
                </colorrampshader>
            </rastershader>
        </rasterrenderer>
        <brightnesscontrast/>
        <huesaturation/>
        <rasterresampler/>
    </pipe>
    <blendMode>0</blendMode>
</qgis>
