class_name Story
## The cast, and all dialogue in the game.
## Dialogue lives in one file per chapter under scripts/story/ (see dialogue.gd
## for the entry format); they are merged into DIALOGUES here.

static var DIALOGUES: Dictionary = _merge([
	StoryCommon.LINES, StoryMossgrave.LINES, StoryHollow.LINES, StoryGlimmer.LINES,
	StoryDrowned.LINES, StoryStarwell.LINES, StoryRootdark.LINES, StoryHearth.LINES,
	StoryEchoes.LINES, StoryHome.LINES,
])

## Keeper sprite sheets (keeper_<id>.png): 0-1 asleep, 2-3 awake, 4-7 walk.
const KEEPER_ANIMS := {"asleep": [[0, 1], 1], "idle": [[2, 3], 2], "walk": [[4, 5, 6, 7], 8], "talk": [[2, 3], 6]}

## Every character. Keys:
##   name, voice         shown name; voice id for Sound.voice (defaults to the key)
##   sprite, frame       horizontal sheet and frame width
##   anims               {anim: [[frames], fps]}; idle, talk, and *_lit variants
##   lit_if              condition that switches to *_lit anims and the bright light
##   light               {color, pos, scale, dim, lit} energies
##   talks               [[condition, dialogue], ...] first match wins
##   where               {level: condition} - only appears in that level while it holds
##   zone, prompt, y, z, unlit, face   placement details
const NPCS := {
	"mossback": {
		"name": "Mossback",
		"talks": [
			["visited_rootdark,!mossback_heard_root", "mossback_after_root"],
			["visited_drowned,!mossback_heard_drowned", "mossback_after_drowned"],
			["visited_glimmerdeep,!mossback_heard_deep", "mossback_after_deep"],
			["mossback_heard_deep", "mossback_later"],
			["met_mossback", "mossback_repeat"],
			["", "mossback_intro"],
		],
	},
	"tallow": {
		"name": "Nan Tallow",
		"sprite": "res://assets/sprites/tallow.png", "frame": 20,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 7], "idle_lit": [[4, 5], 3], "talk_lit": [[6, 7], 7]},
		"lit_if": "gave_tallow|ending_many",
		"light": {"color": Color(1.0, 0.72, 0.4), "pos": Vector2(0, -30), "scale": 0.7, "dim": 0.25, "lit": 0.85},
		"talks": [
			# Echo threads come before the after-ending lines: Echoes can be played after an ending too
			["echo_maud,gave_tallow,!tallow_heard_maud", "tallow_forty_doors"],
			["ending_many", "tallow_epilogue"],
			["gave_tallow", "tallow_after"],
			["met_tallow", "tallow_ask"],
			["", "tallow_intro"],
		],
	},
	"pell": {
		"name": "Pell",
		"sprite": "res://assets/sprites/pell.png", "frame": 11,
		"anims": {"idle": [[0, 1, 2, 3], 12]},
		"unlit": true, "face": false, "zone": Vector2(44, 60), "prompt": 30.0,
		"where": {"old_hollow": "!pell_follows"},
		"talks": [["", "pell_intro"]],
	},
	"burrow": {
		"name": "Burrow",
		"sprite": "res://assets/sprites/burrow.png", "frame": 26,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 8]},
		"talks": [
			["met_burrow,echo_lark,!burrow_heard_lark", "burrow_after_echo"],
			["met_burrow,gave_wisp,!burrow_heard_wisp", "burrow_wisp_thanks"],
			["met_burrow", "burrow_repeat"],
			["", "burrow_intro"],
		],
	},
	"wisp": {
		"name": "Wisp",
		"sprite": "res://assets/sprites/wisp.png", "frame": 12,
		"anims": {"idle": [[0, 1], 2], "idle_lit": [[2, 3], 3]},
		"lit_if": "gave_wisp", "unlit": true, "zone": Vector2(34, 24), "prompt": 22.0,
		"light": {"color": Color(0.8, 1.0, 0.5), "pos": Vector2(-5, -4), "scale": 0.5, "dim": 0.0, "lit": 0.75},
		"where": {"glimmerdeep": "!gave_wisp", "old_hollow": "gave_wisp"},
		"talks": [
			["in:old_hollow,gave_glim,!wisp_heard_glim", "wisp_glim_home"],
			["in:old_hollow,echo_lark,!gave_glim", "wisp_after_echo"],
			["ending_many", "wisp_epilogue"],
			["in:old_hollow", "wisp_hollow"],
			["gave_wisp", "wisp_thanks"],
			["met_wisp", "wisp_repeat"],
			["", "wisp_intro"],
		],
	},
	"ash": {
		"name": "Ash",
		"sprite": "res://assets/sprites/ash.png", "frame": 32,
		"anims": {"idle": [[0, 1], 1], "talk": [[2, 3], 2], "idle_lit": [[4, 5], 2], "talk_lit": [[4, 5], 4]},
		"lit_if": "gave_ash",
		"light": {"color": Color(1.0, 0.68, 0.4), "pos": Vector2(9, -6), "scale": 0.55, "dim": 0.0, "lit": 0.6},
		"where": {"glimmerdeep": "!gave_ash", "old_hollow": "gave_ash"},
		"talks": [
			["in:old_hollow,knows_lark,!told_lark", "ash_lark"],
			["echo_lark,!ash_heard_echo", "ash_after_echo"],
			["keepsake:lantern,!echo_lark,!ash_saw_lantern", "ash_lantern_found"],
			["met_ash,!keepsake:lantern,!echo_lark,!ash_told_lantern", "ash_lantern"],
			["ending_many", "ash_epilogue"],
			["in:old_hollow", "ash_hollow"],
			["gave_ash", "ash_thanks"],
			["met_ash", "ash_repeat"],
			["", "ash_intro"],
		],
	},
	"gudgeon": {
		"name": "Old Gudgeon",
		"sprite": "res://assets/sprites/gudgeon.png", "frame": 48,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 6]},
		"y": -6.0, "zone": Vector2(120, 44), "prompt": 26.0, "face": false,
		"where": {"old_hollow": "gave_gudgeon"},
		"talks": [
			["echo_lark,!gudgeon_heard_lark,gave_gudgeon", "gudgeon_after_echo"],
			["ending_many,in:old_hollow", "gudgeon_epilogue"],  # elsewhere he still ferries you
			["in:old_hollow", "gudgeon_ferry"],
			["in:starwell", "gudgeon_starwell"],
			["in:glimmerdeep,met_gudgeon", "gudgeon_ferry_repeat"],
			["in:glimmerdeep", "gudgeon_intro"],
			["in:drowned,gave_gudgeon,visited_starwell", "gudgeon_dive_again"],
			["in:drowned,gave_gudgeon", "gudgeon_warm"],
			["in:drowned,met_gudgeon_cold", "gudgeon_cold_repeat"],
			["in:drowned", "gudgeon_cold"],
		],
	},
	"archivist": {
		"name": "The Archivist",
		"sprite": "res://assets/sprites/archivist.png", "frame": 22,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 1], 4]},
		"unlit": true, "zone": Vector2(60, 40), "prompt": 46.0, "auto_if": "!gift_hook",
		"light": {"color": Color(0.75, 0.95, 0.9), "pos": Vector2(1, -26), "scale": 0.7, "dim": 0.5, "lit": 0.5},
		"talks": [
			["gift_hook,met_orrin,!archivist_heard_orrin", "archivist_orrin"],
			["gift_hook", "archivist_repeat"],
			["", "archivist_intro"],
		],
	},
	"orrin": {
		"name": "Orrin",
		"sprite": "res://assets/sprites/orrin.png", "frame": 24,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 6], "idle_lit": [[4, 5], 2], "talk_lit": [[6, 7], 6]},
		"lit_if": "gave_orrin",
		"zone": Vector2(56, 34), "prompt": 38.0, "auto_if": "!met_orrin",
		"light": {"color": Color(1.0, 0.8, 0.5), "pos": Vector2(7, -14), "scale": 0.5, "dim": 0.0, "lit": 0.7},
		"where": {"starwell": "!gave_orrin", "old_hollow": "gave_orrin"},
		"talks": [
			["ending_many", "orrin_epilogue"],
			["in:old_hollow,new_names", "orrin_names"],
			["in:old_hollow,!orrin_looked,!names>=10", "orrin_telescope"],
			["in:old_hollow", "orrin_hollow"],
			["orrery_lit,!orrin_saw_stars", "orrin_stars"],
			["orrery_lit,new_names", "orrin_names"],
			["orrery_lit", "orrin_after"],
			["met_orrin", "orrin_repeat"],
			["", "orrin_wake"],
		],
	},
	"bell": {
		"name": "Bell",
		"sprite": "res://assets/sprites/bell.png", "frame": 14,
		"anims": {"idle": [[0, 1], 3], "idle_lit": [[2, 3], 3]},
		"lit_if": "gave_bell", "unlit": true, "zone": Vector2(34, 28), "prompt": 28.0,
		"light": {"color": Color(1.0, 0.85, 0.6), "pos": Vector2(0, -10), "scale": 0.5, "dim": 0.15, "lit": 0.7},
		"where": {"drowned": "!gave_bell", "old_hollow": "gave_bell"},
		"talks": [
			["name:maud,!bell_heard_maud", "bell_maud"],
			["echo_maud,!bell_heard_echo", "bell_after_echo"],
			["keepsake:bell,!echo_maud,!bell_saw_bell", "bell_sees_bell"],
			["met_bell,!keepsake:bell,!echo_maud,!bell_asked_bell", "bell_ask_bell"],
			["ending_many", "bell_epilogue"],
			["in:old_hollow", "bell_hollow"],
			["gave_bell", "bell_thanks"],
			["met_bell", "bell_repeat"],
			["", "bell_intro"],
		],
	},
	"rootmother": {
		"name": "The Root-Mother",
		"sprite": "res://assets/sprites/rootmother.png", "frame": 64,
		"anims": {"idle": [[1], 1], "talk": [[2, 3], 4]},
		"face": false, "z": -5, "zone": Vector2(90, 60), "prompt": 70.0, "auto_if": "!gift_flare",
		"light": {"color": Color(0.78, 0.5, 1.0), "pos": Vector2(0, -36), "scale": 0.8, "dim": 0.3, "lit": 0.3},
		"talks": [
			["gift_flare,!keepsake:page", "rootmother_keepsake"],
			["gift_flare", "rootmother_repeat"],
			["", "rootmother_intro"],
		],
	},
	"sprig": {
		"name": "Sprig",
		"sprite": "res://assets/sprites/sprig.png", "frame": 12,
		"anims": {"idle": [[0, 1], 2], "idle_lit": [[2, 3], 2]},
		"lit_if": "gave_sprig", "zone": Vector2(30, 24), "prompt": 24.0,
		"light": {"color": Color(0.7, 1.0, 0.6), "pos": Vector2(0, -10), "scale": 0.45, "dim": 0.0, "lit": 0.6},
		"where": {"rootdark": "!gave_sprig"},
		"talks": [
			["gave_sprig", "sprig_thanks"],
			["met_sprig", "sprig_repeat"],
			["", "sprig_intro"],
		],
	},
	"sprig_tree": {
		"name": "Sprig",
		"voice": "sprig",
		"sprite": "res://assets/sprites/sapling_tree.png", "frame": 24,
		"grow": [
			["visited_hearth|echo_vesper", "res://assets/sprites/sapling_tree_3.png", 56],
			["visited_rootdark|echo_maud", "res://assets/sprites/sapling_tree_2.png", 40],
		],
		"anims": {"idle": [[0, 1], 1]},
		"face": false, "zone": Vector2(34, 40), "prompt": 46.0,
		"where": {"old_hollow": "gave_sprig"},
		"talks": [["ending_many", "sprig_epilogue"], ["", "sprig_hollow"]],
	},
	"hollow_one": {
		"name": "The Hollow One",
		"sprite": "res://assets/sprites/hollow_one.png", "frame": 48,
		"anims": {"idle": [[0, 1, 2, 3], 5], "talk": [[4, 5], 6]},
		"unlit": true, "zone": Vector2(80, 60), "prompt": 64.0, "auto_if": "!hollow_one_spoke",
		# after The First Page they are Vesper again (Story.NPCS.vesper)
		"where": {"rootdark": "!hollow_one_gone", "old_hollow": "gave_hollow_one,ending_many,!ending_first_page"},
		"talks": [
			["echo_vesper,!hollow_heard_vesper", "hollow_one_vesper"],
			# all three Echoes seen after Many Hands: walk down together (StoryHome)
			["in:old_hollow,ending_many,echo_lark,echo_maud,echo_vesper,!ending_first_page", "hollow_one_walk"],
			["ending_many", "hollow_epilogue"],
			["hollow_one_spoke", "hollow_one_repeat"],
			["", "hollow_one_meet"],
		],
	},

	# --- Echoes & Home ----------------------------------------------------------
	"glim": {
		"name": "Glim", "voice": "glim",
		"sprite": "res://assets/sprites/glim.png", "frame": 20,
		"anims": {"idle": [[0, 1], 2], "idle_lit": [[2, 3], 3]},
		"lit_if": "gave_glim", "unlit": true, "zone": Vector2(40, 26), "prompt": 24.0,
		"light": {"color": Color(0.8, 1.0, 0.5), "pos": Vector2(0, -6), "scale": 0.6, "dim": 0.08, "lit": 0.8},
		"where": {"glimmerdeep": "echo_lark,!gave_glim", "old_hollow": "gave_glim"},
		"talks": [
			["ending_many,in:old_hollow", "glim_epilogue"],
			["in:old_hollow", "glim_hollow"],
			["met_glim", "glim_repeat"],
			["", "glim_found"],
		],
	},
	"vesper": {
		"name": "Vesper", "voice": "vesper",
		"sprite": "res://assets/sprites/hero_idle_vesper.png", "frame": 32,
		"anims": {"idle": [[0, 1, 2, 3, 4, 5], 6]},
		"light": {"color": Color(1.0, 0.8, 0.5), "pos": Vector2(9, -6), "scale": 0.7, "dim": 0.7, "lit": 0.7},
		"where": {"old_hollow": "ending_first_page"},
		"talks": [["", "vesper_epilogue"]],
	},
	# Lark's Echo: the people Lark warmed, one age ago. Warmed, each is a light of their own.
	"lark_burrow": {
		"name": "Burrow", "voice": "burrow", "scale": 0.8,
		"sprite": "res://assets/sprites/burrow.png", "frame": 26,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 8]},
		"lit_if": "gave_lark_burrow", "radius": 76.0,
		"light": {"color": Color(1.0, 0.75, 0.45), "pos": Vector2(0, -10), "dim": 0.0, "lit": 0.85},
		"talks": [["gave_lark_burrow", "lark_burrow_after"], ["", "lark_burrow"]],
	},
	"lark_gudgeon": {
		"name": "Gudgeon", "voice": "gudgeon",
		"sprite": "res://assets/sprites/gudgeon.png", "frame": 48,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 6]},
		"y": -6.0, "zone": Vector2(80, 44), "prompt": 26.0, "face": false,
		"lit_if": "gave_lark_gudgeon", "radius": 104.0,
		"light": {"color": Color(1.0, 0.75, 0.45), "pos": Vector2(0, -8), "dim": 0.0, "lit": 0.9},
		"talks": [["gave_lark_gudgeon", "lark_gudgeon_after"], ["", "lark_gudgeon"]],
	},
	"lark_glim": {
		"name": "Glim", "voice": "glim",
		"sprite": "res://assets/sprites/glim.png", "frame": 20,
		"anims": {"idle": [[0, 1], 2], "idle_lit": [[2, 3], 3]},
		"lit_if": "gave_lark_glim", "unlit": true, "zone": Vector2(40, 26), "prompt": 24.0, "radius": 60.0,
		"light": {"color": Color(0.8, 1.0, 0.5), "pos": Vector2(0, -6), "dim": 0.05, "lit": 0.85},
		"talks": [["gave_lark_glim", "lark_glim_after"], ["", "lark_glim"]],
	},
	"lark_egg": {
		"name": "???", "voice": "wisp", "scale": 0.75,
		"sprite": "res://assets/sprites/wisp.png", "frame": 12,
		"anims": {"idle": [[0, 1], 1], "idle_lit": [[2, 3], 3]},
		"lit_if": "lark:egg_warm", "unlit": true, "zone": Vector2(40, 26), "prompt": 20.0,
		"light": {"color": Color(0.8, 1.0, 0.5), "pos": Vector2(-4, -4), "scale": 0.5, "dim": 0.0, "lit": 0.8},
		"talks": [["!lark:egg_warm", "lark_egg"]],
	},
	# Maud's Echo: the Keepers she calls home (asleep until her bell; then they follow)
	"hollis": {"name": "Hollis", "voice": "keeper", "sprite": "res://assets/sprites/keeper_hollis.png",
		"frame": 16, "anims": KEEPER_ANIMS, "wake": "Mm? Is it supper?"},
	"fitch": {"name": "Fitch", "voice": "keeper", "sprite": "res://assets/sprites/keeper_fitch.png",
		"frame": 16, "anims": KEEPER_ANIMS, "wake": "I'm up! I'm up! Am I late?"},
	"tobin": {"name": "Tobin", "voice": "keeper", "sprite": "res://assets/sprites/keeper_tobin.png",
		"frame": 16, "anims": KEEPER_ANIMS, "wake": "Hm? I was mending. In my sleep."},
	"pim": {"name": "Pim", "voice": "keeper", "sprite": "res://assets/sprites/keeper_pim.png",
		"frame": 16, "anims": KEEPER_ANIMS, "wake": "Who's dripping on my clean floor?"},
	"wren": {"name": "Wren", "voice": "keeper", "sprite": "res://assets/sprites/keeper_wren.png",
		"frame": 16, "anims": KEEPER_ANIMS, "wake": "La la la... oh! Maud?"},
	# Vesper's Echo: Edda walks with you; the same Keepers, alive and cheering you on
	"edda": {"name": "Edda", "voice": "edda", "sprite": "res://assets/sprites/edda.png", "frame": 20,
		"anims": {"idle": [[0, 1], 2], "talk": [[2, 3], 6], "walk": [[4, 5, 6, 7], 8]}},
	"v_hollis": {"name": "Hollis", "voice": "keeper", "sprite": "res://assets/sprites/keeper_hollis.png",
		"frame": 16, "anims": KEEPER_ANIMS, "talks": [["vesper:fear_off", "v_hollis_after"], ["", "v_hollis"]]},
	"v_tobin": {"name": "Tobin", "voice": "keeper", "sprite": "res://assets/sprites/keeper_tobin.png",
		"frame": 16, "anims": KEEPER_ANIMS, "talks": [["vesper:fear_off", "v_tobin_after"], ["", "v_tobin"]]},
	"v_wren": {"name": "Wren", "voice": "keeper", "sprite": "res://assets/sprites/keeper_wren.png",
		"frame": 16, "anims": KEEPER_ANIMS, "talks": [["vesper:fear_off", "v_wren_after"], ["", "v_wren"]]},
	"v_pim": {"name": "Pim", "voice": "keeper", "sprite": "res://assets/sprites/keeper_pim.png",
		"frame": 16, "anims": KEEPER_ANIMS, "talks": [["vesper:fear_off", "v_pim_after"], ["", "v_pim"]]},
	"v_maud": {"name": "Maud", "voice": "maud", "sprite": "res://assets/sprites/hero_idle_maud.png",
		"frame": 32, "anims": {"idle": [[0, 1, 2, 3, 4, 5], 5]},
		"talks": [["vesper:fear_off", "v_maud_after"], ["", "v_maud"]]},
}

## Pell's remarks while following you. One-off keys: enter_<level>, glimmer, hook.
const BARKS := {
	"pell": {
		"enter_mossgrave": ["Trees! I remember trees. Vaguely. I was mostly looking at the moon."],
		"enter_glimmerdeep": ["Oh. It's very... down. Isn't it."],
		"enter_drowned": ["Water. So much water. Moths and water are not friends."],
		"enter_rootdark": ["I don't like this one. I'm saying it now, so it's on record."],
		"enter_hearth": ["Is that it? The big light? It's not very big right now."],
		"enter_starwell": ["Glass all round. And the lake on the other side of it. I'm being very calm."],
		"shadow": ["Your shadow's holding still! Mine never does. I flap."],
		"name": ["A name! Somebody was somebody. That's nice to know."],
		"glimmer": ["Shiny! The rocks are copying you!"],
		"hook": ["You're leaving the light here? I'll stay with it. Obviously."],
		"gave_first": ["You gave light away? On purpose?"],
		"gave": [
			"Less light. More friends. I'm doing the maths and I can't decide.",
			"There goes another one. Warm of you. Literally.",
			"I'll just sit a bit closer, then.",
		],
		"hit": ["Eep! Cold!", "Cold cold cold!", "Shoo! Shoo, cold thing!"],
		"idle": [
			"Have I mentioned I like your lantern?",
			"I knew a moth who flew into the moon. Never came back. Lucky thing.",
			"Left, right, light. Left, right, light.",
			"Where does the dark go when you light it? I wonder that a lot.",
			"Is your scarf getting shorter? Is that normal for you?",
		],
		"idle_dim": [
			"Is it getting darker, or am I getting smaller?",
			"It's a cosy sort of light. Small. Cosy. Fine.",
			"I'll stay close. For warmth. Mine, I mean.",
		],
	},
	# What the dark whispers to Vesper as their fear grows (level.gd WHISPERS).
	"dark": {
		"whisper_1": ["...It's very hot down there."],
		"whisper_2": ["...You'll burn. All of you. Gone."],
		"whisper_3": ["...Nobody would know if you turned back."],
	},
}


## The dialogue an NPC should play right now ("" if none).
static func pick(npc_id: String) -> String:
	var data: Dictionary = NPCS.get(npc_id, {})
	for pair: Array in data.get("talks", []):
		if Game.check(pair[0]):
			return pair[1]
	return ""


## Whether a dialogue has something new in it: it, or a branch of it, sets a flag you
## don't have yet. NPCs show a little speech bubble while what they'd say is news.
static func is_news(id: String, depth := 0) -> bool:
	if id == "" or depth > 2:
		return false
	for entry: Dictionary in DIALOGUES.get(id, []):
		if not Game.check(entry.get("if", "")):
			continue
		if entry.has("set") and not Game.has_flag(entry["set"]):
			return true
		if entry.has("goto") and is_news(entry["goto"], depth + 1):
			return true
		for c: Dictionary in entry.get("choices", []):
			if c.has("goto") and Game.check(c.get("if", "")) and is_news(c["goto"], depth + 1):
				return true
	return false


## How far the hero's scarf (their wick) has burned: 0, 1 or 2.
static func scarf_stage() -> int:
	if Game.has_flag("ending_first_page"):
		return 1  # two wicks shared the Hearth: half each
	if Game.has_flag("visited_hearth") or Game.has_flag("ending_many") or Game.level_id == "hearth":
		return 2
	if Game.has_flag("visited_drowned") or Game.level_id in ["drowned", "rootdark"]:
		return 1
	return 0


static func _merge(parts: Array) -> Dictionary:
	var out := {}
	for part: Dictionary in parts:
		for k: String in part:
			if out.has(k):
				push_warning("Duplicate dialogue id: " + k)
			out[k] = part[k]
	return out
