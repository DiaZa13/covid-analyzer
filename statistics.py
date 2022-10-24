from datetime import date, timedelta
import streamlit as st


def get_last_report(data):
    # Based on: https://www.geeksforgeeks.org/get-yesterdays-date-using-python/
    yesterday = date.today() - timedelta(days=1)
    # get last report
    return data.loc[data['date'].dt.date == yesterday]


def total_cases(data):
    confirmed = data['total_cases'].sum()
    deaths = data['total_deaths'].sum()
    return confirmed, deaths


def cases_evolution(data, country, time):
    evolution = data.loc[data.country == country]
    if time == 'Actual':
        dataset = get_last_report(evolution)
        dataset['total_recovered'] = dataset['total_recovered'].replace(0, evolution['new_recovered'].sum())
    elif time == 'Día':
        # get the mean of the cases by day
        dataset = evolution
    elif time == 'Mes':
        # get the mean of the cases by day
        dataset = evolution.groupby(by=['month'], as_index=False).mean()
    else:
        # get the mean of the cases by day
        dataset = evolution.groupby(by=['month', 'year'], as_index=False).mean()
        dataset['period'] = dataset['month'] + dataset['year'].astype(str)

    return dataset


def compare_countries(data, country, time):
    compare = data.loc[data['country'].isin(country)]
    # separate by day, month or year
    if time == 'Día':
        # get the mean of the cases by day
        dataset = compare.groupby(by=['day', 'country'], as_index=False).mean()
    elif time == 'Mes':
        # get the mean of the cases by day
        dataset = compare.groupby(by=['month', 'country'], as_index=False).mean()
    else:
        # get the mean of the cases by day
        dataset = compare.groupby(by=['month', 'year', 'country'], as_index=False).mean()
        dataset['period'] = dataset['month'] + dataset['year'].astype(str)

    return dataset
