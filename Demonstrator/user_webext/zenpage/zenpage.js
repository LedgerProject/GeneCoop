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

    function extractContent(s) {
        // var span = document.createElement('span');
        // span.innerHTML = s;
        // return span.textContent || span.innerText;
        return s.textContent;
      };

    function processContent(contract) {
        contract = contract.replace(/\n+/g, ' ')
        contract = contract.replace(/\t+/g, ' ')
        contract = contract.replace(/\s+/g, ' ')
        return contract;
    }
    function hash_contract(contract) {
        // no hashing for the moment
        return contract;
    };

    function toggle_instructions(){
        let div = document.querySelector("[id='action-required-genecoop-plugin']");
        if( div !== null){
            div.style = 'display: none;visibility: hidden;';
        }
        
        div = document.querySelector("[id='action-done-genecoop-plugin']");
        if( div !== null){
            div.style = 'display: block;visibility:visible;';
        }
        
    }
    /**
     */
    function perform_action(action, storedSettings) {


        console.log(`${action} called`)
        if (action == 'login') {
            
            if (storedSettings.authCredentials === undefined) {
                onError("Please set your credentials in the add-on");
                return;
            }
            
            const challenge = document.querySelector("[id='challenge']").value;
            console.log("Challenge: ", challenge);

            zen_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, challenge)
                .then((msg_sign) => {
                    console.log("Signature: ", msg_sign);

                    var html = document.querySelector("[id='response']");
                    html.value = JSON.stringify(msg_sign);

                    html = document.querySelector("[id='user_id']");
                    html.value = storedSettings.authCredentials.public_key;
                    
                    toggle_instructions();
                    
                    var button = document.querySelector("[id='proceedButton']");
                    button.style = 'visibility:visible;';
                })
                .catch((error) => {
                    console.error("Error in zenroom sign function: ", error);
                    throw new Error(error);
                });

        } else if (action == 'sign') {
            const contract = document.querySelector("[id='contract']");

            console.log("Contract: ", contract);

            if (storedSettings.authCredentials === undefined) {
                onError("Please set your credentials in the add-on");
                return;
            }

            contract_text = extractContent(contract);
            contract_text = processContent(contract_text);

            const hash = hash_contract(contract_text);

            console.log("Textual Contract: ", hash);

            zen_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, hash)
                .then((msg_sign) => {
                    console.log("Signature: ", msg_sign);

                    var html = document.querySelector("[id='signature']");
                    html.value = JSON.stringify(msg_sign);

                    html = document.querySelector("[id='public_key']");
                    html.value = storedSettings.authCredentials.public_key;

                    toggle_instructions();

                    html = document.querySelector("[id='submitButton']");
                    html.disabled = false;
                })
                .catch((error) => {
                    console.error("Error in zenroom sign function: ", error);
                    throw new Error(error);
                });
        }
    }
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
                    console.log(result);
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
            gettingStoredSettings.then((x) => { perform_action('login', x) }, onError);
        } else if (message.command === "sign") {
            gettingStoredSettings.then((x) => { perform_action('sign', x) }, onError);
        } else if (message.command === "verify") {
            gettingStoredSettings.then((x) => { perform_action('verify', x) }, onError);
        } else if (message.command === "reset") {
            reset();
        }
    });

    console.log("zenpage start");
})();

