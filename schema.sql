CREATE DATABASE studyspark;
USE studyspark;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(64),
    streak INT DEFAULT 0,
    points INT DEFAULT 0,
    last_study_date DATE
);

CREATE TABLE badges (
    badge_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    badge_name VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE study_reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    time TIME,
    days VARCHAR(50),
    enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE study_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_name VARCHAR(100),
    duration INT,
    start_time DATETIME,
    end_time DATETIME,
    actual_duration FLOAT,
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE study_groups (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(100),
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

CREATE TABLE group_members (
    group_id INT,
    user_id INT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES study_groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE group_resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    resource_name VARCHAR(100),
    resource_link VARCHAR(255),
    FOREIGN KEY (group_id) REFERENCES study_groups(group_id)
);