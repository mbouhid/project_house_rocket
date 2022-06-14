import pandas as pd
import streamlit as st


st.set_page_config(layout='wide')
st.title('House Rocket Company')
st.markdown('Welcome to House Rocket Data Analysis')


def get_data(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date'])
    data['bathrooms'] = data['bathrooms'].astype(int)

    #debug
    #st.header('#DEBUG')
    #st.dataframe(data)

    return data

def data_treatment(data):

    # Removendo duplicatas
    data = data.drop_duplicates(subset=['id'], keep='last')

    # Removendo possível erro de digitação
    data = data.loc[data['bedrooms'] != 33]

    return data


def calc_mediana(data):
    st.header('Median per zipcode')

    f_attributes = st.sidebar.multiselect('Select Attributes',
                                          data.columns.sort_values().unique(),
                                          default=(['id', 'date', 'price', 'zipcode', 'condition']))
    f_zipcode = st.sidebar.multiselect('Select Zipcode', data['zipcode'].sort_values().unique())

    if (f_zipcode != []) & (f_attributes != []):
        data = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]
    elif (f_zipcode == []) & (f_attributes != []):
        data = data.loc[:, f_attributes]
    elif (f_zipcode != []) & (f_attributes == []):
        data = data.loc[data['zipcode'].isin(f_zipcode), :]
    else:
        data = data.copy()

    mediana = data[['price', 'zipcode']].groupby('zipcode').median().reset_index()
    mediana.columns = ['zipcode', 'mediana']
    df1 = pd.merge(data, mediana, on='zipcode', how='inner')

    for i in range(len(df1)):
        if (df1.loc[i, 'price'] < df1.loc[i, 'mediana']) & (df1.loc[i, 'condition'] >= 3):
            df1.loc[i, 'status'] = 'Compra'
        else:
            df1.loc[i, 'status'] = 'Não Compra'

    st.dataframe(df1)
    return df1

# Pegar o retorno da função com a nova tabela (mediana)
# identificar a temporada de acordo com a data (verão, inverno,...)
# o preço da mediana tbm varia de acordo com a temporada
# Colocar nova coluna preço de venda:
#   Se preço compra for maior do que a mediana da regiao + temporada (inverno) (atribuir 10% no preço de venda)
#   Se preço compra for menor do que a mediana da regiao + temporada (verão) (atribuir 30% no preço de venda)
# tabela final: id, zipcode, temporada, mediana, p compra, p venda, lucro(compra menos venda)


def season(df1):

    f_status = st.sidebar.checkbox('Somente status de compra')
    f_winter = st.sidebar.checkbox('Somente season winter')
    f_summer = st.sidebar.checkbox('Somente season summer')

    if f_status & f_winter:
        st.header('Buy per Season (winter)')
        df = df1[df1['status'] == 'Compra']
        df.loc[(df['date'].dt.month == 1) |
               (df['date'].dt.month == 2) |
               (df['date'].dt.month == 12), 'season'] = 'winter'
        df = df[df['season'] == 'winter']
        mediana = df[['price', 'zipcode']].groupby('zipcode').median().reset_index()
        winter = df[['season', 'zipcode']].groupby('zipcode').median().reset_index()
        m1 = pd.merge(mediana, winter, on='zipcode', how='inner')
        df3 = pd.merge(df, m1, on='zipcode', how='inner')
        df3['price_sales'] = df3.apply(lambda x: (x['price_x'] * 1.3)
                                       if (x['price_x'] < x['price_y'])
                                       else (x['price_x'] * 1.1), axis=1)
        # Calculando Lucro
        df3['profit'] = df3['price_sales'] - df3['price_x']
        df3.columns = ['id', 'date', 'price_buy', 'zipcode', 'condition',
                       'median_total', 'status', 'season', 'median_zipcode', 'price_sales', 'profit']
        st.dataframe(df3)
        profit_total = round(df3['profit'].sum(), 2)
        st.write(f'O lucro total, se todos os imóveis forem vendidos, será de **${profit_total}**')
    elif f_status & f_summer:
        st.header('Buy per Season (summer)')
        df = df1[df1['status'] == 'Compra']
        df.loc[(df['date'].dt.month == 6) |
               (df['date'].dt.month == 7) |
               (df['date'].dt.month == 8), 'season'] = 'summer'
        df = df[df['season'] == 'summer']
        mediana = df[['price', 'zipcode']].groupby('zipcode').median().reset_index()
        summer = df[['season', 'zipcode']].groupby('zipcode').median().reset_index()
        m1 = pd.merge(mediana, summer, on='zipcode', how='inner')
        df3 = pd.merge(df, m1, on='zipcode', how='inner')
        df3['price_sales'] = df3.apply(lambda x: (x['price_x'] * 1.3)
                                       if (x['price_x'] < x['price_y'])
                                       else (x['price_x'] * 1.1), axis=1)
        # Calculando Lucro
        df3['profit'] = df3['price_sales'] - df3['price_x']
        df3.columns = ['id', 'date', 'price_buy', 'zipcode', 'condition',
                       'median_total', 'status', 'season', 'median_zipcode', 'price_sales', 'profit']
        st.dataframe(df3)
        profit_total = round(df3['profit'].sum(), 2)
        st.write(f'O lucro total, se todos os imóveis forem vendidos, será de **${profit_total}**')
    elif f_status:
        st.header('Only Buys')
        st.dataframe(df1[df1['status'] == 'Compra'])
    else:
        st.header('All data - Choose Filter')
        st.dataframe(df1)
    return None

# media do imoveis waterfront
# media de todos os imoveis
# calculo media de todos imoveis vezes 30%
# comparar calculo com a media waterfront (verdadeiro ou falso - texto)


def water_front(data):
    st.subheader('Waterfront')
    waterfront = data[['waterfront', 'price']].groupby('waterfront').mean().reset_index()
    st.write(waterfront)
    if (waterfront.iloc[0, 1] * 1.3) < waterfront.iloc[1, 1]:
        st.write('A média de preço dos imóveis com vista para a água é maior do que 30%')
    else:
        st.write('A média de preço dos imóveis com vista para a água é menor do que 30%')
    return None

#H2: Imóveis com data de construção menor que 1955, são 50% mais baratos, na média.


def built(data):
    st.subheader('Built until 1955')
    st.write('Hipótese: Os imóvel construídos antes de 1955, são 50% mais baratos do que a média de '
             'preços dos imóveis construídos depois de 1955.')

    df = data[data['yr_built'] <= 1955]
    menor_1955 = df.loc[:, 'price'].mean()
    df2 = data[data['yr_built'] > 1955]
    maior_1955 = df2.loc[:, 'price'].mean()

    st.write(f'A média de preços, de imóveis construídos antes de 1955, é:  {menor_1955:.2f}')
    st.write(f'A média de preços, de imóveis construídos depois de 1955, é:  {maior_1955:.2f}')
    st.write('**Análise do resultado da hipótese:**')  # write in Bold
    st.subheader('Rever calculo')
    compare = menor_1955 / maior_1955
    if compare > 0.5:
        st.write('Falso: Imóveis com data de construção menor que 1955, **NÃO** são mais baratos'
                 ' 50% do que os imóveis construídos depois de 1955.')
        st.write(f'Esse valor corresponde a ****{(1-(menor_1955/maior_1955))*100:.2f}%**** de desconto'
                 f' sobre o valor médio dos imóveis construídos depois de 1955.')
    else:
        st.write('Verdadeiro: Imóveis com data de construção menor que 1955, são mais **BARATOS**'
                 ' do que os imóveis construídos depois de 1955.')
        st.write(f'Esse valor corresponde a ****{(1-(menor_1955/maior_1955))*100:.2f}%**** do valor médio'
                 f'  dos imóveis construídos depois de 1955.')
    return None


#H3: Imóveis sem porão (sqft_basement) possuem área total (sqrt_lot) 50% maiores do que imóveis com porão.

def basement(data):
    st.subheader('With Basement')
    st.write('Hipótese: Imóveis sem porão possuem área total 50% maiores do que imóveis com porão.')

    df = data[data['sqft_basement'] != 0]
    with_basement = df.loc[:, 'sqft_lot'].mean()
    df1 = data[data['sqft_basement'] == 0]
    without_basement = df1.loc[:, 'sqft_lot'].mean()

    st.write(f'Tamanho médio da área total dos imóveis com porão: {with_basement:.2f}')
    st.write(f'Tamanho médio da área total dos imóveis sem porão: {without_basement:.2f}')
    st.write('**Análise do resultado da hipótese:**')  # write in Bold
    compare = (without_basement - with_basement) / with_basement
    if compare > 0.5:
        st.write('Verdadeiro: Imóveis sem porão possuem área total 50% MAIORES do que imóveis com porão.')
        st.write(f'O percentual é de {(compare) * 100:.2f} % ')
    else:
        st.write('Falso: Imóveis sem porão NÃO possuem área total 50% maiores do que imóveis com porão.')
        st.write(f'O percentual é de {(compare) * 100:.2f} % ')

    return None


#H4: O crescimento do preço dos imóveis YoY ( Year over Year ) é de 10%

# calcular media preço por ano, mês a mês (ex: jan14 e jan15)
# grafico demonstrando o percentual de crescimento entre os anos
# Escrever análise se houve crescimento de 10% ou não

def growth(data):
    st.subheader('Annual Growth')
    st.write('Hipótese: O crescimento do preço dos imóveis YoY ( Year over Year ) é de 10%.')
    # Pegar o ano somente
    df = data.copy()
    df['year_date'] = data['date'].dt.year
    df1 = df[['year_date', 'price']].groupby('year_date').mean().reset_index()
    st.write(df1)

    ano1 = df1.loc[0, 'price']
    ano2 = df1.loc[1, 'price']
    calc = ((ano2 - ano1) / ano1) * 100

    if calc >= 10:
        st.write(f'O percentual de crescimento YoY foi de **{calc:.2f} %**.')
    else:
        st.write(f'O percentual de crescimento YoY foi de **{calc:.2f} %**.'
             f' Ou seja, a meta de 10% não foi atingida.')

    return None


#H5: Imóveis com 3 banheiros tem um crescimento MoM ( Month over Month ) de 15%

# comparação mês a mês (jan14 e fev14, fev14 e mar14,....)

def growth_bath(data):
    st.subheader('Month Growth, only 3 baths')
    st.write('Hipótese: Imóveis com 3 banheiros tem um crescimento MoM ( Month over Month ) de 15%.')

    df = data[data['bathrooms'] == 3]
    df['year_date'] = df['date'].dt.year
    df['month_date'] = df['date'].dt.month

    df1 = df[['year_date', 'month_date', 'price']].groupby(['year_date', 'month_date']).mean().reset_index()
    df1['pct_change'] = (df1.sort_values('year_date').select_dtypes(include='float64').pct_change()) * 100
    st.write(df1)

    return None


if __name__ == "__main__":

    path = 'kc_house_data.csv'
    data = get_data(path)
    data = data_treatment(data)
    df1 = calc_mediana(data)
    season(df1)
    st.header('Hipoteses Validation')
    water_front(data)
    built(data)
    basement(data)
    growth(data)
    growth_bath(data)
    #st.write(data.columns)
