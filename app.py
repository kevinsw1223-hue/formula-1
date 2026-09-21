<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Apex Racer: F1 Grand Prix</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }
    body {
      background-color: #111;
      color: #fff;
      font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }
    #game-container {
      position: relative;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
      border-radius: 8px;
      overflow: hidden;
    }
    canvas {
      display: block;
      background-color: #2e7d32; /* 잔디 배경 */
    }
    .hud {
      position: absolute;
      top: 15px;
      left: 15px;
      right: 15px;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
    }
    .hud-card {
      background: rgba(0, 0, 0, 0.75);
      padding: 10px 20px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(5px);
    }
    .speedometer {
      font-size: 24px;
      font-weight: bold;
      color: #00e676;
    }
    .boost-bar-container {
      width: 150px;
      height: 12px;
      background: #333;
      border-radius: 6px;
      overflow: hidden;
      margin-top: 5px;
      border: 1px solid #555;
    }
    .boost-bar {
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, #ff9100, #ff3d00);
      transition: width 0.1s;
    }
    .lap-info {
      font-size: 20px;
      font-weight: bold;
      color: #ffd54f;
      text-align: right;
    }
    #overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      z-index: 10;
    }
    #overlay h1 {
      font-size: 42px;
      color: #e53935;
      margin-bottom: 10px;
      text-shadow: 0 0 10px rgba(229, 57, 53, 0.5);
      letter-spacing: 2px;
    }
    #overlay p {
      font-size: 16px;
      color: #ccc;
      margin-bottom: 25px;
      text-align: center;
      line-height: 1.6;
    }
    .btn {
      background: #e53935;
      color: white;
      border: none;
      padding: 14px 35px;
      font-size: 18px;
      font-weight: bold;
      border-radius: 30px;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 15px rgba(229, 57, 53, 0.4);
    }
    .btn:hover {
      background: #d32f2f;
      transform: translateY(-2px);
    }
  </style>
</head>
<body>

  <div id="game-container">
    <canvas id="gameCanvas" width="960" height="600"></canvas>
    
    <div class="hud">
      <div class="hud-card">
        <div class="speedometer"><span id="speed-text">0</span> KM/H</div>
        <div style="font-size: 11px; color: #aaa; margin-top: 4px;">ERS BOOST</div>
        <div class="boost-bar-container">
          <div id="boost-bar" class="boost-bar"></div>
        </div>
      </div>
      <div class="hud-card">
        <div class="lap-info">LAP <span id="lap-text">1</span> / 3</div>
        <div style="font-size: 13px; color: #aaa; margin-top: 4px;" id="pos-text">POS: 1st</div>
      </div>
    </div>

    <div id="overlay">
      <h1 id="overlay-title">APEX RACER: F1 GP</h1>
      <p id="overlay-desc">
        [W/A/S/D] 또는 [방향키]로 차량을 조작하세요.<br>
        [Space] 키로 ERS 부스터를 가속에 활용할 수 있습니다.<br>
        AI 레이서를 제치고 3랩을 먼저 완주하세요!
      </p>
      <button class="btn" id="start-btn" onclick="startGame()">레이스 시작</button>
    </div>
  </div>

  <script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // 키 입력 상태
    const keys = {};
    window.addEventListener('keydown', e => keys[e.code] = true);
    window.addEventListener('keyup', e => keys[e.code] = false);

    // 트랙 경로 정의 (오벌 서킷)
    const trackOuter = [
      {x: 200, y: 100}, {x: 760, y: 100}, 
      {x: 880, y: 220}, {x: 880, y: 380}, 
      {x: 760, y: 500}, {x: 200, y: 500}, 
      {x: 80, y: 380},  {x: 80, y: 220}
    ];

    const trackInner = [
      {x: 240, y: 220}, {x: 720, y: 220}, 
      {x: 760, y: 260}, {x: 760, y: 340}, 
      {x: 720, y: 380}, {x: 240, y: 380}, 
      {x: 200, y: 340}, {x: 200, y: 260}
    ];

    // AI 웨이포인트 (레이싱 라인)
    const waypoints = [
      {x: 480, y: 160}, {x: 740, y: 160},
      {x: 820, y: 240}, {x: 820, y: 360},
      {x: 740, y: 440}, {x: 220, y: 440},
      {x: 140, y: 360}, {x: 140, y: 240},
      {x: 220, y: 160}
    ];

    class Car {
      constructor(x, y, color, isUser = false) {
        this.x = x;
        this.y = y;
        this.angle = 0; // 라디안
        this.speed = 0;
        this.maxSpeed = isUser ? 7.5 : 6.8;
        this.accel = 0.15;
        this.friction = 0.98;
        this.turnSpeed = 0.045;
        this.color = color;
        this.isUser = isUser;
        this.width = 30;
        this.height = 16;
        
        // ERS 시스템
        this.boost = 100;
        
        // 경기 진행 상태
        this.lap = 1;
        this.currentWaypoint = 0;
        this.passedFinish = false;
        
        // AI 관련
        this.targetWaypoint = 0;
      }

      update() {
        if (this.isUser) {
          this.handleUserInput();
        } else {
          this.handleAI();
        }

        // 공통 물리 적용
        this.speed *= this.friction;
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;

        // 트랙 이탈 (잔디 감속)
        if (this.isOnGrass()) {
          this.speed *= 0.92;
        }

        // 체크포인트 및 랩 카운트
        this.checkLapProgress();
      }

      handleUserInput() {
        // 가속 및 브레이크
        if (keys['KeyW'] || keys['ArrowUp']) {
          this.speed += this.accel;
        }
        if (keys['KeyS'] || keys['ArrowDown']) {
          this.speed -= this.accel * 0.6;
        }

        // ERS 부스터
        if ((keys['Space'] || keys['ShiftLeft']) && this.boost > 0 && (keys['KeyW'] || keys['ArrowUp'])) {
          this.speed += this.accel * 0.8;
          this.boost = Math.max(0, this.boost - 0.8);
        } else if (this.boost < 100) {
          this.boost = Math.min(100, this.boost + 0.15); // 충전
        }

        // 최대 속도 제어
        const currentMax = (keys['Space'] || keys['ShiftLeft']) && this.boost > 0 ? this.maxSpeed * 1.25 : this.maxSpeed;
        if (this.speed > currentMax) this.speed = currentMax;
        if (this.speed < -this.maxSpeed * 0.3) this.speed = -this.maxSpeed * 0.3;

        // 조향 (속도가 일정 이상일 때만 회전 가능)
        if (Math.abs(this.speed) > 0.2) {
          const dir = this.speed > 0 ? 1 : -1;
          if (keys['KeyA'] || keys['ArrowLeft']) this.angle -= this.turnSpeed * dir;
          if (keys['KeyD'] || keys['ArrowRight']) this.angle += this.turnSpeed * dir;
        }
      }

      handleAI() {
        const target = waypoints[this.targetWaypoint];
        const dx = target.x - this.x;
        const dy = target.y - this.y;
        const targetAngle = Math.atan2(dy, dx);

        // Angle 회전 조절
        let diff = targetAngle - this.angle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;

        if (diff > 0.05) this.angle += this.turnSpeed * 0.9;
        else if (diff < -0.05) this.angle -= this.turnSpeed * 0.9;

        // 속도 유지
        if (this.speed < this.maxSpeed) {
          this.speed += this.accel * 0.85;
        }

        // 웨이포인트 도달 확인
        const dist = Math.hypot(dx, dy);
        if (dist < 60) {
          this.targetWaypoint = (this.targetWaypoint + 1) % waypoints.length;
        }
      }

      isOnGrass() {
        // 간단한 원형/박스 경계 체크로 아스팔트 바깥 판정
        const distFromCenter = Math.hypot(this.x - canvas.width / 2, this.y - canvas.height / 2);
        if (this.x > 220 && this.x < 740 && this.y > 220 && this.y < 380) {
          return true; // 트랙 내부 잔디
        }
        if (this.x < 60 || this.x > 900 || this.y < 80 || this.y > 520) {
          return true; // 트랙 외부 잔디
        }
        return false;
      }

      checkLapProgress() {
        // 피니시 라인 (x: 480, y: 100~220 구간)
        if (this.x > 470 && this.x < 490 && this.y >= 100 && this.y <= 220) {
          if (!this.passedFinish && this.currentWaypoint > 4) {
            this.lap++;
            this.currentWaypoint = 0;
            this.passedFinish = true;
            if (this.isUser) {
              document.getElementById('lap-text').innerText = Math.min(this.lap, 3);
            }
          }
        } else {
          this.passedFinish = false;
        }

        // 웨이포인트 진행도 체크
        const wp = waypoints[this.currentWaypoint];
        if (Math.hypot(wp.x - this.x, wp.y - this.y) < 100) {
          this.currentWaypoint = (this.currentWaypoint + 1) % waypoints.length;
        }
      }

      draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        // 그림자
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(-this.width / 2 + 3, -this.height / 2 + 3, this.width, this.height);

        // 차체 메인
        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);

        // 콕핏 & 날개 (F1 형태 디테일)
        ctx.fillStyle = '#111';
        ctx.fillRect(-this.width / 2 - 3, -this.height / 2 + 1, 5, this.height - 2); // 프론트 윙
        ctx.fillRect(this.width / 2 - 2, -this.height / 2, 4, this.height); // 리어 윙
        ctx.fillRect(-2, -3, 8, 6); // 콕핏

        // 바퀴 4개
        ctx.fillStyle = '#000';
        ctx.fillRect(-this.width / 2 + 4, -this.height / 2 - 3, 7, 3);
        ctx.fillRect(this.width / 2 - 10, -this.height / 2 - 3, 7, 3);
        ctx.fillRect(-this.width / 2 + 4, this.height / 2, 7, 3);
        ctx.fillRect(this.width / 2 - 10, this.height / 2, 7, 3);

        ctx.restore();
      }
    }

    // 변수 초기화
    let playerCar;
    let aiCars = [];
    let isRaceRunning = false;
    const TOTAL_LAPS = 3;

    function initRace() {
      playerCar = new Car(440, 140, '#e53935', true); // 사용자 (레드)
      aiCars = [
        new Car(410, 180, '#00e676', false), // AI 1 (그린)
        new Car(380, 140, '#29b6f6', false)  // AI 2 (블루)
      ];
    }

    function drawTrack() {
      // 아스팔트 노면
      ctx.fillStyle = '#37474f';
      ctx.beginPath();
      drawPoly(trackOuter);
      ctx.fill();

      // 트랙 내중앙 잔디
      ctx.fillStyle = '#2e7d32';
      ctx.beginPath();
      drawPoly(trackInner);
      ctx.fill();

      // 억제선/커브 (연석)
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 4;
      ctx.stroke();

      // 피니시 라인 (체커기 패턴)
      ctx.save();
      ctx.fillStyle = '#fff';
      for (let i = 100; i < 220; i += 15) {
        ctx.fillRect(480, i, 8, 8);
        ctx.fillRect(488, i + 8, 8, 8);
      }
      ctx.restore();
    }

    function drawPoly(points) {
      ctx.moveTo(points[0].x, points[0].y);
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }
      ctx.closePath();
    }

    function updateHUD() {
      // 속도 및 ERS 업데이트
      const kmh = Math.round(Math.abs(playerCar.speed) * 38);
      document.getElementById('speed-text').innerText = kmh;
      document.getElementById('boost-bar').style.width = playerCar.boost + '%';

      // 순위 계산
      const allCars = [playerCar, ...aiCars];
      allCars.sort((a, b) => {
        if (a.lap !== b.lap) return b.lap - a.lap;
        return b.currentWaypoint - a.currentWaypoint;
      });

      const pos = allCars.indexOf(playerCar) + 1;
      const posSuffix = pos === 1 ? '1st' : pos === 2 ? '2nd' : '3rd';
      document.getElementById('pos-text').innerText = `POS: ${posSuffix}`;
    }

    function checkRaceEnd() {
      if (playerCar.lap > TOTAL_LAPS) {
        endRace('VICTORY!', '#00e676', '축하합니다! F1 그랑프리에서 우승하셨습니다!');
      } else {
        aiCars.forEach((ai, idx) => {
          if (ai.lap > TOTAL_LAPS) {
            endRace('DEFEAT...', '#e53935', `AI 레이서가 먼저 완주했습니다. (${idx + 1}위 기록)`);
          }
        });
      }
    }

    function startGame() {
      document.getElementById('overlay').style.display = 'none';
      initRace();
      isRaceRunning = true;
      requestAnimationFrame(gameLoop);
    }

    function endRace(title, color, desc) {
      isRaceRunning = false;
      const overlay = document.getElementById('overlay');
      const titleElem = document.getElementById('overlay-title');
      const descElem = document.getElementById('overlay-desc');
      const btn = document.getElementById('start-btn');

      overlay.style.display = 'flex';
      titleElem.innerText = title;
      titleElem.style.color = color;
      descElem.innerText = desc;
      btn.innerText = '다시 레이스';
    }

    function gameLoop() {
      if (!isRaceRunning) return;

      // 1. Update
      playerCar.update();
      aiCars.forEach(ai => ai.update());
      updateHUD();
      checkRaceEnd();

      // 2. Draw
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawTrack();
      aiCars.forEach(ai => ai.draw());
      playerCar.draw();

      requestAnimationFrame(gameLoop);
    }

    // 초기 화면 렌더링
    initRace();
    drawTrack();
    playerCar.draw();
    aiCars.forEach(ai => ai.draw());
  </script>
</body>
</html>
