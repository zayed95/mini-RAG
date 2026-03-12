# Mini-RAG

A minimal RAG application to mimic the development of real life production level AI systems.

## Requirements
* Python 3.8 or later
  
### Setup
1. Download and install MiniConda https://www.anaconda.com/docs/getting-started/miniconda/main#quick-command-line-install
2. Create new environment using the following command
```bash
$ conda create -n mini-rag
```
3. Activate the virtual environment using the following command
```bash
$ conda activate mini-rag
```
5. Install required packages using the following command
```bash
$ pip install -r requirements.txt
```

#### Set up environmental variables 
```bash
$ cp .env.example .env
```

#### Run FastAPI server
```bash
$ uvicorn main:app --reload
```

#### Run Docker Compose services
```bash
$ docker compose up -d
$ cp .env.example .env
```
- Update user credentials in the `.env` file.
