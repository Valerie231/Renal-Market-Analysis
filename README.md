This project is aimed to gather and analyse Warsaw rental market data and derive insights about the prices variability. 
The project consists of two parts: data scraping part and data analysis part. 

Files description:
 1. apartament_parser_olx_with_otodom.py
    This script gets data from the OLX advertisements using different algorythms depending on the ad source:
    for otodom advertisements posted on olx, there is a distinct piece of code adjusted to the otodom website structure.
 2. full_otodom_parser.py
    Python script created explicitely for otodom platform, it will be used in further analysis due to higher data
    availability on otodom and up to 10x higher amount of active advertisements.
 3. Rental market analysis.ipynb
    Ipython notebook with step-by-step data exploration and cleaning, as well as OLS regression analysis with necessary
    data transformations applied. This file also includes data visualisations, charts and regression output.
    The interpretation of the regression results is included in the last part.

Libraries used:
beautiful soup
requests
pandas 
matplotlib.pyplot
numpy
geopandas
folium
googlemaps
scipy.stats
sklearn.preprocessing
statsmodels





