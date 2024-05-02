import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np

from .style_functions import style_figure, style_error
from utils.error_utils import var_exists

def get_callbacks_hydrometeors(app, config):

    @app.callback(Output(component_id='intermediate-ds-hydrometeors', component_property='data'),
                Input(component_id='datepicker', component_property='date'),
                Input(component_id='path', component_property='value'),
                Input(component_id='height_slider', component_property='value'))
    def get_hydrometeors_data(seldate, path, level_range):
        """ Get hydrometeor data for the selected date and height range
        
        :param seldate: selected date
        :param path: path to the data
        :param level_range: selected height range
        :return: json data set with hydrometeors
        """
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')

        ds = xr.open_dataset(
            path+'/'+ config['paths']['prefix_meteogram'] + seldate + config['paths']['postfix_meteogram']+'.nc')
        # only get up to around 12 km height and every 6th time step to reduce data size for speedup
        var_list_mass = ['QV', 'QC', 'QI', 'QR', 'QS', 'QG', 'QH']
        var_list_number = ['QNC', 'QNI', 'QNR', 'QNS', 'QNG', 'QNH'] 
        var_list = var_list_mass + var_list_number

        var_list = var_exists(var_list, ds)

        ds_sub = ds[var_list].isel(
                        height_2=slice(level_range[0],level_range[1]), 
                        time=slice(0, len(ds.time), 6))
        df = ds_sub.to_dataframe()
        df = df.reset_index()
        
        # add total hydrometeor amount to the data frame
        df['total hydrometeors'] = 0
        for var in var_list_mass:
            df['total hydrometeors'] += df[var]
        # TODO: add total hydrometeor number conc. to the var_list

        var_list_mass = var_list_mass + ['total hydrometeors']
        # convert data so that plotting is easier and possible also with log values
        for varname in var_list_mass:
            df.loc[df[varname] < 1e-8, varname] = -9
            df.loc[df[varname] >= 1e-8, varname] = np.log10(df.loc[df[varname] >= 1e-8, varname].values)
        # the data set must be converted to json so that it is stored as binary to be used in other functions
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output(component_id='hydrometeors_plot', component_property='figure'),
                Input('dropdown_hydrometeors', 'value'),
                Input('intermediate-ds-hydrometeors', 'data'))
    def hydrometeors_graph_update(dropdown_value, df_json):
        df = pd.read_json(df_json, orient='split')    
        
        # check if the variable is in the dataframe, if not use default error plot
        if dropdown_value not in df.columns:
            fig = go.Figure()
            fig = style_error(fig)
            return fig

        fig = go.Figure(data=
                go.Contour(z=df['{}'.format(dropdown_value)], x=df['time'], y=df['height_2'],
                    colorscale='jet', coloraxis='coloraxis'))
        
        if (dropdown_value != 'QV') & (dropdown_value[1] != 'N'):  # Add a colon after the condition
            fig.update_traces(contours=dict(start=-8, end=-2, size=1)
                     )
        # apply styling to the figure
        fig = style_figure(fig)
        fig.update_layout(title='',
                            xaxis_title='Time [UTC]',
                            yaxis_title='Height [m]'
                            )
        
        if (dropdown_value != 'QV') & (dropdown_value[1] != 'N'):
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title='log10 [kg/kg]',
                    ),
                )
        elif (dropdown_value == 'QV') :
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title='[kg/kg]',
                    ),
                )
            
        return fig

