# importar bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import io
from io import BytesIO
import datetime
import re
import base64
from PIL import Image

# função principal da aplicação
def app():
        st.set_page_config(page_title="Rimor - GGMF",layout="wide",page_icon='fibra.png',initial_sidebar_state="collapsed",menu_items={'About': "# Rimor uma aplicação para visualização de dados"
        })
        #logo tentativa
        
        @st.experimental_memo
        def get_img_as_base64(file):
                with open(file, "rb") as f:
                        data = f.read()
                return base64.b64encode(data).decode()


        img = get_img_as_base64("dark.png")

        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
        background-image: url("data:image/png;base64,{img}");
        background-size: 100%;
        background-position: top left;
        background-repeat: no-repeat;
        background-attachment: fixed;
        }}
        [data-testid="stSidebar"] > div:first-child {{
        background-image: url("data:image/png;base64,{img}");
        background-position: center; 
        background-repeat: no-repeat;
        background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
        }}
        [data-testid="stToolbar"] {{
        right: 2rem;
        }}
        </style>
        """

        st.markdown(page_bg_img, unsafe_allow_html=True)
      


                
        # titulo da aplicação)
        image = Image.open('Imagem4.png')
        st.image(image)
        #new_image = image.resize((, 238))
        #st.image(new_image)
        # titulo da aplicação)
        # sub titulo da aplicação
        with open("designe.css") as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.subheader('Espaço para análise exploratória do seu experimento.')
       
        # adicionando uplouder buttom
        uplouded_file = st.file_uploader(label="Faça o uploud da sua medição processada aqui!", type=['xlsx'])
        # ler arquivo csv
        if uplouded_file is not None:
                arquivo = pd.read_excel(uplouded_file)
                # O famono Back END

                #Baixando o arquivo e substituindo NAs das colunas de interesse  
                arquivo[['atributo']] = arquivo[['atributo']].replace(np.nan,0)
                arquivo['atributo'] = arquivo['atributo'].replace(0,"Sem atributo")
                df = arquivo[arquivo['fuste'] ==1]
                df = df.rename(columns={"h_total": "Altura", "dap": "DAP", "vol_ind": "Volume"})

                ### Sub tabela para fazer o coeficiente de variação 
                cv = lambda x: np.std(x, ddof=1) / np.mean(x) * 100 

                tabela_cv = df.groupby(['fator1', 'idade'])['DAP', 'Altura', 'Volume'].apply(cv).round(1).reset_index()
                tabela_cv.columns = ['Material genético', 'Idade', 'DAP (CV%)','Altura (CV%)', 'Volume (CV%)']
                ### Sub tabela para media 
                tabela_resumo= df.groupby(['experimento','fator1'])['DAP','Altura','Volume'].mean().round(2).reset_index()
                tabela_resumo.columns = ['Experimento', 'Material genético', 'DAP médio (cm)','Altura média (m)', 'Volume médio (m³)']
                #juntando as duas primeiras sub tabelas
                tabela_cv_media = tabela_resumo.merge(tabela_cv, how='inner', on='Material genético')
                #Calculos de sobrevivencia e mortalidade
                table_rates = df
                table_rates['total_tree'] = table_rates.groupby('fator1')['DAP'].transform('size')
                table_rates = df[df['DAP'].notnull()]
                table_rates = table_rates[['fator1','total_tree']]
                table_rates["live_tree"] = table_rates.groupby('fator1')['fator1'].transform('size')
                table_rates["died_tree"] = table_rates["total_tree"]-table_rates["live_tree"]
                table_rates["die_rate"] = round((table_rates["died_tree"]/table_rates["total_tree"])*100,2)
                table_rates["survive_rate"] = round((table_rates["live_tree"]/table_rates["total_tree"])*100,2)
                table_rates.drop_duplicates(inplace=True)
                table_rates.columns = ['Material genético','Total de árvores', 'Árvores vivas', 
                'Árvores mortas','Taxa de mortalidade %', 'Sobrevivência %']
                table_rates.round(1)
                #Juntando tabelas de medias/cv e de sobrevivencia/mortalidade
                tabela_resumo = tabela_cv_media.merge(table_rates, how='inner', on='Material genético')
                tabela_resumo.drop_duplicates(inplace=True)
                
                #uma lista de dap maior que zero/usando no filtro de mat gen
                maior_0 = df[df['DAP']>0]
                maior_0 = df[df['Volume']>0]
                maior_0 = df[df['Altura']>0]
                #base do filtro de mat gen do grafico histograma
                mat_gen = df.copy()
                #O mano Front END
                exp = arquivo['experimento'][0]
                exp_t = "Tabela resumo: " + exp
                # adicionar texto na página
                st.subheader(exp_t)
                # criando imagem do dataset
                st.dataframe(tabela_resumo)

                
                #criando tituto de primeiros gráficos
                st.subheader("Gráficos - Atributos e Material genético")
                #criando um select box para escolha de variaveis
                coluna = st.selectbox('Selecione entre as variaveis', ("Altura", "DAP", "Volume"))
                #setando labels
                if coluna == "Altura":
                        label = 'Altura (m)'
                elif coluna == "Volume":
                        label = 'Volume (m³)'
                else:
                        label = 'DAP (cm)' 

                
                #grafico  histograma de atributo 
                #st.write("Histograma - Frequência do" , label, "dos indivíduos dentro de cada atributo")
                #Histograma_Atributos = px.histogram(df, x=coluna, color='atributo',barmode='overlay',labels={
                #coluna: label
                #})
                #Histograma_Atributos.update_layout({
                        #'plot_bgcolor': 'rgb(235, 235, 235)',
                #'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                #'font_color': 'rgb(235, 235, 235)'
                #})
                #st.plotly_chart(Histograma_Atributos, use_container_width=True)

                #filtro de matgen
                if st.checkbox('Aplicar filtro de Material genético'):
                        material = st.selectbox('Selecione o material genético', (list(maior_0['fator1'].unique())))
                        maior_0 = maior_0[maior_0['fator1']== material]
                        mat_gen = mat_gen[mat_gen['fator1']== material]
                        tamanho=None
                
                else:
                        tamanho=4000

                #histograma mat gen
                st.write("Histograma - Frequência do" , label, "dos indivíduos")
                Histograma_Matgen = px.histogram(mat_gen, x=coluna, color='atributo',hover_name='fator1', barmode='overlay',labels={
                coluna: label,
                'fator1' : "Material genético"
                })
                Histograma_Matgen.update_layout({
                        'plot_bgcolor': 'rgb(235, 235, 235)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font_color': 'rgb(235, 235, 235)'
                })
                st.plotly_chart(Histograma_Matgen, use_container_width=True)
                #box plot mat gen

                st.write("Box plot - " , label, "por material genético")

                Boxplot_Matgen = px.box(data_frame=maior_0, x="fator1", y=coluna, width=tamanho, color="fator1", 
                                hover_name='atributo',
                                points='all', height=None, labels={
                coluna: label,
                'fator1': 'Material genético'                   
                })
                Boxplot_Matgen.update_layout({
                        'plot_bgcolor': 'rgb(235, 235, 235)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font_color': 'rgb(235, 235, 235)'
                })
                st.plotly_chart(Boxplot_Matgen)

                #escrevendo subtitulo segunda leva grafica
                st.subheader("Gráficos - Valores médios")
                #criando um select box para escolha de medias
                media = st.selectbox('Selecione entre as variáveis médias', ('Altura média (m)', "DAP médio (cm)", 'Volume médio (m³)','DAP (CV%)','Altura (CV%)','Volume (CV%)'))
                #setando labels
                if media == 'Altura média (m)':
                        label2 = 'Altura (m)'
                elif media == 'Volume médio (m³)':
                        label2 = 'Volume (m³)'
                elif media == 'DAP (CV%)':
                        label2 = 'DAP (CV%)'
                elif media == 'Altura (CV%)':
                        label2 = 'Altura (CV%)'
                elif media == 'Volume (CV%)':
                        label2 = 'Volume (CV%)'
                else:
                        label2 = 'DAP (cm)' 
                st.write("Gráfico de barras" ,label2 ,"médio de cada material genético")

                Barras_medias = px.bar(tabela_resumo, x='Material genético', y= tabela_resumo[media].round(2),  width=4000,color ='Sobrevivência %',
                text_auto=True,
                labels={'y': label2})
                                
                Barras_medias.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

                Barras_medias.update_layout( xaxis={'categoryorder':'total descending'})

                Barras_medias.update_layout({
                        'plot_bgcolor': 'rgb(235, 235, 235)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font_color': 'rgb(235, 235, 235)'
                })
                st.plotly_chart(Barras_medias)

                #escrevendo subtitulo terceira leva grafica
                st.subheader("Gráficos - disperção")
                disp2 = st.selectbox('Selecione seu eixo x', ("Altura", "DAP", "Volume"))
                disp= st.selectbox('Selecione seu eixo y', ("Altura", "DAP", "Volume"))
                #setando labels
                if disp == "Altura":
                        label = 'Altura (m)'
                elif disp == "Volume":
                        label = 'Volume (m³)'
                else:
                        label = 'DAP (cm)' 
                #grafico de disperção
                st.write("Gráfico de dispersão",disp,"x",disp2,"por atributo")
                Scatter_Atributos = px.scatter(df, x=disp2, y=disp,  color="atributo", hover_name='fator1', trendline="ols", 
                 trendline_scope="overall",opacity=0.65, 
                 size=df[disp].replace(np.nan,0),labels={
                'DAP': 'DAP (cm)',
                'Altura': 'Altura (m)',
                'atributo' : "Atributo"                
                })
                Scatter_Atributos.update_layout({
                        'plot_bgcolor': 'rgb(235, 235, 235)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font_color': 'rgb(235, 235, 235)'
                })
                st.plotly_chart(Scatter_Atributos)

                #disperção mat gen
                st.write("Gráfico de dispersão",disp,"x",disp2,"por material genético")
                Scatter_Matgen = px.scatter(df, x=disp2, y=disp,  color="fator1", hover_name='atributo', trendline="ols", 
                 trendline_scope="overall",opacity=0.65, 
                 size=df[disp].replace(np.nan,0),labels={
                'Altura': 'Altura (cm)',
                'Volume': 'Volume (m³)',
                'fator1' : "Material genético"                
                })
                Scatter_Matgen.update_layout({
                        'plot_bgcolor': 'rgb(235, 235, 235)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font_color': 'rgb(235, 235, 235)'
                })
                st.plotly_chart(Scatter_Matgen)

                texto = st.text_input('Digite o seu nome!!! Você chegou ao final da aplicação!!!')
                        # Escrevendo o texto do usuário na tela
                if texto:
                        st.write('Obrigado por usar o Rimor', texto, 'volte sempre!!!')
                
                #select do side bar

                add_selectbox = st.sidebar.selectbox(
                "Qual gráfico voce gostaria de baixar? (O gráfico será baixado no estado atual)",
                ('Histograma por Material Genético', 'Boxplot por Material Genético','Barras medias'
                ,'Disperção por Atributos','Disperção por Material Genético')
                )

                if add_selectbox == 'Histograma por Material Genético':
                        baixar = Histograma_Matgen
                elif add_selectbox == 'Boxplot por Material Genético':
                        baixar = Boxplot_Matgen
                elif add_selectbox == 'Barras medias':
                        baixar = Barras_medias
                elif add_selectbox == 'Disperção por Atributos':
                        baixar = Scatter_Atributos
                elif add_selectbox == 'Disperção por Material Genético':
                        baixar = Scatter_Matgen
                
                #botão legal para baixar graficos

                buffer = io.StringIO()
                baixar.write_html(buffer, include_plotlyjs='cdn')
                html_bytes = buffer.getvalue().encode()

                st.sidebar.download_button(
                label='📥 Download Gráfico HTML',
                data=html_bytes,
                file_name='gráfico.html',
                mime='text/html'
                )
                
                #funçãozinha do botão que gera excel

                def to_excel(df):
                        output = BytesIO()
                        writer = pd.ExcelWriter(output, engine='xlsxwriter')
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                        workbook = writer.book
                        worksheet = writer.sheets['Sheet1']
                        format1 = workbook.add_format({'num_format': '0.00'}) 
                        worksheet.set_column('A:A', None, format1)  
                        writer.save()
                        processed_data = output.getvalue()
                        return processed_data

                df_xlsx = to_excel(tabela_resumo)
                st.sidebar.download_button(label='📥 Download tabela resumo em Excel',
                                                data=df_xlsx ,
                                                file_name= 'Tabela_Resumo.xlsx')


        # chamada para executar a aplicação principal
if __name__ == '__main__':
        app()
        
