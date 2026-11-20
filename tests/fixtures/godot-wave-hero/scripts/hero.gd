extends CharacterBody3D
# Deliberately under-tuned: fixed hit-stop on a fast sword, run clip at a fixed rate.

const MOVE_SPEED := 6.0
const SPRINT_SPEED := 9.5
const ATTACK_COOLDOWN := 0.2
const HIT_STOP_TIME := 0.12

@onready var anim: AnimationPlayer = $Model/AnimationPlayer
var attack_timer := 0.0


func _physics_process(delta: float) -> void:
	var dir := Input.get_vector("left", "right", "up", "down")
	var speed := SPRINT_SPEED if Input.is_action_pressed("sprint") else MOVE_SPEED
	velocity.x = dir.x * speed
	velocity.z = dir.y * speed
	move_and_slide()
	if dir.length() > 0.1:
		anim.play("run")
	else:
		anim.play("idle")
	attack_timer -= delta


func attack() -> void:
	if attack_timer > 0.0:
		return
	attack_timer = ATTACK_COOLDOWN
	anim.play("slash")
	for enemy in $SwordArea.get_overlapping_bodies():
		enemy.take_damage(10)
		hit_stop(HIT_STOP_TIME)


func hit_stop(duration: float) -> void:
	Engine.time_scale = 0.0
	await get_tree().create_timer(duration, true, false, true).timeout
	Engine.time_scale = 1.0
