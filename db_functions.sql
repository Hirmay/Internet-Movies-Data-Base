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
	raise exception using message = 'This is an error';
END;
$$;

CALL error_gen();

------------------------------


CREATE OR REPLACE FUNCTION contains(parent varchar(100), child varchar(100))
RETURNS BOOLEAN
LANGUAGE plpgsql
AS
$$
DECLARE
cnt int;
len int := LENGTH(child);
parentLen int := LENGTH(parent);
begin
cnt:=1;
while cnt + len <= parentLen+1 loop
--raise notice '%,  %', SUBSTR(parent,cnt,len), child;
  if LOWER(SUBSTR(parent,cnt,len)) = LOWER(child) then
return true;
  end if;
  cnt := cnt + 1;
end loop;
--raise notice 'child: %', child;
return false;
end;
$$;