# Free UK Geospatial Data Overview

This document summarizes the main **free geospatial datasets** available in the UK, including Ordnance Survey (OS) OpenData, OpenStreetMap, government portals, property boundaries, environment, and satellite imagery. All sources are legal for personal, academic, and (in most cases) commercial use. Use this as a reference for data discovery, download, and integration.

---

## Ordnance Survey (OS) — Free Datasets

Available at: [https://osdatahub.os.uk/downloads/open](https://osdatahub.os.uk/downloads/open)

| Dataset                | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| **OS OpenMap – Local** | Detailed vector base map of towns, roads, rail, buildings            |
| **OS Boundary-Line**   | Political/administrative boundaries (parliamentary, councils, wards) |
| **OS Open Roads**      | Road network with road names and classifications                     |
| **OS Open Rivers**     | Watercourses, rivers, and streams                                    |
| **OS Terrain 50**      | Contour lines and digital terrain model (DTM) at 50m resolution      |
| **OS Open Names**      | Gazetteer with place names, grid refs, and postcodes                 |
| **Code-Point Open**    | Postcode centroid coordinates (first part of postcode)               |

- **Licence:** OS OpenData Licence (free for personal, academic, or commercial use)

---

## OpenStreetMap (OSM)

Available at: [https://download.geofabrik.de/europe/great-britain.html](https://download.geofabrik.de/europe/great-britain.html)

| Data                       | Description                                      |
| -------------------------- | ------------------------------------------------ |
| Roads, buildings, railways | Detailed, user-generated data with good coverage |
| Points of interest         | Schools, hospitals, shops, parks, etc.           |
| Paths, cycleways           | Often more detailed than OS for foot travel      |
| Land use & water           | Woods, residential zones, lakes, etc.            |

- **Licence:** Open Database License (ODbL)

---

## Government Portals

### [data.gov.uk](https://data.gov.uk)
- Searchable portal for UK public datasets (flood, land cover, soil, transport, property, etc.)

### [Environment Agency](https://environment.data.gov.uk/)
- Flood risk maps (Zones 2 & 3, river flood risk)
- LiDAR Elevation Data (0.25–2m resolution)
- Catchment and river basin data
- Surface water and drainage data
- **Licence:** Open Government Licence (OGL)

---

## Cadastral & Property Data

### [HM Land Registry INSPIRE Polygons](https://use-land-property-data.service.gov.uk/datasets/inspire)
- Property boundary polygons (England & Wales)
- GML download + WMS API
- Does *not* include ownership info (that's paid)
- **Licence:** INSPIRE Directive (free for public use)

---

## Environment & Land Cover

### [UKCEH Land Cover Map 2019 (Open)](https://catalogue.ceh.ac.uk/documents/9f9f43e4-8b2c-4c0d-a5e5-4e4c4b54d8a6)
- Generalised land cover at 25m resolution
- Cropland, woodland, urban, etc.
- Based on satellite and survey data
- **Licence:** Free for non-commercial use

---

## Satellite Imagery

### [Copernicus Open Access Hub](https://scihub.copernicus.eu/)
- Sentinel-2 imagery (10–20m resolution, optical)
- Sentinel-1 (SAR for terrain, water, infrastructure)
- **Licence:** Free & open for any use

---

## Summary Table

| Category            | Free Source               | Example Datasets           |
| ------------------- | ------------------------- | -------------------------- |
| Topographic maps    | OS OpenMap, OS Terrain 50 | Roads, rivers, contours    |
| Admin boundaries    | OS Boundary-Line          | Council areas, wards       |
| Property boundaries | HM Land Registry INSPIRE  | Parcel outlines            |
| Flood & water       | Environment Agency        | Flood Zones, LiDAR, rivers |
| Elevation           | OS Terrain 50, EA LiDAR   | DTM, contours              |
| Land cover          | UKCEH, Copernicus         | Land use types             |
| Roads & buildings   | OSM, OS Open Roads        | Full GB coverage           |
| Satellite imagery   | Copernicus (Sentinel-2)   | Updated every 5 days       |

---

## Usage Notes
- Most datasets are available in GIS-friendly formats (Shapefile, GML, GeoJSON, CSV).
- QGIS is recommended for viewing and combining these datasets.
- Always check the licence for commercial use, but most OS OpenData and OGL datasets are business-friendly.
- For scripting/automation, Python (with `geopandas`, `fiona`, `rasterio`) or PowerShell can be used to download and process data.

---

## Need Help?
- For step-by-step download, QGIS setup, or data integration, refer to this document and mention "FREE_UK_GEODATA_OVERVIEW.md" in your request.
- For the latest links and updates, always check the official data provider’s website. 