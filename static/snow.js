function createSnowflake() {
    const snowflake = document.createElement('div');
    snowflake.className = 'snowflake';
    snowflake.textContent = '❆';
    snowflake.style.left = Math.random() * window.innerWidth + 'px';
    snowflake.style.animationDuration = (3 + Math.random() * 5) + 's';  // 3〜8秒のランダム時間
    snowflake.style.fontSize = (10 + Math.random() * 20) + 'px';  // サイズのランダム化
    document.body.appendChild(snowflake);

    setTimeout(() => {
        snowflake.remove();  // 5秒後に雪の結晶を削除
    }, 5000);  // 5秒後に削除することでDOMの要素数を減らす
}

setInterval(createSnowflake, 200);  // 200msごとに雪を生成