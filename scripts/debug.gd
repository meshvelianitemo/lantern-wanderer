extends Node
## Developer helpers driven by command-line user args (after "--"), e.g.
##   Godot.exe --path . -- --skip-intro --level=glimmerdeep --door=1 --shot=C:/tmp/a.png
##   --shot=PATH       save a screenshot of the game view, then quit
##   --frames=N        frames to wait before the screenshot (default 90)
##   --level=ID        start in levels/ID.txt        --door=ID   arrive at that door
##   --warp=X,Y        move the player to tile X,Y on start
##   --hold=ACTION     keep an input action pressed (e.g. move_right, or move_right@60 from frame 60)
##   --dialogue=ID     open a dialogue on start
##   --embers=N        start with N embers           --given=N   pretend N embers were shared
##   --flags=a,b,c     set story flags               --skip-intro  no title screen / fade / card
##   --press=A@N,...   tap input action A on frame N (e.g. interact@40,move_down@80; jump@60~15 holds it)
##   --trace=N         print the player's position every N frames
##   --key=NAME@N,...  press a real keyboard key on frame N (e.g. Q@50,Escape@80), for rebinding
##   --pad             show gamepad prompts      --window  apply the window settings (see Settings)
##   --sfxlog          print every sound effect, marking the ones played during dialogue
##   --record=DIR      save frames from --from=N up to --frames into DIR (every --every=K-th), then quit.
##                     Run Godot with --fixed-fps 60 so frames are evenly spaced; art_src/gifs.py makes GIFs.

var skip_intro := false

var _shot := ""
var _record := ""
var _from := 0
var _every := 1
var _frames := 90
var _warp := Vector2i(-1, -1)
var _hold := ""
var _dialogue := ""
var _embers := 0
var _trace := 0
var _n := 0
## frame -> actions to press / release on that frame
var _presses := {}
var _releases := {}
## frame -> keyboard keys to press on that frame
var _keys := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if not OS.get_cmdline_user_args().is_empty():
		Game.save_path = "user://debug_save.json"
	# taps happen at the very start of a frame, like real input does
	get_tree().process_frame.connect(_tap)
	for arg in OS.get_cmdline_user_args():
		var kv := arg.trim_prefix("--").split("=", true, 1)
		var value := kv[1] if kv.size() > 1 else ""
		match kv[0]:
			"shot": _shot = value
			"record": _record = value
			"from": _from = int(value)
			"every": _every = maxi(1, int(value))
			"frames": _frames = int(value)
			"warp":
				var xy := value.split(",")
				_warp = Vector2i(int(xy[0]), int(xy[1]))
			"hold": _hold = value
			"dialogue": _dialogue = value
			"embers": _embers = int(value)
			"given": Game.embers_given = int(value)
			"level": Game.level_id = value
			"door": Game.entry_door = value
			"flags":
				for f in value.split(",", false):
					Game.flags[f] = true
			"press":  # action@frame, or action@frame~frames to hold it down
				for item in value.split(",", false):
					var ab := item.split("@")
					var tf := ab[1].split("~")
					var f := int(tf[0])
					var hold := int(tf[1]) if tf.size() > 1 else 1
					if not _presses.has(f):
						_presses[f] = []
					_presses[f].append(ab[0])
					if not _releases.has(f + hold):
						_releases[f + hold] = []
					_releases[f + hold].append(ab[0])
			"skip-intro":
				skip_intro = true
				Game.started = true
			"trace": _trace = int(value)
			"sfxlog": Sound.log_sfx = true
			"key":
				for item in value.split(",", false):
					var ab := item.split("@")
					var f := int(ab[1])
					if not _keys.has(f):
						_keys[f] = []
					_keys[f].append(OS.find_keycode_from_string(ab[0]))


func _tap() -> void:
	for a: String in _releases.get(_n + 1, []):
		Input.action_release(a)
	for a: String in _presses.get(_n + 1, []):
		Input.action_press(a)
	for code: Key in _keys.get(_n + 1, []):
		for down in [true, false]:
			var ev := InputEventKey.new()
			ev.physical_keycode = code
			ev.keycode = code
			ev.pressed = down
			Input.parse_input_event(ev)


func _process(_delta: float) -> void:
	_n += 1
	if _n == 2:
		if _warp.x >= 0 and Game.player:
			Game.player.global_position = Vector2(_warp.x * 16 + 8, (_warp.y + 1) * 16)
			Game.checkpoint = Game.player.global_position
			var cam := get_viewport().get_camera_2d()
			if cam and cam.has_method("snap_to_target"):
				cam.snap_to_target()
		for i in _embers:
			Game.add_ember()
	if _n == 12 and _dialogue != "":
		Dialogue.run(_dialogue)
	if _hold != "":
		var hp := _hold.split("@")
		if hp.size() == 1 or _n >= int(hp[1]):
			Input.action_press(hp[0])

	if _trace > 0 and _n % _trace == 0 and Game.player:
		var p: Player = Game.player
		print("frame %d  pos %s  tile %s  floor %s  embers %d" % [_n, p.global_position.round(),
			Vector2i(p.global_position / 16.0), p.is_on_floor(), Game.embers])
	if _record != "":
		if _n >= _from and (_n - _from) % _every == 0:
			get_viewport().get_texture().get_image().save_png("%s/f%05d.png" % [_record, _n])
		if _n >= _frames:
			get_tree().quit()
	if _shot != "" and _n == _frames:
		var img := get_viewport().get_texture().get_image()
		img.save_png(_shot)
		print("window %s  mode %d" % [DisplayServer.window_get_size(), DisplayServer.window_get_mode()])
		get_tree().quit()
