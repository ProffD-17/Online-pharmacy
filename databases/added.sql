-- the SQL I wrote to add on to the db
-- users table
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "email" TEXT NOT NULL UNIQUE,
    "is_active" INTEGER NOT NULL DEFAULT 1,
    "password_hash" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "role_id" INTEGER DEFAULT 1,
    "firstname" TEXT NOT NULL,
    "surname" TEXT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- roles table
CREATE TABLE "roles" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL
);

INSERT INTO roles ("id", "name") VALUES (1, 'patient');
INSERT INTO roles ("id", "name") VALUES (2, 'doctor');


-- prescriptions
CREATE TABLE "prescritions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "patient_id" INTEGER NOT NULL,
    "medicine_id" INTEGER NOT NULL,
    "doctor_id" INTEGER NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES generic(generic_id)
);
