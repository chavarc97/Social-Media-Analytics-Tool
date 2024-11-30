# Social-Media-Analytics-Tool

Start by setting the python virtual env

> python3 -m venv env && source env/bin/activate && pip install -r requirements.txt

Run Mongo

> docker run --name mongodb -d -p 27017:27017 mongo
Run APIS server:
Run main file
> python app.py
API available in
http://localhost:5000


Run Cassandra

> docker run --name node01 -p 9042:9042 -d cassandra

Run DGraph

> docker run --name dgraph -d -p 8080:8080 -p 9080:9080 dgraph/standalone

Run the server
