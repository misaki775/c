import statsmodels.api as sm
from itertools import product
from Datawrangling import *

def clean_ols(y_type):
    if y_type == 'One_mile':
        df_ols = df_final[['City', 'One_mile',
                       'minc', 'hhd_exp', 'pct_SNAP',
                       'transit_dist', 'transit_freq', 'avg_vehicle', 
                       'shr_Kids', 'shr_Seniors',
                       'shr_White', 'shr_Black', 'shr_Hispanic']]
    else:
        df_ols = df_final[['City', 'Half_mile',
                       'minc', 'hhd_exp', 'pct_SNAP',
                       'transit_dist', 'transit_freq', 'avg_vehicle', 
                       'shr_Kids', 'shr_Seniors',
                       'shr_White', 'shr_Black', 'shr_Hispanic']]
    df_ols = df_ols.dropna()
    return df_ols

df_ols_one = clean_ols('One_mile')
df_ols_half = clean_ols('Half_mile')

#OLS for One mile
def one_ols(df_ols, cities):
    aff_vars = ['minc', 'hhd_exp', 'pct_SNAP']
    acc_vars = ['transit_dist', 'transit_freq', 'avg_vehicle']
    ctrl_vars = ['shr_Kids', 'shr_Seniors', 
                'shr_White', 'shr_Black', 'shr_Hispanic']
    
    for city in cities:
        df_city = df_ols[df_ols['City'] == city]
    
        #Generate all combinations
        combinations = list(product(aff_vars, acc_vars))

        for aff_var, acc_var in combinations:
            independent_vars = [aff_var, acc_var] + ctrl_vars

            X = df_city[independent_vars]
            X = sm.add_constant(X)
            y = df_city['One_mile']

            model = sm.OLS(y, X).fit()

            print(f'{city}, combinations of {aff_var} and {acc_var} in one mile')
            print(model.summary())
            print('\n' + '-'*80 + '\n')

cities = ['Chicago', 'Houston', 'Los Angeles', 'New York']
one_ols(df_ols_one, cities)


#OLS for HALF mile
def half_ols(df_ols, cities):
    aff_vars = ['minc', 'hhd_exp', 'pct_SNAP']
    acc_vars = ['transit_dist', 'transit_freq', 'avg_vehicle']
    ctrl_vars = ['shr_Kids', 'shr_Seniors', 
                'shr_White', 'shr_Black', 'shr_Hispanic']
    
    for city in cities:
        df_city = df_ols[df_ols['City'] == city]
    
        #Generate all combinations
        combinations = list(product(aff_vars, acc_vars))

        for aff_var, acc_var in combinations:
            independent_vars = [aff_var, acc_var] + ctrl_vars

            X = df_city[independent_vars]
            X = sm.add_constant(X)
            y = df_city['Half_mile']

            model = sm.OLS(y, X).fit()
            
            print(f'{city}, combinations of {aff_var} and {acc_var} in half mile')
            print(model.summary())
            print('\n' + '-'*80 + '\n')

cities = ['Chicago', 'Houston', 'Los Angeles', 'New York']
half_ols(df_ols_half, cities)