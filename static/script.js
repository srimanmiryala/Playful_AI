let board = null;
let game = new Chess();



// Initialize the chessboard
board = Chessboard("chessboard", {
    draggable: true,
    position: "start",
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
});


// Initialize chessboard
function initBoard() {
    board = Chessboard('board', {
        draggable: true,
        dropOffBoard: 'snapback',
        position: 'start',
        onDrop: handleMove
    });
}

// Handle piece movement
async function handleMove(source, target) {
    let move = game.move({ from: source, to: target, promotion: 'q' });

    if (move === null) return 'snapback';

    // Send move to the Flask server
    const response = await fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: move.san })
    });

    const data = await response.json();
    if (data.status === "success") {
        game.load(data.fen);
        board.position(game.fen());
    } else {
        alert("Invalid move!");
        return 'snapback';
    }
}

// Reset board
async function resetBoard() {
    const response = await fetch('/reset', { method: 'POST' });
    const data = await response.json();
    game.reset();
    board.position('start');
}

window.onload = initBoard;

//sendMessage
function sendMessage() {
    let inputField = document.getElementById("user-input");
    let message = inputField.value.trim();

    if (message === "") return;

    let chatBox = document.getElementById("chat-box");

    // Display user message
    chatBox.innerHTML += `<div id="user_input" style="color: cyan;"> ${message}</div>`;

    // Send request to Flask backend (modify as needed)
    fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ query: message }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        chatBox.innerHTML += `<div id="bot_reply" style="color: yellow;">${data.response}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    inputField.value = "";
}

//const difficultySelector = document.getElementById("difficulty-selector");
//console.log(difficultySelector)


    const slider = document.getElementById("difficulty-selector");
    const output = document.getElementById("difficulty-value");

    // Function to adjust step dynamically
    slider.addEventListener("input", function () {
        let value = parseInt(slider.value);

        if (value >= 1 && value <= 5) {
            slider.step = 1;
        } else if (value > 5 && value <= 10) {
            slider.step = 2;
        } else if (value > 10 && value <= 15) {
            slider.step = 3;
        } else {
            slider.step = 5;
        }

        output.textContent = ""+value;
    });

