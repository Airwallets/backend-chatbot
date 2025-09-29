# Mental Health Fastapi server

## Server Structure (Layered architecture)

References: https://fastapi.tiangolo.com/tutorial/bigger-applications/#dependencies

Recommended library: https://fastapi.tiangolo.com/project-generation/ 

main.py: Main entry, to incorporate all routers, and setup on-start and on-shutdown tasks for whole server.

config.py: Load the .env fields and make it public for all endpoints.

dependencies.py: Include common dependencies across all api/routers (eg: authentication).

routers/: Store api endpoints for different group of routers, to separate concerns (eg: users, chatbot, etc.)

db/: Store main code for database schema/model (ORM) and CRUD support. Allow flexibility to change db if needed.

services/: Store Business Logic. In this case, the main chatbot (LLM) and location API handling.

utils/: Common utils function that is suitable across folder (eg: simple string parsing, etc.)


## Development

Make a .env file, following the format of .env.example but with appropriate values.

Generate a new secret key (and keep it a secret) with:

```
openssl rand -hex 32
```

Run the following commands to start the server locally
```
pip install -r requirements.txt

# For everything (including starting db, load data)
docker compose up

# For just the server (Run in the /server from terminal)
fastapi dev ./app/main.py
```
Since some api depends on the Database, to test those, it's recommended to start
 the entire docker compose (as instructed in the main repo README)

## Testing

After each new endpoint, please add a unit test in tests/

This will be run in CI/CD automatically during pull request, or can be run
locally by running in the terminal (inside the docker container, since 
the postgresql db settings is now in os.env):
```shell
./cicd_scripts/docker_test.sh
```

## Chatbot setup

1. Obtain a Mistral API Key (for the LLM) and HuggingFace AccessToken (from Hugging Face, for the tokenizer).
2. Accept the terms for Mistral tokenizer on hugging face: https://huggingface.co/mistralai/Mixtral-8x7B-v0.1 
3. For now: Access pgadmin, query all the uiud, and create embeddings for all of them through api endpoints, if first time set up.
4. The chatbot can only use the tool after all of this.