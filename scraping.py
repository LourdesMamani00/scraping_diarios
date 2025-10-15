import requests #para hacer peticiones http
from bs4 import BeautifulSoup #para parsear html
import pandas as pd # para analizar y manejar datitos, 
import re # sirve para buscar, validar y limpiar textos, para expresiones regulares, es rapido
from datetime import date, datetime #fechas
from urllib.parse import urljoin # unir urls relativas con absolutas
import os #para manejar archivos y directorios
from newspaper import Article # newspaper es para hacer scrapping de diarios

#########################################################################################################
#   CONFIGURACIONES INICIALES
########################################################################################################
# INSTALAR: pip install openpyxl

########################################
# 1. PALABRAS CLAVES
########################################

#palabras claves FIJARSE BIEN LUEGO \sate\s O PARO
PALABRAS_CLAVES = re.compile(
    r'paro[a-zA-Z]*|paran|asambleas?|huelga|marcha|cortes? de ruta|cortan ruta|corte? de calle|cortan calle|'
    r'trabaj[a-zA-Z]*|sindica[a-zA-Z]*|paritari[a-zA-Z]*|gremi[a-zA-Z]*|cgt|'
    r'\suta\s|\sate\s|luz y fuerza|uepc|\ssep\s|\sutep\s|surrbac|economia popular|economia informal|'
    r'conflicto|despid[a-zA-Z]*|salar[a-zA-Z]*|transporte|aguinaldo|sueldo|bancaria|'
    r'delegad[a-zA-Z]*|limpieza|precariza[a-zA-Z]*|cadete|repartidor[a-zA-Z]*|aplicaciones|'
    r'suspen[a-zA-Z]*|laboral[a-zA-Z]*|conciliacion|moviliz[a-zA-Z]*|ajuste|protest[a-zA-Z]*|derechos?|cortes?',
    flags=re.IGNORECASE
)
#----------------------------------------------------------------------
#########################################
# 2. DIARIOS, CARPETAS Y ETIQUETAS (PARAMETROS DE LOS DIARIOS)
#########################################

A_PRUEBA_DE_NOTICIAS_LARGAS = "truncar"  # o "gencsv"

DIARIOS = [
    "https://www.laizquierdadiario.com/",
    "https://www.lavoz.com.ar/",
    "http://www.lavozdesanjusto.com.ar/",
    "https://www.eldiariocba.com.ar/",
    "https://www.cba24n.com.ar/",
    "https://www.puntal.com.ar/",
]

CARPETAS = [
    "la_izquierda",
    "la_voz_del_interior",
    "la_voz_de_san_justo",
    "el_diario_villa_maria",
    "cba24n",
    "puntal_rio_cuarto",
]

''' Los html tags son las reglas o patrones de busqueda que se usan para beautifullsoup. Ejemplo:
<div class="columnista">
  <a href="nota1.html">Nota 1</a>
</div>
<h2><a href="nota2.html">Nota 2</a></h2>
----------------------------------------------
soup.select("div.columnista a")
lo que encontro: <a href="nota1.html">Nota 1</a>
'''
HTML_TAGS = [
    ["div.columnista a", "h2 a", "h3 a"],
    ["h2 a", "h1 a", "article a", "main article seccion h1", "div article a", "article a"],
    ["a"], #"main seccion div article a", "article a"
    ["h2 a"],
    ["div a"],
    ["h1 a", "h2 a", "h3 a"],
]

#VER BIEN LUEGO QUE ONDA CON ESTO
ETIQUIETA_TITULOS = [
    ['h1'], ['h1'], ['article h1'], ['article h1'], ['article h1'], ['article h1']
]

#VER BIEN LUEGO QUE ONDA CON ESTO
ETIQUETA_NOTAS = [
    ['div p'], ['article p'], ['div p'], ['div p'], ['div p'], ['div p']
]

####################################################################################################################
# FUNCIONES AUXILIARES
##################################################################################################################

#conseguir los enlaces, consta de 2 parametros: la url y la tematica o etiqueta
def get_scraping_links(pag_web, tag_link):
    """Obtiene todos los enlaces válidos desde una página HTML."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(pag_web, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[WARN] No se pudo acceder a {pag_web} - Código {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for tag in soup.select(tag_link):
            href = tag.get("href")
            if href:
                full_link = requests.compat.urljoin(pag_web, href)
                links.append(full_link)
        return list(set(links))
    except Exception as e:
        print(f"[ERROR] scraping_links({pag_web}): {e}")
        return []


#IMPORTANTE: aplicar un flitro de cordoba, solo de cordoba con izquierda diario, los demas diarios son locales
def extraer_seccion(url): #preguntar luego si es correcto
    ''' esta funcion extrae la seccion del link, ejemplo: extract section("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123")
    Devuelve: "provincia-de-buenos-aires" . Si no encuentra la seccion devuelve "NA"'''
    url = url.lower()
    match = re.search(r'\.com(?:\.ar)?/([^/]+)/?', url) #busca el patron .com/ seguido de cualquier caracter que no sea /, una o mas veces, seguido de /
    #print(match)
    #print(match.group(1) if match else "NA")
    return match.group(1) if match else "NA" #si encuentra el patron devuelve el primer elemento del grupo, sino NA
print("extraer seccion:")
link = "https://www.lavoz.com.ar/ciudadanos/centros-de-jubilados-denuncian-demoras-en-pagos-de-pami-por-los-talleres-sociopreventivos/"
extraer_seccion(link)
print("FIN DE EXTRAER SECCION")
#TENER CUIDAdo con esto
#fijarse bien luego, este siempre devuelve el ultimo elemento del link o los ultimos elementos del link
def link_length(url):  #fijarse bien luego, este siempre devuelve el ultimo elemento del link
    """esta funcion devuelve la cantidad de palabras en el link, ejemplo: link_length("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123-extra-paro")
    devuelve: 3 donde  es la cantidad de palabras en la seccion del link que es noticia123 extra paro"
    """
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    return len(url.split("-")) ##no se si deberia 1 
print("FIN DE LINK LENGTH")
link = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123-extra-paro"
print(link_length(link))
print("FIN DE LINK LENGTH")

#se fija si el link tiene palabras claves, posiblemente cambiar nombre de funcion, tal vez deberia retornar NA para checkear?
def create_tags(url):
    """esta funcion crea tags a partir del link, ejemplo:
    create_tag("https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés/casas-paro-noticia123")
    devuelve: "paro"
    """
    url = url.lower() #convierte a minusculas
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    #print("URL EN CREATE TAG")
    #print(url)
    url = (url.replace("á","a").replace("é","e")
              .replace("í","i").replace("ó","o").replace("ú","u")
              .replace("-", " ")) #elimina tildes y reemplaza guiones por espacios
    tags = PALABRAS_CLAVES.findall(url) #busca todas las coincidencias de palabras claves en el url
    return " ".join(tags) #une las palabras claves encontradas en una sola cadena separada por espacios, si no encuentra palabras claves devuelve vacio ' '


# ejemplo de uso create tag, CREO QUE ESTA MAL, FIJARSE QUE ONDA CON LAS EXPRESIONES REGULARES
#ejemplo = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés-paro-trabajadores/paro-noticia123/"
'''
ejemplo= "https://www.lavoz.com.ar/ciudadanos/transporte-urbano-de-cordoba-podria-haber-asambleas-la-semana-proxima/"
print("EJEMPLO DE CREATE TAG")
print("este es el ejemplo: ")
print(create_tags(ejemplo))

print("FIN DEL EJEMPLO DE CREATE TAG")
url = "https://www.laizquierdadiario.com/huelga-Trabajadores-en-huelga-por-mejores-salarios-paro"
print(create_tags(url))
'''
#----------------------------------------------------------------------

def crear_enlaces(diario, html_tags):
    """ Crea un Dataframe  con las fechas, los diarios, los links, la seccion, el tamanio del link y las palabras claves """
    links = []
    for tag in html_tags:
        links.extend(get_scraping_links(diario, tag))
    links = list(set(links))  # Elimina duplicados
    print(f"[INFO] {len(links)} enlaces encontrados en {diario}")
    
    if "laizquierdadiario.com" in diario:
        provincia = "Cordoba"
        filtro_url = f"laizquierdadiario.com/{provincia}"
        links_filtrados = [link for link in links if filtro_url in link]

        print(f"[INFO] {len(links_filtrados)} enlaces encontrados de {provincia} en {diario}")

        links = links_filtrados
    
    data = []
    for link in links:
        data.append({
            "fecha": date.today(),
            "diario": diario,
            "link": link,
            "seccion": extraer_seccion(link), #devuelve la seccion del link o NA
            "tamanio_link": link_length(link), #devuelve la cantidad de palabras que vienen luego de la seccion
            "palabras_claves": create_tags(link) #devuelve la palabra clave encontrada en el link, fijarse que onda con la palabra claave paro
        })
    df = pd.DataFrame(data)
    print(f"se creo que dataframe para {diario}")
    print("este es el famoso Dataframe: ")
   
    #print(df)
    return df

#diario = "https://www.laizquierdadiario.com/"
#html_tags = ["div.columnista a", "h2 a", "h3 a"]

#diario = "https://www.lavoz.com.ar/"
#html_tags = ["h2 a", "h1 a, article a", "main article seccion h1", "div article a", "article a"]

#en la voz de san justo no tienen "seccion como tal, tiene otra forma de definir los links por "seccion""
# diario = "https://www.lavozdesanjusto.com.ar/"
# html_tags = ["a", "main seccion div article a", "article a"]

# diario = "https://www.eldiariocba.com.ar/"
# html_tags = ["h2 a"] #div article div a

# diario = "https://www.cba24n.com.ar/"
# html_tags = ["div a"]

# diario =     "https://www.puntal.com.ar/"
# html_tags = ["h1 a", "h2 a", "h3 a", "figure a"] #div article figure a

#df = crear_enlaces(diario, html_tags)
# # Mostrar solo las filas donde 'palabras_claves' no está vacía
#df_filtrado = df[df["palabras_claves"].notna() & (df["palabras_claves"] != "")]
#print(df_filtrado)

#print(df.head(60))

#print(df.head())

def obtener_titulo_y_contenido(url, etiqueta_titulo, etiqueta_nota):
    """Obtiene el título y el contenido de una noticia dada su URL y las etiquetas HTML correspondientes."""
    try:
        articulo = Article(url)
        articulo.download()
        articulo.parse()
        return articulo.title, articulo.text
    except Exception as e:
        return Null, Null       
#la voz del interior
# url = "https://www.lavoz.com.ar/servicios/bono-de-100000-para-jubilados-cordobeses-cuando-se-paga-y-a-quienes-les-corresponde/"
# etiqueta_titulo = 'h1'
# etiqueta_nota = 'article p'
# titulo, contenido = obtener_titulo_y_contenido(url, etiqueta_titulo, etiqueta_nota)
# print("Titulo:", titulo)
# print("Contenido:", contenido[:500])  # Muestra solo los primeros 500 caracteres del contenido


#FALTA LA FUNCION CREAR ENLACES Y LA DE RELLENAR DATOS O OBTENER TITULOS Y CONTENIDOS


##################################################################################################################
#   FUNCION PRINCIPAL O SCRAPING PRINCIPAL
##################################################################################################################

for i, diario in enumerate(DIARIOS):
    #obtiene los enlaces y los pone en un dataframe
    df_sin_filtro = crear_enlaces(diario, HTML_TAGS[i])
    if df_sin_filtro.empty: 
        continue
    #primero filtra los enlaces, si tiene palabras claves las guarda en el dataframe y sino tiene las quita, despues excluye las secciones que no interesan
    df = df_sin_filtro[df_sin_filtro["palabras_claves"].notna() & (df_sin_filtro["palabras_claves"] != "")]
    df = df[df["tamanio_link"] > 3] #VER ESTO LUEGO

    if "lavoz.com.ar" in diario:
        excluir = ['avisos', 'vos', 'NA', 'deportes', 'espacio-de-marca', 'espacio-publicidad', 'tendencias']
    elif "lavozdesanjusto.com.ar" in diario:
        excluir = ['NA','suplementos']
    elif "eldiariocba.com.ar" in diario:
        excluir = ['culturales','el-equipo','espacio-patrocinado']
    elif "cba24n.com.ar" in diario:
        excluir = ['deportes','tecnologia','espectaculos','programa','contenido-de-marca','vamos-al-movil']
    else:
        excluir = []

    df = df[~df['seccion'].isin(excluir)]
    #print(f"[INFO] {len(df_sin_filtro)} enlaces obtenidos de {diario}")
    #print(f"[INFO] {len(df)} enlaces con palabras clave")

    #obtiene los titulos y el contenido de los links con palabras claves
    etiqueta = ETIQUIETA_TITULOS[i]
    nota_etiqueta = ETIQUETA_NOTAS[i]
    df["titulo"] = None
    df["contenido"] = None
    #rellena el df
    for idx, row in df.iterrows():   
        titulo, contenido = obtener_titulo_y_contenido(row["link"], etiqueta, nota_etiqueta)
        df.at[idx, "titulo"] = titulo
        df.at[idx, "contenido"] = contenido

    df["contenido"] = df["contenido"].fillna("").str.replace("\n", " ", regex=False)

    if A_PRUEBA_DE_NOTICIAS_LARGAS == "truncar":
        df["contenido"] = df["contenido"].str.slice(0, 32767)

    fecha = date.today().strftime("%Y%m%d")
    filename = f"{fecha}_scraping_{CARPETAS[i]}"
    os.makedirs(CARPETAS[i], exist_ok=True)

    if A_PRUEBA_DE_NOTICIAS_LARGAS == "gencsv":
        df.to_csv(f"{CARPETAS[i]}/{filename}.csv", index=False)
    else:
        df.to_excel(f"{CARPETAS[i]}/{filename}.xlsx", index=False)

    print(f"[OK] Guardado archivo para {CARPETAS[i]} ({len(df)} noticias con palabras clave)")




"""
texto = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés/noticia123"
print(create_tag(texto))
"""

"""""
# URL que queremos analizar
pagina = "https://www.laizquierdadiario.com/"

# Selector de etiquetas: todas las etiquetas <a>
selector = "a"

# Llamamos a la función
enlaces = get_scraping_links(pagina, selector)

# Mostramos los primeros 10 enlaces
print(enlaces[:10])


textos= [
    "El gremio discute paritarias con el gobierno.",
    "Se realizó una asamblea de trabajadores.",
    "Los sindicalistas organizaron una huelga.",
    "el bajo salario de lxs docentes",
    "uta esta en paro",
    "la economia popular esta en auge, ojala no haya ajuste, muy utopico en la Argentina a la que gobierna Milei",
    "pinpon es un munieco muy guapo y de carton",
    "BASTA DE RECORTE SALARIAL!"
]

for t in textos:
    if PALABRAS_CLAVES.search(t):
        print("Coincidencia:", t)
"""
# funcion para obtener los links, se usa en crate_links
# def get_scraping_links():

# para linux fedora instalar:
# /bin/python -m pip install --user pandas
# para windows
#  Pulsa Win + R, escribe cmd y presiona Enter o
#Busca PowerShell y ábrelo.
# python -m pip install --user pandas
# o, si tienes el lanzador de Python (py):
# py -m pip install --user pandas


# para bautiful soup instalar:   pip install requests beautifulsoup4


