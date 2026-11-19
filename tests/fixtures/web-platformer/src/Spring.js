// A spring pad that throws the player up but leaves the forgiveness timers running.
export function bounceOnSpring(player) {
  const squashAmount = 0.3;
  player.sprite.setScale(1 + squashAmount, 1 - squashAmount);
  player.sprite.body.setVelocityY(-700);
}
