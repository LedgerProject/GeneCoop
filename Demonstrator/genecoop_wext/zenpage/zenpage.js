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
      
    /**
     */
    function sign() {

        console.log("Sign called")
        let gettingStoredSettings = browser.storage.local.get();
        gettingStoredSettings.then(zen_sign, onError);
    }
    /**
     */
    function zen_sign(storedSettings) {

        const token = document.querySelector("[data-label='token']").textContent;
        console.log("Token: ", token);
        const data = {
            "message": token,
            "Signer": {
                "keypair": {
                    "private_key": storedSettings.authCredentials.private_key,
                    "public_key": storedSettings.authCredentials.public_key
                }
            }
        }
        console.log("Data: ", data);
        zencode_exec(sign_script, { data: JSON.stringify(data), keys: {}, conf: `color=0, debug=0` })
            .then((result) => {
                console.log(result);
                const msg_sign = JSON.parse(result.result)["message.signature"]
                var signature_html = document.querySelector("[id='signature']");
                signature_html.value = JSON.stringify(msg_sign);
            })
            .catch((error) => {
                console.error("Error in sign function: ", error);
                throw new Error(error);
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
        if (message.command === "sign") {
            sign();
        } else if (message.command === "verify") {
            verify();
        } else if (message.command === "reset") {
            reset();
        }
    });

    console.log("zenpage start");
})();

