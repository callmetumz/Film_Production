-- 01_schema.sql
-- Film Production Database: creates the database and its nine tables.
-- CSC312 Practical Assignment 2. Needs MySQL 8.0.16 or later (CHECK constraints).
-- Run this file first, then 02_sample_data.sql.

DROP DATABASE IF EXISTS film_production_db;
CREATE DATABASE film_production_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE film_production_db;

-- ---------------------------------------------------------------------------
-- Strong entities
-- ---------------------------------------------------------------------------

CREATE TABLE FILM (
    FilmID          INT           NOT NULL AUTO_INCREMENT,
    Title           VARCHAR(200)  NOT NULL,
    ReleaseYear     SMALLINT      NULL,
    RuntimeMinutes  SMALLINT      NULL,
    CONSTRAINT pk_film PRIMARY KEY (FilmID),
    CONSTRAINT chk_film_runtime CHECK (RuntimeMinutes > 0)
);

CREATE TABLE ACTOR (
    ActorID     INT           NOT NULL AUTO_INCREMENT,
    FirstName   VARCHAR(100)  NOT NULL,
    LastName    VARCHAR(100)  NULL,       -- NULL when credited under one name
    BirthYear   SMALLINT      NULL,
    CONSTRAINT pk_actor PRIMARY KEY (ActorID)
);

CREATE TABLE CREW_MEMBER (
    CrewMemberID  INT           NOT NULL AUTO_INCREMENT,
    FirstName     VARCHAR(100)  NOT NULL,
    LastName      VARCHAR(100)  NOT NULL,
    ContactEmail  VARCHAR(254)  NULL,
    CONSTRAINT pk_crew_member PRIMARY KEY (CrewMemberID)
);

CREATE TABLE ROLE (
    RoleID    INT           NOT NULL AUTO_INCREMENT,
    RoleName  VARCHAR(100)  NOT NULL,
    CONSTRAINT pk_role PRIMARY KEY (RoleID),
    CONSTRAINT uq_role_name UNIQUE (RoleName)
);

CREATE TABLE LOCATION (
    LocationID    INT           NOT NULL AUTO_INCREMENT,
    LocationName  VARCHAR(150)  NOT NULL,
    Address       VARCHAR(255)  NULL,
    City          VARCHAR(100)  NULL,
    CONSTRAINT pk_location PRIMARY KEY (LocationID)
);

-- ---------------------------------------------------------------------------
-- Weak entities (primary key includes the parent key: strong relationships)
-- ---------------------------------------------------------------------------

-- Multivalued attribute "genre" of FILM
CREATE TABLE FILM_GENRE (
    FilmID     INT          NOT NULL,
    GenreName  VARCHAR(30)  NOT NULL,
    CONSTRAINT pk_film_genre PRIMARY KEY (FilmID, GenreName),
    CONSTRAINT fk_film_genre_film FOREIGN KEY (FilmID)
        REFERENCES FILM (FilmID) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bridge entity for the many-to-many relationship between FILM and ACTOR
CREATE TABLE FILM_CAST (
    FilmID         INT           NOT NULL,
    ActorID        INT           NOT NULL,
    CharacterName  VARCHAR(150)  NOT NULL,
    CONSTRAINT pk_film_cast PRIMARY KEY (FilmID, ActorID),
    CONSTRAINT fk_film_cast_film FOREIGN KEY (FilmID)
        REFERENCES FILM (FilmID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_film_cast_actor FOREIGN KEY (ActorID)
        REFERENCES ACTOR (ActorID) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Bridge entity for the many-to-many relationship between FILM and CREW_MEMBER,
-- with the ROLE performed
CREATE TABLE FILM_CREW (
    FilmID        INT  NOT NULL,
    CrewMemberID  INT  NOT NULL,
    RoleID        INT  NOT NULL,
    CONSTRAINT pk_film_crew PRIMARY KEY (FilmID, CrewMemberID, RoleID),
    CONSTRAINT fk_film_crew_film FOREIGN KEY (FilmID)
        REFERENCES FILM (FilmID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_film_crew_member FOREIGN KEY (CrewMemberID)
        REFERENCES CREW_MEMBER (CrewMemberID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_film_crew_role FOREIGN KEY (RoleID)
        REFERENCES ROLE (RoleID) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------------
-- Filming sessions (own primary key: weak relationships to FILM and LOCATION)
-- ---------------------------------------------------------------------------

CREATE TABLE PRODUCTION_SCHEDULE (
    ScheduleID   INT   NOT NULL AUTO_INCREMENT,
    FilmID       INT   NOT NULL,
    LocationID   INT   NOT NULL,
    FilmingDate  DATE  NOT NULL,
    StartTime    TIME  NULL,
    EndTime      TIME  NULL,
    CONSTRAINT pk_production_schedule PRIMARY KEY (ScheduleID),
    CONSTRAINT fk_schedule_film FOREIGN KEY (FilmID)
        REFERENCES FILM (FilmID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_schedule_location FOREIGN KEY (LocationID)
        REFERENCES LOCATION (LocationID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_schedule_times CHECK (EndTime > StartTime)
);
