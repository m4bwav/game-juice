extends CharacterBody2D

const SPEED := 220.0
const JUMP_VELOCITY := -420.0
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
var health := 3

@onready var sprite: Sprite2D = $Sprite2D


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	var dir := Input.get_axis("move_left", "move_right")
	velocity.x = dir * SPEED
	move_and_slide()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("jump"):
		jump()


func jump() -> void:
	if is_on_floor():
		velocity.y = JUMP_VELOCITY


func take_damage(amount: int) -> void:
	health -= amount
	if health <= 0:
		die()


func die() -> void:
	get_tree().reload_current_scene()
