document.addEventListener("DOMContentLoaded", function () {
    for (let i = 0; i < 50; i++) {
        let snow = document.createElement("div");
        snow.className = "snowflake";
        snow.textContent = "❄";
        snow.style.left = Math.random() * 100 + "vw";
        snow.style.animationDuration = 3 + Math.random() * 5 + "s";
        snow.style.fontSize = (Math.random() * 10 + 10) + "px";
        snow.style.opacity = Math.random();
        document.body.appendChild(snow);
    }
});
