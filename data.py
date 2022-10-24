# lybraries
import pandas as pd
import numpy as np

# population by country
locations = pd.read_csv('population.csv')
locations = locations.loc[locations['Year'] == 2021]
locations = locations.drop(columns=['Code', 'Year'])
locations = locations.rename(columns={'Entity': 'country', 'Population (historical estimates)': 'population'})
locations['population_millions'] = locations['population'].apply(lambda x: x / 1_000_000)


def normalized(cases, country):
    population = locations.loc[locations['country'] == country, 'population_millions']
    if len(population) > 0:
        return round(cases / population.iloc[0], 3)
    else:
        return np.nan


def data_wrangling(confirmed, deaths, recovered):
    # delete unnecessary columns
    confirmed.drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)
    deaths.drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)
    recovered.drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    # rename certain columns
    confirmed.rename(columns={'Country/Region': 'Country'}, inplace=True)
    deaths.rename(columns={'Country/Region': 'Country'}, inplace=True)
    recovered.rename(columns={'Country/Region': 'Country'}, inplace=True)

    # convert the data into a tidy format
    confirmed = confirmed.melt(['Country'], var_name='Date', value_name='Confirmed_cases')
    deaths = deaths.melt(['Country'], var_name='Date', value_name='Death_cases')
    recovered = recovered.melt(['Country'], var_name='Date', value_name='Recovered_cases')

    # group the cases by date and country without taking into account the state
    confirmed = confirmed.groupby(['Country', 'Date'], as_index=False).sum()
    deaths = deaths.groupby(['Country', 'Date'], as_index=False).sum()
    recovered = recovered.groupby(['Country', 'Date'], as_index=False).sum()

    # Convert the date into datetime format
    confirmed['Date'] = pd.to_datetime(confirmed['Date'])
    deaths['Date'] = pd.to_datetime(deaths['Date'])
    recovered['Date'] = pd.to_datetime(recovered['Date'])

    # merge the datasets to get a final set
    dataset = pd.merge(pd.merge(confirmed, deaths, on=['Country', 'Date']), recovered, on=['Country', 'Date'])

    dataset = dataset.rename(
        columns={'Country': 'country', 'Date': 'date', 'Confirmed_cases': 'total_cases', 'Death_cases': 'total_deaths',
                 'Recovered_cases': 'total_recovered'})

    # cleaning memory
    del confirmed, deaths, recovered

    return dataset


def new_information(data):
    # sorting the data to calculate the new cases by day
    data = data.sort_values(by=['country', 'date'])

    # frequency of new cases by day
    data['new_cases'] = data.groupby(by='country')['total_cases'].diff()
    data['new_deaths'] = data.groupby(by='country')['total_deaths'].diff()
    data['new_recovered'] = data.groupby(by='country')['total_recovered'].diff()

    # cumulative frequency of infected cases
    # confirmed - (deaths + recovered)
    data = data.assign(infected_cases=lambda x: (x['total_cases'] - (x['total_deaths'] + x['total_recovered'])))

    # replace some new values
    data.fillna(0)
    data['new_deaths'] = data['new_deaths'].apply(lambda x: x if x >= 0 else np.nan)
    data['new_recovered'] = data['new_recovered'].apply(lambda x: x if x >= 0 else np.nan)

    data['total_cases_per_million'] = data[['total_cases', 'country']].apply(lambda x: normalized(*x), axis=1)
    data['total_deaths_per_million'] = data[['total_deaths', 'country']].apply(lambda x: normalized(*x), axis=1)
    data['total_recovered_per_million'] = data[['total_recovered', 'country']].apply(lambda x: normalized(*x), axis=1)

    # save the new data into a csv file
    # data.to_csv('covid.csv', encoding='utf-8', index=False)
    return data
