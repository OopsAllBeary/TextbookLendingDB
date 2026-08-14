console.log("BOOKSTORE CONTENT SCRIPT LOADED");

let currentLookup = null;

window.addEventListener(
    "message",
    (event) => {

        if (
            event.source !== window
        ) {
            return;
        }

        const message =
            event.data;

        if (
            !message ||
            message.source !==
                "TEXTBOOK_LENDING_TRACKER" ||
            message.type !==
                "BOOKSTORE_RESULTS"
        ) {
            return;
        }

        console.log(
            "BOOKSTORE RESULTS RECEIVED FROM PAGE:",
            message.data
        );

        chrome.runtime.sendMessage(
            {
                type:
                    "BOOKSTORE_RESULTS",

                data:
                    message.data
            }
        );
    }
);


chrome.runtime.onMessage.addListener(
    (
        message,
        sender,
        sendResponse
    ) => {

        if (
            message?.type ===
            "BOOKSTORE_PING"
        ) {

            sendResponse({
                ready: true
            });

            return;
        }

        console.log(
            "BOOKSTORE MESSAGE RECEIVED:",
            message
        );

        if (
            message.type !==
            "bookstore_lookup"
        ) {
            return;
        }

        currentLookup = message;

        startBookstoreLookup();

        sendResponse({
            success: true
        });

        return true;
    }
);

function startBookstoreLookup() {

    if (!currentLookup) {
        return;
    }

    console.log(
        "Starting bookstore lookup for:",
        currentLookup.studentId
    );

    waitForStudentForm();
}

function waitForStudentForm() {

    console.log(
        "Waiting for Student ID form..."
    );


    const findInput = () => {

        const input =
            document.querySelector(
                "#STUDENTID-FORM-INPUT"
            );

        if (input) {

            console.log(
                "Student ID form found."
            );

            return input;
        }

        return null;
    };


    // -----------------------------------------
    // Check immediately
    // -----------------------------------------

    const existingInput =
        findInput();

    if (existingInput) {

        fillStudentId(
            existingInput
        );

        return;
    }


    // -----------------------------------------
    // Mutation observer
    // -----------------------------------------

    const observer =
        new MutationObserver(
            () => {

                const input =
                    findInput();

                if (!input) {
                    return;
                }

                cleanup();

                fillStudentId(
                    input
                );
            }
        );


    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );


    // -----------------------------------------
    // Fast polling fallback
    // -----------------------------------------

    const poller =
        setInterval(
            () => {

                const input =
                    findInput();

                if (!input) {
                    return;
                }

                cleanup();

                fillStudentId(
                    input
                );

            },
            100
        );


    // -----------------------------------------
    // Safety timeout
    // -----------------------------------------

    const timeout =
        setTimeout(
            () => {

                cleanup();

                console.error(
                    "Student ID form did not appear within 15 seconds."
                );

            },
            15000
        );


    function cleanup() {

        observer.disconnect();

        clearInterval(
            poller
        );

        clearTimeout(
            timeout
        );
    }
}

function fillStudentId(input) {

    if (!currentLookup) {
        return;
    }


    const studentId =
        String(
            currentLookup.studentId
        );


    console.log(
        "Filling Student ID:",
        studentId
    );


    input.focus();


    // Use the native setter so React/
    // other framework-controlled inputs
    // see the value change.

    const setter =
        Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            "value"
        ).set;


    setter.call(
        input,
        studentId
    );


    input.dispatchEvent(
        new Event(
            "input",
            {
                bubbles: true
            }
        )
    );


    input.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );


    console.log(
        "Student ID entered:",
        input.value
    );


    clickStudentIdButton();
}

function clickStudentIdButton() {

    console.log(
        "Looking for Student ID ENTER button..."
    );


    const findButton = () => {

        return document.querySelector(
            ".input-group.student-id-form button"
        );
    };


    const existingButton =
        findButton();


    if (existingButton) {

        console.log(
            "Clicking ENTER button."
        );

        existingButton.click();

        waitForCourseForm();

        return;
    }


    const observer =
        new MutationObserver(
            () => {

                const button =
                    findButton();

                if (!button) {
                    return;
                }

                cleanup();

                console.log(
                    "Clicking ENTER button."
                );

                button.click();

                waitForCourseForm();
            }
        );


    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );


    const poller =
        setInterval(
            () => {

                const button =
                    findButton();

                if (!button) {
                    return;
                }

                cleanup();

                console.log(
                    "Clicking ENTER button."
                );

                button.click();

                waitForCourseForm();

            },
            100
        );


    const timeout =
        setTimeout(
            () => {

                cleanup();

                console.error(
                    "Student ID ENTER button "
                    + "did not appear within 15 seconds."
                );

            },
            15000
        );


    function cleanup() {

        observer.disconnect();

        clearInterval(
            poller
        );

        clearTimeout(
            timeout
        );
    }
}

function waitForCourseForm() {

    console.log(
        "Waiting for course selection form..."
    );

    const existingCampus =
        document.querySelector(
            'select[name="campusdropdown"]'
        );

    const existingTerm =
        document.querySelector(
            'select[name="termdropdown"]'
        );

    if (
        existingCampus &&
        existingTerm
    ) {

        configureCourseForm(
            existingCampus,
            existingTerm
        );

        return;
    }


    const observer =
        new MutationObserver(
            () => {

                const campus =
                    document.querySelector(
                        'select[name="campusdropdown"]'
                    );

                const term =
                    document.querySelector(
                        'select[name="termdropdown"]'
                    );

                if (
                    !campus ||
                    !term
                ) {
                    return;
                }

                observer.disconnect();

                configureCourseForm(
                    campus,
                    term
                );
            }
        );


    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
}

function configureCourseForm(
    campus,
    term
) {

    console.log(
        "Course selection form detected."
    );


    let campusValue;


    if (
        String(currentLookup.programId)
        === "4058"
    ) {

        campusValue =
            "Marietta Campus";

    } else if (
        String(currentLookup.programId)
        === "4065"
    ) {

        campusValue =
            "North Metro Campus";

    } else {

        console.error(
            "Unknown bookstore program ID:",
            currentLookup.programId
        );

        return;
    }


    console.log(
        "Selecting campus:",
        campusValue
    );


    campus.value =
        campusValue;


    campus.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );


    console.log(
        "Selecting term:",
        currentLookup.termId
    );


    term.value =
        String(
            currentLookup.termId
        );


    term.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );


    console.log(
        "Course selections configured."
    );


    clickFindCourses();
}

function clickFindCourses() {

    const button =
        document.querySelector(
            ".button-container button"
        );


    if (!button) {

        console.error(
            "FIND COURSES button not found."
        );

        return;
    }


    console.log(
        "Clicking FIND COURSES."
    );


    button.click();
}