class_name Rising
extends Node2D
## Something rising from the bottom of the level: the flood in Maud's Echo ("water"),
## the cold in Vesper's ("dark"). It climbs at `speed` px/s (faster when far below
## the player, so nobody waits on it), and if it reaches the player it sends them back
## to their last landing and sinks to `DROP` px below it. Paused during dialogue,
## and until `start()` (or the level's "rising_start" event).

## How far below a landing the surface drops when the player is sent back to it.
const DROP := 56.0
## Below this many px under the player it hurries.
const HURRY_GAP := 200.0

var mode := "water"
var speed := 10.0
var running := false
## World y of the surface.
var surface_y := 0.0
var width_px := 0.0
## The surface never climbs above this (the top of the level, or a dry landing).
var ceiling_y := -INF

var _body: ColorRect
var _edge: Line2D
var _glow: PointLight2D
var _t := 0.0
var _sound_t := 0.0


func _ready() -> void:
	add_to_group("rising")
	z_index = 6
	_body = ColorRect.new()
	_body.color = Color(0.05, 0.11, 0.16, 0.86) if mode == "water" else Color(0.01, 0.0, 0.03, 0.97)
	_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_body)
	_edge = Line2D.new()
	_edge.width = 2.0
	_edge.default_color = Color(0.55, 0.75, 0.8, 0.8) if mode == "water" else Color(0.25, 0.12, 0.35, 0.9)
	add_child(_edge)
	if mode == "water":
		_body.material = Util.unlit_material()
	_place()


func start() -> void:
	running = true


func _place() -> void:
	_body.position = Vector2(0, surface_y)
	_body.size = Vector2(width_px, 4000.0)
	var pts := PackedVector2Array()
	var x := 0.0
	while x <= width_px:
		var wave := sin(_t * 2.2 + x * 0.09) * (1.2 if mode == "water" else 2.5)
		pts.append(Vector2(x, surface_y + roundf(wave)))
		x += 8.0
	_edge.points = pts


func _physics_process(delta: float) -> void:
	_t += delta
	var p: Player = Game.player
	if running and p and not Game.in_dialogue and not p.frozen:
		var gap := surface_y - p.global_position.y
		var v := speed * (2.5 if gap > HURRY_GAP else 1.0)
		surface_y = maxf(surface_y - v * delta, ceiling_y)
		_sound_t -= delta
		if _sound_t <= 0.0 and gap < 120.0:
			_sound_t = 4.0
			Sound.sfx("dark_rise" if mode == "dark" else "splash", -14.0)
		if p.body_center().y > surface_y + 4.0:
			_catch(p)
	_place()


func _catch(p: Player) -> void:
	if mode == "water":
		p.drown()
	else:
		Sound.sfx("dark_rise")
		p.respawn()
	# sink back below the landing they return to
	await p.respawned
	surface_y = maxf(surface_y, Game.checkpoint.y + DROP)
	for f: Node2D in Game.followers:
		f.global_position = Game.checkpoint
