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
                labels=['D??a', 'Mes', 'A??o']):
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
    st.title('Analizador de la evoluci??n de COVID-19')
    st.caption('Source code [Covid Evolution Analyzer](https://github.com/DiaZa13/covid-analyzer)')
    # description of the analyzer and COVID-19
    st.markdown(
        'Los ??ltimos dos a??os han generado un gran impacto en la vida de los seres humanos, esto a causa del COVID-19 y todas y todas las acciones tomadas'
        'por los gobiernos para resguardar la vida de sus ciudadanos. El COVID-19 es una enfermedad infecciosa causada por el virus SARS-CoV-2. Una de las principales'
        'medidas de los gobiernos para evitar propagar el contagio del COVID-19 fue la cuarentena y el uso obligatorio de la mascarilla. Si bien, en la actualidad el n??mero de contagios'
        'ha disminuido considerablemente a??n no se puede descartar el virus como una amenaza. Es por ello que a continuaci??n se detallan una serie de gr??ficas que '
        'permitir??n evaluar la evoluci??n de los casos confirmados, de las muertes y de los recuperados de COVID-19 alrededor del mundo.')

    st.image('https://medlineplus.gov/images/COVID19_share.jpg')
    st.caption('Fuente: MedilinePlus')

with dataset:
    st.header("Reportes diarios de COVID-19 ")
    # description
    st.markdown(
        'Los conjuntos de datos utilizados para el an??lisis son prove??dos por [HumData.org](https://www.linkedin.com/in/tim-denzler/). Se utiliz?? el conjunto de'
        'casos confirmados, casos fallecidos y recuperados, esta informaci??n es actualizada diariamente, por lo que los datos a continuaci??n presentados son datos en'
        'tiempo real. Cada uno de estos datos se proceso y valid?? la informaci??n para finalmente hacer una uni??n y obtener el dataset '
        'para an??lisis.')

    # read the dataset
    covid_data = get_data()
    # get the countries
    countries = covid_data.country.unique()
    last_report = get_last_report(covid_data)
    confirmed, deaths = total_cases(last_report)
    recovered = covid_data['new_recovered'].sum()

    '''
    ### Estad??sticas generales
    '''
    spacer, row, spacer1, row1, spacer2, row2, spacer3, row3, spacer4 = st.columns(
        (.2, 1.6, .2, 1.6, .2, 1.6, .2, 1.6, .2))
    with row:
        # unique_games_in_df = df_data_filtered.game_id.nunique()
        # calculate the number of countries
        str_games = "??????? " + str(len(countries)) + " Pa??ses"
        st.markdown(str_games)
    with row1:
        # unique_teams_in_df = len(np.unique(df_data_filtered.team).tolist())
        # calculate the total number of confirmed cases
        str_teams = "???????" + str(confirmed) + " Confirmados"
        st.markdown(str_teams)
    with row2:
        # total_goals_in_df = df_data_filtered['goals'].sum()
        str_goals = "??????" + str(deaths) + " Fallecidos"
        st.markdown(str_goals)
    with row3:
        # total_shots_in_df = df_data_filtered['shots_on_goal'].sum()
        # calculate the total number of recovered
        str_shots = "??????? " + str(recovered) + " Recuperados"
        st.markdown(str_shots)

    st.markdown("")
    see_data = st.expander('Haz click para observar los datos ????')
    with see_data:
        st.dataframe(data=covid_data.reset_index(drop=True))
    st.text('')

    # actual infected cases graph
    '''
    ### Casos infectados reportados a la fecha
    Se muestra una gr??fica que permite visualizar los casos infectados `(confirmados - (fallecidos + recuperados))` de cada uno de los pa??ses reportados hasta la fecha
    '''
    st.bar_chart(data=last_report, x='country', y='infected_cases')

with evolution:
    st.header("Evoluci??n de los casos reportados ")
    # description
    st.markdown(
        'A continuaci??n se puede analizar la evoluci??n de los nuevos casos reportados, tanto diariamente, por mes o un resumen anual-mensual. Para el caso mensual y peri??dico se'
        'calcul?? el promedio de los casos reportados para cada uno de esos periodos')

    ev_country, ev_time = user_params(countries, 'Seleccione un pa??s', False, 'ev_radio', 'ev_country')
    ev_confirmed, ev_deaths, ev_recovered = st.tabs(['??????? Confirmados', '??????Fallecidos', '??????? Recuperados'])
    evolution = cases_evolution(covid_data, ev_country, ev_time)
    if ev_time == 'D??a':
        time = 'date'
    elif ev_time == 'Mes':
        time = 'month'
    else:
        time = 'period'

    ev_confirmed.line_chart(data=evolution, x=time, y='new_cases')
    ev_deaths.line_chart(data=evolution, x=time, y='new_deaths')
    ev_recovered.line_chart(data=evolution, x=time, y='new_recovered')

with compare:
    st.header('Comparaci??n de estad??sticas entre pa??ses')
    # description
    st.markdown(
        "En las siguientes gr??ficas se podr?? realizar una an??lisis m??s profundo al poder comparar la evoluci??n de los caso reportados por pa??s. Para esta comparaci??n"
        " se utiliza la normalizaci??n de los casos reportados por mill??n de habitantes. Para poder observar alguna gr??fica debe de primero seleccionar al menos"
        " un pa??s.")
    comp_country, comp_time = user_params(countries, 'Seleccione los pa??ses que desea comparar', True, 'comp_radio',
                                          'comp_country', labels=['Mes', 'A??o'])
    comp_confirmed, comp_deaths = st.tabs(['??????? Confirmados', '??????Fallecidos'])

    evolution = compare_countries(covid_data, comp_country, comp_time)
    if comp_time == 'Mes':
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
    st.header("An??lisis de casos recuperados vs fallecidos ")
    # description
    st.markdown(
        "En este apartado se permite realizar un an??lisis m??s profundo en cuanto a los casos que resultaron en fallecimiento con respecto a aquellos"
        "que se reportaron como recuperados")
    diff_country, diff_time = user_params(countries, 'Seleccione un pa??s', False, 'diff_radio', 'diff_country',
                                          labels=['Actual', 'D??a', 'Mes', 'A??o'])
    diff_deaths, diff_recovered = st.tabs(['??????Fallecidos', '??????? Recuperados'])

    evolution = cases_evolution(covid_data, diff_country, diff_time)

    if diff_time == 'Actual':
        time = 'country'
    elif diff_time == 'D??a':
        time = 'date'
    elif diff_time == 'Mes':
        time = 'month'
    else:
        time = 'period'

    diff_deaths.bar_chart(data=evolution, x=time, y=['total_deaths', 'total_recovered'])
