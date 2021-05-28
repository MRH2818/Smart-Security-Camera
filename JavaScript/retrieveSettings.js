var recTolLabel = {
    id : "recTol",
    labelForText : "Facial Recognition Tolerance:",
    rangeId : "recTolSlider"};

var certTolLabel = {
    id : "certTol",
    labelForText : "Certification Tolerance:",
    rangeId : "certTolSlider"};

var confirmTimeLabel = {
    id : "confirmTime",
    labelForText : "Confirmation Time:",
    rangeId : "confirmTimeSlider"};

var imgDiffTol = {
    id : "imgDiffTol",
    labelForText : "Tolerance Between Two Frames:",
    rangeId : "imgDiffTolSlider"};

var minPercLabel = {
    id : "minPerc",
    labelForText : "Minimum Percentage of Positive Queries:",
    rangeId : "minPercSlider"
};
function getSettings() {
    urlForSettings = "/information/settings/retrieve";

    fetch(urlForSettings)
        .then(response => {

            if (response.ok) {
                return response.json();
            }

            return "Error Retrieving Status";
        }).then(settingsData => {

            //console.log(settingsData);

            if (settingsData == "Error Retrieving Status") {
                return;
            }

            document.getElementById(recTolLabel.rangeId).value = settingsData.recTolerance;
            document.getElementById(minPercLabel.rangeId).value = settingsData.minPercOfPosImgs;
            document.getElementById(imgDiffTol.rangeId).value = settingsData.imageDifferenceTol;
            document.getElementById(confirmTimeLabel.rangeId).value = settingsData.confirmationTime;
            document.getElementById(certTolLabel.rangeId).value = settingsData.certifyTolerance;
            
            setRangeValue(recTolLabel.id, recTolLabel.labelForText, settingsData.recTolerance);
            setRangeValue(certTolLabel.id, certTolLabel.labelForText, settingsData.certifyTolerance);
            setRangeValue(confirmTimeLabel.id, confirmTimeLabel.labelForText, settingsData.confirmationTime);
            setRangeValue(imgDiffTol.id, imgDiffTol.labelForText, settingsData.imageDifferenceTol);
            setRangeValue(minPercLabel.id, minPercLabel.labelForText, settingsData.minPercOfPosImgs);
        });
}
function setRangeValue (labelId, labelForText, rangeValue) {
    document.getElementById(labelId).innerText = `${labelForText} ${rangeValue} `;
}
