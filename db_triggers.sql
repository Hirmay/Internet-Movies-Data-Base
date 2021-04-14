------------------trigger to delete movies------------------ 

CREATE OR REPLACE FUNCTION delete_movies() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
begin
  delete from movie_genre where movie_genre.movie_id = OLD.movie_id;
  delete from movie_produced_by where movie_produced_by.movie_id = OLD.movie_id;
  delete from movie_cast where movie_cast.movie_id = OLD.movie_id;
  delete from movie_review where movie_review.movie_id = OLD.movie_id;
  update ott_platform set total = total -1 where platform_name = OLD.platform;
  --delete from movie where movie.movie_id = OLD.movie_id;
  RETURN OLD;
end;
$$;

CREATE TRIGGER movie_delete 
BEFORE DELETE ON movie
FOR EACH ROW 
EXECUTE PROCEDURE delete_movies();

delete from movie where movie_id = '1';

------------------trigger to delete shows------------------ 

CREATE OR REPLACE FUNCTION delete_shows() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
begin
  delete from show_genre where show_genre.show_id = OLD.show_id;
  delete from show_produced_by where show_produced_by.show_id = OLD.show_id;
  delete from show_cast where show_cast.show_id = OLD.show_id;
  delete from show_review where show_review.show_id = OLD.show_id;
  update ott_platform set total = total -1 where platform_name = OLD.platform;
  --delete from show where show.show_id = OLD.show_id;
  RETURN OLD;
end;
$$;

CREATE TRIGGER show_delete 
BEFORE DELETE ON tv_show
FOR EACH ROW 
EXECUTE PROCEDURE delete_shows();

delete from show where show_id = '1';

---------------------------trigger to delete celebs-----------------------------------

CREATE OR REPLACE FUNCTION delete_celeb() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
begin
  --delete from movie_produced_by where movie_produced_by.person_id = OLD.person_id;
  delete from movie_cast where movie_cast.person_id = OLD.person_id;
  delete from show_cast where show_cast.person_id = OLD.person_id;
  update movie set director = NULL where director = OLD.person_id;
  RETURN OLD;
end;
$$;

CREATE TRIGGER celeb_delete 
BEFORE DELETE ON celebrity
FOR EACH ROW 
EXECUTE PROCEDURE delete_celeb();

--to test the above trigger: 
delete from celebrity where person_id = '20';

-----------if review contains an abusive word trigger will fire-------------

CREATE OR REPLACE FUNCTION check_abusive() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
	r_abusive record;
begin
	for r_abusive in select words from abusive_words loop
	  if r_abusive.words in (select unnest(string_to_array(NEW.content,' '))) then
		-- raise notice '%', r_abusive.words;
		UPDATE db_user SET warning = warning + 1 where 
		username = NEW.username;
		raise exception using message = 'Abusive language detected';
		RETURN OLD;
	  end if;
	end loop;
	RETURN NEW;
end;
$$;

CREATE TRIGGER check_abusive_trigger
BEFORE INSERT ON movie_review
FOR EACH ROW 
EXECUTE PROCEDURE check_abusive();

----------add ott platform if it doesnt exist else update count----------------

CREATE OR REPLACE FUNCTION add_ott() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
	r_ott record;
begin
  if NEW.platform is NULL then
	RETURN NEW;
  end if;
  for r_ott in select * from ott_platform loop
	if r_ott.platform_name = NEW.platform then 
	  	update ott_platform set total = total + 1 where platform_name = NEW.platform;
		RETURN NEW;
	end if;
  end loop;
  insert into ott_platform(platform_name, total) values(NEW.platform, 1);
  RETURN NEW;
end;
$$;

CREATE TRIGGER ott_add 
BEFORE INSERT ON movie
FOR EACH ROW 
EXECUTE PROCEDURE add_ott();

INSERT INTO movie(movie_id, title, platform) VALUES('1111','Test','Netflix');
INSERT INTO movie(movie_id, title) VALUES('1112','Test2');

----------add production house if it doesnt exist else update count----------------

CREATE OR REPLACE FUNCTION add_prod() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
	r_prod record;
begin
  for r_prod in select * from Production_company loop
	if r_prod.company_name = NEW.company_name then 
	  	update Production_company set total_produced = total_produced + 1 
		  where company_name = NEW.company_name;
		RETURN NEW;
	end if;
  end loop;
  insert into Production_company(company_name, total_produced) 
  values(NEW.company_name, 1);
  RETURN NEW;
end;
$$;

CREATE TRIGGER prod_add 
BEFORE INSERT ON movie_produced_by
FOR EACH ROW 
EXECUTE PROCEDURE add_prod();

insert into movie_produced_by(movie_id, company_name) values('1111', 'WingNut Films');

----------delete from movie_produced_by----------------

CREATE OR REPLACE FUNCTION delete_mov_prod() RETURNS TRIGGER 
LANGUAGE plpgsql
as $$
DECLARE
	r_prod record;
begin
  for r_prod in select * from Production_company loop
	if r_prod.company_name = OLD.company_name then 
	  	update Production_company set total_produced = total_produced - 1 
		  where company_name = OLD.company_name;
		RETURN OLD;
	end if;
  end loop;
end;
$$;

CREATE TRIGGER mov_prod_delete 
BEFORE DELETE ON movie_produced_by
FOR EACH ROW 
EXECUTE PROCEDURE delete_mov_prod();


-----------------------------------------------------------
DELETE FROM db_user;
INSERT INTO db_user(email, username, date_of_birth, firstname, lastname, hash,warning) 
VALUES('ro@gmail.com','ro','2000-01-01','r','p','temphash',0);

INSERT INTO movie(movie_id, title, platform) VALUES('1111','Test','Netflix');


DELETE FROM movie_review;
INSERT INTO movie_review(review_id, posted_on, content, up_votes, movie_id, username)
VALUES ('mr0001','2000-01-01','this fuck movie is good', 0, '1','ro');

INSERT INTO movie_review(review_id, posted_on, content, up_votes, movie_id, username)
VALUES ('mr0002','2000-01-01','this movie is sooo good', 0, '2','ro');