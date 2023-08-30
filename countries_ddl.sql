-- this would be the DDL for the database. I used it as a reference for the sqlalchemy models
-- This has really no use
CREATE DATABASE challenge_db;

CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    flag VARCHAR(255) NOT NULL UNIQUE,
    population INT NOT NULL,
    currencies VARCHAR(255) NOT NULL,
    languages VARCHAR(255) NOT NULL,
    continents VARCHAR(255) NOT NULL,
    capitals VARCHAR(255) NOT NULL
);