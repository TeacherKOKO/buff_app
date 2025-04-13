const canvas = document.getElementById("snow-canvas");
const ctx = canvas.getContext("2d");

let w = window.innerWidth;
let h = window.innerHeight;
canvas.width = w;
canvas.height = h;

const snowflakes = [];
const maxFlakes = 300;

for (let i = 0; i < maxFlakes; i++) {
    snowflakes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 2 + 1,
        d: Math.random() * maxFlakes,
        speed: Math.random() * 3 + 0.5,
        wind: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.6 + 0.4
    });
}

function draw() {
    ctx.clearRect(0, 0, w, h);
    for (let i = 0; i < maxFlakes; i++) {
        const f = snowflakes[i];
        const gradient = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, f.r);
        gradient.addColorStop(0, `rgba(255, 255, 255, ${f.opacity})`);
        gradient.addColorStop(0.5, `rgba(200, 240, 255, ${f.opacity * 0.5})`);
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

        ctx.beginPath();
        ctx.fillStyle = gradient;
        ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
        ctx.fill();
    }
    update();
}

let angle = 0;
function update() {
    angle += 0.01;
    for (let i = 0; i < maxFlakes; i++) {
        const f = snowflakes[i];
        f.y += f.speed;
        f.x += Math.cos(angle + f.d) * f.wind;

        if (f.y > h || f.x > w || f.x < 0) {
            snowflakes[i] = {
                x: Math.random() * w,
                y: 0,
                r: f.r,
                d: f.d,
                speed: Math.random() * 3 + 0.5,
                wind: Math.random() * 2 + 0.5,
                opacity: Math.random() * 0.6 + 0.4
            };
        }
    }
}

setInterval(draw, 25);

window.addEventListener("resize", () => {
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = w;
    canvas.height = h;
});
