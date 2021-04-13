CREATE OR REPLACE PROCEDURE filter_movies(
	released_after date default '1000-01-01', 
	released_before date default CURRENT_DATE,
	gen varchar(10) default '',
 	min_rating float default 0,
	max_rating float default 10,
	plat varchar(20) default ''
)
LANGUAGE plpgsql
AS $$
BEGIN
	delete from filtered_movies;
	insert into filtered_movies select distinct movie_genre.movie_id from movie_genre, movie 
	where(
		SUBSTR(movie_genre.genre,1,LENGTH(gen))=gen and movie_genre.movie_id=movie.movie_id and
		movie.release_date >= release_after and movie.release_date <= release_before and 
		movie.rating>=min_rating and movie.rating<=max_rating and 
		SUBSTR(movie.platform,1,LENGTH(plat))=plat
	);
	select * from filtered_movies;
END $$;

--------------------------------------------------------------------

CREATE or REPLACE PROCEDURE search_movies(dob Date)
LANGUAGE plpgsql
AS $$
DECLARE
BEGIN
	if is_adult(dob) then 
		select title from movies where movie.rated='U';
	else 
		select title from movies;
	END if;
END $$;

-------------------------------------------
CREATE OR REPLACE PROCEDURE temp
LANGUAGE plpgsql
AS $$
DECLARE
	company production_company.company_name%type;
begin
	select company_name from production_company into company
end;

----------------------------------------------------

CREATE OR REPLACE PROCEDURE search_movie(dob DATE, title varchar(100))
LANGUAGE plpgsql
AS $$
DECLARE
begin
  if is_adult(dob) then 
	select * from movies where movie where movie.title like '%title%';
  else 
	select * from movies where movie where (movie.title like '%title%' and movie.rated='U'); 
  end if;
end $$;

------------------------------------------------------------

CREATE OR REPLACE PROCEDURE search_celeb(dob DATE, name varchar(100))
LANGUAGE plpgsql
AS $$
DECLARE
begin
  
end $$;