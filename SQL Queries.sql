-------------------------------------------------------------------
-- Find how many spectators per artist for each day and location --
-------------------------------------------------------------------
with artist_stage as
	(select
		location,
		artist
	from boombastic.stages
	where artist is not null)

select b.artist, a.location,day,count(distinct id) specs
from
(select
	id,
    artist,
    arrived,
    moved,
    start,
    finish,
    a.location,
	case
        when (start > 240 + 160) and (start < 480 +80) then 2
        when (start > 480 + 160) and (start < 720 +80) then 3
        else 1
	end day
from boombastic.attendees a
left join boombastic.stages s on a.location = s.location and ((a.arrived < s.start and a.moved > s.start) or(a.arrived < s.finish and a.moved > s.finish)))b
left join artist_stage a on b.artist = a.artist
group by artist, day
order by specs desc;


-------------------------------------------------------------------
-- See how much time each spectator spend on the different places --
-------------------------------------------------------------------

select
	b.id,
    name,
    location,
    total_stayed
from
(select id, location, sum(stayed) total_stayed
from
	(select *,
		   moved-arrived stayed
	from boombastic.attendees) a
group by id, location) b
left join boombastic.attendee_names n on n.id = b.id
-- where location like "Food Truck%"  /*To find most hungry person*/
-- where location = "WC"			/*To find the bathroom lover*/
-- where location like "%Stage"    /*To find the people who spent most time in stages*/
order by  total_stayed desc


