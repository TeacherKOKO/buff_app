document.addEventListener("DOMContentLoaded", () => {
    const snowContainer = document.createElement("div");
    snowContainer.style.position = "fixed";
    snowContainer.style.top = 0;
    snowContainer.style.left = 0;
    snowContainer.style.width = "100%";
    snowContainer.style.height = "100%";
    snowContainer.style.pointerEvents = "none";
    snowContainer.style.zIndex = "9999";
    document.body.appendChild(snowContainer);
  
    const createSnowflake = () => {
      const snowflake = document.createElement("div");
      snowflake.textContent = "❄️";
      snowflake.style.position = "absolute";
      snowflake.style.top = "-2em";
      snowflake.style.left = Math.random() * 100 + "vw";
      snowflake.style.fontSize = Math.random() * 10 + 10 + "px";
      snowflake.style.opacity = Math.random();
      snowflake.style.animation = `fall ${Math.random() * 5 + 5}s linear forwards`;
      snowContainer.appendChild(snowflake);
  
      setTimeout(() => {
        snowflake.remove();
      }, 10000);
    };
  
    setInterval(createSnowflake, 200);
  });  