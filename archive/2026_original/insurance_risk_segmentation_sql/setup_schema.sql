/* PostgreSQL setup for the local portfolio dataset.
   1) Run this file once.
   2) Import data/insurance.csv into raw.insurance with CSV header enabled.
   3) Run insurance_charges_analysis.sql from top to bottom.
*/

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.insurance;

CREATE TABLE raw.insurance (
  age       INTEGER,
  sex       TEXT,
  bmi       NUMERIC,
  children  INTEGER,
  smoker    TEXT,
  region    TEXT,
  charges   NUMERIC
);
