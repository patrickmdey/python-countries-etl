import pandas as pd
import os
import xlsxwriter
from matplotlib import pyplot as plt

def calculate_a_by_b(df, a, b, remove_comma_sep=True):
    if remove_comma_sep:
        df = df[df[b].str.contains(",") == False]
    return df.groupby(b).sum()[a].sort_values(ascending=False)[:10].reset_index()

def calculate_currencies_by_country(df):
    df = df[df["currencies"] != ""]
    df = df[df["currencies"].str.contains(",") == False]
    return df.groupby("currencies").count()["name"].sort_values(ascending=False).head(10).reset_index()

def plot_currency_by_country(df):
    df = df[df["currencies"] != ""]
    df = df[df["currencies"].str.contains(",") == False]

    plt.clf()
    x = df.groupby("currencies").count()["name"].sort_values(ascending=False).head(10).index
    y = df.groupby("currencies").count()["name"].sort_values(ascending=False).head(10)
    plt.bar(x, y)
    plt.title("Monedas más usadas en función de la cantidad de países que las usan")
    plt.xlabel("Moneda")
    plt.ylabel("Cantidad de países")
    plt.tight_layout()
    plt.savefig("plots/currency_by_country.png")

def plot_languages_by_country(df):

    df = df[df["languages"] != ""]
    df = df[df["languages"].str.contains(",") == False]

    plt.clf()
    x = df.groupby("languages").count()["name"].sort_values(ascending=False).head(5).index
    y = df.groupby("languages").count()["name"].sort_values(ascending=False).head(5)
    plt.bar(x, y)
    plt.title("5 lenguas más habladas en función de la cantidad de países que las hablan")
    plt.xlabel("Lengua")
    plt.ylabel("Cantidad de países")

    plt.tight_layout()
    
    plt.savefig("plots/languages_by_country.png")

def plot_pie_population_by_continent(df):
    plt.clf()
    df = df[df["continents"] != ""]
    df = df[df["continents"].str.contains(",") == False]
    plt.pie(df.groupby("continents").sum()["population"], 
            labels=df.groupby("continents").sum()["population"].index, autopct='%1.1f%%')
    plt.title("Población por continente")
    plt.tight_layout()
    plt.savefig("plots/population_by_continent.png")


def calculate_metrics(df):
    try:
        os.makedirs("plots", exist_ok=False)
    except FileExistsError:
        pass

    plot_pie_population_by_continent(df)
    plot_currency_by_country(df)
    plot_languages_by_country(df)

    dict_metrics = {
        # "most_populated_countries": most_populated_countries(df),
        "most_populated_continents": calculate_a_by_b(df, "population", "continents"),
        "most_speaked_languages": calculate_a_by_b(df, "population", "languages"),
        "most_used_currencies":  calculate_currencies_by_country(df)
        }
    
    # for value in dict_metrics.values():
    #     print(value.head(1))

    return dict_metrics



def create_excel_file(df, excel_path="countries.xlsx"):
    """Creates the excel file with the table data, calculates
    the metrics, save plots and then saves them to the same excel file
    Args:
        df (pandas.DataFrame): Dataframe with the data to insert
        excel_path (str, optional): Path of the excel file to save the metrics
    """
    workbook = xlsxwriter.Workbook(excel_path)
    
    """Writes the countries dataframe to the excel worksheet 'Paises' """
    worksheet = workbook.add_worksheet("Paises")
    headers = ["Nombre", "Población", "Capital", "Moneda", "Lenguas", "Continente", "Bandera"]
    cells = ["A1", "B1", "C1", "D1", "E1", "F1", "G1"]
    for idx, header in enumerate(headers):
        worksheet.write(cells[idx], header)
    for idx, row in df.iterrows():
        worksheet.write(f"A{idx+2}", row["name"])
        worksheet.write(f"B{idx+2}", row["population"])
        worksheet.write(f"C{idx+2}", row["capitals"])
        worksheet.write(f"D{idx+2}", row["currencies"])
        worksheet.write(f"E{idx+2}", row["languages"])
        worksheet.write(f"F{idx+2}", row["continents"])
        worksheet.write(f"G{idx+2}", row["flag"])

    metrics = calculate_metrics(df)
    worksheet = workbook.add_worksheet("Metrics")

    images = ["plots/population_by_continent.png", "plots/currency_by_country.png", "plots/languages_by_country.png"]

    worksheet.write("A1", "Población por continente")
    worksheet.write("A2", "Continente")
    worksheet.write("B2", "Población")

    for idx, row in metrics["most_populated_continents"].iterrows():
        worksheet.write(f"A{idx+3}", row["continents"])
        worksheet.write(f"B{idx+3}", row["population"])

    worksheet.write("E1", "Lenguas más habladas")
    worksheet.write("E2", "Lengua")
    worksheet.write("F2", "Población")

    for idx, row in metrics["most_speaked_languages"].iterrows():
        worksheet.write(f"E{idx+3}", row["languages"])
        worksheet.write(f"F{idx+3}", row["population"])
    
    worksheet.write("I1", "Monedas más usadas")
    worksheet.write("I2", "Moneda")
    worksheet.write("J2", "Cantidad de países")

    for idx, row in metrics["most_used_currencies"].iterrows():
        worksheet.write(f"I{idx+3}", row["currencies"])
        worksheet.write(f"J{idx+3}", row["name"])

    scale = {"x_scale": 0.3, "y_scale": 0.3}
    worksheet.insert_image("A15", images[0], scale)
    worksheet.insert_image("E15", images[1], scale)
    worksheet.insert_image("I15", images[2], scale)

    workbook.close()

    