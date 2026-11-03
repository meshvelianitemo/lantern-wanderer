class_name StoryCommon
## Lines shared by every chapter: shrines, embers, Wickways, the Little Hearth.

const LINES := {
	"shrine_lit": [
		{"who": "", "text": "The old shrine drinks from your flame and glows warm again."},
		{"who": "", "text": "Should you stumble, its warmth will remember you."},
	],
	"first_ember": [
		{"who": "", "text": "An ember! Your lantern drinks it in and burns a little brighter."},
	],
	"first_name_stone": [
		{"who": "", "text": "A small stone with a name carved on it, still faintly warm. Somebody wanted this name remembered."},
		{"who": "", "text": "(The names you find are kept in your Journal. Press {key:journal}, or open it from the pause menu.)"},
	],
	"wickway_light": [
		{"who": "", "text": "An old Keeper lift. Its cage-lantern is cold, and its chain climbs away into the dark above."},
		{"event": "light_wickway", "who": "", "text": "You hold your flame to the wick inside. It drinks, and catches."},
		{"who": "", "text": "Far above, something old creaks awake. The Wickway will carry you between here and Old Hollow now."},
		{"goto": "wickway_ride_up"},
	],
	"wickway_ride_up": [
		{"who": "", "text": "The Wickway hums, ready to rise.",
			"choices": [
				{"text": "Ride up to Old Hollow.", "event": "ride"},
				{"text": "Not yet."},
			]},
	],
	"wickway_ride_down": [
		{"who": "", "text": "The Wickway's lantern burns. Its chain drops away into the deep.",
			"choices": [
				{"text": "Ride down.", "event": "ride"},
				{"text": "Not yet."},
			]},
	],
	"wickway_cold": [
		{"who": "", "text": "An old Keeper lift, its cage-lantern cold. The chain drops through the floor into the dark."},
		{"who": "", "text": "Someone would have to light it from below."},
	],
	"hearth_rest": [
		{"if": "!given>=2", "who": "", "text": "The Little Hearth crackles. You warm your hands, and the Hollow remembers you."},
		{"if": "given>=2,!given>=4", "who": "", "text": "The Little Hearth crackles. A few more faces sit around it now than before."},
		{"if": "given>=4", "who": "", "text": "The Little Hearth roars. The whole Hollow is warm, and full of quiet talk."},
		{"if": "ending_many", "who": "", "text": "You sit down by the fire, very small and very tired. Someone puts a blanket around you."},
		{"if": "ending_many", "who": "", "text": "For the first time in a long while, nobody has to go anywhere."},
		{"if": "ending_many", "goto": "the_end_card"},
	],
}
