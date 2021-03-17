# The Demonstrator

The demostrator is written in Python (we use v3.8) and is based on Django.

## Installation

### Server
If you want to run the code on your premises, after cloning this repository perform the following actions:

1. Install Python 3.8
2. (Optional) Install a virtual environment manager such as miniconda or virtualenv.
3. (Optional) create a virtual environment and activate it. Ex `conda create -n Demonstrator python==3.8` and then `conda activate Demonstrator`
4. Install requirements: `pip install -r pip_requirements.txt`
5. Change directory to `Genecoop/Demonstrator/ResearchInterface`
6. Fill in your self-created credentials in `researcher.json` and rename it to `.researcher.json`
7. Fill in your self-created credentials in `superuser.json` and rename it to `.superuser.json`
8. if you want to run a production version of Django create the file `.secret_key` with a suitable Django secrete key
9. Run the webserver that serves the apps: `./startDevelopment.sh` for development or `startProduction.sh` for production (runs on Linux with screen)

You should see some output ending with something similar to the following (for `startDevelopment.sh`):
```
INFO 2021-03-17 18:08:11,377 Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 17, 2021 - 18:08:11
Django version 3.1.5, using settings 'labspace.settingsD'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Build Web extensions
(not needed to run the application, only if you want to modify the web extensions)

There are two web extensions, one for the researcher and one for the DNA donor (user). The instructions are the same for both, here we show the instructions for the researcher one.

In order to build a development version of the researcher web extension, and save it to your Downloads directory, do the following:
```
$ cd researcher_webext # cd user_webext for the user
$ npm install
$ cd zenpage
$ ./prepair_bundle.sh
$ cd ..
$ web-ext build --a ~/Downloads -n researcher_webext.zip 
```

To install and configure the researcher web extension in Firefox:
* Browse to: about:debugging
* Click "This Firefox" -> "Load temporary add-on"
* Select the researcher_webext.zip file in your Downloads directory
* Browse to about:addons
* Click on "..." -> preferences for the "genecoop_research" addon (genecoop_donor for the user one)
* Fill in the username, public key, and private key with the values you wrote in `ResearchInterface/.researcher.json`, click save. (for the user you need to generate your own keypair, username is not used at the moment).
* To test if the configuration is correct, navigate to locahost:8000/request, and click on the extension; you should see two (or more) buttons: 'login' and 'sign'.

To build a signed, downloadable self hosted version of the webextension:
```
web-ext sign --api-key=<KEY> --api-secret=<SECRET> --channel=unlisted
```
then copy the xpi file to the django static directory (`./ResearchInterface/researcher_req/static/researcher_req/` for the researcher and `./ResearchInterface/genecoop/static/genecoop/` for the user)

## Operations

If these step were successful, you can access the Researcher interface at `http://127.0.0.1:8000/request` and the consent interface at `http://127.0.0.1:8000/consent`.

Both pages will show a login window, and the instructions to log in using the web extension.
In the Researcher interface the first page shows a list of existing requests if there are any, divided in pending (waiting for a reply) and answered.
In order to create a new consent request you need to click on Create Request in the menu.

After generating one or more requests and signing them with the web extension, you can send the user the token corrisponding to the request (externally to this application).
The recipient of the token can enter it on the page at `http://127.0.0.1:8000/consent`.

The user can then reply to each single question in the consent and sign it. Once at least a token is signed, a user can also login to inspect what operations have been performed with their data.
