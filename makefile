
init:
	pip install -r requirements.txt

start-server:
	nodemon -L app.py

start-client:
	cd client && npm start

start-app:
	@make clean-celery
	docker-compose kill && docker-compose up --build --remove-orphans

freeze: 
	pip freeze > requirements.txt

test:
	python -m pytest --cov-report term-missing --cov=api api

test-watch:
	nodemon --watch api -e py --exec "python -m pytest api"

start-celery:
	celery worker -A api.util.tasks --loglevel=info

start-celery-beat:
	celery beat -A api.util.tasks --loglevel=info

start-celery-watch:
	nodemon -L --watch api/util/tasks.py --exec "make start-celery"

clean-celery:
	rm -f celerybeat*

lint-fix:
	autopep8 --in-place --aggressive --aggressive api/**/*.py

test-app:
	make test && cd client && npm run test
