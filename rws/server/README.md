Dependencies:

python

pandas
  -to manipulate data
  
plotly
  -display data

-------------------------------------------------------

DRIVER

-collects data
-ocassionally summarize and write data
-start server

Three different storages:
1. In memory (python data structure)
2. On disk (csv)
3. Cloud (dropbox)

Timers:
1. write to disk
2. write to dropbox
3. calculate stats


-------------------------------------------------------

SERVER

-API between Graph and website

-------------------------------------------------------

Graphs:
-look at in memory data
-merge with historical data when necessary 
-implement different features with plotly

-------------------------------------------------------

Website:
-Pull up different graphs on the interface
-Change graph type and data
-Add more than one datatype with time on X axis

-------------------------------------------------------