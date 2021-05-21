var url = '/information/status';

console.log("Running Code")

function requestStatus() {
    
    fetch(url)
        .then(response => {

            if (response.ok) {
                return response.json();
            }

            return "Error Retrieving Status";
        }).then(data => {
            postMessage(data);
        });
    
    
    setTimeout(requestStatus, 3000)
}

requestStatus();