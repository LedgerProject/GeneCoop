// import {zencode_exec} from './zenroom/dist/module/zenroom';
const { zencode_exec } = require("zenroom");

(function () {

    /**
     * Check and set a global guard variable.
     * If this content script is injected into the same page again,
     * it will do nothing next time.
     */
    if (window.hasRun) {
        console.log("zenpage already started")
        return;
    }
    window.hasRun = true;

    const hello_script = 'print("Hello World!")';

    const sign_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create the signature of a request
    Given I am 'Signer'
    Given I have my 'keypair'
    Given that I have a 'string' named 'message'
    When I create the signature of 'message'
    When I rename the 'signature' to 'message.signature'
    Then print the 'message.signature'`;

    function onError(e) {
        console.error(e);
    }

    function toggle_instructions() {
        let div = document.querySelector("[id='action-required-genecoop-plugin']");
        if (div !== null) {
            div.style = 'display: none;visibility: hidden;';
        }

        div = document.querySelector("[id='action-done-genecoop-plugin']");
        if (div !== null) {
            div.style = 'display: block;visibility:visible;';
        }

    }

    /**
     */
    function perform_action(action, storedSettings) {


        console.log(`${action} called`)
        if (action == 'login') {
            var username_html = document.querySelector("[id='username']");
            if (storedSettings.authCredentials === undefined) {
                username_html.value = "Please set your credentials in the add-on";
                return;
            }
            username_html.value = storedSettings.authCredentials.username;
            const challenge = document.querySelector("[id='challenge']").value;
            console.log("Challenge: ", challenge);


            zen_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, challenge)
                .then((msg_sign) => {
                    console.log("Signature: ", msg_sign);

                    var signature_html = document.querySelector("[id='response']");
                    signature_html.value = JSON.stringify(msg_sign);

                    toggle_instructions();
                    var button = document.querySelector("[id='proceedButton']");
                    button.style = 'visibility:visible;';

                })
                .catch((error) => {
                    console.error("Error in zenroom sign function: ", error);
                    throw new Error(error);
                });

        } else if (action == 'sign') {

            if (storedSettings.authCredentials === undefined) {
                throw new Error("Please set your credentials in the add-on");
            }

            const token_els = document.querySelectorAll("[data-label='token']");

            console.log("Tokens: ", token_els);

            let proms = [];
            token_els.forEach(token_el => {

                var token = token_el.textContent

                console.log("Token: ", token);

                proms.push(new Promise(function (resolve, reject) {
                    zen_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, token)
                        .then((msg_sign) => {
                            console.log("Signature: ", msg_sign);

                            var signature_html = document.querySelector(`[id='signature-${token}']`);
                            signature_html.value = JSON.stringify(msg_sign);
                            resolve("OK");
                        })
                        .catch((error) => {
                            console.error("Error in zenroom sign function: ", error);
                            reject(error);
                        });
                }));

            });

            Promise.all(proms)
                .then((values) => {
                    console.log("Out of promises: ", values);
                    toggle_instructions();
                    var submit_html = document.querySelector("[id='submit']");
                    submit_html.disabled = false;

                })
                .catch((error) => {
                    onError(error);
                }
                );
        }
    }
    /**
     */


    /**
     */
    function zen_sign(public_key, private_key, tosign) {

        const data = {
            "message": tosign,
            "Signer": {
                "keypair": {
                    "private_key": private_key,
                    "public_key": public_key
                }
            }
        }
        console.log("Data: ", data);
        return new Promise(function (resolve, reject) {

            zencode_exec(sign_script, { data: JSON.stringify(data), keys: {}, conf: `color=0, debug=0` })
                .then((result) => {
                    console.log("Zenroom result", result);
                    const msg_sign = JSON.parse(result.result)["message.signature"];
                    console.log("Msg signature: ", msg_sign);
                    resolve(msg_sign);
                }).catch((error) => {
                    console.error("Error in zenroom sign function: ", error);
                    reject(error);
                });
        });

    }

    // /**
    //  */
    function verify(key) {
        console.log("Verify called")
        zencode_exec(script).then(({ result }) => console.log(result))
    }

    // /**
    //  */
    function reset() {
        console.log("Reset called")
        let existingSignatures = document.querySelectorAll(".signature");
        for (let sig of existingSignatures) {
            sig.remove();
        }
    }

    // /**
    //  * Listen for messages from the background script.
    // */
    browser.runtime.onMessage.addListener((message) => {
        let gettingStoredSettings = browser.storage.local.get();
        if (message.command === "login") {
            gettingStoredSettings.then((x) => { perform_action('login', x) }, onError)
                .catch((error) => {
                    throw new Error(error);
                });
        } else if (message.command === "sign") {
            gettingStoredSettings.then((x) => { perform_action('sign', x) }, onError)
                .catch((error) => {
                    throw new Error(error);
                });
        } else if (message.command === "reset") {
            reset();
        }
    });

    console.log("zenpage start");
})();

