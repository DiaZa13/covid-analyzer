# Basado en: https://github.com/tdenzl/BuLiAn/blob/main/BuLiAn.py
import streamlit as st
import pandas as pd
import altair as alt
from data import data_wrangling, new_information
from statistics import get_last_report, total_cases, cases_evolution, compare_countries


@st.experimental_memo
def get_data():
    base_url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%'
    confirmed_data = pd.read_csv(
        '{}2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv'.format(
            base_url))
    deaths_data = pd.read_csv(
        '{}2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv'.format(base_url))
    recovered_data = pd.read_csv(
        '{}2Ftime_series_covid19_recovered_global.csv&filename=time_series_covid19_recovered_global.csv'.format(
            base_url))
    data = data_wrangling(confirmed_data, deaths_data, recovered_data)

    data = new_information(data)
    # separate the date into day, month and year
    data['day'] = data['date'].dt.day
    data['month'] = data['date'].dt.month_name()
    data['year'] = data['date'].dt.year
    return data


# Define the base time-series chart.
def get_line_chart(data, x_axis, y_axis, x_label, y_label, hue):
    hover = alt.selection_single(fields=[x_axis], nearest=True, on="mouseover", empty="none", )

    lines = (alt.Chart(data).mark_line(point=True)
             .encode(x=x_axis, y=y_axis, color=hue))

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (alt.Chart(data).mark_rule()
                .encode(x=x_axis, y=y_axis, opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                        tooltip=[
                            alt.Tooltip(x_axis, title=x_label),
                            alt.Tooltip(y_axis, title=y_label),
                        ],
                        )
                .add_selection(hover)
                )
    return (lines + points + tooltips).interactive()

def user_params(data: [str], select_label: str, multiselect: bool, radio_key: str, country_key: str,
                labels=['Día', 'Mes', 'Año']):
    ms, col1, me = st.columns((.1, 2, .5))
    if multiselect:
        selected_country = col1.multiselect(select_label, data, key=country_key)
    else:
        selected_country = col1.selectbox(select_label, data, key=country_key)

    # select the time stamp
    selected_time = col1.radio('Seleccione un formato de tiempo', labels, key=radio_key)
    return selected_country, selected_time


# page configuration
st.set_page_config(page_title='Casos De Covid-19', page_icon='random', layout='wide')


header = st.container()
dataset = st.container()
evolution = st.container()
compare = st.container()
difference = st.container()

with header:
    st.title('Analizador de la evolución de COVID-19')
    st.caption('Source code [Covid Evolution Analyzer](https://www.linkedin.com/in/tim-denzler/)')
    # description of the analyzer and COVID-19
    st.markdown(
        'Los últimos dos años han generado un gran impacto en la vida de los seres humanos, esto a causa del COVID-19 y todas y todas las acciones tomadas'
        'por los gobiernos para resguardar la vida de sus ciudadanos. El COVID-19 es una enfermedad infecciosa causada por el virus SARS-CoV-2. Una de las principales'
        'medidas de los gobiernos para evitar propagar el contagio del COVID-19 fue la cuarentena y el uso obligatorio de la mascarilla. Si bien, en la actualidad el número de contagios'
        'ha disminuido considerablemente aún no se puede descartar el virus como una amenaza. Es por ello que a continuación se detallan una serie de gráficas que '
        'permitirán evaluar la evolución de los casos confirmados, de las muertes y de los recuperados de COVID-19 alrededor del mundo.')

    st.image('https://medlineplus.gov/images/COVID19_share.jpg')
    st.caption('Fuente: MedilinePlus')

with dataset:
    st.header("Reportes diarios de COVID-19 ")
    # description
    st.markdown(
        'Los conjuntos de datos utilizados para el análisis son proveídos por [HumData.org](https://www.linkedin.com/in/tim-denzler/). Se utilizó el conjunto de'
        'casos confirmados, casos fallecidos y recuperados, esta información es actualizada diariamente, por lo que los datos a continuación presentados son datos en'
        'tiempo real. Cada uno de estos datos se proceso y validó la información para finalmente hacer una unión y obtener el dataset '
        'para análisis.')

    # read the dataset
    covid_data = get_data()
    # get the countries
    countries = covid_data.country.unique()
    last_report = get_last_report(covid_data)
    confirmed, deaths = total_cases(last_report)
    recovered = covid_data['new_recovered'].sum()

    '''
    ### Estadísticas generales
    '''
    spacer, row, spacer1, row1, spacer2, row2, spacer3, row3, spacer4 = st.columns(
        (.2, 1.6, .2, 1.6, .2, 1.6, .2, 1.6, .2))
    with row:
        # unique_games_in_df = df_data_filtered.game_id.nunique()
        # calculate the number of countries
        str_games = "🏟️ " + str(len(countries)) + " Países"
        st.markdown(str_games)
    with row1:
        # unique_teams_in_df = len(np.unique(df_data_filtered.team).tolist())
        # calculate the total number of confirmed cases
        str_teams = "🧾️" + str(confirmed) + " Confirmados"
        st.markdown(str_teams)
    with row2:
        # total_goals_in_df = df_data_filtered['goals'].sum()
        str_goals = "☠️" + str(deaths) + " Fallecidos"
        st.markdown(str_goals)
    with row3:
        # total_shots_in_df = df_data_filtered['shots_on_goal'].sum()
        # calculate the total number of recovered
        str_shots = "🕊️ " + str(recovered) + " Recuperados"
        st.markdown(str_shots)

    st.markdown("")
    see_data = st.expander('Haz click para observar los datos 👇')
    with see_data:
        st.dataframe(data=covid_data.reset_index(drop=True))
    st.text('')

    # actual infected cases graph
    '''
    ### Casos infectados reportados a la fecha
    Se muestra una gráfica que permite visualizar los casos infectados `(confirmados - (fallecidos + recuperados))` de cada uno de los países reportados hasta la fecha
    '''
    st.bar_chart(data=last_report, x='country', y=['infected_cases'])

with evolution:
    st.header("Evolución de los casos reportados ")
    # description
    st.markdown(
        'A continuación se puede analizar la evolución de los nuevos casos reportados, tanto diariamente, por mes o un resumen anual-mensual. Para el caso mensual y periódico se'
        'calculó el promedio de los casos reportados para cada uno de esos periodos')

    ev_country, ev_time = user_params(countries, 'Seleccione un país', False, 'ev_radio', 'ev_country')
    ev_confirmed, ev_deaths, ev_recovered = st.tabs(['🧾️ Confirmados', '☠️Fallecidos', '🕊️ Recuperados'])
    evolution = cases_evolution(covid_data, ev_country, ev_time)
    if ev_time == 'Día':
        time = 'date'
    elif ev_time == 'Mes':
        time = 'month'
    else:
        time = 'period'

    ev_confirmed.line_chart(data=evolution, x=time, y='new_cases')
    ev_deaths.line_chart(data=evolution, x=time, y='new_deaths')
    ev_recovered.line_chart(data=evolution, x=time, y='new_recovered')

with compare:
    st.header('Comparación de estadísticas entre países')
    # description
    st.markdown(
        "En las siguientes gráficas se podrá realizar una análisis más profundo al poder comparar la evolución de los caso reportados por país. Para esta comparación"
        " se utiliza la normalización de los casos reportados por millón de habitantes. Para poder observar alguna gráfica debe de primero seleccionar al menos"
        " un país.")
    comp_country, comp_time = user_params(countries, 'Seleccione los países que desea comparar', True, 'comp_radio',
                                          'comp_country')
    comp_confirmed, comp_deaths = st.tabs(['🧾️ Confirmados', '☠️Fallecidos'])

    evolution = compare_countries(covid_data, comp_country, comp_time)
    if comp_time == 'Día':
        time = 'date'
    elif comp_time == 'Mes':
        time = 'month'
    else:
        time = 'period'
    if len(comp_country) > 0:
        # confirmed cases
        chart_cases = get_line_chart(evolution, time, 'total_cases_per_million', comp_time, 'Cases_per_million',
                                     'country')
        comp_confirmed.altair_chart(chart_cases, use_container_width=True)
        # death cases
        chart_deaths = get_line_chart(evolution, time, 'total_deaths_per_million', comp_time, 'Deaths_per_million',
                                      'country')
        comp_deaths.altair_chart(chart_deaths, use_container_width=True)

with difference:
    st.header("Análisis de casos recuperados vs fallecidos ")
    # description
    st.markdown(
        "En este apartado se permite realizar un análisis más profundo en cuanto a los casos que resultaron en fallecimiento con respecto a aquellos"
        "que se reportaron como recuperados")
    diff_country, diff_time = user_params(countries, 'Seleccione un país', False, 'diff_radio', 'diff_country',
                                          labels=['Actual', 'Día', 'Mes', 'Año'])
    diff_deaths, diff_recovered = st.tabs(['☠️Fallecidos', '🕊️ Recuperados'])

    evolution = cases_evolution(covid_data, diff_country, diff_time)

    if diff_time == 'Actual':
        time = 'country'
    elif diff_time == 'Día':
        time = 'date'
    elif diff_time == 'Mes':
        time = 'month'
    else:
        time = 'period'

    diff_deaths.bar_chart(data=evolution, x=time, y=['total_deaths', 'total_recovered'])