-- the SQL I wrote to add on to the db

-- users table
CREATE TABLE "users" (
    "user_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "email" TEXT NOT NULL UNIQUE,
    "is_active" INTEGER NOT NULL DEFAULT 1,
    "password_hash" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "role_id" INTEGER DEFAULT 1,
    "firstname" TEXT NOT NULL,
    "lastname" TEXT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- roles table
CREATE TABLE "roles" (
    "role_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL
);

INSERT INTO roles ("role_id", "name") VALUES (1, 'patient');
INSERT INTO roles ("role_id", "name") VALUES (2, 'doctor');
INSERT INTO roles ("role_id", "name") VALUES (3, 'pharmacist');


-- prescriptions
CREATE TABLE "prescriptions" (
    "prescripton_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "patient_id" INTEGER NOT NULL,
    "medicine_id" INTEGER NOT NULL,
    "doctor_id" INTEGER NOT NULL,
    "repeating" INTEGER NOT NULL DEFAULT 0,
    "repeating_start" TEXT,
    "repeating_end" TEXT,
    "repeat_interval" INTEGER,
    "last_ordered" TEXT,
    "times_ordered" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES users(user_id),
    FOREIGN KEY (doctor_id) REFERENCES users(user_id),
    FOREIGN KEY (medicine_id) REFERENCES generic(medicine_id)
);

-- prescripton orders
CREATE TABLE "orders" (
    "order_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "prescription_id" INTEGER NOT NULL,
    "completed" INTEGER NOT NULL,
    "order_date" TEXT NOT NULL,
    "completion_date" TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
);

CREATE TABLE "medicine_requests" (
    "medicine_request_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "patient_id" INTEGER NOT NULL,
    "medicine_id" INTEGER NOT NULL,
    "request_date" TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES users(user_id),
    FOREIGN KEY (medicine_id) REFERENCES generic(medicine_id)
);