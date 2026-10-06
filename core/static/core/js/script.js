window.history.scrollRestoration = "manual";

window.addEventListener("load", function () {
    window.scrollTo(0, 0);
});

const passwordToggle = document.getElementById("password-toggle");
const passwordInput = document.getElementById("password");

if (passwordToggle && passwordInput) {

    passwordToggle.addEventListener("click", function () {

        const isPassword = passwordInput.type === "password";

        passwordInput.type = isPassword ? "text" : "password";

        passwordToggle.setAttribute(
            "aria-label",
            isPassword ? "Hide password" : "Show password"
        );

        passwordToggle.setAttribute(
            "aria-pressed",
            isPassword ? "true" : "false"
        );

    });

}