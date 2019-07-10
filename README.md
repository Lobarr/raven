
# Raven

Microservice API Gateway as a service

### Setup Prerequisites

- Python 3 - [Install](https://www.python.org/downloads/)
- Node >= 10 - [Install](https://nodejs.org/en/download/current/)
- Docker - [Install](https://docs.docker.com/install/)


### Setup Instructions
* Clone the repo by running the following command
```shell
git clone git@github.ibm.com:Jesuloba-Egunjobi/raven.git && cd raven
```
* Create virtual environment and activate
```shell
python3 -m venv venv
source ./venv/bin/activate
```
* Install api dependencies
```shell
pip install -r requirements.txt
```
* Install client dependencies 
```shell
cd client && npm install
```

If you've made it here, you're all set!

### Running the application

- It as simple as running the following command

```
make start-app
```

- `http://localhost:3000` - frontend
- `http://localhost:3001` - backend

### Example `.env`
```
PORT=3001
ENV=dev
```
