// Toggle between sign-in and sign-up panels
const signInBtn = document.getElementById("signIn");
const signUpBtn = document.getElementById("signUp");
const container = document.querySelector(".container");

signInBtn.addEventListener("click", () => {
    container.classList.remove("right-panel-active");
});

signUpBtn.addEventListener("click", () => {
    container.classList.add("right-panel-active");
});


// Hide each message individually after 3 seconds
const logoutMessage = document.querySelector(".message-container");

if (logoutMessage) {
    setTimeout(() => {
        logoutMessage.classList.add("hidden");
    }, 5000); // Message visible for 5 seconds
}

