import os
import pandas as pd
import requests
import json
from Textprocessing import *
from bs4 import BeautifulSoup
from io import BytesIO
import geopandas

base_path = r'/Users/misaki/Documents/GitHub/final-project-workalcoholic'
url = 'https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data/'

# Following 2 functions is to webscrape the biggest and the main dataset from
# usda website. We use the beautiful soup to scrape the hyperlinke and found the
# one for the needed dataset. We can easily change to download another dataset
# (if needed) by changing the index number:
def web_scraping(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find('body').find_all('a')
    href_links = [link for link in links if link.get('href')]
    file_url = 'https://www.ers.usda.gov' + href_links[65].get('href')
    return file_url

def download_main(url,sheet_name):
    response = requests.get(url)
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name = sheet_name)
    return df

# Due to the speciality of the tract number of the California that starts with
# 0, loading the csv data will cause the lost of first digit. Hence, to make 
# sure the correctness of the tractid, we use the function to add zero if the 
# lenth is not enough:
def add_zero(tractid):
    if len(tractid) != 11:
        lenth = len(tractid)
        return (11-lenth)*'0' + tractid
    else:
        return tractid
    
def load_main_data():
    # Download the data directly using webscrape function:
    df = download_main(excel_url,'Food Access Research Atlas')
    df = df[['CensusTract','Pop2010','TractBlack','TractHispanic','TractWhite',
             'TractKids','TractSeniors','LALOWI1_10','LALOWI05_10']]
    df = df.rename(columns = {'CensusTract': 'TRACTID',
                              'LALOWI1_10':'One_mile','LALOWI05_10':'Half_mile'})
    # Apply add zero and astype(str) for every dataset loaded to avoid mistakes:
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    # Calculate the demographic share for later OLS purposes:
    df['shr_Black'] = df['TractBlack']/df['Pop2010']
    df['shr_White'] = df['TractWhite']/df['Pop2010']
    df['shr_Hispanic'] = df['TractHispanic']/df['Pop2010']
    df['shr_Kids'] = df['TractKids']/df['Pop2010']
    df['shr_Seniors'] = df['TractSeniors']/df['Pop2010']
    return df

# For every factor, we have four separte dataset for four states. Since the data
# has similarity in the file name, it is more convenient to load it in fucntion:
def load_4state(name):
    state_list = ['IL','TX','NY','CA']
    path_state =[]
    for state in state_list:
        file = 'data/' + state + name
        path = os.path.join(base_path,file)
        path_state.append(path)
    df_il = pd.read_csv(path_state[0],skiprows = 1)
    df_tx = pd.read_csv(path_state[1],skiprows = 1)
    df_ny = pd.read_csv(path_state[2],skiprows = 1)
    df_ca = pd.read_csv(path_state[3],skiprows = 1)
    return df_il, df_tx,df_ny,df_ca
        
def load_expenditure():
    df_il,df_tx,df_ny,df_ca = load_4state('_hhd_exp.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df = df[['GeoID','total_avg']]
    # Change name in every data for the convenience in later meging:
    df = df.rename(columns = {'total_avg': 'hhd_exp',
                              'GeoID':'TRACTID'})
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df

def load_med_income():
    df_il,df_tx,df_ny,df_ca = load_4state('_minc.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df = df[['GeoID','mhhinc']]
    df = df.rename(columns = {'mhhinc': 'minc',
                              'GeoID':'TRACTID'})
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df

def load_snap():
    df_il,df_tx,df_ny,df_ca = load_4state('_pct_SNAP.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df = df[['GeoID','pfamsnap']]
    df = df.rename(columns = {'pfamsnap': 'pct_SNAP',
                              'GeoID':'TRACTID'})
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df


def merge_indicator1(income,expenditure,snap):
    df = income.merge(expenditure,on = 'TRACTID',
                       how = 'inner').merge(snap,on = 'TRACTID',how = 'inner')
    return df


def load_distance():
    df_il,df_tx,df_ny,df_ca = load_4state('_transit_dist.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    # There is some unexpected issue in the underlying data that Scientific
    # notation is left in the column for 'GeoID', hence, we use the 'GeoID_Formatted'
    # instead and do some necessary text processing:
    df['TRACTID'] = df['GeoID_Formatted'
                       ].str.replace('="','').str.replace('"','').str[:-1]
    df = df.groupby('TRACTID')['d4a'].mean().reset_index()
    df = df.rename(columns = {'d4a': 'transit_dist'})
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df


def load_freq():
    df_il,df_tx,df_ny,df_ca = load_4state('_transit_freq.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df['TRACTID'] = df['GeoID_Formatted'
                           ].str.replace('="','').str.replace('"','').str[:-1]
    df = df.groupby('TRACTID')['d4d'].mean().reset_index()
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    df = df.rename(columns = {'d4d': 'transit_freq'})
    return df


def load_nocar():
    df_il,df_tx,df_ny,df_ca = load_4state('_avg_vhc.csv')
    df = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df = df[['GeoID','avmv']]
    df = df.rename(columns = {'avmv': 'avg_vehicle',
                              'GeoID':'TRACTID'})
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df

def merge_indicator2(distance,freq,nocar):
    mid = pd.merge(distance,freq,on = 'TRACTID',how = 'inner')
    df = pd.merge(mid,nocar,on = 'TRACTID',how = 'inner')
    return df

def load_census():
    # Functions in the Textprocessing py has been imported and used here to
    # load the census No. for all 4 cities:
    census_chi = load_txt('chi_censusblock.txt') 
    census_ny = load_txt('ny_censusblock.txt') 
    census_hou = load_txt('hou_censusblock.txt')
    census_la = load_txt('la_censusblock.txt')
    chicago, census_chi = tract_number(census_chi,'Chicago')
    newyork, census_ny = tract_number(census_ny,'New York')
    houston, census_hou = tract_number(census_hou,'Houston')
    la, census_la = tract_number(census_la,'Los Angeles')
    df = pd.concat([census_chi, census_ny,census_hou,census_la],ignore_index=True)
    df['TRACTID'] = df['TRACTID'].astype(str)
    df['TRACTID'] = df['TRACTID'].apply(add_zero)
    return df

# Merge all the data for just numeric data and eport it for the later use in
# OLS regression and plotting:
def merge_all(main,indicator1,indicator2,census_no):
    df_1 = main.merge(indicator1,on = 'TRACTID',
                      how = 'inner').merge(indicator2, on = 'TRACTID',how = 'inner')
    df = df_1.merge(census_no,on = 'TRACTID',how = 'inner')
    df['TRACTID'] = df['TRACTID'].astype(str)
    return df

# Merge the dataset with shapefile, but no need to export it.
def merge_shp():
    df_il = geopandas.read_file(os.path.join(base_path,
                                          'tl_2020_17_tract/tl_2020_17_tract.shp'))
    df_ny = geopandas.read_file(os.path.join(base_path,
                                          'tl_2020_36_tract/tl_2020_36_tract.shp'))
    df_tx = geopandas.read_file(os.path.join(base_path,
                                          'tl_2020_48_tract/tl_2020_48_tract.shp'))
    df_ca = geopandas.read_file(os.path.join(base_path,
                                          'tl_2020_06_tract/tl_2020_06_tract.shp'))
    df_shp = pd.concat([df_il,df_tx,df_ny,df_ca],ignore_index=True)
    df_shp = df_shp.rename(columns = {'GEOID':'TRACTID'})
    df = df_shp.merge(df_final, on = 'TRACTID', how = 'inner')
    df['TRACTID'] = df['TRACTID'].astype(str)
    return df

excel_url = web_scraping(url)
expenditure = load_expenditure()
med_income = load_med_income()
snap = load_snap()
indicator1 = merge_indicator1(med_income,expenditure,snap)
main_data = load_main_data()
distance = load_distance()
freq = load_freq()
nocar = load_nocar()
indicator2 = merge_indicator2(distance,freq,nocar)
census_no = load_census()
df_final = merge_all(main_data,indicator1,indicator2,census_no)
df_final.to_csv('Final_Data.csv', index=False)
df_final_shp = merge_shp()