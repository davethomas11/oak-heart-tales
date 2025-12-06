//====================================
// Server setup
//====================================
var game_server = sinon.fakeServer.create();
game_server.fakeHTTPMethods = true;
game_server.getHTTPMethod = function (xhr) {
    return xhr.requestHeaders['X-HTTP-Method-Override'] || xhr.method;
}
game_server.autoRespond = true;
game_server.autoRespondAfter = 80;
game_server.xhr.useFilters = true;
game_server.xhr.addFilter(function (method, url, async, username, password) {
    return url === "/" || url.indexOf("http") === 0;
});



//====================================
// Request Handling
//====================================

function RequestHandler() {
    function parseParams(str) {
        var re = /([^&=]+)=?([^&]*)/g;
        var decode = function (str) {
            return decodeURIComponent(str.replace(/\+/g, ' '));
        };
        var params = {}, e;
        if (str) {
            if (str.substr(0, 1) == '?') {
                str = str.substr(1);
            }
            while (e = re.exec(str)) {
                var k = encodeHTML(decode(e[1]));
                var v = encodeHTML(decode(e[2]));
                if (params[k] !== undefined) {
                    if (!Array.isArray(params[k])) {
                        params[k] = [params[k]];
                    }
                    params[k].push(v);
                } else {
                    params[k] = v;
                }
            }
        }
        return params;
    }

    function getQuery(url) {
        var question = url.indexOf("?");
        var hash = url.indexOf("#");
        if (hash == -1 && question == -1) return "";
        if (hash == -1) hash = url.length;
        return question == -1 || hash == question + 1 ? url.substring(hash) :
            url.substring(question + 1, hash);
    }

    function encodeHTML(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
    }

    function params(request) {
        const xhr = request;
        const method = xhr.requestHeaders['X-HTTP-Method-Override'] || xhr.method
        if (method === "GET") {
            return parseParams(getQuery(request.url));
        } else {
            return parseParams(request.requestBody);
        }
    }

    this.params = params;
}

game_server.requestHandler = new RequestHandler();


//====================================
// Routing
//====================================

game_server.paths = new Set();
game_server.onGet = (path, response) => {
    game_server.paths.add(path);
    game_server.respondWith("GET", path, function (request) {
        let params = game_server.requestHandler.params;
        let headers = {};
        let body = response(request, params(request), headers);
        request.respond(200, headers, body);
    });
}

game_server.onPut = (path, response) => {
    game_server.paths.add(path);
    game_server.respondWith("PUT", path, function (request) {
        let headers = {};
        let body = response(request, params(request), headers);
        request.respond(200, headers, body);
    });
}

game_server.onPost = (path, response) => {
    game_server.paths.add(path);
    game_server.respondWith("POST", path, function (request) {
        let headers = {};
        let body = response(request, params(request), headers);
        request.respond(200, headers, body);
    });
}

game_server.onDelete = (path, response) => {
    game_server.paths.add(path);
    game_server.respondWith("DELETE", path, function (request) {
        let headers = {};
        let body = response(request, params(request), headers);
        request.respond(200, headers, body);
    });
}

const originalFetch = window.fetch;
// Mock global fetch to route requests through game_server
// This is for hyperscript fetch calls
window.fetch = function(input, init = {}) {
    const url = typeof input === 'string' ? input : input.url;
    const pathSetup = !!Array.from(game_server.paths).find((path) => {
        if (typeof path === 'string') {
            return path === url;
        } else if (path instanceof RegExp) {
            return path.test(url);
        }
        return false;
    });
    if (!pathSetup) {
        // If the path is not set up in the game_server, use the original fetch
        return originalFetch(input, init);
    }

    return new Promise((resolve, reject) => {
        const method = (init.method || 'GET').toUpperCase();
        const headers = init.headers || {
            'User-Agent': 'mock-fetch-agent',
            'Accept': '*/*'
        };
        const body = init.body || null;

        // Create and send a real XMLHttpRequest
        const realXhr = new XMLHttpRequest();

        for (const key in headers) {
            if (headers.hasOwnProperty(key)) {
                realXhr.setRequestHeader(key, headers[key]);
            }
        }
        realXhr.onload = function () {
            resolve(new Response(realXhr.responseText, {
                status: realXhr.status,
                headers: realXhr.getAllResponseHeaders() || {}
            }));
        };
        realXhr.onerror = function () {
            console.error(`Mock fetch intercepted: ${method} ${url}`);
            reject(new Error('Network error'));
        };
        realXhr.open(method, url, true);
        realXhr.send(body);
    });
};