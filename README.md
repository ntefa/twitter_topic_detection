# twitter_topic_detection
Python scripts performing emerging topic detection in Twitter.

## Summary
This bunch of scripts can be used to find hot topics, defined as topics extensively treated in a considered time window but rarely in the past. The procedure used to achieve this goal, is well described in the paper "Emerging  topic  detection  on  twitter  based  on temporal and social terms evaluation" by Cataldi et al, with the only difference the lack of usage of the PageRank algorithm, due to the complexity of acquisition and computing of the whole Twitter graph. Instead, a simpler follower-followee rule has been used in order to evaluate the authority of the various tweet authors.

The procedure, can be summarized in the following steps:

0 - Data retrieval via Twitter API streaming;

1 - Data preprocessing;

2 - Compute terms' energy within time intervals;

3 - Emerging terms selection by ranking their energy values;

4 - Create a graph which links the extracted emerging terms to their relative co-occurrent terms;

5 - Retrieve topics from graph applying Depth First Search(DFS).

A more accurate description of the functions implemented, their own objective, inputs/outputs, as well as results and math behind, can be found in the "An_Intelligent_Topic_tracking_System_in_Python__The___Covid_19___case.pdf" file.
