CREATE TABLE ticket_flights(
    subs_type varchar( 10 ) NOT NULL,
    CHECK ( subs_type IN ( 'normal', 'silent', 'disabled' ) ),
);