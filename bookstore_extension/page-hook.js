(() => {

    const TARGET = "/courseMaterial/results";

    function isTarget(url) {

        try {
            return new URL(
                url,
                window.location.href
            ).pathname.includes(TARGET);
        } catch {
            return false;
        }
    }


    function sendResult(data) {

        window.postMessage(
            {
                source: "TEXTBOOK_LENDING_TRACKER",
                type: "BOOKSTORE_RESULTS",
                data: data
            },
            "*"
        );
    }


    // -------------------------------------------------
    // FETCH
    // -------------------------------------------------

    const originalFetch = window.fetch;

    window.fetch = async function (...args) {

        const response =
            await originalFetch.apply(
                this,
                args
            );

        try {

            const request =
                args[0];

            const init =
                args[1] || {};

            const url =
                typeof request === "string"
                    ? request
                    : request?.url;


            if (url && isTarget(url)) {

                const clone =
                    response.clone();

                let body = null;

                try {
                    body = await clone.json();
                } catch {
                    body = await clone.text();
                }


                sendResult({
                    method: "FETCH",
                    url: url,

                    requestBody:
                        init.body || null,

                    status:
                        response.status,

                    response: body
                });
            }

        } catch (error) {

            console.error(
                "Textbook Lending Tracker fetch hook error:",
                error
            );
        }


        return response;
    };


    // -------------------------------------------------
    // XMLHttpRequest
    // -------------------------------------------------

    const originalOpen =
        XMLHttpRequest.prototype.open;

    const originalSend =
        XMLHttpRequest.prototype.send;


    XMLHttpRequest.prototype.open =
        function (
            method,
            url,
            ...rest
        ) {

            this._tltMethod =
                method;

            this._tltUrl =
                url;

            return originalOpen.call(
                this,
                method,
                url,
                ...rest
            );
        };


    XMLHttpRequest.prototype.send =
        function (body) {

            try {

                if (
                    this._tltUrl &&
                    isTarget(this._tltUrl)
                ) {

                    this.addEventListener(
                        "load",
                        function () {

                            let responseData =
                                this.responseText;

                            try {
                                responseData =
                                    JSON.parse(
                                        responseData
                                    );
                            } catch {
                                // Leave as text
                            }


                            sendResult({
                                method:
                                    "XHR",

                                url:
                                    this._tltUrl,

                                requestBody:
                                    body || null,

                                status:
                                    this.status,

                                response:
                                    responseData
                            });
                        }
                    );
                }

            } catch (error) {

                console.error(
                    "Textbook Lending Tracker XHR hook error:",
                    error
                );
            }


            return originalSend.call(
                this,
                body
            );
        };

})();