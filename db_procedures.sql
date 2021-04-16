--------------filter function for movies---------------------
CREATE OR REPLACE FUNCTION filtered_movies(
	released_after date default '1000-01-01', 
	released_before date default CURRENT_DATE,
	gen varchar(10) default '',
 	min_rating float default 0,
	max_rating float default 10,
	plat varchar(20) default ''
)
RETURNS table(
	movie_id varchar
)
language plpgsql
AS $$
declare
begin
  return query 
	select movie_genre.movie_id from movie_genre, movie where(
		movie.release_date >= released_after 
		and movie.release_date<= released_before 
		and movie_genre.movie_id = movie.movie_id 
		and (movie_genre.genre = gen or gen ='') 
		and movie.rating >= min_rating 
		and movie.rating <= max_rating 
		and (contains(movie.platform,plat) or plat = '')
	);
end;
$$;

-----------------search function for movies, ordered by rating-----------------------------
-- Frontend Done

create or replace function search_movies_by_rating (
  dob Date,
  movie_title varchar(100)
) 
	returns table (
		movie_id varchar
	) 
	language plpgsql
as $$
begin
	if is_adult(dob) then 
		return query 
		select movie.movie_id from movie where contains(title, movie_title) order by rating desc;
	else
	return query 
		select movie.movie_id from movie where contains(title, movie_title)
		and rated = 'PG-13' order by rating desc;
	end if;
end;
$$;

select search_movies_by_rating('2000-11-11', 'l');

-----------------search function for movies, ordered by likes-----------------------------

create or replace function search_movies_by_likes (
  dob Date,
  movie_title varchar(100)
) 
	returns table (
		movie_id varchar
	) 
	language plpgsql
as $$
begin
	if is_adult(dob) then 
		return query 
		select movie.movie_id from movie where contains(title, movie_title) order by likes desc;
	else
	return query 
		select movie.movie_id from movie where contains(title, movie_title)
		and rated = 'PG-13' order by likes desc;
	end if;
end;
$$;

select search_movies_by_rating('2000-11-11', 'g');

------------------------search function for celebs------------------------------------
-- Frontend Done


create or replace function search_celebs (
  celeb_name varchar(100)
) 
	returns table (
		person_id varchar
	) 
	language plpgsql
as $$
begin
	return query
		select celebrity.person_id from celebrity where 
		contains(CONCAT(firstname,' ',lastname),celeb_name); 
end;
$$;

------------------displays the movie a celeb has worked on---------------------------------

create or replace function display_celeb_movies (
  celeb_id varchar(100),
  dob DATE
) 
	returns table (
		movie_id varchar
	) 
	language plpgsql
as $$
begin
	return query
		select movie_cast.movie_id from movie_cast where person_id = celeb_id; 
end;
$$;

select display_celeb_movies('14','2000-11-11');

-----------------display movie reviews ----------------------------------

create or replace function display_movie_reviews (
  mov_ID varchar(10)
) 
	returns table (
		review_Id varchar(10),
		posted_On Date,
		contenT varchar(1000),
		up_Votes int,
		userName varchar(20)
	) 
	language plpgsql
as $$
begin
	return query
		select movie_review.review_id, movie_review.posted_on, movie_review.content, movie_review.up_votes, movie_review.username 
		from movie_review where movie_id = mov_ID order by up_votes desc;
end;
$$;

select display_movie_reviews('2');



-------------------display movie details-------------------------------------

create or replace function display_movies (
  mov_id varchar(100)
) 
	returns table (
		movie_id varchar(10),
		title varchar(60),
		production_cost float,
		rating float,
		rated varchar(10),
		release_date Date,
		platform varchar(20),
		likes int,
		runtime int,
		director varchar(10)
	) 
	language plpgsql
as $$
begin
	return query
		select movie.movie_id, movie.title, movie.production_cost, movie.rating,
		movie.rated, movie.release_date, movie.platform, movie.likes, 
		movie.runtime, movie.director from movie
		where movie.movie_id = mov_id;
end;
$$;

select display_movies('12');


-----------------add to wishlist--------------

CREATE OR REPLACE PROCEDURE add_to_wishlist(
		username varchar(20), movie_ID varchar(10)
	)
LANGUAGE plpgsql
AS $$
DECLARE
begin
	insert into wishlist (username, movie_ID);
end $$;

---------------delete from wishlist---------------------
CREATE OR REPLACE PROCEDURE delete_from_wishlist(
		usernam varchar(20), mov_ID varchar(10)
	)
LANGUAGE plpgsql
AS $$
DECLARE
begin
	delete from wishlist where username = usernam and movie_id = mov_id;
end $$;

-----------------display wishlist ------------------------------------

create or replace function display_wishlist (
  		usern varchar(100)
	) 
	returns table (
		movie_id varchar
	) 
	language plpgsql
as $$
begin
	return query
		select wishlist.movie_id from wishlist where wishlist.username = usern; 
end;
$$;

select display_wishlist('ro');

----------------------get genre rating for graph -----------------------------
create or replace function get_genre_rating () 
	returns table (
		gen varchar(100),
		avg_rating float
	) 
	language plpgsql
as $$
declare
	r_movie_genre record;
	r_movie record;
	r_gens record;
	cnt float:=0;
	total int:=0;
begin
	delete from genre_rating;
	for r_gens in select distinct genre from movie_genre loop
		cnt:=0;
		total:=0;
	  for r_movie_genre in select * from movie_genre where genre = r_gens.genre loop
		for r_movie in select * from movie 
		where movie.movie_id = r_movie_genre.movie_id loop
			cnt:=cnt+r_movie.rating;
			total:=total + 1;
		end loop;
	  end loop;
	  insert into genre_rating(genre,rating) values(r_gens.genre,cnt/total);
	end loop;
	return query
		select genre, rating from genre_rating;
end;
$$;

select get_genre_rating();


------------get ott rating and total movies on that platform for graph---------------------

create or replace function get_ott_rating () 
	returns table (
		platform varchar(100),
		avg_rating float,
		total_movies int
	) 
	language plpgsql
as $$
declare
	r_ott record;
	r_movie record;
	cnt float:=0;
	total int:=0;
begin
	delete from ott_rating;
	for r_ott in select * from ott_platform loop 
		cnt:= 0;
		total:= 0;
		for r_movie in select * from movie loop
		  if r_movie.platform = r_ott.platform_name then 
			cnt:= cnt + r_movie.rating;
			total:=total+1;
		  end if;
		end loop;
		insert into ott_rating(platform, rating, total) values(r_ott.platform_name, cnt, total); 
	end loop;
	return query
		select ott_rating.platform, rating, ott_rating.total from ott_rating;
end;
$$;

select get_ott_rating();

-----------------add like to movie or remove like if the movie is already liked----------------
create or replace procedure add_like(mov_id varchar(10), usernam varchar(20)) 
language plpgsql 
as $$
declare 
	r_liked_movies record;
	flag int:=0;
begin
	for r_liked_movies in select * from liked_movies loop
	  if r_liked_movies.movie_id = mov_id and r_liked_movies.username = usernam then
		flag:=1;
		update movie set likes = likes - 1 where movie_id = mov_id;
		delete from liked_movies where movie_id = mov_id and username = usernam;
	  end if;
	end loop;
	if flag = 0 then
		update movie set likes = likes + 1 where movie_id = mov_id;
		insert into liked_movies(movie_id, username) values(mov_id, usernam);
	end if;
end;
$$;

--------add upvote to review or remove upvote if already upvoted ----------------
create or replace procedure add_upvote(rev_id varchar(10), usernam varchar(20))
language plpgsql
as $$ 
declare
	r_upvoted_reviews record;
	flag int:=0;
begin
  for r_upvoted_reviews in select * from upvoted_reviews loop
	  if r_upvoted_reviews.review_id = rev_id and r_upvoted_reviews.username = usernam then
		flag:=1;
		update movie_review set up_votes = up_votes - 1 where review_id = rev_id;
		delete from upvoted_reviews where review_id = rev_id and username = usernam;
	  end if;
	end loop;
	if flag = 0 then
		update movie_review set up_votes = up_votes + 1 where review_id = rev_id;
		insert into upvoted_reviews(review_id, username) values(rev_id, usernam);
	end if;
end;
$$;