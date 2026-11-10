-- all the sql I added to the database
-- users table
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "email" TEXT NOT NULL UNIQUE,
    "is_active" INTEGER NOT NULL,
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

INSERT INTO roles ("id", "name") VALUES (1, 'user');
INSERT INTO roles ("id", "name") VALUES (2, 'doctor');