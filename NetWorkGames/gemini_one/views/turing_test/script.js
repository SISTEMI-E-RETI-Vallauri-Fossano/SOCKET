function sendMessage() {
    const message = document.getElementById("message").value;
    if (message.trim() === "") return;

    const chatBox = document.getElementById("chat");
    chatBox.innerHTML += `<div>You: ${message}</div>`;

    // Send the message to the server
    fetch("/send_message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => response.json())
    .then(data => {
        chatBox.innerHTML += `<div>AI: ${data.response}</div>`;
    });

    document.getElementById("message").value = "";
}
