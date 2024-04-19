import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np

from .style_functions import style_figure

def get_callbacks_hydrometeors(app):

    @app.callback(Output(component_id='intermediate-ds-hydrometeors', component_property='data'),
                Input(component_id='datepicker', component_property='date'),
                Input(component_id='path', component_property='value'),
                Input(component_id='height_slider', component_property='value'))
    def get_hydrometeors_data(seldate, path, level_range):
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')

        ds = xr.open_dataset(
            path+'/METEOGRAM_patch001_' + seldate + '_koeln.nc')
        # only get up to around 12 km height and every 6th time step to reduce data size for speedup
        ds_sub = ds[['QV', 'QC', 'QI', 'QR', 'QS', 'QG', 'QH']].isel(
                        height_2=slice(level_range[0],level_range[1]), 
                        time=slice(0, len(ds.time), 6))
        df = ds_sub.to_dataframe()
        df = df.reset_index()
        
        # add total hydrometeor amount to the data frame
        df['total hydrometeors'] = df['QC'] + df['QI'] + df['QR'] + df['QS'] + df['QG'] + df['QH']

        # convert data so that plotting is easier and possible also with log values
        for varname in ['QC', 'QI', 'QR', 'QS', 'QG', 'QH', 'total hydrometeors']:
            df.loc[df[varname] < 1e-8, varname] = -9
            df.loc[df[varname] >= 1e-8, varname] = np.log10(df.loc[df[varname] >= 1e-8, varname].values)
        # the data set must be converted to json so that it is stored as binary to be used in other functions
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output(component_id='hydrometeors_plot', component_property='figure'),
                Input('dropdown_hydrometeors', 'value'),
                Input('intermediate-ds-hydrometeors', 'data'))
    def hydrometeors_graph_update(dropdown_value, df_json):
        df = pd.read_json(df_json, orient='split')    
        
        fig = go.Figure(data=
                go.Contour(z=df['{}'.format(dropdown_value)], x=df['time'], y=df['height_2'],
                    colorscale='jet'))
        
        if dropdown_value != 'QV':  # Add a colon after the condition
            fig.update_traces(contours=dict(start=-8, end=-2, size=1)
                     )
        #fig.update_layout(coloraxis_colorbar=dict(
         #           tickvals=[-8, -6, -4, -2, 1],
          #          ticktext=['10-8', '10-6' '10-4', '10-2', '10^0'],
         #       ))
        # apply styling to the figure
        fig = style_figure(fig)

        if dropdown_value == 'QC':
            fig.update_layout(title='',
                            xaxis_title='Time',
                            yaxis_title=''
                            )
        return fig

