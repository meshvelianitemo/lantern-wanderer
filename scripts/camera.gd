extends Camera2D
## Follows the player with look-ahead and pixel-snapped smoothing.

@export var look_ahead := 28.0
@export var height_offset := -22.0
@export var smoothing := 5.0

var _pos := Vector2.ZERO
var _ahead := 0.0
var _snapped := false


func _ready() -> void:
	make_current()


func snap_to_target() -> void:
	_snapped = false


func _physics_process(delta: float) -> void:
	var target := Game.player
	if target == null:
		return
	var facing: int = target.facing
	_ahead = lerpf(_ahead, facing * look_ahead, 1.0 - exp(-2.5 * delta))
	var desired := target.global_position + Vector2(_ahead, height_offset)
	if not _snapped:
		_pos = desired
		_snapped = true
	_pos = _pos.lerp(desired, 1.0 - exp(-smoothing * delta))
	global_position = _pos.round()
