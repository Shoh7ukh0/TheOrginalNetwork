'use strict';

const baseURL = "/"

let localVideo = document.querySelector('#localVideo');


let otherUser;
let remoteRTCMessage;

let iceCandidatesFromCaller = [];
let peerConnection;
let remoteStream;
let localStream;

let callInProgress = false;

let remoteVideos = {};

//event from html
let nimadir = []
function call(inde) {

    otherUser = nimadir[inde];

    beReady()
        .then(bool => {
            processCall(nimadir[inde])
        })
}

//event from html
function answer() {
    //do the event firing

    beReady()
        .then(bool => {
            processAccept();
        })

    document.getElementById("answer").style.display = "none";
}

let pcConfig = {
    "iceServers":
        [
            // { "url": "stun:stun.jap.bloggernepal.com:5349" },
            // {
            //     "url": "turn:turn.jap.bloggernepal.com:5349",
            //     "username": "guest",
            //     "credential": "somepassword"
            // },
            // {"url": "stun:stun.l.google.com:19302"}
            {urls: 'stun:178.250.157.153:3478'},
            {
                urls: "turn:178.250.157.153:3478",
                username: "test",
                credential: "test123"
            }
        ]
};

// Set up audio and video regardless of what devices are present.
let sdpConstraints = {
    offerToReceiveAudio: true,
    offerToReceiveVideo: true
};

/////////////////////////////////////////////

let socket;
let callSocket;
function connectSocket() {
    let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
    console.log(ws_scheme);
    let url_for_back = ws_scheme + window.location.host + '/ws/call/' + myName + "/"
    if (admin==='admin') {
        url_for_back = ws_scheme + window.location.host + '/ws/call/' + myName + "/" + admin + "/" 
    }
    callSocket = new WebSocket(url_for_back);

    callSocket.onopen = event =>{
    //let's send myName to the socket
        callSocket.send(JSON.stringify({
            type: 'login',
            data: {
                name: myName
            }
        }));
    }

    let father_div = document.querySelector("#call")

    callSocket.onmessage = (e) =>{
        let response = JSON.parse(e.data);

        // console.log(response);

        let type = response.type;

        if(type == 'connection') {
            console.log(response.data.active_admins)
            father_div.innerHTML = ''
            const arr = response.data.active_admins
            nimadir = arr
            for(let i=0; i<arr.length; i++) {
                console.log(arr[i])
                let nimadir1 = arr[i]
                const newCardHTML = `
                    <div class="dialWrapper">
                        <p>${arr[i]}</p>
                        <div class="dialNumpadHWrapper">
                            <div class="dialNumber">
                            </div>
                            <div class="dialNumber">
                                <button class="dialActionButton" onclick="call(${i})">Call</button>
                            </div>
                            <div class="dialNumber">
                            </div>
                        </div>
                    </div>
                `;
                father_div.insertAdjacentHTML('beforeend', newCardHTML)
            }
        }

        if(type == 'call_received') {
           
            onNewCall(response.data)
        }
        if(type == 'extra_call_received') {
           
            onExtraNewCall(response.data)
        }
        if(type == 'new_call') {
           
            beReady()
                .then(bool => {
                    processExtraCall(response.data.to_user)
                })
                }
        if(type == 'call_answered') {
            onCallAnswered(response.data);
        }

        if(type == 'new_user') {
            alert('keldi');
        }
        // if(type == 'extra_answer_call') {
        //     onCallAnswered(response.data);
        // }

        if(type == 'ICEcandidate') {
            onICECandidate(response.data);
        }
        if(type == 'admin_disconnected') {
            console.log(response.data.active_admins)
            father_div.innerHTML = ''
            const arr = response.data.active_admins
            nimadir = arr
            for(let i=0; i<arr.length; i++) {
                console.log(arr[i])
                let nimadir1 = arr[i]
                const newCardHTML = `
                    <div class="dialWrapper">
                        <p>${arr[i]}</p>
                        <div class="dialNumpadHWrapper">
                            <div class="dialNumber">
                            </div>
                            <div class="dialNumber">
                                <button class="dialActionButton" onclick="call(${i})">Call</button>
                            </div>
                            <div class="dialNumber">
                            </div>
                        </div>
                    </div>
                `;
                father_div.insertAdjacentHTML('beforeend', newCardHTML)
            }
        }
    }

    const onNewCall = (data) =>{
        //when other called you
        //show answer button

        otherUser = data.caller;
        remoteRTCMessage = data.rtcMessage

        // document.getElementById("profileImageA").src = baseURL + callerProfile.image;
        document.getElementById("callerName").innerHTML = otherUser;
        document.getElementById("call").style.display = "block";
        document.getElementById("answer").style.display = "block";
    }
    const onExtraNewCall = (data) =>{
        //when other called you
        //show answer button

        otherUser = data.caller;
        remoteRTCMessage = data.rtcMessage

        beReady()
            .then(bool => {
                extraprocessAccept();
            })
    }

    const onCallAnswered = (data) =>{
        //when other accept our call
        remoteRTCMessage = data.rtcMessage
        peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));

        document.getElementById("calling").style.display = "none";

        console.log("Call Started. They Answered");
        // console.log(pc);

        callProgress()
    }

    const onICECandidate = (data) =>{
        // console.log(data);
        console.log("GOT ICE candidate");

        let message = data.rtcMessage

        let candidate = new RTCIceCandidate({
            sdpMLineIndex: message.label,
            candidate: message.candidate
        });

        if (peerConnection) {
            console.log("ICE candidate Added");
            peerConnection.addIceCandidate(candidate);
        } else {
            console.log("ICE candidate Pushed");
            iceCandidatesFromCaller.push(candidate);
        }

    }

}

/**
 * 
 * @param {Object} data 
 * @param {number} data.name - the name of the user to call
 * @param {Object} data.rtcMessage - the rtc create offer object
 */
function sendCall(data) {
    //to send a call
    console.log("Send Call");

    // socket.emit("call", data);
    callSocket.send(JSON.stringify({
        type: 'call',
        data
    }));

    document.getElementById("call").style.display = "block";
    // document.getElementById("profileImageCA").src = baseURL + otherUserProfile.image;
    document.getElementById("otherUserNameCA").innerHTML = otherUser;
    document.getElementById("calling").style.display = "block";
}



/**
 * 
 * @param {Object} data 
 * @param {number} data.caller - the caller name
 * @param {Object} data.rtcMessage - answer rtc sessionDescription object
 */
function answerCall(data) {
    //to answer a call
    // socket.emit("answerCall", data);
    callSocket.send(JSON.stringify({
        type: 'answer_call',
        data
    }));
    callProgress();
}

function extraanswerCall(data) {
    //to answer a call
    // socket.emit("answerCall", data);
    callSocket.send(JSON.stringify({
        type: 'answer_call',
        data
    }));
    callProgress();
}
/**
 * 
 * @param {Object} data 
 * @param {number} data.user - the other user //either callee or caller 
 * @param {Object} data.rtcMessage - iceCandidate data 
 */
function sendICEcandidate(data) {
    //send only if we have caller, else no need to
    console.log("Send ICE candidate");
    // socket.emit("ICEcandidate", data)
    callSocket.send(JSON.stringify({
        type: 'ICEcandidate',
        data
    }));

}

function beReady() {
    return navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true
    })
        .then(stream => {
            localStream = stream;
            localVideo.srcObject = stream;

            return createConnectionAndAddStream()
        })
        .catch(function (e) {
            alert('getUserMedia() error: ' + e.name);
        });
}

function createConnectionAndAddStream() {
    createPeerConnection();
    peerConnection.addStream(localStream);
    return true;
}

function processExtraCall(userName) {
    peerConnection.createOffer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);
        callSocket.send(JSON.stringify({
            type: 'extra_call',
            data: {
                name: userName,
                rtcMessage: sessionDescription
            }
        }));
    }, (error) => {
        console.log("Error");
    });
}

function processCall(userName) {
    peerConnection.createOffer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);
        sendCall({
            name: userName,
            rtcMessage: sessionDescription
        })
    }, (error) => {
        console.log("Error");
    });
}

function processAccept() {

    peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
    peerConnection.createAnswer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);

        if (iceCandidatesFromCaller.length > 0) {
            //I am having issues with call not being processed in real world (internet, not local)
            //so I will push iceCandidates I received after the call arrived, push it and, once we accept
            //add it as ice candidate
            //if the offer rtc message contains all thes ICE candidates we can ingore this.
            for (let i = 0; i < iceCandidatesFromCaller.length; i++) {
                //
                let candidate = iceCandidatesFromCaller[i];
                console.log("ICE candidate Added From queue");
                try {
                    peerConnection.addIceCandidate(candidate).then(done => {
                        console.log(done);
                    }).catch(error => {
                        console.log(error);
                    })
                } catch (error) {
                    console.log(error);
                }
            }
            iceCandidatesFromCaller = [];
            console.log("ICE candidate queue cleared");
        } else {
            console.log("NO Ice candidate in queue");
        }

        answerCall({
            caller: otherUser,
            rtcMessage: sessionDescription
        })

    }, (error) => {
        console.log("Error");
    })
}

function extraprocessAccept() {

    peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
    peerConnection.createAnswer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);

        if (iceCandidatesFromCaller.length > 0) {
            //I am having issues with call not being processed in real world (internet, not local)
            //so I will push iceCandidates I received after the call arrived, push it and, once we accept
            //add it as ice candidate
            //if the offer rtc message contains all thes ICE candidates we can ingore this.
            for (let i = 0; i < iceCandidatesFromCaller.length; i++) {
                //
                let candidate = iceCandidatesFromCaller[i];
                console.log("ICE candidate Added From queue");
                try {
                    peerConnection.addIceCandidate(candidate).then(done => {
                        console.log(done);
                    }).catch(error => {
                        console.log(error);
                    })
                } catch (error) {
                    console.log(error);
                }
            }
            iceCandidatesFromCaller = [];
            console.log("ICE candidate queue cleared");
        } else {
            console.log("NO Ice candidate in queue");
        }

        extraanswerCall({
            caller: otherUser,
            rtcMessage: sessionDescription
        })

    }, (error) => {
        console.log("Error");
    })
}

/////////////////////////////////////////////////////////

function createPeerConnection() {
    try {
        peerConnection = new RTCPeerConnection(pcConfig);
        // peerConnection = new RTCPeerConnection();
        peerConnection.onicecandidate = handleIceCandidate;
        peerConnection.onaddstream = handleRemoteStreamAdded;
        peerConnection.onremovestream = handleRemoteStreamRemoved;
        console.log('Created RTCPeerConnnection');
        return;
    } catch (e) {
        console.log('Failed to create PeerConnection, exception: ' + e.message);
        alert('Cannot create RTCPeerConnection object.');
        return;
    }
}

function handleIceCandidate(event) {
    if (event.candidate) {
        console.log("Local ICE candidate");

        sendICEcandidate({
            user: otherUser,
            rtcMessage: {
                label: event.candidate.sdpMLineIndex,
                id: event.candidate.sdpMid,
                candidate: event.candidate.candidate
            }
        })

    } else {
        console.log('End of candidates.');
    }
}


function handleRemoteStreamAdded(event) {
    console.log('Remote stream added.');
    
    // Create a new video element for each remote stream
    const newVideo = document.createElement('video');
    newVideo.style.width = '250px';  // Adjust the width as needed
    newVideo.autoplay = true;
    newVideo.playsinline = true;
    newVideo.id = 'remoteVideo' + event.stream.id;  // Assign a unique ID
    newVideo.srcObject = event.stream;

    // Add the new video element to the grid
    document.getElementById('remoteVideoGrid').appendChild(newVideo);
    remoteVideos[event.stream.id] = newVideo;

    // Update the grid layout based on the number of remote videos
    updateGridLayout();
}

function updateGridLayout() {
    const gridContainer = document.getElementById('remoteVideoGrid');
    const videoCount = Object.keys(remoteVideos).length;

    // Calculate the number of columns based on the number of videos
    const columns = Math.ceil(Math.sqrt(videoCount));

    // Update the grid layout
    gridContainer.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;

    // Update the width of each video element
    const videoWidth = 100 / columns;
    for (const id in remoteVideos) {
        remoteVideos[id].style.width = `${videoWidth}%`;
    }
}


function handleRemoteStreamRemoved(event) {
    console.log('Remote stream removed. Event: ', event);
    remoteVideo.srcObject = null;
    localVideo.srcObject = null;
}

window.onbeforeunload = function () {
    if (callInProgress) {
        stop();
    }
};


function stop() {
    localStream.getTracks().forEach(track => track.stop());
    callInProgress = false;
    peerConnection.close();
    peerConnection = null;
    document.getElementById("call").style.display = "block";
    document.getElementById("answer").style.display = "none";
    document.getElementById("inCall").style.display = "none";
    document.getElementById("calling").style.display = "none";
    document.getElementById("endVideoButton").style.display = "none"
    otherUser = null;
}

function callProgress() {

    document.getElementById("videos").style.display = "block";
    document.getElementById("otherUserNameC").innerHTML = otherUser;
    document.getElementById("inCall").style.display = "block";

    callInProgress = true;
}
