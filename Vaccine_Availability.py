
# library imports
import numpy as np
import pandas as pd
import json
# from datetime import datetime
# from datetime import timedelta


# plotly dash streamlit imports
import plotly
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# import os
# os.chdir \
#     ('C:\\Users\\sangavi\\Desktop\\Courses\\SelfLearning\\Projects\\Covid Dashboard\\Vaccine_availability_deployment')


# cowin api
from cowin_api import CoWinAPI
cowin = CoWinAPI()

# loading the json from /data folder
with open('state_ids.json') as f:
    states_ids = json.load(f)

# create list of states
states = (states_ids.values())

# load state_district_codes
with open('state_district_codes.json')as f:
    state_district_codes = json.load(f)


# create a district and state-id mapping:
# district_to_state = {}
# for key in state_district_codes:
#     inner_dict = {}
#     for index in range(len(state_district_codes[key])):
# #         print('yes')
#         inner_dict[state_district_codes[key][index]['district_id']] = state_district_codes[key][index]['district_name']
#     district_to_state[key] = inner_dict
# district_to_state


# ### Dash


# columns for the data-table to be displayed
cols = ['center_id' ,'name' ,'available_capacity' ,'Vaccine' ,'address', 'pincode', 'from' ,'to']

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style = {'backgroundColor' :'#f0f0f0', 'height' :'1600px'}, children = [

    html.Div(html.H2('VACCINE AVAILABILITY'), style = dict(fontWeight = 'Bold', \
                                                           fontFamily = 'Helvetica' ,backgroundColor ='#dedcdc'
                                                         ,color = 'Black', \
                                                           textAlign = 'Center' ,height = '50px', padding = '2.3px')),

    html.Div(html.H5('Choose your State') ,style =dict(fontFamily = 'Helvetica', \
                                                      backgroundColor ='#f0f0f0' ,color = 'Black', textAlign = 'left')),
    html.Div(
        dcc.Dropdown(
            id = 'states',
            options = [{'label': item_2, 'value': item_1} for item_1, item_2 in states_ids.items()],
            style = {'backgroundColor' :'#d4d1cb'}
            # 'color':'#1b1a26'
        ) ,style = {'background-color' :'rgb(50,50,50)' ,'margin-top' :'-20px'}),
    html.Div(html.H5('Choose your District') ,style =dict(fontFamily = 'Helvetica', \
                                                         backgroundColor ='#f0f0f0' ,color = 'Black', textAlign = 'left')),
    html.Div(
        dcc.Dropdown(
            id = 'districts',
            style = {'backgroundColor' :'#d4d1cb' ,  }  # '#1b1a26'

        ) ,style = {'background-color' :'rgb(50,50,50)', 'margin-top' :'-20px'}),

    html.Div(
        dash_table.DataTable(
            id = 'info-table',
            columns=[{'name' :item, 'id': item, "deletable" :False ,'selectable' :False} for  item in cols],
            style_cell_conditional = [{
                'textAlign' :'left',
                'backgroundColor' :'rgb(50,50,50)'
            }
            ],
            style_cell = {
                'backgroundColor' :'rgb(50,50,50)',
                'color' :'white',
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_table = {'margin-left' :'40px' ,'height': '600px', 'overflowY': 'auto'},

            style_header = {
                'backgroundColor' :'#000000',
                'fontWeight': 'bold'
            },
            fill_width = True
        ) ,style = {'margin-right' :'300px', 'margin-left' :'200px'}
    ),
    #             html.Div(id='vaccine-shot-count', style={'whiteSpace': 'pre-line'})
])

@app.callback(Output('districts', 'options'),
              [Input('states' ,'value')],
              )
def update_districts_dropdown(value):
    # extract the districts for the selected state
    dropdown_values = state_district_codes[str(value)]
    # make the lis of dicts a single dict
    result = {}
    for item in dropdown_values:
        result[item['district_id']] = item['district_name']
    # generate options for the dropdown
    options = [{'label' :item2, 'value' :item1} for item1 ,item2 in result.items()]

    return options


@app.callback(
    Output('info-table', 'data'),
    [Input('districts', 'value')])
def callback_a(value):
    district_id = str(value)
    query_dict = cowin.get_availability_by_district(district_id = district_id)
    # convert it into a df
    data = pd.DataFrame(query_dict['centers'])
    # calculate availability
    avail = []
    vaccine = []
    for index in range(data.shape[0]):
        if len(data['sessions'][index]) != 2:
            avail.append \
                (str(data['sessions'][index][0]['available_capacity'] ) +' on ' +'  ' +data['sessions'][index][0]
                    ['date'])
            vaccine.append(data['sessions'][index][0]['vaccine' ] +'- ' +data['sessions'][index][0]['date'])
        else:
            avail.append \
                (str(data['sessions'][index][0]['available_capacity'] ) +' on ' +'  ' +data['sessions'][index][1]
                    ['date'])
            vaccine.append(data['sessions'][index][1]['vaccine' ] +'- ' +data['sessions'][index][1]['date'])

    data['available_capacity'] = avail
    data['Vaccine'] = vaccine

    #     data['Vaccine'] = [data['sessions'][index][1]['vaccine'] for index in range(len(data['sessions']))]
    data = data[['center_id' ,'name' ,'available_capacity' ,'Vaccine' ,'address', 'pincode', 'from' ,'to']]
    print(data.head())
    return data.to_dict(orient='records')

if __name__ == '__main__':
    app.run_server(debug = True)






