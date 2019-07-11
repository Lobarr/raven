
init:
	pip install -r requirements.txt

start-server:
	nodemon app.py

start-client:
	cd client && npm start

start-app:
	docker-compose kill && docker-compose up --build --remove-orphans

freeze: 
	pip freeze > requirements.txt

test:
	python -m pytest 
