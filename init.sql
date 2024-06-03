CREATE TABLE chatbot_work_scheduler (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    user_name VARCHAR(30),
    working_time INTEGER[],
    performance INTEGER
);

CREATE TABLE chatbot_material (
    id SERIAL PRIMARY KEY,
    material_name VARCHAR(30),
    expired TIMESTAMP,
    quantity INTEGER
);

CREATE TABLE chatbot_machine (
    id SERIAL PRIMARY KEY,
    machine_name VARCHAR(30),
    expired TIMESTAMP,
    predicted TIMESTAMP,
    performance INTEGER,
    type VARCHAR(30)
);
