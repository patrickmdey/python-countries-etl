## Python Challenge Pasante

## Pasos realizados durante la realización del ejercicio

### 1. Análisis del dataset

Realicé un get a la API de paises y analicé cuales eran las keys del dataset y que valores contenían (especificamente, los campos que requiere el challenge)<br>
Por ejemplo, los campos de interes tienen este formato:

```json
"name": {
        "common": "Guinea-Bissau",
        "official": "Republic of Guinea-Bissau",
        "nativeName": {
            "por": {
                "official": "Rep\u00fablica da Guin\u00e9-Bissau",
                "common": "Guin\u00e9-Bissau"
            },
            "pov": {
                "official": "Rep\u00fablica da Guin\u00e9-Bissau",
                "common": "Guin\u00e9-Bissau"
            }
        }
}
```

Por lo que decidi tomar únicamente el valor de "common"

```json
"capital": [
        "Bissau"
]
```

No siempre contiene una única capital por lo que voy a concatenar, separados por una coma, los strings de las capitales.

```json
"currencies": {
        "XOF": {
            "name": "West African CFA franc",
            "symbol": "Fr"
        }
    }
```

Según el país, podían haber mas de una moneda por lo que me quedo con las abreviaciones (key) de las distintas currency. Nuevamente las concateno separadas por una coma

```json
"languages": {
        "por": "Portuguese",
        "pov": "Upper Guinea Creole"
    }

```

Lo mismo con las lenguas, puede haber más de una por pais. Es de mi interes el valor y no la clave. Tabien las concateno separadas por una coma.

```json
"flags": {
        "png": "https://flagcdn.com/w320/gw.png",
        "svg": "https://flagcdn.com/gw.svg",
        "alt": "The flag of Guinea-Bissau features a red vertical band on its hoist side that takes up about two-fifth the width of the field, and two equal horizontal bands of yellow and green adjoining the vertical band. A five-pointed black star is centered in the vertical band."
    }
```

Como me interesa la imagen de la bandera del pais, unicamente me quedo con el png

```json
"population": 1967998
```

Population siempre viene un int por lo que lo tomo como viene

```json

 "continents": [
        "Africa"
    ],
```

Finalmente, continents viene en una lista por lo que tambien puede ocurrir que no solo sea un continente. Las concateno con un string.



### 2. Import de la API a postgreSQL

A modo de guía esta subido el archivo vemo_ddl.sql que contiene el comando para la creación de las tabla en la base de datos para enteder bien cómo almaceno los datos.

En los casos que los valores no son únicos, por ejemplo lenguajes, los almaceno concatenando los distintos strings separandolos con una coma.
Si bien no es la manera convencional de hacerlo (debería crear distintas tablas que representen tanto los modelos como las relaciones), para mantener la simplicidad del ejercicio 

En todos los casos, pasé a minúscula todos los datos recibidos para tener consistencia en todas las entradas
