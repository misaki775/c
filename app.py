import os 
import pandas as pd
import geopandas as gpd
from shiny import ui, render, reactive, App
from shinywidgets import output_widget, render_widget
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from Datawrangling import df_final_shp

income_vars = ['minc','hhd_exp','pct_SNAP']
access_vars = ['transit_freq', 'transit_dist','avg_vehicle']
control_vars = ['shr_Black','shr_Hispanic','shr_White','shr_Kids','shr_Seniors',]

base_path = r'/Users/misaki/Documents/GitHub/final-project-workalcoholic'
app_data = df_final_shp

logo_url = "img_lookup.png"
app_ui = ui.page_fluid(
    
    ui.navset_tab(
        ui.nav('Maps', 
               ui.row(
                   ui.column(6,ui.h1('Food Desert Mapping')),
                   ui.column(6,
                             ui.input_radio_buttons('distance', 'Select Distance', 
                                                    choices = {'One_mile':'One mile','Half_mile':'Half mile'}))),
               ui.row(
                   ui.column(6,
                             ui.input_select('var', 'Select Indicator', choices = income_vars + access_vars)),
                   ui.column(6,
                             ui.input_select('city', 'Select City', choices = ['Chicago', 'Los Angeles','New York','Houston']))),
               ui.row(
                   ui.column(6, ui.output_plot('comparison_map')),
                   ui.column(6, ui.output_plot('base_map'))),
               ui.row(
                   ui.output_text(
                       'explaination'))),
        ui.nav('Variable & Model Lookup',
               ui.img(src = logo_url,
                               height = 600,
                               width = 1000)
                       ),
        
        ui.nav('Visualization',
               ui.row(
                   ui.column(12,
                             ui.input_select(
                                 'city2','Select City', 
                                 choices = ['Chicago', 'Los Angeles','New York','Houston']))),
               ui.row(
                   ui.column(12,ui.output_plot('hist_1'))),
               ui.row(
                   ui.column(12, ui.output_plot(
                        'hist_2')))
              ),
        ui.nav('Dataset', ui.output_table('app_table'))
        )
    )
    
    
   
       
  
      
   


def server(input, output, session):
    @reactive.Calc
    def get_app_data():
        return app_data[app_data['City'] == input.city()]
    def get_hist_data():
        return app_data[app_data['City'] == input.city2()]
    def set_range_var():
        vmin = app_data[input.var()].min()
        vmax = app_data[input.var()].max()
        norm = Normalize(vmin=vmin, vmax=vmax)
        return vmin, vmax, norm
    def set_range_base():
        vmin = app_data[input.distance()].min()
        vmax = app_data[input.distance()].max()
        norm = Normalize(vmin=vmin, vmax=vmax)
        return vmin, vmax, norm
    def reg():
        app_data = get_app_data()
        X = app_data[income_vars + access_vars + control_vars]
        y = app_data[input.dependent()]
        model = sm.OLS(y, X).fit()
        return model
        
    @output
    @render.plot
    def base_map():
        app_data = get_app_data()
        vmin_inc, vmax_inc, norm_inc = set_range_base()
        ax = app_data.plot(column = input.distance(), legend = True, cmap = 'viridis',
                   vmin = vmin_inc, vmax = vmax_inc, norm = norm_inc)
        ax.set_title(f'Food Desert Population in {input.city()}')
        return ax
    @render.plot
    def comparison_map():
        app_data = get_app_data()
        vmin_acs, vmax_acs, norm_acs = set_range_var()
        ax = app_data.plot(column = input.var(), legend = True, cmap = 'viridis',
                   vmin = vmin_acs, vmax = vmax_acs, norm = norm_acs)
        ax.set_title(f'{input.var()} in {input.city()}')
        return ax
    @render.plot
    def hist_1():
        hist_data = get_hist_data()
        ax = sns.histplot(hist_data['One_mile'], kde=False, color='#5E89BE', bins=10)
        ax.set_title(f'Distribution of Food Desert Population in {input.city2()} within one mile')
        return ax
    @render.plot
    def hist_2():
        hist_data = get_hist_data()
        ax = sns.histplot(hist_data['Half_mile'], kde=False, color='#99B7DC', bins=10)
        ax.set_title(f'Distribution of Food Desert Population in {input.city2()} within half a mile')
        return ax
    @render.text
    def explaination():
        return 'Income and expenditured are measured in dollars. Distance is measured in meters.'
    def select_reminder():
        return f'{input.regressors()} in {input.city()} selected'
    
    @render.table()
    def reg_result():
        model = reg()
        return model.summary()
    @render.table
    def app_table():
        return get_app_data()
    


img_dir = Path(__file__).parent / '/Users/cean/Documents/GitHub/final-project-workalcoholic/'
    
app = App(app_ui, server,static_assets = img_dir)