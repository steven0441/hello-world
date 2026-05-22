import * as Phaser from 'phaser';
import type { BeanState } from '@/types';

const CELL_W = 600;
const CELL_H = 400;

// Layout positions
const DESK_X = 280;
const DESK_Y = 130;
const BED_X = 90;
const BED_Y = 110;
const SAFE_X = 490;
const SAFE_Y = 120;
const RESTROOM_X = 100;
const RESTROOM_Y = 290;
const IDLE_X = 290;
const IDLE_Y = 230;

export class BeanCellScene extends Phaser.Scene {
  private bean!: Phaser.GameObjects.Container;
  private beanBody!: Phaser.GameObjects.Graphics;
  private speechBubble!: Phaser.GameObjects.Container;
  private speechText!: Phaser.GameObjects.Text;
  private bubbleBox!: Phaser.GameObjects.Graphics;
  private zParticles: Phaser.GameObjects.Text[] = [];
  private currentState: BeanState = 'idle';
  private idleTween?: Phaser.Tweens.Tween;
  private blinkTimer?: Phaser.Time.TimerEvent;
  private typingTimer?: Phaser.Time.TimerEvent;
  private beanEyes!: Phaser.GameObjects.Graphics;
  private beanArm!: Phaser.GameObjects.Graphics;
  private alertIndicator!: Phaser.GameObjects.Text;
  private milestoneOverlay!: Phaser.GameObjects.Container;
  private decorations: Phaser.GameObjects.Text[] = [];

  constructor() {
    super({ key: 'BeanCellScene' });
  }

  preload() {}

  create() {
    this.drawCell();
    this.createBean();
    this.createSpeechBubble();
    this.createAlertIndicator();
    this.createMilestoneOverlay();
    this.startIdleBehavior();

    // Listen to external events (from React via EventBus)
    this.game.events.on('bean:state', this.setState, this);
    this.game.events.on('bean:speak', this.speak, this);
    this.game.events.on('bean:milestone', this.showMilestone, this);
    this.game.events.on('bean:decorate', this.addDecoration, this);
  }

  destroy() {
    this.game.events.off('bean:state', this.setState, this);
    this.game.events.off('bean:speak', this.speak, this);
    this.game.events.off('bean:milestone', this.showMilestone, this);
    this.game.events.off('bean:decorate', this.addDecoration, this);
  }

  // ─── Cell Drawing ────────────────────────────────────────────────────────

  private drawCell() {
    // Floor — office carpet (beige/cream tiles)
    const floor = this.add.graphics();
    floor.fillStyle(0xe8e0d0, 1);
    floor.fillRect(0, 0, CELL_W, CELL_H);

    // Carpet tile grid
    const tileG = this.add.graphics();
    tileG.lineStyle(0.5, 0xd4c9b0, 0.5);
    for (let x = 0; x <= CELL_W; x += 40) tileG.lineBetween(x, 0, x, CELL_H);
    for (let y = 0; y <= CELL_H; y += 40) tileG.lineBetween(0, y, CELL_W, y);

    // Walls — off-white drywall
    const walls = this.add.graphics();
    walls.fillStyle(0xf0ebe0, 1);
    walls.fillRect(0, 0, CELL_W, 60);         // top wall
    walls.fillRect(0, 0, 50, CELL_H);         // left wall
    walls.fillRect(CELL_W - 50, 0, 50, CELL_H); // right wall

    // Wall baseboard
    const baseboard = this.add.graphics();
    baseboard.lineStyle(3, 0xc8b89a, 1);
    baseboard.lineBetween(50, 60, CELL_W - 50, 60);
    baseboard.lineBetween(50, 60, 50, CELL_H);
    baseboard.lineBetween(CELL_W - 50, 60, CELL_W - 50, CELL_H);

    // Fluorescent lights on ceiling
    this.drawFluorescentLights();

    // ─ Furniture ─
    this.drawBed();
    this.drawDesk();
    this.drawSafe();
    this.drawRestroom();
    this.drawIronBars();
  }

  private drawFluorescentLights() {
    const lights = this.add.graphics();
    // Two fluorescent strips
    for (const x of [180, 420]) {
      lights.fillStyle(0xf5f0e0, 1);
      lights.fillRect(x - 60, 8, 120, 14);
      lights.lineStyle(1, 0xe0d8c0, 1);
      lights.strokeRect(x - 60, 8, 120, 14);
      // Glow effect
      lights.fillStyle(0xfffff0, 0.3);
      lights.fillRect(x - 70, 4, 140, 22);
    }
    // Flicker effect
    this.time.addEvent({
      delay: 4000 + Math.random() * 6000,
      loop: true,
      callback: () => this.flickerLights(lights),
    });
  }

  private flickerLights(lights: Phaser.GameObjects.Graphics) {
    this.tweens.add({
      targets: lights,
      alpha: { from: 1, to: 0.3 },
      duration: 50,
      yoyo: true,
      repeat: 2,
    });
  }

  private drawBed() {
    const g = this.add.graphics();
    // Bed frame
    g.fillStyle(0x8b7355, 1);
    g.fillRect(BED_X - 35, BED_Y - 25, 70, 50);
    // Mattress
    g.fillStyle(0xfafafa, 1);
    g.fillRect(BED_X - 32, BED_Y - 22, 64, 44);
    // Pillow
    g.fillStyle(0xf0f0f0, 1);
    g.fillRoundedRect(BED_X - 28, BED_Y - 20, 30, 20, 3);
    // Sheet fold
    g.lineStyle(1, 0xddd8d0, 1);
    g.lineBetween(BED_X - 32, BED_Y + 2, BED_X + 32, BED_Y + 2);
    // Label
    this.add.text(BED_X, BED_Y + 38, 'COT', {
      fontSize: '8px', color: '#888880', fontFamily: 'monospace',
    }).setOrigin(0.5);
  }

  private drawDesk() {
    const g = this.add.graphics();
    // Desk surface
    g.fillStyle(0x8b6914, 1);
    g.fillRect(DESK_X - 55, DESK_Y - 10, 110, 60);
    g.fillStyle(0xa07820, 1);
    g.fillRect(DESK_X - 53, DESK_Y - 8, 106, 8);
    // Monitor
    g.fillStyle(0x1a1a2e, 1);
    g.fillRect(DESK_X - 20, DESK_Y - 38, 40, 28);
    g.fillStyle(0x0d4f8b, 1);
    g.fillRect(DESK_X - 17, DESK_Y - 35, 34, 22);
    // Monitor stand
    g.fillStyle(0x1a1a2e, 1);
    g.fillRect(DESK_X - 4, DESK_Y - 10, 8, 4);
    // Keyboard
    g.fillStyle(0xd0c8b8, 1);
    g.fillRect(DESK_X - 22, DESK_Y + 6, 44, 12);
    // Papers/folders
    g.fillStyle(0xfffde8, 1);
    g.fillRect(DESK_X + 25, DESK_Y - 5, 22, 28);
    g.fillStyle(0xffecb3, 1);
    g.fillRect(DESK_X + 27, DESK_Y - 8, 20, 28);
    // Label
    this.add.text(DESK_X, DESK_Y + 58, 'DESK', {
      fontSize: '8px', color: '#888880', fontFamily: 'monospace',
    }).setOrigin(0.5);
  }

  private drawSafe() {
    const g = this.add.graphics();
    // Safe body
    g.fillStyle(0x2c3040, 1);
    g.fillRect(SAFE_X - 22, SAFE_Y - 28, 44, 48);
    // Safe door
    g.lineStyle(2, 0x404860, 1);
    g.strokeRect(SAFE_X - 18, SAFE_Y - 24, 36, 40);
    // Dial
    g.fillStyle(0x8899aa, 1);
    g.fillCircle(SAFE_X, SAFE_Y - 4, 8);
    g.fillStyle(0x6677aa, 1);
    g.fillCircle(SAFE_X, SAFE_Y - 4, 5);
    // Dial notch
    g.lineStyle(2, 0xccddee, 1);
    g.lineBetween(SAFE_X, SAFE_Y - 4, SAFE_X + 4, SAFE_Y - 8);
    // Handle
    g.fillStyle(0x607080, 1);
    g.fillRect(SAFE_X + 10, SAFE_Y + 6, 6, 12);
    // Label
    this.add.text(SAFE_X, SAFE_Y + 28, 'SAFE', {
      fontSize: '8px', color: '#888880', fontFamily: 'monospace',
    }).setOrigin(0.5);
  }

  private drawRestroom() {
    const g = this.add.graphics();
    // Partition walls
    g.fillStyle(0xf0ebe0, 1);
    g.fillRect(RESTROOM_X - 45, RESTROOM_Y - 35, 90, 3);  // top
    g.fillRect(RESTROOM_X + 42, RESTROOM_Y - 35, 3, 60);  // right
    // Door (partial — open)
    g.lineStyle(2, 0x8b7355, 1);
    g.lineBetween(RESTROOM_X - 45, RESTROOM_Y - 35, RESTROOM_X - 45, RESTROOM_Y + 25);
    // Toilet
    g.fillStyle(0xffffff, 1);
    g.fillEllipse(RESTROOM_X - 20, RESTROOM_Y + 5, 22, 28);
    g.fillStyle(0xf8f8f8, 1);
    g.fillRect(RESTROOM_X - 30, RESTROOM_Y - 12, 20, 8);
    // Sink
    g.fillStyle(0xfafafa, 1);
    g.fillRect(RESTROOM_X + 8, RESTROOM_Y - 8, 24, 20);
    g.lineStyle(1, 0xdddddd, 1);
    g.strokeRect(RESTROOM_X + 8, RESTROOM_Y - 8, 24, 20);
    // Faucet
    g.fillStyle(0xc0c8d0, 1);
    g.fillRect(RESTROOM_X + 17, RESTROOM_Y - 14, 6, 8);
    // Label
    this.add.text(RESTROOM_X, RESTROOM_Y + 38, 'RESTROOM', {
      fontSize: '8px', color: '#888880', fontFamily: 'monospace',
    }).setOrigin(0.5);
  }

  private drawIronBars() {
    const g = this.add.graphics();
    // Bottom bar base
    g.fillStyle(0x2a2a2a, 1);
    g.fillRect(180, CELL_H - 40, 240, 8);
    g.fillRect(180, CELL_H - 8, 240, 8);
    // Bars
    g.lineStyle(5, 0x3a3a3a, 1);
    for (let x = 195; x <= 408; x += 22) {
      g.lineBetween(x, CELL_H - 40, x, CELL_H - 8);
    }
    // Bar sheen
    g.lineStyle(1, 0x606060, 0.6);
    for (let x = 197; x <= 408; x += 22) {
      g.lineBetween(x, CELL_H - 39, x, CELL_H - 9);
    }
    // Label above bars
    this.add.text(300, CELL_H - 50, '⛓  C O N D E M N E D  ⛓', {
      fontSize: '9px', color: '#666655', fontFamily: 'monospace', letterSpacing: 2,
    }).setOrigin(0.5);
  }

  // ─── Bean Sprite (Dylan from Severance) ──────────────────────────────────

  private createBean() {
    this.bean = this.add.container(IDLE_X, IDLE_Y);

    this.beanBody = this.add.graphics();
    this.beanEyes = this.add.graphics();
    this.beanArm = this.add.graphics();

    this.drawBeanSprite();

    this.bean.add([this.beanBody, this.beanArm, this.beanEyes]);
    this.bean.setDepth(10);
  }

  private drawBeanSprite() {
    const g = this.beanBody;
    g.clear();

    // Shoes — black
    g.fillStyle(0x1c1c1c, 1);
    g.fillEllipse(-5, 16, 10, 6);
    g.fillEllipse(5, 16, 10, 6);

    // Slacks — near-black charcoal
    g.fillStyle(0x1a252f, 1);
    g.fillRect(-8, 4, 7, 14);
    g.fillRect(2, 4, 7, 14);

    // Shirt — pale office blue
    g.fillStyle(0xd6eaf8, 1);
    g.fillRect(-8, -8, 16, 14);

    // Blazer / jacket — dark navy
    g.fillStyle(0x2c3e50, 1);
    g.fillRect(-10, -8, 5, 14);    // left lapel
    g.fillRect(6, -8, 5, 14);     // right lapel
    g.fillRect(-10, -8, 20, 4);   // shoulders

    // Tie — small dark red stripe
    g.fillStyle(0x8b1a1a, 1);
    g.fillRect(-1, -6, 3, 10);

    // Head — skin tone
    g.fillStyle(0xf5cba7, 1);
    g.fillCircle(0, -16, 9);

    // Hair — dark
    g.fillStyle(0x2c2c2c, 1);
    g.fillRect(-9, -23, 18, 6);
    g.fillRect(-9, -23, 18, 3);

    // Glasses frames
    const eyes = this.beanEyes;
    eyes.clear();
    eyes.lineStyle(1.5, 0x7f8c8d, 1);
    eyes.strokeRect(-8, -19, 6, 5);
    eyes.strokeRect(2, -19, 6, 5);
    eyes.lineBetween(-2, -17, 2, -17); // bridge

    // Eyes (pupils)
    eyes.fillStyle(0x1a1a1a, 1);
    eyes.fillRect(-6, -17, 2, 2);
    eyes.fillRect(4, -17, 2, 2);

    // Mouth — neutral flat line
    eyes.lineStyle(1, 0xcc9977, 1);
    eyes.lineBetween(-3, -10, 3, -10);

    // Arms at sides
    const arm = this.beanArm;
    arm.clear();
    arm.fillStyle(0x2c3e50, 1);
    arm.fillRect(-14, -7, 5, 10);
    arm.fillRect(10, -7, 5, 10);
    // Hands
    arm.fillStyle(0xf5cba7, 1);
    arm.fillCircle(-12, 5, 4);
    arm.fillCircle(13, 5, 4);
  }

  private drawBeanTyping() {
    const arm = this.beanArm;
    arm.clear();
    arm.fillStyle(0x2c3e50, 1);
    // Arms bent forward (typing)
    arm.fillRect(-13, -5, 5, 8);
    arm.fillRect(9, -5, 5, 8);
    // Hands forward
    arm.fillStyle(0xf5cba7, 1);
    arm.fillCircle(-10, 4, 4);
    arm.fillCircle(11, 4, 4);
  }

  // ─── Speech Bubble ───────────────────────────────────────────────────────

  private createSpeechBubble() {
    this.speechBubble = this.add.container(0, 0).setDepth(20).setVisible(false);
    this.bubbleBox = this.add.graphics();
    this.speechText = this.add.text(0, 0, '', {
      fontSize: '10px', color: '#1a1a2e', fontFamily: 'monospace',
      wordWrap: { width: 160 },
    }).setOrigin(0);
    this.speechBubble.add([this.bubbleBox, this.speechText]);
  }

  speak(text: string, duration = 4000) {
    this.speechBubble.setVisible(true);
    this.speechText.setText(text);
    const tw = this.speechText.width + 16;
    const th = this.speechText.height + 10;

    this.bubbleBox.clear();
    this.bubbleBox.fillStyle(0xfffff8, 0.95);
    this.bubbleBox.fillRoundedRect(-tw / 2 - 8, -th - 12, tw, th, 6);
    this.bubbleBox.lineStyle(1, 0x888880, 0.8);
    this.bubbleBox.strokeRoundedRect(-tw / 2 - 8, -th - 12, tw, th, 6);
    // Tail
    this.bubbleBox.fillStyle(0xfffff8, 0.95);
    this.bubbleBox.fillTriangle(-4, -12, 4, -12, 0, -4);

    this.speechText.setPosition(-tw / 2, -th - 8);
    this.speechBubble.setPosition(this.bean.x, this.bean.y);

    if (duration > 0) {
      this.time.delayedCall(duration, () => this.speechBubble.setVisible(false));
    }
  }

  // ─── Alert Indicator ─────────────────────────────────────────────────────

  private createAlertIndicator() {
    this.alertIndicator = this.add.text(300, 10, '', {
      fontSize: '11px', color: '#ff4040', fontFamily: 'monospace', fontStyle: 'bold',
    }).setOrigin(0.5, 0).setDepth(15).setVisible(false);
  }

  // ─── Milestone Overlay ───────────────────────────────────────────────────

  private createMilestoneOverlay() {
    this.milestoneOverlay = this.add.container(CELL_W / 2, CELL_H / 2).setDepth(50).setVisible(false);

    const bg = this.add.graphics();
    bg.fillStyle(0x080810, 0.88);
    bg.fillRoundedRect(-160, -90, 320, 180, 12);
    bg.lineStyle(2, 0xf5c542, 1);
    bg.strokeRoundedRect(-160, -90, 320, 180, 12);

    const starText = this.add.text(0, -70, '✦  MILESTONE  ✦', {
      fontSize: '12px', color: '#f5c542', fontFamily: 'monospace', fontStyle: 'bold',
    }).setOrigin(0.5);

    const iconText = this.add.text(0, -20, '', {
      fontSize: '32px',
    }).setOrigin(0.5).setName('ms-icon');

    const labelText = this.add.text(0, 30, '', {
      fontSize: '11px', color: '#e2e8f0', fontFamily: 'monospace',
    }).setOrigin(0.5).setName('ms-label');

    const subText = this.add.text(0, 60, 'Bean will keep this. Forever.', {
      fontSize: '9px', color: '#4a5568', fontFamily: 'monospace',
    }).setOrigin(0.5);

    this.milestoneOverlay.add([bg, starText, iconText, labelText, subText]);
  }

  showMilestone({ icon, label }: { icon: string; label: string }) {
    const iconEl = this.milestoneOverlay.getByName('ms-icon') as Phaser.GameObjects.Text;
    const labelEl = this.milestoneOverlay.getByName('ms-label') as Phaser.GameObjects.Text;
    iconEl.setText(icon);
    labelEl.setText(label);

    this.milestoneOverlay.setVisible(true).setAlpha(0);
    this.tweens.add({
      targets: this.milestoneOverlay,
      alpha: 1,
      duration: 500,
      onComplete: () => {
        this.time.delayedCall(3500, () => {
          this.tweens.add({
            targets: this.milestoneOverlay,
            alpha: 0,
            duration: 500,
            onComplete: () => this.milestoneOverlay.setVisible(false),
          });
        });
      },
    });

    this.setState('celebrating');
  }

  addDecoration(icon: string) {
    const x = 460 + (this.decorations.length % 3) * 20;
    const y = 170 + Math.floor(this.decorations.length / 3) * 20;
    const deco = this.add.text(x, y, icon, { fontSize: '14px' }).setDepth(5);
    this.decorations.push(deco);
  }

  // ─── State Machine ────────────────────────────────────────────────────────

  setState(state: BeanState) {
    if (this.currentState === state) return;
    this.clearState();
    this.currentState = state;

    switch (state) {
      case 'working': this.enterWorking(); break;
      case 'sleeping': this.enterSleeping(); break;
      case 'safe': this.enterSafe(); break;
      case 'alert': this.enterAlert(); break;
      case 'celebrating': this.enterCelebrating(); break;
      default: this.enterIdle(); break;
    }
  }

  private clearState() {
    this.idleTween?.stop();
    this.blinkTimer?.destroy();
    this.typingTimer?.destroy();
    this.clearZParticles();
    this.alertIndicator.setVisible(false);
    this.drawBeanSprite();
  }

  private enterIdle() {
    this.moveTo(IDLE_X, IDLE_Y, () => {
      this.idleTween = this.tweens.add({
        targets: this.bean,
        x: { from: IDLE_X - 20, to: IDLE_X + 20 },
        duration: 2800,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut',
      });
      // Occasionally look up
      this.time.addEvent({
        delay: 5000,
        loop: true,
        callback: () => {
          if (this.currentState === 'idle') {
            this.speak('...', 1500);
          }
        },
      });
    });
  }

  private enterWorking() {
    this.moveTo(DESK_X, DESK_Y + 30, () => {
      this.drawBeanTyping();
      this.startTypingAnimation();
    });
  }

  private enterSleeping() {
    this.moveTo(BED_X, BED_Y + 10, () => {
      this.bean.setAngle(90);
      this.startZParticles();
    });
  }

  private enterSafe() {
    this.moveTo(SAFE_X, SAFE_Y + 35, () => {
      this.speak('The numbers are... adequate.', 3000);
    });
  }

  private enterAlert() {
    // Run fast to desk
    this.tweens.add({
      targets: this.bean,
      x: DESK_X,
      y: DESK_Y + 30,
      duration: 400,
      ease: 'Cubic.easeOut',
      onComplete: () => {
        this.drawBeanTyping();
        this.alertIndicator.setText('⚠ BILL DUE').setVisible(true);
        this.tweens.add({
          targets: this.alertIndicator,
          alpha: { from: 1, to: 0.3 },
          duration: 600,
          yoyo: true,
          repeat: -1,
        });
        this.speak('A bill is due. Immediate attention required.', 5000);
      },
    });
  }

  private enterCelebrating() {
    this.tweens.add({
      targets: this.bean,
      y: this.bean.y - 20,
      duration: 200,
      yoyo: true,
      repeat: 4,
      onComplete: () => {
        this.time.delayedCall(5000, () => {
          if (this.currentState === 'celebrating') this.setState('idle');
        });
      },
    });
    this.speak('...noted.', 2000);
  }

  // ─── Helpers ──────────────────────────────────────────────────────────────

  private moveTo(x: number, y: number, onComplete?: () => void) {
    this.tweens.add({
      targets: this.bean,
      x,
      y,
      duration: 600,
      ease: 'Cubic.easeInOut',
      onComplete,
    });
  }

  private startTypingAnimation() {
    let frame = 0;
    this.typingTimer = this.time.addEvent({
      delay: 220,
      loop: true,
      callback: () => {
        frame++;
        if (frame % 2 === 0) {
          this.drawBeanTyping();
        } else {
          this.drawBeanSprite();
        }
      },
    });
  }

  private startZParticles() {
    this.clearZParticles();
    let i = 0;
    this.time.addEvent({
      delay: 800,
      loop: true,
      callback: () => {
        if (this.currentState !== 'sleeping') return;
        const z = this.add.text(this.bean.x + 10 + i * 5, this.bean.y - 10 - i * 8, 'z', {
          fontSize: `${10 + i * 2}px`, color: '#9bb5cc', fontFamily: 'monospace',
        }).setDepth(15);
        this.zParticles.push(z);
        this.tweens.add({
          targets: z,
          y: z.y - 30,
          alpha: 0,
          duration: 1800,
          onComplete: () => z.destroy(),
        });
        i = (i + 1) % 3;
      },
    });
  }

  private clearZParticles() {
    for (const z of this.zParticles) z.destroy();
    this.zParticles = [];
    this.bean.setAngle(0);
  }

  private startIdleBehavior() {
    this.time.delayedCall(500, () => this.setState('idle'));
  }
}
