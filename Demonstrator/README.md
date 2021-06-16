# The Demonstrator

The demostrator is written in Python (we use v3.8) and has a Django back-end plus 2 web-extensions for the front-end.

## Installation

### Server
If you want to run the code on your premises, after cloning this repository perform the following actions:

1. Install Python 3.8
2. (Optional) Install a virtual environment manager such as miniconda or virtualenv.
3. (Optional) create a virtual environment and activate it. Ex `conda create -n Demonstrator python==3.8` and then `conda activate Demonstrator`
4. Install requirements: `pip install -r pip_requirements.txt`
5. Change directory to `Genecoop/Demonstrator/ResearchInterface`
6. Fill in your self-created credentials in `.researcher_template.json` and rename it to `.researcher.json`
7. Fill in your self-created credentials in `.superuser_template.json` and rename it to `.superuser.json`
8. if you want to run a production version of Django create the file `.secret_key` with a suitable Django secrete key (see instructions online)
9. Run the webserver that serves the apps: `./startDevelopment.sh` for development or `startProduction.sh` for production (runs on Linux with screen)

You should see some output ending with something similar to the following (for `startDevelopment.sh`):
```
June 16, 2021 - 14:50:23
Django version 3.2.4, using settings 'consent_server.settingsD'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Build Web extensions
This part is not needed to run the application, only if you want to modify the web extensions.

There are two web extensions, one for the researcher and one for the DNA donor (user). The instructions are the same for both (unless specified), here we show the instructions for the researcher one.

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
1. Browse to: about:debugging
2. Click "This Firefox" -> "Load temporary add-on"
3. Select the researcher_webext.zip file in your Downloads directory
4. Browse to about:addons
5. Click on "..." -> preferences for the "genecoop_research" addon (genecoop_donor for the user one)
6. Fill in the username, which has to be of the form http://localhost:8000/ids/<username\>
7. Fill in the public key and private key with the values you wrote in `ResearchInterface/.researcher.json`, click save.
8. To test if the configuration is correct, navigate to http://localhost:8000/request, and click on the extension; you should see two buttons: 'login' and 'sign'.

For the DNA donor extension, step 7 and 8 should be replaced with:
  
7. Select 3 questions and provide an answer to each of them
8. To test if the configuration is correct, navigate to http://localhost:8000/consent, and click on the extension; you should see two buttons: 'login' and 'sign'.
  
You can also build a signed, downloadable self hosted version of the webextension. This step will require that you modify the manifest.json file of both web-extension with your own id for the plugin and it is not encouraged.

First you need to get credentials from [Mozilla](https://extensionworkshop.com/documentation/publish/signing-and-distribution-overview/).

Then execute:
```
web-ext sign --api-key=<KEY> --api-secret=<SECRET> --channel=unlisted
```

Copy the xpi file to the django static directory (`./ResearchInterface/researcher_app/static/researcher_app/` for the researcher and `./ResearchInterface/donor_app/static/donor_app/` for the user).
  
In this way if you navigate with Firefox to http://localhost:8000/consent or http://localhost:8000/request, the login window will offer you to download and install the plugin you just built.

## Operations

If these step were successful, you can access the Researcher interface at `http://127.0.0.1:8000/request` and the consent interface at `http://127.0.0.1:8000/consent`.

Both pages will show a login window, and the instructions to log in using the web extension.
In the Researcher interface the first page shows a list of existing requests if there are any, divided in pending (waiting for a reply) and answered.
In order to create a new consent request you need to click on Create Request in the menu.

After generating one or more requests and signing them with the web extension, you can send the user the token corrisponding to the request (externally to this application).
The recipient of the token can enter it on the page at `http://127.0.0.1:8000/consent`.

The user can then reply to each single question in the consent and sign it. Once at least a token is signed, a user can also login to inspect what operations have been performed with their data.

Once a consent is signed, the researcher will see it in the Answered section. Clicking on each answered request lead to a page where the researcher can perform the different experiments which they have received consent for.
  
Each action is logged and visible for the DNA donor on the DNA donor website showing the consent used by the researcher to perform their experiment.

User id are available at http://localhost:8000/ids/<username\> and signed consents (in [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) format) are available at http://localhost:8000/docs/<token\>.

At http://localhost:8000/data/ there is a simple datasafe application where the URL of VC (in the form http://localhost:8000/docs/<token\>) can be entered. The app verifies the VC and shows its content.
