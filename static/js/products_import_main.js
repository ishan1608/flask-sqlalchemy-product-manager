/* global tus */
/* eslint no-console: 0 */

"use strict";

let upload = null;
let uploadIsRunning = false;
const toggleBtn = document.querySelector("#toggle-btn");
const input = document.querySelector("input[type=file]");
const progress = document.querySelector(".progress");
const progressBar = progress.querySelector(".bar");
const alertBox = document.querySelector("#support-alert");
const uploadResult = document.querySelector("#upload-result");

// Initialize Toastr Options
toastr.options = {
    'closeButton': true,
    'debug': false,
    'newestOnTop': true,
    'progressBar': false,
    'positionClass': 'toast-top-right',
    'preventDuplicates': false,
    'onclick': null,
    'showDuration': '300',
    'hideDuration': '1000',
    'timeOut': '5000',
    'extendedTimeOut': '1000',
    'showEasing': 'swing',
    'hideEasing': 'linear',
    'showMethod': 'fadeIn',
    'hideMethod': 'fadeOut'
};

if (!tus.isSupported) {
    alertBox.classList.remove("hidden");
}

toggleBtn.addEventListener("click", function (e) {
    e.preventDefault();

    if (upload) {
        if (uploadIsRunning) {
            upload.abort();
            toggleBtn.textContent = "resume upload";
            uploadIsRunning = false;
        } else {
            upload.start();
            toggleBtn.textContent = "pause upload";
            uploadIsRunning = true;
        }
    } else {
        if (input.files.length > 0) {
            startUpload();
        } else {
            input.click();
        }
    }
});

input.addEventListener("change", startUpload);

function startUpload() {
    let file = input.files[0];
    // Only continue if a file has actually been selected.
    // IE will trigger a change event even if we reset the input element
    // using reset() and we do not want to blow up later.
    if (!file) {
        return;
    }

    toggleBtn.textContent = "pause upload";

    let options = {
        endpoint: '/products-csv-upload',
        resume: true,
        chunkSize: Infinity,
        retryDelays: [0, 1000, 3000, 5000],
        metadata: {
            filename: file.name,
            filetype: file.type
        },
        onError: function (error) {
            if (error.originalRequest) {
                console.log(error);
                toastr.options.showDuration = 5000;
                toastr.options.onclick = function () {
                    console.log('retry requested');
                    upload.start();
                    uploadIsRunning = true;
                };
                toastr['error']('Retry ?', 'Failed to Upload');
                return;
            } else {
                toastr.options.onclick = null;
                console.log(error);
                toastr['error']("Failed Upload", 'Success');
            }

            reset();
        },
        onProgress: function (bytesUploaded, bytesTotal) {
            let percentage = (bytesUploaded / bytesTotal * 100).toFixed(2);
            progressBar.style.width = percentage + "%";
            console.log(bytesUploaded, bytesTotal, percentage + "%");
        },
        onSuccess: function () {
            uploadResult.textContent = "Successfully Uploaded " + upload.file.name + " (" + upload.file.size + " bytes)";
            toastr.options['onclick'] = null;
            toastr['success']("Successfully Uploaded " + upload.file.name + " (" + upload.file.size + " bytes)", 'Success');
            reset();
        }
    };

    upload = new tus.Upload(file, options);
    upload.start();
    uploadIsRunning = true;
}

function reset() {
    input.value = "";
    toggleBtn.textContent = "start upload";
    upload = null;
    uploadIsRunning = false;
}
