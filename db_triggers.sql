CREATE OR REPLACE TRIGGER movie_delete BEFORE DELETE ON movie
FOR EACH ROW
	delete from movie_cast where movie_cast.movie_id= OLD.movie_id;
	delete from reviews where reviews.movie_id= OLD.movie_id;
	delete from movie_produced_by where movie_produced_by.movie_id = OLD.movie_id;




CREATE OR REPLACE FUNCTION check_abusive() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
	r_abusive record;
	r_db_user record;
	--warn int;
begin
	for r_abusive in select words from abusive_words loop
	  if r_abusive.words in (select unnest(string_to_array(NEW.content,' '))) then
		raise notice '%', r_abusive.words;
		for r_db_user in select * from db_user loop
		  if r_db_user.username = NEW.username then
		  	-- UPDATE 
			-- warn := r_db_user.warnings;	
			UPDATE db_user SET warnings = r_db_user.warnings + 1;
			--raise notice '% warning ', r_db_user.warnings;
		  end if;
		end loop;
		EXIT;
	  end if;
	end loop;
	RETURN NEW;
end;
$$;

CREATE TRIGGER check_abusive_trigger
BEFORE INSERT ON movie_review
FOR EACH ROW 
EXECUTE PROCEDURE check_abusive();

-- do
-- $$
-- declare
-- 	rec record;
-- begin
-- 	DBMS_OUTPUT.PUT_LINE('yes');
-- 	-- for rec in select words from abusive_words
-- 	-- loop
-- 	-- 	if rec.words in (select unnest(string_to_array('fuck me',' '))) then
-- 	-- 		raise notice '%', rec.words;	
-- 	-- 	end if;
-- 	-- 	--raise notice '%', rec.words;	
-- 	-- end loop;
-- end;
-- $$
-- ;


DELETE FROM db_user;
INSERT INTO db_user(email, username, date_of_birth, firstname, lastname, hash,warnings) 
VALUES('ro@gmail.com','ro','2000-01-01','r','p','temphash',0);

INSERT INTO movie(movie_id, title) VALUES('1','Test');


DELETE FROM movie_review;
INSERT INTO movie_review(review_id, posted_on, content, up_votes, movie_id, username)
VALUES ('mr0001','2000-01-01','this fuck movie is good', 0, '1','ro');

INSERT INTO movie_review(review_id, posted_on, content, up_votes, movie_id, username)
VALUES ('mr0002','2000-01-01','this fuck movie is sooo good', 0, '1','ro');