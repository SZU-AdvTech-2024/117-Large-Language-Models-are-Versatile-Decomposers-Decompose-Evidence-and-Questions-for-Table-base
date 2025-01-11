ResolvePackageNotFound:
  - libcxx
  - readline=8.1.2
  - ncurses=6.3
  - libffi=3.3





```bash
Judge whether a statement is true or false based on the given table.


/*
table caption : 2008 sidecarcross world championship.
col : position | driver / passenger | equipment | bike no | points
row 1 : 1 | dani毛l willemsen / reto gr眉tter | ktm - ayr | 1 | 531
row 2 : 2 | kristers sergis / kaspars stupelis | ktm - ayr | 3 | 434
row 3 : 3 | jan hendrickx / tim smeuninx | zabel - vmc | 2 | 421
row 4 : 4 | joris hendrickx / kaspars liepins | zabel - vmc | 8 | 394
row 5 : 5 | marco happich / meinrad schelbert | zabel - mefo | 7 | 317
row 6 : 6 | maris rupeiks / haralds kurpnieks | zabel - mefo | 6 | 297
row 7 : 7 | vaclav rozehnal / marek rozehnal | zabel - vmc | 5 | 273
row 8 : 8 | janis daiders / lauris daiders | zabel - vmc | 10 | 269
row 9 : 9 | nicky pulinx / ondrej cermak | zabel - vmc | 14 | 244
*/
statement : bike number 3 is the only one to use equipment ktm - ayr.
in the table:
there are 2 bike number use equipment ktm - ayr.
bike number 3 use equipment ktm - ayr.
the anwser is : False


/*
table caption : 1957 vfl season.
col : home team | home team score | away team | away team score | venue | crowd | date
row 1 : footscray | 6.6 (42) | north melbourne | 8.13 (61) | western oval | 13325 | 10 august 1957
row 2 : essendon | 10.15 (75) | south melbourne | 7.13 (55) | windy hill | 16000 | 10 august 1957
row 3 : st kilda | 1.5 (11) | melbourne | 6.13 (49) | junction oval | 17100 | 10 august 1957
row 4 : hawthorn | 14.19 (103) | geelong | 8.7 (55) | brunswick street oval | 12000 | 10 august 1957
row 5 : fitzroy | 8.14 (62) | collingwood | 8.13 (61) | glenferrie oval | 22000 | 10 august 1957
row 6 : richmond | 11.9 (75) | carlton | 7.9 (51) | punt road oval | 22000 | 10 august 1957
*/
statement : collingwood was the away team playing at the brunswick street oval venue.
in the table:
collingwood was the away team playing at the glenferrie oval.
the anwser is : False


/*
table caption : co - operative commonwealth federation (ontario section).
col : year of election | candidates elected | of seats available | of votes | % of popular vote
row 1 : 1934 | 1 | 90 | na | 7.0%
row 2 : 1937 | 0 | 90 | na | 5.6%
row 3 : 1943 | 34 | 90 | na | 31.7%
row 4 : 1945 | 8 | 90 | na | 22.4%
row 5 : 1948 | 21 | 90 | na | 27.0%
row 6 : 1951 | 2 | 90 | na | 19.1%
row 7 : 1955 | 3 | 98 | na | 16.5%
row 8 : 1959 | 5 | 98 | na | 16.7%
*/
statement : the 1937 election had a % of popular vote that was 1.4% lower than that of the 1959 election.
in the table:
the % of popular vote of the 1937 election is 5.6%.
the % of popular vote of the 1959 election is 16.7%.
the anwser is : False


/*
table caption : 2003 pga championship.
col : place | player | country | score | to par
row 1 : 1 | shaun micheel | united states | 69 + 68 = 137 | - 3
row 2 : t2 | billy andrade | united states | 67 + 72 = 139 | - 1
row 3 : t2 | mike weir | canada | 68 + 71 = 139 | - 1
row 4 : 4 | rod pampling | australia | 66 + 74 = 140 | e
row 5 : t5 | chad campbell | united states | 69 + 72 = 141 | + 1
row 6 : t5 | jos茅 c贸ceres | argentina | 73 + 68 = 141 | + 1
row 7 : t5 | ernie els | south africa | 71 + 70 = 141 | + 1
row 8 : t5 | tim herron | united states | 69 + 72 = 141 | + 1
row 9 : t5 | phil mickelson | united states | 66 + 75 = 141 | + 1
row 10 : t6 | tom pernice , jr | united states | 70 + 72 = 142 | + 2
row 11 : t7 | adam scott | australia | 72 + 71 = 143 | + 3
*/
statement : phil mickelson was one of five players with + 1 to par , all of which had placed t5.
in the table:
there are 5 players with + 1 to par.
phil mickelson was 1 players with + 1 to par.
all of them placed t5.
the anwser is : True


Judge whether a statement is true or false based on the given table.




/*
table caption : 1947 kentucky wildcats football team
col : game | wildcats points | opponents
row 1 : 2 | 20 | 0
row 2 : 3 | 20 | 7
row 3 : 4 | 26 | 0
row 4 : 5 | 14 | 0
row 5 : 9 | 36 | 0
*/
statement : the wildcats kept the opposing team scoreless in four games
in the table:
the wildcats kept the opposing team scoreless in 4 games.



- - - - - - - - - - ->>
True
```

