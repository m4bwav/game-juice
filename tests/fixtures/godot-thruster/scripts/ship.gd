extends CharacterBody2D

const THRUST := 400.0

@onready var thrust_loop: AudioStreamPlayer = $ThrustLoop


func _process(delta: float) -> void:
	if Input.is_action_pressed("thrust"):
		velocity += Vector2.UP.rotated(rotation) * THRUST * delta
		thrust_loop.play()
	else:
		thrust_loop.stop()
	move_and_slide()
