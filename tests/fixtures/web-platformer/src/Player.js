import Phaser from "phaser";

// Deliberately under-juiced: feel numbers live where they are used.
export class Player {
  constructor(sprite) {
    this.sprite = sprite;
    this.coyoteLeft = 0;
    this.jumpBufferLeft = 0;
  }

  update(dt, onGround, jumpPressed) {
    this.coyoteLeft = onGround ? 0.12 : Math.max(this.coyoteLeft - dt, 0);
    this.jumpBufferLeft = jumpPressed ? 0.1 : Math.max(this.jumpBufferLeft - dt, 0);
    if (this.jumpBufferLeft > 0 && this.coyoteLeft > 0) this.jump();
  }

  jump() {
    this.sprite.body.setVelocityY(-420);
    this.coyoteLeft = 0;
    this.jumpBufferLeft = 0;
  }
}
