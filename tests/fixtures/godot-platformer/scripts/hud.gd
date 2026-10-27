extends CanvasLayer

var score := 0
@onready var score_label: Label = $ScoreLabel


func add_score(points: int) -> void:
	score += points
	score_label.text = "Score: %d" % score


func _on_start_button_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/level1.tscn")
