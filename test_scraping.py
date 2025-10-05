from scraping import get_scraping_links, extract_section


# test para saber si la funcion get_scraping_links funciona correctamente, pasa el test
def test_get_scraping_links():
    pagina = "https://www.lavoz.com.ar/"
    selector = "a"
    enlaces = get_scraping_links(pagina, selector)
    assert isinstance(enlaces, list), "El resultado debe ser una lista"
    assert len(enlaces) > 0, "La lista de enlaces no debe estar vacía"
    assert all(isinstance(link, str) for link in enlaces), "Todos los enlaces deben ser cadenas de texto"
    # Verificar que los enlaces comienzan con 'http' o 'https'
    assert all(link.startswith("http") for link in enlaces), "Todos los enlaces deben comenzar con 'http' o 'https'"


def test_extract_section():
    url1 = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123"
    url2 = "https://www.laizquierdadiario.com/Nacional/noticia456"
    url3 = "https://www.laizquierdadiario.com/Internacional/noticia789"
    url4 = "https://www.laizquierdadiario.com/noticia000"  # No tiene sección
    url5 = "https://www.otherwebsite.com/Some-Section/news"  # No coincide con el patrón

    print("Holiiiiiiiiiiiiiiiiis")
    print(extract_section(url1))

    assert extract_section(url1) == "provincia-de-buenos-aires", "Error en la extracción de la sección para url1"
    print(extract_section(url1))
    assert extract_section(url2) == "nacional", "Error en la extracción de la sección para url2"
    assert extract_section(url3) == "internacional", "Error en la extracción de la sección para url3"
    assert extract_section(url4) == "NA", "Error en la extracción de la sección para url4"
    print(extract_section(url5))
    assert extract_section(url5) == "NA", "Error en la extracción de la sección para url5"