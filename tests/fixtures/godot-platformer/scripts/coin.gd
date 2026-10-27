extends Area2D

signal collected(value)

@export var value := 1


func _on_body_entered(body: Node2D) -> void:
	if body.name == "Player":
		collect()


func collect() -> void:
	collected.emit(value)
	queue_free()
