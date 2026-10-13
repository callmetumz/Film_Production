-- 03_queries.sql
-- Film Production Database: the ten queries for section 6.0 of the report.
-- Run 01_schema.sql and 02_sample_data.sql first.
-- main.py reads this file and runs every query that starts with a "-- Q" line.

USE film_production_db;

-- Q1 [Simple] Films released from 2015 onwards
-- Lists the company's most recent films, newest first.
SELECT FilmID, Title, ReleaseYear, RuntimeMinutes
FROM FILM
WHERE ReleaseYear >= 2015
ORDER BY ReleaseYear DESC, Title;

-- Q2 [Simple] Crew members with no contact email on file
-- Shows whose contact details still have to be collected.
SELECT CrewMemberID, FirstName, LastName
FROM CREW_MEMBER
WHERE ContactEmail IS NULL
ORDER BY LastName, FirstName;

-- Q3 [Medium] How often each location is used
-- LEFT JOIN with COUNT, MIN and MAX. Locations that were never used show 0 sessions.
SELECT l.LocationName,
       l.City,
       COUNT(s.ScheduleID) AS Sessions,
       MIN(s.FilmingDate)  AS FirstSession,
       MAX(s.FilmingDate)  AS LastSession
FROM LOCATION l
LEFT JOIN PRODUCTION_SCHEDULE s ON s.LocationID = l.LocationID
GROUP BY l.LocationID, l.LocationName, l.City
ORDER BY Sessions DESC, l.LocationName;

-- Q4 [Medium] Films that run longer than the average film
-- Subquery in the WHERE clause.
SELECT Title, ReleaseYear, RuntimeMinutes
FROM FILM
WHERE RuntimeMinutes > (SELECT AVG(RuntimeMinutes) FROM FILM)
ORDER BY RuntimeMinutes DESC;

-- Q5 [Medium] Cast list for films with "Mandela" in the title
-- INNER JOIN with the string functions LIKE and CONCAT_WS.
SELECT f.Title,
       CONCAT_WS(' ', a.FirstName, a.LastName) AS Actor,
       fc.CharacterName
FROM FILM_CAST fc
INNER JOIN FILM f  ON f.FilmID = fc.FilmID
INNER JOIN ACTOR a ON a.ActorID = fc.ActorID
WHERE f.Title LIKE '%Mandela%'
ORDER BY f.Title, Actor;

-- Q6 [Medium] Scheduled filming time per film
-- INNER JOIN with COUNT, SUM and AVG, and the date and time functions
-- TIMESTAMPDIFF and DATE_FORMAT. Only sessions with both times set are counted.
SELECT f.Title,
       COUNT(*) AS TimedSessions,
       ROUND(SUM(TIMESTAMPDIFF(MINUTE, s.StartTime, s.EndTime)) / 60, 1) AS TotalHours,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE, s.StartTime, s.EndTime)) / 60, 1) AS AvgHoursPerSession,
       DATE_FORMAT(MIN(s.FilmingDate), '%d %b %Y') AS FirstDay
FROM PRODUCTION_SCHEDULE s
INNER JOIN FILM f ON f.FilmID = s.FilmID
WHERE s.StartTime IS NOT NULL AND s.EndTime IS NOT NULL
GROUP BY f.FilmID, f.Title
ORDER BY TotalHours DESC
LIMIT 10;

-- Q7 [Complex] Crew members who held three or more roles on the same film
-- Four tables, GROUP BY on two columns and HAVING after aggregation.
SELECT f.Title,
       CONCAT(c.FirstName, ' ', c.LastName) AS CrewMember,
       COUNT(*) AS RolesHeld,
       GROUP_CONCAT(r.RoleName ORDER BY r.RoleName SEPARATOR ', ') AS Roles
FROM FILM_CREW fc
INNER JOIN FILM f        ON f.FilmID = fc.FilmID
INNER JOIN CREW_MEMBER c ON c.CrewMemberID = fc.CrewMemberID
INNER JOIN ROLE r        ON r.RoleID = fc.RoleID
GROUP BY f.FilmID, f.Title, c.CrewMemberID, c.FirstName, c.LastName
HAVING COUNT(*) >= 3
ORDER BY RolesHeld DESC, f.Title;

-- Q8 [Complex] Films that are not ready for production
-- Four tables with LEFT JOINs and COUNT(DISTINCT). HAVING with OR keeps films that
-- have no filming sessions or that have a small crew (fewer than 8 people).
SELECT f.Title,
       f.ReleaseYear,
       COUNT(DISTINCT fc.ActorID)      AS CastSize,
       COUNT(DISTINCT fw.CrewMemberID) AS CrewSize,
       COUNT(DISTINCT s.ScheduleID)    AS Sessions
FROM FILM f
LEFT JOIN FILM_CAST fc          ON fc.FilmID = f.FilmID
LEFT JOIN FILM_CREW fw          ON fw.FilmID = f.FilmID
LEFT JOIN PRODUCTION_SCHEDULE s ON s.FilmID = f.FilmID
GROUP BY f.FilmID, f.Title, f.ReleaseYear
HAVING COUNT(DISTINCT s.ScheduleID) = 0
    OR COUNT(DISTINCT fw.CrewMemberID) < 8
ORDER BY Sessions, CrewSize, f.Title;

-- Q9 [Complex] Actors the company casts most often, and the directors they worked with
-- Five tables. HAVING keeps actors who appear in at least three films.
SELECT CONCAT_WS(' ', a.FirstName, a.LastName) AS Actor,
       COUNT(DISTINCT f.FilmID)        AS Films,
       COUNT(DISTINCT fw.CrewMemberID) AS DifferentDirectors,
       MIN(f.ReleaseYear)              AS FirstFilm,
       MAX(f.ReleaseYear)              AS LatestFilm
FROM ACTOR a
INNER JOIN FILM_CAST fc ON fc.ActorID = a.ActorID
INNER JOIN FILM f       ON f.FilmID = fc.FilmID
INNER JOIN FILM_CREW fw ON fw.FilmID = f.FilmID
INNER JOIN ROLE r       ON r.RoleID = fw.RoleID
WHERE r.RoleName = 'Director'
GROUP BY a.ActorID, a.FirstName, a.LastName
HAVING COUNT(DISTINCT f.FilmID) >= 3
ORDER BY Films DESC, Actor;

-- Q10 [Complex] Busiest locations for crime, action and thriller films
-- Nested subqueries, AND/OR conditions and HAVING. A location is listed when its
-- number of these sessions is above the average number of sessions per location.
SELECT l.LocationName,
       l.City,
       COUNT(*)                 AS Sessions,
       COUNT(DISTINCT s.FilmID) AS Films
FROM PRODUCTION_SCHEDULE s
INNER JOIN LOCATION l ON l.LocationID = s.LocationID
WHERE s.FilmID IN (SELECT g.FilmID
                   FROM FILM_GENRE g
                   WHERE g.GenreName IN ('Crime', 'Action', 'Thriller'))
  AND (l.City IN ('Johannesburg', 'Soweto', 'Cape Town') OR l.City IS NULL)
GROUP BY l.LocationID, l.LocationName, l.City
HAVING COUNT(*) > (SELECT AVG(t.SessionCount)
                   FROM (SELECT COUNT(*) AS SessionCount
                         FROM PRODUCTION_SCHEDULE
                         GROUP BY LocationID) AS t)
ORDER BY Sessions DESC, l.LocationName;
