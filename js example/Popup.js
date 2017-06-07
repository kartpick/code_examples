const _ = require('lodash');
window.jQuery = window.$ = require('jquery');
let Main = {};

class Popup {
    constructor() {
        this.token = '';
    }

    showPluginInterface(res) {
        const logoutView = $('#logoutView');
        const spinnerView = $('#spinner');

        spinnerView.hide();

        this.token = res.token;

        logoutView.find('.userName').html(res.user.email);
        logoutView.find('.subscr').html(res.license.subscr_expires_at);
        logoutView.show();
    }

    showLogin() {
        $('#loginView').show();
    }

    login(interactive) {
        Main.signInUser(interactive).then(response => {
            this.showPluginInterface(response);
        }).catch(() => {
            this.showLogin();
        });
    }

    logout() {
        Main.logoutUser(this.token).then(this.resetAfterLogout);
    }

    resetAfterLogout() {
        const loginView = $('#loginView');
        const logoutView = $('#logoutView');

        this.token = '';

        logoutView.find('.userName').html('');
        logoutView.find('.subscr').html('');
        logoutView.hide();

        loginView.show();
    }
}

// Загружаем background и jquery
$(() => {
    chrome.runtime.getBackgroundPage(bg => {
        Main = bg.mainClass;
        const popup = new Popup(Main);
        popup.login(false);

        $('#loginView .login').click(() => {
            popup.login(true);
        });

        $('#logoutView .logout').click(() => {
            popup.logout();
        });
    });
});
