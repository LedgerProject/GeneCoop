// import {zencode_exec} from './zenroom/dist/module/zenroom';
const { zencode_exec } = require("zenroom");

const hello_script = 'print("Hello World!")';

function zen_hash(questions, answers) {
    const hash_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create hashes of questions and answers
    Given I have a 'string dictionary' named 'userChallenges'
    Given I have a 'string' named 'Question1' in 'userChallenges'
    Given I have a 'string' named 'Answer1' in 'userChallenges'
    Given I have a 'string' named 'Question2' in 'userChallenges'
    Given I have a 'string' named 'Answer2' in 'userChallenges'
    Given I have a 'string' named 'Question3' in 'userChallenges'
    Given I have a 'string' named 'Answer3' in 'userChallenges'
    When I create the hash of 'userChallenges'
    and I rename the 'hash' to 'userChallenges.hash'
    When I create the 'base64 dictionary'
    and I rename the 'base64 dictionary' to 'hashedAnswers'
    When I create the hash of 'Question1'
    and I rename the 'hash' to 'Question1.hash'
    When I insert 'Question1.hash' in 'hashedAnswers'
    When I create the hash of 'Question2'
    and I rename the 'hash' to 'Question2.hash'
    When I insert 'Question2.hash' in 'hashedAnswers'
    When I create the hash of 'Question3'
    and I rename the 'hash' to 'Question3.hash'
    When I insert 'Question3.hash' in 'hashedAnswers'
    When I create the hash of 'Answer1'
    and I rename the 'hash' to 'Answer1.hash'
    When I insert 'Answer1.hash' in 'hashedAnswers'
    When I create the hash of 'Answer2'
    and I rename the 'hash' to 'Answer2.hash'
    When I insert 'Answer2.hash' in 'hashedAnswers'
    When I create the hash of 'Answer3'
    and I rename the 'hash' to 'Answer3.hash'
    When I insert 'Answer3.hash' in 'hashedAnswers'
    Then print 'hashedAnswers'`;

    var ques_ans = {};

    for (let count = 0; count < questions.length; count++) {
        ques_ans["Question" + (count + 1)] = questions[count];
        ques_ans["Answer" + (count + 1)] = answers[count];
    }
    const data_tohash = {
        "userChallenges": ques_ans
    };

    console.log("Hash data to zenroom: ", JSON.stringify(data_tohash));

    return new Promise(function (resolve, reject) {
        zencode_exec(hash_script, { data: JSON.stringify(data_tohash), keys: {}, conf: `color=0, debug=1` })
            .then((result) => {
                console.log("Result from zenroom hash: ", JSON.stringify(result));
                // const msg_sign = JSON.parse(result.result)["hashedAnswers"];
                // console.log("Msg signature: ", msg_sign);
                resolve(result);
            }).catch((error) => {
                console.error("Error in zenroom hash function: ", error);
                reject(error);
            });
    });

}

function zen_sign(public_key, private_key, tosign) {
    const sign_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create the signature of a request
    Given I am 'Signer'
    Given I have my 'keypair'
    Given that I have a 'string' named 'message'
    When I create the signature of 'message'
    When I rename the 'signature' to 'message.signature'
    Then print the 'message.signature'`;

    const data = {
        "message": tosign,
        "Signer": {
            "keypair": {
                "private_key": private_key,
                "public_key": public_key
            }
        }
    };
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
        if (storedSettings.authCredentials === undefined && storedSettings.keypair_recovery === undefined) {
            onError("Please select and answer the questions in the add-on settings");
            return;
        }
        if (storedSettings.authCredentials === undefined){
            zen_hash(storedSettings.keypair_recovery.selectedQuestionTexts, storedSettings.keypair_recovery.answers)
                .then((msg_hash) => {
                    console.log("Hash: ", msg_hash);
                })
                .catch((error) => {
                    console.error("Error in zenroom hash function: ", error);
                    throw new Error(error);
                });
            
        }

        if (action == 'login') {

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
    //  * Listen for messages from the browserAction script.
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

