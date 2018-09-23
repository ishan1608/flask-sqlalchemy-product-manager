'use strict';

var ISG = ISG || {};

$(function () {
    let $webhookUrl = $('#webhook-url');

    $.ajax({
        method: 'GET',
        url: ISG.webhookConfigResourceUrl,
    }).done(function (data) {
        $webhookUrl.val(data.object);
    }).fail(function () {
        toastr["error"]('Error fetching webhook configuration', "Success");
    });

    let $webhookUrlSubmit = $('#webhook-url-submit');
    $webhookUrlSubmit.on('click', function () {
        $.ajax({
            method: 'POST',
            url: ISG.webhookConfigResourceUrl,
            data: {
                url: $webhookUrl.val()
            }
        }).done(function (data) {
            $webhookUrl.val(data.object);
            toastr['success']('Webhook updated to ' + data.object, 'Success');
        }).fail(function () {
            toastr["error"]('Error updating webhook configuration', "Success");
        });
    });
});