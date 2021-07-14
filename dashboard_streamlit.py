# %%

import json
import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots
from datetime import date, datetime

# %%

#GET DATA
url1 = 'https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_state.csv'
url2 = 'https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_malaysia.csv'
url3 = 'https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/static/population.csv'
url4 = 'https://query.data.world/s/64itw4xd4l43sq7n6fwgagvsqcojjd'
url5 = 'https://query.data.world/s/4gtzoe6nkuueyikifwpsiko5rbqzxl'

res1 = requests.get(url1, allow_redirects=True)
with open('vax_state.csv','wb') as file:
    file.write(res1.content)
vax_state_df = pd.read_csv('vax_state.csv')

res2 = requests.get(url2, allow_redirects=True)
with open('vax_malaysia.csv','wb') as file:
    file.write(res2.content)
vax_malaysia_df = pd.read_csv('vax_malaysia.csv')

res3 = requests.get(url3, allow_redirects=True)
with open('population.csv', 'wb') as file:
    file.write(res3.content)
population = pd.read_csv('population.csv')

res4 = requests.get(url4, allow_redirects=True)
with open('covid-19_my_state.csv', 'wb') as file:
    file.write(res4.content)
cases_state_df = pd.read_csv('covid-19_my_state.csv')

res5 = requests.get(url5, allow_redirects=True)
with open('covid-19_my.csv', 'wb') as file:
    file.write(res5.content)
cases_malaysia_df = pd.read_csv('covid-19_my.csv')

# %%

#DATA OPERATIONS

#Convert date format
vax_malaysia_df['date'] = pd.to_datetime(vax_malaysia_df['date'])
vax_state_df['date'] = pd.to_datetime(vax_state_df['date'])
cases_malaysia_df['date'] = pd.to_datetime(cases_malaysia_df['date'])
cases_state_df['date'] = pd.to_datetime(cases_state_df['date'])

population_states = pd.DataFrame(population).drop(['idxs', 'pop_18', 'pop_60'], axis=1)[1:]
population_malaysia = pd.DataFrame(population).drop(['idxs', 'pop_18', 'pop_60'], axis=1)[:1]

# %%

#Format state and columns  in cases_state_df
rename_dict = {
    'JOHOR': "Johor", 
    'KEDAH': "Kedah", 
    'KELANTAN': "Kelantan", 
    'MELAKA': "Melaka", 
    'NEGERI SEMBILAN': "Negeri Sembilan",
    'PAHANG': "Pahang", 
    'PULAU PINANG': "Pulau Pinang", 
    'PERAK': "Perak",
    'PERLIS': "Perlis",
    'SELANGOR': "Selangor",
    'TERENGGANU': "Terengganu",
    'SABAH': "Sabah",
    'SARAWAK': "Sarawak",
    'WP KUALA LUMPUR': "W.P. Kuala Lumpur",
    'WP LABUAN': "W.P. Labuan",
    'WP PUTRAJAYA': "W.P. Putrajaya"
}

cases_state_df['state'] = cases_state_df['state'].replace(rename_dict)

# %%
#Merge population into DataFrame
vax_state_df = pd.merge(population_states, vax_state_df, on="state")
cases_state_df = pd.merge(population_states, cases_state_df, on="state")

#Calculate percentage using population
vax_state_df['percentage_fully_vaccinated'] = vax_state_df["dose2_cumul"] / vax_state_df['pop'] * 100
vax_malaysia_df['percentage_fully_vaccinated'] = vax_malaysia_df["dose2_cumul"] / sum(vax_state_df['pop'].unique()) * 100

# %%

#Key analytics
total_first_dose_malaysia = vax_malaysia_df['dose1_daily'].sum()
total_second_dose_malaysia = vax_malaysia_df['dose2_daily'].sum()
pct_fully_vax_malaysia = total_second_dose_malaysia / population_malaysia['pop'].sum()*100
daily_new_cases = cases_malaysia_df['new_cases'].iloc[-1]
daily_deaths = cases_malaysia_df['new_deaths'].iloc[-1]
cumul_deaths = cases_malaysia_df['total_deaths'].iloc[-1]
# %%
#Group by state

daily_vax1 = vax_malaysia_df['dose1_daily'].iloc[-1]
daily_vax2 = vax_malaysia_df['dose2_daily'].iloc[-1]
daily_vaxsum = daily_vax1 + daily_vax2





# %%

# FRONT END

st.set_page_config(layout="wide", page_title="Malaysia Vaccination Dashboard", initial_sidebar_state="expanded")
st.title("MALAYSIA VACCINATION DASHBOARD")
st.text("Data queried at {} from: \n1. github.com/CITF-Malaysia/citf-public \n2. data.world/wnarifin/covid-19-my".format(datetime.now().strftime("%H:%M:%S %d-%m-%Y")))
st.write('--------')
c1, c2, c3 = st.beta_columns((1, 1, 1))
st.write('--------')
d1, d2 = st.beta_columns((1, 1))
# st.write('--------')
e1, e2 = st.beta_columns((10, 1))
st.write('--------')
f1, f2 = st.beta_columns((10, 1))
st.write('--------')


country_list = ["Malaysia",
                "Johor", 
                "Kedah", 
                "Kelantan", 
                "Melaka", 
                "Negeri Sembilan",
                "Pahang", 
                "Pulau Pinang", 
                "Perak",
                "Perlis",
                "Selangor",
                "Terengganu",
                "Sabah",
                "Sarawak",
                "W.P. Kuala Lumpur",
                "W.P. Labuan",
                "W.P. Putrajaya"]


# %%
#GEOJSON

geojson_malaysia = json.load(open('Malaysia.geojson'))

choro_vax_state_df = vax_state_df.groupby('state').tail(1)

# choro_vax_state_df = choro_vax_state_df.rename(columns={'state': 'name'})

state_id_map = {}
for feature in geojson_malaysia['features']:
    feature['id'] = feature['properties']['id']
    state_id_map[feature['properties']['name']] = feature['id']
    
# state_id_map['putrajaya'] = state_id_map['putajaya']
# del state_id_map['putajaya']

choro_vax_state_df['id'] = choro_vax_state_df['state'].apply(lambda x: state_id_map[x])


# %%


# %%

#Merge dataframes

malaysia_df = pd.merge(cases_malaysia_df.drop(['location', 'recover', 'total_recover', 'icu', 'support'], axis=1), vax_malaysia_df, on="date")
states_df = pd.merge(cases_state_df, vax_state_df, on=("state", "date"))

#%%
#Clean up states_df columns
states_df = states_df.rename(columns={'pop_x': 'pop'}).drop(['pop_y'], axis=1)
# %%



select = st.sidebar.selectbox('Select to view key analytics by state:', country_list, key='1')
if select == 'Malaysia':
    filtered_df = malaysia_df
else:
    filtered_df = states_df[states_df['state']==select].drop(['state', 'pop'], axis=1)


#State new cases   
with c1:   
    # filtered_df_percentage = filtered_df["dose2_cumul"] / filtered_df['pop'] * 100
    # st.subheader('{} new cases today in {}, totalling up to {} COVID-19 cases to date.'.format(filtered_df['new_cases'].iloc[-1], select, filtered_df['total_cases'].iloc[-1]))
    st.title('{:.0f}'.format(filtered_df['new_cases'].iloc[-1]))
    st.subheader('New Cases in {} Today'.format(select))
    st.write('--------')
    st.title('{:.0f}'.format(filtered_df['total_cases'].iloc[-1]))
    st.subheader('Total Cases in {} to Date'.format(select))

    
#New vaccinations today    
with c2:
    # st.title("%s doses administered today nationally" %daily_vaxsum)
    # st.subheader('{} lives lost in {} today, totalling up to {} deaths due to COVID-19.'.format(filtered_df['new_deaths'].iloc[-1], select, filtered_df['total_deaths'].iloc[-1]))
    st.title(filtered_df['new_deaths'].iloc[-1])
    st.subheader('Deaths in {} Today'.format(select))
    st.write('--------')
    st.title(filtered_df['total_deaths'].iloc[-1])
    st.subheader('Total COVID-19 Deaths in {}'.format(select))
    
with c3:
    # st.title("%.2f%%  fully vaccinated nationally" %pct_fully_vax_malaysia)
    # st.subheader('{} new vaccinations in {} today, totalling up to {} vaccinations administered.'.format(filtered_df['total_daily'].iloc[-1], select, filtered_df['total_cumul'].iloc[-1]))
    st.title(filtered_df['total_daily'].iloc[-1])
    st.subheader('Vaccines Administered in {} Today'.format(select))
    st.write('--------')
    st.title('{:.2f}%'.format(filtered_df['percentage_fully_vaccinated'].iloc[-1]))
    st.subheader('Fully Vaccinated in {}'.format(select))
    
with d1:
    chart_cases_state = px.line(filtered_df,
                        x="date",
                        y="total_cases")
    chart_cases_state.update_traces(marker_color='rgb(181, 52, 113)',
                                    marker_line_color='rgb(181, 52, 113)',
                                    marker_line_width=2.5, opacity=1)
    # chart_cases_state.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
    st.header("COVID-19 cases in {}".format(select))
    st.write(chart_cases_state)

with d2:
    chart_new_cases_state = px.bar(filtered_df,
                                    x='date',
                                    y='new_cases')
    chart_new_cases_state.update_traces(marker_color='rgb(181, 52, 113)',
                                        marker_line_color='rgb(181, 52, 113)',
                                        marker_line_width=0, opacity=1)
    # chart_cases_state.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
    st.header("Daily new cases in {}".format(select))
    st.write(chart_new_cases_state)

with e1:
    #Vaccination of all states chart
    chart_vax_state = px.line(vax_state_df,
              x="date",
              y="percentage_fully_vaccinated",
              color='state')
    chart_vax_state.update_layout(width=1300, height=500, margin={"r":0,"t":0,"l":0,"b":0})
    chart_vax_state.update_yaxes(range=[0, 100])
    st.header("Daily new vaccination by state")
    st.text('Click on legend to view by state')
    st.write(chart_vax_state)


with f1:
    choro = px.choropleth(choro_vax_state_df, 
                      locations='id', 
                      geojson=geojson_malaysia, 
                      color='percentage_fully_vaccinated',
                      hover_name='state',
                      labels='Percentage Fully Vaccinated',
                      color_continuous_scale="RdPu_r",
                      template='plotly_dark',
                      range_color=(0,100))
    choro.update_geos(fitbounds='locations', visible=False)
    choro.update_layout(width=1300, height=500, margin={"r":0,"t":0,"l":0,"b":0})
    st.header("Nationwide vaccination map")
    st.text("Hover to view percentage")
    st.write(choro)

with f2:
    st.text(" ")



# %%
