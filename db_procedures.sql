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

------------------------------------------------------

CREATE OR REPLACE PROCEDURE search_movie(dob DATE, movie_title varchar(100))
LANGUAGE plpgsql
AS $$
DECLARE
	r_movie record;
	cnt int;
	len int := LENGTH(movie_title);
	movie_len int;
begin
  if is_adult(dob) then 
	for r_movie in select * from movie loop
		cnt := 1;
		movie_len := LENGTH(r_movie.title);
		while cnt + len <= movie_len loop
		  if LOWER(SUBSTR(r_movie.title,cnt,len)) = LOWER(movie_title) then
			raise notice '%', r_movie.title;
		  end if;
		  cnt := cnt + 1;
		end loop;
	end loop;
  else
	for r_movie in select * from movie where (movie.rated = 'PG-13') loop
		cnt := 1;
		movie_len := LENGTH(r_movie.title);
		while cnt + len <= movie_len loop
		  if LOWER(SUBSTR(r_movie.title,cnt,len)) = LOWER(movie_title) then
			raise notice '%', r_movie.title;
		  end if;
		  cnt := cnt + 1;
		end loop;
	end loop;
  end if;
end 
$$;

CALL search_movie('2000-11-11','Lord');

------------------------------------------------------------

CREATE OR REPLACE PROCEDURE search_celeb(celeb_name varchar(100))
LANGUAGE plpgsql
AS $$
DECLARE
	compare varchar(100);
	r_celeb record;
	len int := LENGTH(celeb_name);
	compLen int;
	cnt int;
begin
	for r_celeb in select * from celebrity loop
	  compare := CONCAT(r_celeb.firstname,' ', r_celeb.lastname);
	  compLen := LENGTH(compare);
	  cnt:=1;
	  while cnt + len <= compLen loop
		if LOWER(SUBSTR(compare,cnt,len)) = LOWER(celeb_name) then
			raise notice '%',compare;
		end if;
		cnt:= cnt+1;
	  end loop;
	end loop;
end $$;

CALL search_celeb('Tim');

---------------------------------------------------
CREATE OR REPLACE PROCEDURE celeb_movies(celeb_id varchar(100), dob DATE)
LANGUAGE plpgsql
AS $$
DECLARE
	r_movie record;
begin
	for r_movie in select * from movie, movie_cast where 
	(movie.movie_id = movie_cast.movie_id and movie_cast.person_id = celeb_id) loop
	  if r_movie.rated = 'R' then 
		if is_adult(dob) then 
		  raise notice '%', r_movie.title;
		end if;
	  else 
	  	raise notice '%', r_movie.title;
	  end if;
	end loop;
end $$;

CALL celeb_movies('2','2000-11-11');

--------------------------------------------------------
