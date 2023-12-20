let currentRecipient = '';
let chatInput = $('#chat-input');
let chatButton = $('#btn-send');
let userList = $('#user-list');
let messageList = $('#messages');

function countActiveUsers(users) {
    let activeUserCount = 0;
    for (let i = 0; i < users.length; i++) {
        if (users[i].status === 'active') {
            activeUserCount++;
        }
    }
    return activeUserCount;
}

function updateUserList() {
    $.getJSON('api/v1/user/', function (data) {

        userList.empty();

        const activeUserCount = countActiveUsers(data);

        console.log(`Active User Count: ${activeUserCount}`);

        userList.children('.user').remove();
        for (let i = 0; i < data.length; i++) {
            const user = data[i];
            const userItem = `
            <div class="mt-4 h-40 user" data-username="${user.username}" data-userid="${user.id}">
                <div class="chat-tab-list custom-scrollbar">
                    <ul class="nav flex-column nav-pills nav-pills-soft">
                        <li data-bs-dismiss="offcanvas">
                            <a href="" class="nav-link active text-start" data-bs-toggle="pill" role="tab">
                                <div class="d-flex">
                                <div class="flex-shrink-0 avatar avatar-story me-2">
                                    <img class="avatar-img rounded-circle" src="../../static/assets/images/avatar/10.jpg" alt="">
                                </div>
                                <div class="flex-grow-1 d-block">
                                    <h6 class="mb-0 mt-1">${user.username}</h6>
                                    <div class="user-last-message">${user.lastMessage}</div>
                                </div>
                                </div>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>`;
            $(userItem).appendTo('#user-list');

            // Oxirgi xabar malumotini olish
            getLastMessage(user.username, i);
        }

        $('.user').click(function () {
            userList.children('.active').removeClass('active');
            let selected = $(this);
            selected.addClass('active');
            const username = selected.data('username');
            setCurrentRecipient(username);
        });
    });
}

function getLastMessage(username, index) {
    $.getJSON(`api/v1/get_last_message/${username}/`, function (data) {
        const lastMessage = data.body || 'No messages';
        $(`.user-last-message:eq(${index})`).text(lastMessage);
    });
}

function drawMessage(message) {
    let position = 'left';
    const date = new Date(message.timestamp);
    // Soatni olish
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const formattedTime = `${hours}:${minutes}`

    if (message.user === currentUser) position = 'right';
    const messageItem = `
            <li class="message ${position}">
                <div class="avatar"><img class="avatar-img rounded-circle" src="../../static/assets/images/avatar/10.jpg" alt=""></div><br>
                <div class="text_wrapper">
                    <p class="text">${message.body}</p><br>
                </div>
                <div class="box">
                    <span class="small">${formattedTime}</span>
                    <span class="seen-badge">
                        ${message.is_seen ? '<i class="bi bi-check"></i>' : '<i class="bi bi-check-all"></i>'}
                    </span>
                </div>
            </li>`;
    $(messageItem).appendTo('#messages');
}

function getConversation(recipient) {
    $.getJSON(`/api/v1/message/?target=${recipient}`, function (data) {
        messageList.children('.message').remove();
        for (let i = data['results'].length - 1; i >= 0; i--) {
            drawMessage(data['results'][i]);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });

}

function getMessageById(message) {
    id = JSON.parse(message).message
    $.getJSON(`/api/v1/message/${id}/`, function (data) {
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            drawMessage(data);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });
}

function sendMessage(recipient, body) {
    $.post('/api/v1/message/', {
        recipient: recipient,
        body: body
    }).fail(function () {
        alert('Error! Check console!');
    });
}

function setCurrentRecipient(username) {
    currentRecipient = username;
    getConversation(currentRecipient);
    enableInput();
}


function enableInput() {
    chatInput.prop('disabled', false);
    chatButton.prop('disabled', false);
    chatInput.focus();
}

function disableInput() {
    chatInput.prop('disabled', true);
    chatButton.prop('disabled', true);
}

$(document).ready(function () {
    updateUserList();
    disableInput();

//    let socket = new WebSocket(`ws://127.0.0.1:8000/?session_key=${sessionKey}`);
    var socket = new WebSocket(
        'ws://' + window.location.host +
        '/ws?session_key=${sessionKey}')

    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
        if (chatInput.val().length > 0) {
            sendMessage(currentRecipient, chatInput.val());
            chatInput.val('');
        }
    });

    socket.onmessage = function (e) {
        getMessageById(e.data);
    };
});