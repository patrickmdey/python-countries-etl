import pandas as pd
import os
from matplotlib import pyplot as plt

def most_populated_countries(df):
    return df.sort_values(by="population", ascending=False).head(10)["name", "population"]

def calculate_population_by_continent(df):
    return df.groupby("continents").sum()["population"].sort_values(ascending=False).head(10)

def calculate_population_by_language(df):
    df = df[df["languages"].str.contains(",") == False]
    return df.groupby("languages").sum()["population"].sort_values(ascending=False).head(10)

def calculate_currency_by_country(df):
    return df.groupby("currencies").count()["name"].sort_values(ascending=False).head(10)

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
    plt.pie(df.groupby("continents").sum()["population"], labels=df.groupby("continents").sum()["population"].index, autopct='%1.1f%%')
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

    return {
        "most_populated_countries": calculate_population_by_continent(df),
        "most_populated_continents": calculate_population_by_continent(df),
        "most_speaked_languages": calculate_population_by_language(df),
        "most_used_currencies": calculate_currency_by_country(df),
    }
