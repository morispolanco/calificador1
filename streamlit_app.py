import streamlit as st
import pandas as pd
import openai

# Accedemos a la clave de API de OpenAI a través de una variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Agregamos un título al principio
st.title('Evaluador de ensayos')

# Agregamos información en una columna a la izquierda
st.sidebar.subheader('Instrucciones')
st.sidebar.markdown('Suba un archivo .XLSX con los ensayos de sus alumnos.')
st.sidebar.subheader('Autor')
st.sidebar.markdown('Moris Polanco')

# Pedimos al usuario que suba el archivo Excel
archivo = st.file_uploader('Cargar archivo Excel', type=['xlsx'])

# Si se subió un archivo, lo procesamos
if archivo:
    # Leemos el archivo con pandas
    data = pd.read_excel(archivo)

    # Pedimos al usuario que seleccione las columnas con el título y el ensayo
    columnas = data.columns
    columna_titulo = st.selectbox('Selecciona la columna que contiene los títulos:', columnas)
    columna_ensayo = st.selectbox('Selecciona la columna que contiene los ensayos:', columnas)

    # Obtenemos los títulos y los ensayos del archivo
    titulos = data[columna_titulo].tolist()
    ensayos = data[columna_ensayo].tolist()

    # Utilizamos la API de GPT-3 para calificar cada ensayo
    resultados = []
    for i, ensayo in enumerate(ensayos):
        prompt = f"Califica el ensayo titulado '{titulos[i]}'. "
        prompt += f"Ensayo: {ensayo}. "
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            n=1,
            stop=None,
            timeout=60,
        )
        justificacion = response.choices[0].text.strip()

        # Obtenemos la calificación y la justificación
        calificacion = justificacion.split("Nota:")[1].split(".")[0].strip()
        justificacion = justificacion.replace(calificacion, "la nota obtenida", 1)

        # Si la calificación es menor que 10, señalamos qué falta para alcanzarla
        if float(calificacion) < 10:
            justificacion += f"\n\nPara obtener una calificación de 10, el ensayo debería incluir: {response.choices[0].text.split('Para obtener una calificación de 10, el ensayo debería incluir:')[1]}"

        resultados.append({'Ensayo': titulos[i], 'Justificación': justificacion})

    # Mostramos los resultados en una tabla
    st.write('Resultados:')
    tabla = pd.DataFrame(resultados)
    st.table(tabla)
