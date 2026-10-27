import Phaser from 'phaser';

export default class GameScene extends Phaser.Scene {
  constructor() {
    super('game');
    this.score = 0;
  }

  create() {
    this.player = this.physics.add.sprite(400, 550, 'ship');
    this.bullets = this.physics.add.group();
    this.enemies = this.physics.add.group();
    this.scoreText = this.add.text(16, 16, 'Score: 0');
    this.cursors = this.input.keyboard.createCursorKeys();
    this.physics.add.overlap(this.bullets, this.enemies, this.hitEnemy, null, this);
    this.physics.add.overlap(this.player, this.enemies, this.playerDie, null, this);
  }

  update() {
    this.player.setVelocityX(0);
    if (this.cursors.left.isDown) this.player.setVelocityX(-300);
    if (this.cursors.right.isDown) this.player.setVelocityX(300);
    if (Phaser.Input.Keyboard.JustDown(this.cursors.space)) this.shoot();
  }

  shoot() {
    const bullet = this.bullets.create(this.player.x, this.player.y - 20, 'bullet');
    bullet.setVelocityY(-500);
  }

  hitEnemy(bullet, enemy) {
    bullet.destroy();
    enemy.destroy();
    this.addScore(10);
  }

  addScore(points) {
    this.score += points;
    this.scoreText.setText('Score: ' + this.score);
  }

  playerDie() {
    this.scene.restart();
  }
}
