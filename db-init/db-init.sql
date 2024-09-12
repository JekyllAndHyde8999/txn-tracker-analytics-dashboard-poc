CREATE DATABASE txntracker;
\c txntracker;

-- member table contains details of family members
CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    name VARCHAR(60),
    birthday DATE
);

-- credit card table to keep track of credit cards in use
CREATE TABLE creditcard (
    id SERIAL PRIMARY KEY,
    cc_number VARCHAR(20),
    cc_provider VARCHAR(60),
    cc_owner INT,
    CONSTRAINT fk_cc_owner
        FOREIGN KEY (cc_owner) REFERENCES member(id)
)
