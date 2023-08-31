# Countries ETL Process with emails

Objetivo: Desarrollar una herramienta ETL (Extract, Transform, Load) para mostrar información sobre
los países del mundo.

1. Configurar el entorno necesario para un proyecto en Python.
2. Usar SQLAlchemy, o cualquier ORM de tu preferencia, para establecer una interacción con una
   base de datos relacional.
3. Crear una base de datos destinada a almacenar la información de los países. Se debe definir un
   modelo de datos que incluya los siguientes campos: Nombre, Capital, Moneda, Continente,
   Lenguaje, Población y Bandera.
4. Recopilar datos sobre los países de la API disponible en https://restcountries.com/v3.1/all.
5. Realizar la transformación necesaria de los datos obtenidos para producir un archivo de salida en
   formato Excel (.xlsx) con las siguientes características:
   A. Una hoja llamada "Paises" que liste todos los países con los campos mencionados.
   B. Una hoja llamada "Metricas" con gráficos y/o KPIs que consideres relevantes.

6. Cargar la lista de países en la base de datos creada y configurar un sistema que envíe un correo
   electrónico diario con el archivo Excel adjunto.

## Configuración y uso

1.  Asegurarse de tener instalado en el ambiente una base de datos `postgres (PostgreSQL) 14.8` o superior con una base de datos creada (utilizar el mismo nombre en la configuración del `.env` que se menciona mas adelante)
2.  Asegurarse de tener instalado `Python 3.11.4` o superior junto a la versión de pip correspondiente.<br>Es recomendable generar un _virtual environment_ para aislar las dependencias del proyecto. Esto puede realizarse ejecutando el siguiente comando

    ```sh
        $> python3 -m venv .venv
    ```

    Luego, podemos acceder al mismo ejecutando el comando

    ```sh
        $> source .venv/bin/activate
    ```

3.  Ahora descargaremos las dependencias necearias para el correcto funcionamiento del proyecto. Esto lo hacemos ejecutando

    ```sh
        $> pip3 install -r requirements.txt
    ```

4.  Para reducir al máximo la modificación del código, el proyecto necesita de dos archivos de configuración

    El primero es el que cuenta con las variables de entorno: `.env`. Este archivo tambien es importante ya que contiene las credenciales para enviar los mails y de estar harcodeados en el codigo sería inseguro.<br> A modo de ejemplo:

    ```
    POSTGRESQL_USR=postgres
    POSTGRESQL_PASS=postgres
    POSTGRESQL_URL=postgresql://postgres:postgres@127.0.0.1:5432/challenge_db
    API_URL=https://restcountries.com/v3.1/all
    EMAIL_SERVER=smtp.gmail.com
    EMAIL_USR=usr@gmail.com
    EMAIL_PASS=1234
    ```

    El segundo archivo de configuración contiene la información necesaria para enviar el mail. Este debe llamarse `email_config.json` y tiene el siguiente formato:

    ```json
    {
    	"recipient": ["recip1@gmail.com", "recip2@gmail.com"],
    	"subject": "metricas diarias",
    	"body": "Metricas de los paises"
    }
    ```

5.  Una vez tenemos todo configurado, podemos ejectuar el proceso ETL que se conecta a la base de datos utilizando las variables de entorno, hace el request a la API, transforma los datos como los necesitamos y los guarda en la base de datos. Finalmente calcula las métricas y genera el archivo excel. Esto lo hacemos ejecutando el siguiente comando
    ```bash
        $> python3 run_etl.py
    ```
6.  Por último, como queremos que se envie un mail con el archivo de métricas todos los dias, debemos configurar el entorno para que lo haga. Decidi utilizar la funcionalidad de linux `crontab` que permite ejecutar un comando todas las veces que se cumpla una condición. En este caso que se mande el mail todos los dias a las 8am. Esto puede hacerse ejecutando los siguientes comandos
    ```bash
        $> chmod +x add_crontab_config.sh
        $> ./add_crontab_config.sh
    ```

## Análisis del dataset

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

## Import de la API a postgreSQL

A modo de guía esta subido el archivo vemo_ddl.sql que contiene el comando para la creación de las tabla en la base de datos para enteder bien cómo almaceno los datos.

En los casos que los valores no son únicos, por ejemplo lenguajes, los almaceno concatenando los distintos strings separandolos con una coma.
Si bien no es la manera convencional de hacerlo (debería crear distintas tablas que representen tanto los modelos como las relaciones), para mantener la simplicidad del ejercicio

En todos los casos, pasé a minúscula todos los datos recibidos para tener consistencia en todas las entradas
