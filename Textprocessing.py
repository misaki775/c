import os
import pandas as pd

base_path = r'/Users/misaki/Documents/GitHub/final-project-workalcoholic'
def load_txt(file_name):
    with open(os.path.join(base_path,file_name), 'r') as file:
        content = file.readlines()
        # Skip the first line and the last line that doesn't contain useful 
        # information:
        content =  content[1:-1]
    return content

def tract_number(city,city_name):
    census_list = []
    for line in city:
        line = line.replace(';;;',';')
        line = line.split(';')
        # Make sure every GeoID for the census block has a lenth of 15 numbers:
        assert len(line[1]) == 15
        line[4] = line[4].replace('.','')
        if len(line[4]) !=6:
            a = 6-len(line[4])
            line[4] = a*'0' + line[4]
        census_list.append(line)
    df = pd.DataFrame(census_list, 
                      columns = ['Type','FULLCODE','STATE','COUNTY',
                                 'TRACT','BLOCK','PLACE','COUSUB','SHEETS'])
    # Census blocks is the smallest geographic unit used by the United States 
    # Census Bureau. According to the coding rule, a 15-digit GeoID consists a 
    # 2-digit STATE code, 3 digit COUNTY code, a 6-digit TRACT Code and 4-digit 
    # BlOCK Code. Hence, we can get the 11-digit GeoID (census tracts) for all 
    # census blocks in any city with the data provided:
    df['TRACTID'] = df['STATE'] + df['COUNTY'] +df['TRACT']
    assert len(df['TRACTID'] == 11)
    # Draw all distinct values:
    df_distinct = pd.DataFrame(df['TRACTID'].unique(),
                               columns = ['TRACTID'])
    # Make sure that the type of the Census Tract is string, in cases of unwanted
    # issues in the later merging:
    df_distinct['TRACTID'] = df_distinct['TRACTID'].astype(str)
    df_distinct['City'] = city_name
    return df,df_distinct