from OLSRegression import *
import os
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import numpy as np
import seaborn as sns

base_path = r'/Users/misaki/Documents/GitHub/final-project-workalcoholic'

def uni_ols(x_acc,x_aff,y,city):
    if y == 'One_mile':
        df = df_ols_one
    else:
        df = df_ols_half
    # Select city:
    df_city = df[df['City'] == city]
    # Calculate the estimated coefficient and intercept to draw the OLS line:
    acc_var = df_city[x_acc]
    aff_var = df_city[x_aff]
    acc_var = sm.add_constant(acc_var)
    aff_var = sm.add_constant(aff_var)
    y_var = df_city[y]
    model_acc = sm.OLS(y_var, acc_var).fit()
    model_aff = sm.OLS(y_var, aff_var).fit()
    params_acc = model_acc.params
    params_aff = model_aff.params
    intercept_acc, slope_acc = params_acc['const'], params_acc[x_acc]
    intercept_aff, slope_aff = params_aff['const'], params_aff[x_aff]
    predictions_acc = intercept_acc + slope_acc * df_city[x_acc]
    predictions_aff = intercept_aff + slope_aff * df_city[x_aff]
    return df_city[x_acc],df_city[x_aff],df_city[y],predictions_acc,predictions_aff
    
def visualize (x_acc,x_aff,y,city):
    acc, aff, y_var, predictions_acc,predictions_aff = uni_ols(x_acc,x_aff,y,city)
    fig, axs = plt.subplots(2, 1, figsize = (8,11))
    # Plot the first subplot for the selected acc indicator:
    axs[0].scatter(acc,y_var,color  = 'steelblue',s = 15, alpha = 0.8)
    axs[0].plot(acc, predictions_acc, color='black', linewidth = 2)
    # Plot the first subplot for the selected aff indicator:
    axs[1].scatter(aff,y_var,color  = 'steelblue',s = 15, alpha = 0.8)
    axs[1].plot(aff, predictions_aff, color='black', linewidth = 2)
    # Customize the subplots:
    axs[0].set_xlim([min(acc),max(acc)])
    axs[0].set_xlabel(x_acc)
    axs[0].set_ylim([min(y_var),max(y_var)])
    axs[0].set_ylabel('Low income Low Accessibility within ' + y)
    axs[0].set_title('Bivariate regression plots of ' 
                     + x_acc + ' and ' + y + ' in ' + city)
    
    axs[1].set_xlim([min(aff),max(aff)])
    axs[1].set_ylim([min(y_var),max(y_var)])
    axs[1].set_xlabel(x_aff)
    axs[1].set_ylabel('Low income Low Accessibility within ' + y)
    axs[1].set_title('Bivariate regression plots of ' 
                     + x_aff + ' and ' + y + ' in ' + city)
    name = y + '_by_' + x_acc + '_&_ +'+x_aff + '_in_' + city +'.png'
    plt.tight_layout()
    fig.savefig(os.path.join(base_path,'plot/'+ name))
    plt.show()
    return fig

# Genereate plots here only for significant results, but will show all the plots 
# in shiny:
visualize('hhd_exp','avg_vehicle','Half_mile','Chicago')
visualize('hhd_exp','avg_vehicle','Half_mile','Houston')
visualize('hhd_exp','transit_dist','Half_mile','Houston')
visualize('hhd_exp','pct_SNAP','Half_mile','New York')
visualize('hhd_exp','avg_vehicle','Half_mile','New York')

def plot_bar():
    df = df_final.groupby('City')['minc', 'hhd_exp', 'pct_SNAP','transit_dist', 'transit_freq', 'avg_vehicle'].mean().reset_index()
    fig, axes = plt.subplots(2, 3, figsize=(28,12))
    sns.barplot(x = 'City', y = 'minc' ,ax = axes[0,0], data = df)
    sns.barplot(x = 'City', y = 'hhd_exp' ,ax = axes[0,1], data = df)
    sns.barplot(x = 'City', y = 'pct_SNAP' ,ax = axes[0,2], data = df)
    sns.barplot(x = 'City', y = 'transit_dist' ,ax = axes[1,0], data = df)
    sns.barplot(x = 'City', y = 'transit_freq' ,ax = axes[1,1], data = df)
    sns.barplot(x = 'City', y = 'avg_vehicle' ,ax = axes[1,2], data = df)
    axes[0, 0].set_title('Summary of Income Indicator by Cities', fontsize= 20, x = 1.8,y=1.05)
    axes[1, 0].set_title('Summary of Acess Indicator by Cities', fontsize= 20 , x = 1.8,y=1.02)
    fig.savefig(os.path.join(base_path,'plot/'+ 'Summary Plot.png'))
    return fig
plot_bar()
