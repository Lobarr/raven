
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
	pytest --cov-report term-missing --cov=api tests

test-watch:
	ptw --ignore ./client --ignore ./venv -v

start-celery:
	celery worker -A api.util.tasks --loglevel=info

start-celery-beat:
	celery beat -A api.util.tasks --loglevel=info

start-celery-watch:
	nodemon -L --watch api/util/tasks.py --exec "make start-celery"
