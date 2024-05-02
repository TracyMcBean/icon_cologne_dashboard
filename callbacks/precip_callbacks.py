from dash.dependencies import Input, Output
#from app import app  # import the dash app object

from datetime import datetime
import xarray as xr
import pandas as pd
import plotly.express as px
import numpy as np

from .style_functions import style_figure

def get_callbacks_precip(app, config):
    @app.callback(Output(component_id='intermediate-ds-precip', component_property='data'),
              Input(component_id='datepicker', component_property='date'),
              Input(component_id='path', component_property='value'))
    def get_precip_data(seldate, path):
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')

        ds = xr.open_dataset(
            path+'/'+ config['paths']['prefix_meteogram'] + seldate + config['paths']['postfix_meteogram']+'.nc')

        # Get precipitation as snow, rain and total precip
        # TODO: Here the error handling is missing, if the variables are not in the dataset
        ds_sub = ds[['RAIN_GSP', 'RAIN_CON', 'SNOW_GSP', 'SNOW_CON']]
        ds_sub['SNOW'] = ds_sub.SNOW_GSP + ds_sub.SNOW_CON
        ds_sub['RAIN'] = ds_sub.RAIN_GSP + ds_sub.RAIN_CON
        ds_sub['PRECIP'] = ds_sub['SNOW'] + ds_sub['RAIN']

        # Reformat the data so that plotly can plot it directly
        ds_flat = ds_sub[['PRECIP', 'RAIN', 'SNOW']].to_array().values.flatten()
        names_list = np.asarray([['PRECIP'] * len(ds_sub['PRECIP'].values), ['RAIN'] * len(ds_sub['RAIN'].values),
                                ['SNOW'] * len(ds_sub['SNOW'].values)]).reshape(len(ds_flat))
        time_vals = np.asarray([ds_sub.time.values, ds_sub.time.values, ds_sub.time.values]).reshape(len(ds_flat))
        df = pd.DataFrame({'time': time_vals, 'name': names_list, 'values': ds_flat})

        # The data set must be converted to json so that it is stored as binary to be used in other functions
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output(component_id='precip_plot', component_property='figure'),
              Input('intermediate-ds-precip', 'data'))
    def precip_graph_update(df_json):
        df = pd.read_json(df_json, orient='split')
        fig = px.line(df, x='time', y='values', color='name')
        fig.update_layout(title={
            'text': 'Select the precipitation type by clicking on the legend',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Time',
        yaxis_title='kg m-2',
        legend_title='Precip Type'
        )
        # apply styling to the figure
        fig = style_figure(fig)

        return fig
