/**
* Listen for clicks on the buttons, and send the appropriate message to
* the content script in the page.
*/
// import * as zenroom from './zenroom/dist/main/index.js';
// import {zenroom as zenroom_exec} from '../zenpage/zenroom.js';
// import {zenroom_exec} from '../node_modules/zenroom/dist/module/index.js'

const loginPage = `body > :not(.notexisting) {
    color: red;
  }`;

const signPage = `body > :not(.notexisting) {
    color: green;
 }`;

const verifyPage = `body > :not(.notexisting) {
    color: blue;
  }`;

function listenForClicks() {
    document.addEventListener("click", (e) => {

        function perform_action(tabs) {
            console.log("Action called")
            switch (e.target.textContent) {
                case "Login":
                    login(tabs);
                    break;
                case "Sign":
                    sign(tabs);
                    break;
                default:
                    console.error("Unknwon action: " + e.target.textContent);
                    break;
            }
        }

        function login(tabs) {
            //browser.tabs.insertCSS({ code: loginPage }).then(() => {
                browser.tabs.sendMessage(tabs[0].id, {
                    command: "login"
                });
            //});
        }

        function sign(tabs) {
            //browser.tabs.insertCSS({ code: signPage }).then(() => {
                browser.tabs.sendMessage(tabs[0].id, {
                    command: "sign"
                });
            //});
        }

        function verify(tabs) {
            browser.tabs.insertCSS({ code: verifyPage }).then(() => {
                browser.tabs.sendMessage(tabs[0].id, {
                    command: "verify"
                });
            });
        }
        /**
        * Remove the CSS from the active tab,
        * send a "reset" message to the content script in the active tab.
        */
        function reset(tabs) {
            browser.tabs.removeCSS({ code: signPage })
                .then(browser.tabs.removeCSS({ code: verifyPage }))
                .then(() => {
                    browser.tabs.sendMessage(tabs[0].id, {
                        command: "reset",
                    });
                });
        }

        /**
        * Just log the error to the console.
        */
        function reportError(error) {
            console.error(`Error: ${error}`);
        }

        /**
        * Get the active tab,
        * then call "beastify()" or "reset()" as appropriate.
        */
        if (e.target.classList.contains("action")) {
            browser.tabs.query({ active: true, currentWindow: true })
                .then(perform_action)
                .catch(reportError);
        }
        else if (e.target.classList.contains("reset")) {
            browser.tabs.query({ active: true, currentWindow: true })
                .then(reset)
                .catch(reportError);
        }
    });
}

/**
* There was an error executing the script.
* Display the popup's error message, and hide the normal UI.
*/
function reportExecuteScriptError(error) {
    document.querySelector("#popup-content").classList.add("hidden");
    document.querySelector("#error-content").classList.remove("hidden");
    console.error(`Failed to execute content script: ${error.message}`);
}

/**
* When the popup loads, inject a content script into the active tab,
* and add a click handler.
* If we couldn't inject the script, handle the error.
*/
console.log("popup start")
// browser.tabs.executeScript({ file: "/zenpage/zenpage.js" })
    browser.tabs.executeScript({ file: "/zenpage/zenpage.bundle.js" })
    .then(listenForClicks)
    .catch(reportExecuteScriptError);
