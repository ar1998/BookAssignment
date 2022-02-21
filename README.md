# Book inventory


## Run Without Contanier

### [Setup Commands]

**pip install -r requirements.txt** _ <! ---install the dependencies-->_

### [Running Server]

**uvicorn main:app --reload** _<! --- starts the server -->_

# Run in Docker Container

### [Setup]
**uncomment sections in Dockerfile(Line:15) and main.py(line:186)**

### [Build Image]
**docker build -t books .**

### [Run container]
**docker run -p 8000:8000 -ti books**