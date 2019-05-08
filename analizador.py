import numpy as np
import pandas as pd
from bottle import route, run
import matplotlib.pyplot as plt
import tempfile
import os
import dropbox


token = '2LSGMO_SETAAAAAAAAAAEGFCm9QjaipYWYV9P484x-7OqfSf-sEDibbSn5bKNiRz'	# Clave de acceso
dbx = dropbox.Dropbox(token)


@route('/grafica', method=['GET', 'POST'])
def grafica():

    excel = tempfile.NamedTemporaryFile(suffix=".xls", delete=False)
    froute = excel.name  # Ruta del fichero temporal
    print(froute)
    dbx.files_download_to_file(froute, "/stadistics.xls")  # Guardamos el .xls en el fichero temporal
    dataframe = pd.read_excel(froute)
    dataframe.plot(kind='barh', x='Autor', y='Seguidores')
    plt.xlabel('Seguidores')
    plt.ylabel('Autores')
    plt.tight_layout()
    plt.savefig('grafica.png')
    plt.show()

@route('/estadistica', method=['GET', 'POST'])
def estadistica():

    excel = tempfile.NamedTemporaryFile(suffix=".xls", delete=False)
    froute = excel.name  # Ruta del fichero temporal
    dbx.files_download_to_file(froute, "/stadistics.xls")  # Guardamos el .xls en el fichero temporal
    dataframe = pd.read_excel(froute)

    yield "<center>"
    yield "MEDIA DE SEGUIDORES <br/>"
    yield "======================== <br/>"
    yield "La media es de " + repr(dataframe['Seguidores'].mean()) + " seguidores<br/><br/>"
    yield "DESVIACIÓN TÍPICA <br/>"
    yield "======================== <br/>"
    yield "La desviación típica es de " + repr(dataframe['Seguidores'].std()) + "<br/><br/>"
    yield "SUMA DE SEGUIDORES <br/>"
    yield "======================== <br/>"
    yield "La suma es de " + repr(dataframe['Seguidores'].sum()) + " seguidores<br/><br/>"
    yield "MEDIANA <br/>"
    yield "======================== <br/>"
    yield "La mediana es " + repr(dataframe['Seguidores'].median()) + "<br/><br/>"
    yield "NÚMERO MÁXIMO DE SEGUIDORES <br/>"
    yield "======================== <br/>"
    yield "El número máximo de seguidores es " + repr(dataframe['Seguidores'].max()) + " seguidores<br/><br/>"
    yield "NÚMERO MÍNIMO DE SEGUIDORES <br/>"
    yield "======================== <br/>"
    yield "El número mínimo de seguidores es " + repr(dataframe['Seguidores'].min()) + "<br/><br/>"
    yield "NÚMERO DE TWEETS REGISTRADOS <br/>"
    yield "======================== <br/>"
    yield "El número de tweets registrados es " + repr(dataframe['ID'].count())
    yield "<center/>"

run(host='localhost', port=8080, debug=True)