extends CharacterBody3D
# harvestwright: gait-hoof-steps held-out fixture
const WALK_SPEED := 4.0
const GALLOP_SPEED := 9.0
@onready var hoof_player: AudioStreamPlayer3D = $HoofPlayer
var step_timer := 0.0

func _physics_process(delta: float) -> void:
	var speed := GALLOP_SPEED if Input.is_action_pressed("gallop") else WALK_SPEED
	velocity = -transform.basis.z * speed
	move_and_slide()
	step_timer -= delta
	if step_timer <= 0.0:
		play_hoof()
		step_timer = 0.5

func play_hoof() -> void:
	hoof_player.play()
