-- Creates database TutorH_dev_db
CREATE DATABASE IF NOT EXISTS TutorH_dev_db;
USE TutorH_dev_db;
CREATE USER IF NOT EXISTS 'TutorH_dev'@'localhost';
SET PASSWORD FOR 'TutorH_dev'@'localhost' = 'TutorH_dev_pwd';
GRANT ALL PRIVILEGES ON TutorH_dev_db.* TO 'TutorH_dev'@'localhost';
GRANT SELECT ON performance_schema.* TO 'TutorH_dev'@'localhost';
