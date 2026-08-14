const PYTHON_URL =
    "http://127.0.0.1:8765/bookstore-results";

console.log("BOOKSTORE EXTENSION WORKER LOADED");

let lookupBeingSent = false;
let lastLookupKey = null;

const BOOKSTORE_URL =
    "https://www.bkstr.com/chattahoocheetechstore/shop/textbooks-and-course-materials";

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (
            message?.type !==
            "BOOKSTORE_RESULTS"
        ) {
            return;
        }


        console.log(
            "Sending bookstore results to Python..."
        );


        fetch(
            PYTHON_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    message.data
                )
            }
        )
        .then(response => {

            if (!response.ok) {

                throw new Error(
                    `Python server returned ${response.status}`
                );
            }

            return response.text();
        })
        .then(() => {

            console.log(
                "Bookstore results sent to Python."
            );

            lookupBeingSent = false;

            // ---------------------------------
            // Close the BKSTR tab
            // ---------------------------------

            if (
                sender &&
                sender.tab &&
                sender.tab.id
            ) {

                console.log(
                    "Closing BKSTR tab:",
                    sender.tab.id
                );


                chrome.tabs.remove(
                    sender.tab.id
                );
            }

        })
        .catch(error => {

            console.error(
                "Could not contact Textbook Lending Tracker:",
                error
            );
        });


        return false;
    }
);


async function checkForBookstoreLookup() {

    if (lookupBeingSent) {
        return;
    }

    try {

        console.log(
            "Checking Python for bookstore lookup..."
        );

        const response = await fetch(
            "http://127.0.0.1:8765/bookstore-lookup",
            {
                cache: "no-store"
            }
        );

        console.log(
            "Python response:",
            response.status
        );

        if (!response.ok) {
            return;
        }

        const text = await response.text();

        if (
            !text ||
            text === "null"
        ) {
            return;
        }

        const lookup = JSON.parse(text);

        console.log(
            "BOOKSTORE LOOKUP RECEIVED:",
            lookup
        );


        lookupBeingSent = true;


        let tabs = await chrome.tabs.query({
            url: [
                "https://www.bkstr.com/*"
            ]
        });


        let tab;


        // -------------------------------------------------
        // Find existing BKSTR tab
        // -------------------------------------------------

        if (tabs.length) {

            tab = tabs[0];

            console.log(
                "Using existing BKSTR tab:",
                tab.id
            );

        }


        // -------------------------------------------------
        // No BKSTR tab exists — open one
        // -------------------------------------------------

        else {

            console.log(
                "No BKSTR tab found. Opening BKSTR..."
            );

            tab = await chrome.tabs.create({
                url:
                    "https://www.bkstr.com/chattahoocheetechstore/shop/textbooks-and-course-materials"
            });

            console.log(
                "BKSTR tab opened:",
                tab.id
            );

        }


        // -------------------------------------------------
        // Wait for the page to finish loading
        // -------------------------------------------------

        if (tab.status !== "complete") {

            console.log(
                "Waiting for BKSTR page to finish loading..."
            );

            await waitForTabLoad(tab.id);

        }


        // -------------------------------------------------
        // Wait for content script
        // -------------------------------------------------

        console.log(
            "WAITING FOR BKSTR CONTENT SCRIPT:",
            tab.id
        );

        const contentScriptReady =
            await waitForContentScript(
                tab.id
            );


        if (!contentScriptReady) {

            console.error(
                "BKSTR content script did not become available."
            );

            

            return;

        }


        // -------------------------------------------------
        // Send lookup
        // -------------------------------------------------

        console.log(
            "SENDING LOOKUP TO BKSTR TAB:",
            tab.id
        );

        await chrome.tabs.sendMessage(
            tab.id,
            lookup
        );

        console.log(
            "Lookup successfully sent."
        );


    } catch (error) {

        console.error(
            "BOOKSTORE WORKER ERROR:",
            error
        );

        lookupBeingSent = false;

    }

}

function waitForTabLoad(tabId) {

    return new Promise((resolve) => {

        chrome.tabs.get(
            tabId,
            (tab) => {

                if (
                    chrome.runtime.lastError ||
                    !tab
                ) {
                    resolve();
                    return;
                }

                if (
                    tab.status === "complete"
                ) {
                    resolve();
                    return;
                }


                const listener = (
                    updatedTabId,
                    changeInfo
                ) => {

                    if (
                        updatedTabId !== tabId
                    ) {
                        return;
                    }

                    if (
                        changeInfo.status ===
                        "complete"
                    ) {

                        chrome.tabs.onUpdated.removeListener(
                            listener
                        );

                        resolve();

                    }

                };


                chrome.tabs.onUpdated.addListener(
                    listener
                );

            }
        );

    });

}

async function waitForContentScript(
    tabId,
    timeout = 10000
) {

    const startTime = Date.now();

    while (
        Date.now() - startTime < timeout
    ) {

        try {

            await chrome.tabs.sendMessage(
                tabId,
                {
                    type: "BOOKSTORE_PING"
                }
            );

            return true;

        } catch (error) {

            await new Promise(
                resolve => setTimeout(
                    resolve,
                    500
                )
            );

        }

    }

    return false;

}


console.log(
    "BOOKSTORE POLLING STARTED"
);


setInterval(
    checkForBookstoreLookup,
    2000
);


checkForBookstoreLookup();



function wait(ms) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                ms
            )
    );
}


async function sendLookupToTab(
    tabId,
    lookup
) {

    // Try immediately first.

    try {

        await chrome.tabs.sendMessage(
            tabId,
            lookup
        );

        console.log(
            "Lookup sent successfully."
        );

        return;

    } catch (error) {

        console.log(
            "Content script not ready yet."
        );
    }


    // Content script may still be loading.
    // Retry for up to 15 seconds.

    const start =
        Date.now();


    while (
        Date.now() - start <
        15000
    ) {

        await wait(250);


        try {

            await chrome.tabs.sendMessage(
                tabId,
                lookup
            );


            console.log(
                "Lookup sent successfully."
            );

            return;

        } catch (error) {

            // Still loading.
        }
    }


    throw new Error(
        "BKSTR content script did not become ready."
    );
}


console.log(
    "BOOKSTORE POLLING STARTED"
);


setInterval(
    checkForBookstoreLookup,
    250
);


checkForBookstoreLookup();

console.log("BOOKSTORE POLLING STARTED");

setInterval(
    checkForBookstoreLookup,
    2000
);