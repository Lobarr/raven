
init:
	pip install -r requirements.txt

start-server:
	nodemon -L app.py

start-client:
	cd client && npm start

start-app:
	docker-compose kill && docker-compose up --build --remove-orphans

freeze: 
	pip freeze > requirements.txt

test:
	pytest tests

test-watch:
	ptw --ignore ./client --ignore ./venv -v
