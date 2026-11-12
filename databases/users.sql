-- the SQL I wrote to add on to the db
-- users table
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "email" TEXT NOT NULL UNIQUE,
    "is_active" INTEGER NOT NULL DEFAULT 1,
    "password_hash" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "role_id" INTEGER DEFAULT 1,
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
--CREATE TABLE "prescritions" (
--    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
