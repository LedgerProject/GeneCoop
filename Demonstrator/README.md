# The Demonstrator

The demostrator is written in Python (we use v3.8) and is currently based on Django.

## Installation
If you want to run the code on your premises, after cloning this repository perform the following actions:

1. Install Python 3.8
2. (Optional) Install a virtual environment manager such as miniconda or virtualenv.
3. (Optional) create a virtual environment and activate it. Ex `conda create -n Demonstrator python==3.8` and then `conda activate Demonstrator`
4. Install requirements: `pip install -r pip_requirements.txt`
5. Change directory to `Genecoop/Demonstrator/ResearchInterface`
6. Run the webserver that serves the apps: `./startDevelopment.sh` for development or `startProduction.sh` for production (runs on Linux with screen)

You should see a message similar to the following:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 18, 2020 - 00:02:12
Django version 3.1.4, using settings 'labspace.settingsD'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Operations
If these step were successful, you can access the Researcher interface at `http://127.0.0.1:8000/request` and the consent interface at `http://127.0.0.1:8000/consent`

With the Researcher interface you can define a consent request; the first page also shows a list of existing requests (the db has been pre-populated to have some instances to show).

After generating a request, you can generate a token. Ideally this token is sent by the researcher to the user, 
who is supposed to enter the token on the page at `http://127.0.0.1:8000/consent`.

When they do so, a consent is generated which is the mapping of the researcher request using a vocabulary the user is supposed to understand (still in development).

The user can then reply to each single question in the consent and sign it. 

For a complete picture of the planned flow that we want to implement
have a look at the [technical description](https://github.com/LedgerProject/GeneCoop/blob/master/Demonstrator/Documentation/Technical_Design/demonstrator_tech_design.md).
