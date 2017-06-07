import {params} from "./Settings";

class Api {

    constructor() {}

    /**
    * @param {String} token User identification token
    * @param {String} license User license object
    * @return {Promise} Promise
    */
    getUserByToken(token, license) {
        return new Promise((resolve, reject) => {
            if (!token) {
                reject();
                return;
            }

            const url = params.api_url;
            const post = {
                request: 'google_auth',
                token,
                license
            };
            const data = new FormData();
            data.append('json', JSON.stringify(post));

            fetch(url, {
                method: 'POST',
                body: data
            }).then((response) => {

                if (response.status !== 200) {
                    console.error(`Login error. Status Code: ${response.status}`);
                    reject();
                } else {
                    return response.json();
                }
            }).then((response) => {

                if (response.type === 'response') {
                    resolve(response);
                } else {
                    reject();
                }
            }).catch((err) => {
                console.error(`User login fetch Error: ${err}`);
                reject();
            });
        });
    }

    getLicense(token) {
        return new Promise((resolve, reject) => {
            const cws_license_api_url = `https://www.googleapis.com/chromewebstore/v1.1/userlicenses/${chrome.runtime.id}`;

            fetch(cws_license_api_url, {
                headers: {'Authorization': `Bearer ${token}`}
            }).then((response) => {
                if (response.status !== 200) {
                    console.error(`Api get license: response status: ${response.status}`);
                    reject();
                } else {
                    return response.json();
                }
            }).then((license) => {
                this.saveLicense(license).then(resolve).catch(reject);
            }).catch((err) => {
                console.error(`Api get license: catched error: ${err}`);
                reject();
            });
        });
    }

    saveLicense(license) {
        return new Promise((resolve) => {
            chrome.storage.sync.set({license}, resolve);
        });
    }
}

export default new Api();
