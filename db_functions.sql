CREATE or REPLACE FUNCTION is_adult(dob Date) 
returns boolean 
language plpgsql
as
$$
DECLARE
BEGIN
	if date_part('year',AGE(CURRENT_DATE,dob))>=18 then
		return TRUE;
	else
		return FALSE;
	END if;
END;
$$;

----------------------------------------------------

CREATE or REPLACE PROCEDURE error_gen()
language plpgsql
as
$$
DECLARE
BEGIN
	raise exception using message = 'Tirth madarchod';
END;
$$;

CALL error_gen();

