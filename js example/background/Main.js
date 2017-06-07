import Api from "./Api";
import {Settings} from "./Settings";
const _ = require('lodash');

class Main {

    constructor() {}

    signInUser(interactive = true) {
        return new Promise((resolve, reject) => {
            chrome.identity.getAuthToken({interactive}, (token) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                    return;
                }

                this.checkLicense(token).then((license) => {
                    // Got License, update user
                    Api.getUserByToken(token, license).then((user) => {
                        resolve({user, license});
                    }).catch(reject);
                }).catch(reject);
            });
        });
    }

    logoutUser(token) {
        return new Promise((resolve, reject) => {
            if (!token) {
                reject();
                return;
            }

            chrome.identity.launchWebAuthFlow({'url': 'https://accounts.google.com/logout'}, () => {
                resolve();
            });
        });
    }

    checkLicense(token) {
        return new Promise((resolve, reject) => {
            if (!token) {
                reject();
                return;
            }

            chrome.storage.sync.get('license', (license) => {

                if (_.isEmpty(license)) {
                    resolve(license);
                } else {
                    Api.getLicense(token).then(resolve).catch(reject);
                }
            });
        });
    }
}


window.settingsClass = Settings;
window.mainClass = new Main();
