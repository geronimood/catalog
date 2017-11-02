# Project logs_analysis

Python code for database queries and display of the answers.

## Getting Started

You will need the files 'logs_analysis.py' and the 'news' postgresql database.

I used Vagrant 1.9.2 as a virtual machine and Uvuntu 16.04.3 to run the database and the database queries.

### Views definitions

I used the following views to answer the questions:

view top_articles:

create view top_articles as select articles.author, count(articles.author) as views from log, articles where SUBSTRING(log.path, 10) = articles.slug group by articles.author order by views desc limit 3;

view errors_per_day:

create view errors_per_day as select to_char(time, 'YYYY-MM-DD'), count(time) as errors from log where status = '404 NOT FOUND' group by to_char(time, 'YYYY-MM-DD');

view views_per_day:

create view views_per_day as select to_char(time, 'YYYY-MM-DD'), count(time) as views from log group by to_char(time, 'YYYY-MM-DD');

#### Design of the Python code

For each question, I defined a procedure to do the SQL query and fecth the result - see procedures get_popular_articles, get_popular_authors and get_errors.

Then, I added three procedures to display the answers properly in plain text - see procedures display_answer_1, display_answer_2 and display_answer_3.

Finally, the three display procedures get called.

##### Coding style test

I used the PEP8 online check (http://pep8online.com/) to check the Python code for PEP8 style requirements - it passed with zero warnings.

###### Author

* **Christoph Zeller** - *Initial work* -
