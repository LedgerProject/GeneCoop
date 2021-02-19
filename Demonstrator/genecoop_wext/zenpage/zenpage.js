// import {zenroom_exec} from './zenroom/dist/module/zenroom';
const {zenroom_exec} = require("zenroom");

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

    const script = 'print("Hello World!")';


    
    /**
     */
    function sign(key) {
        console.log("Sign called")
        zenroom_exec(script).then(({result}) => console.log(result))
    }

    // /**
    //  */
    function verify(key) {
        console.log("Verify called")
        zenroom_exec(script).then(({result}) => console.log(result))
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
            sign(message.key);
        } else if (message.command === "verify") {
            verify();
        } else if (message.command === "reset") {
            reset();
        }
    });

    console.log("zenpage start");
    sign("");
})();

