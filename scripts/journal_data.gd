class_name JournalData
## Everything the Journal can show. Entries stay "???" until you have found
## them (see journal.gd for the rules of each page).

## Places, in the order of the journey. Known once visited.
const PLACES := [
	{"id": "mossgrave", "name": "Mossgrave Woods", "sub": "Chapter I",
		"text": "A dusk forest at the foot of the mountain. Mossback the totem keeps watch, and a cave mouth leads down into the dark.",
		"pell": "Trees! I remember trees. Vaguely. I was mostly looking at the moon."},
	{"id": "old_hollow", "name": "Old Hollow", "sub": "The Last Warm Place",
		"text": "A village under the roots of one enormous fallen tree. Forty doors, once. Everyone you warm comes home here.",
		"pell": "Best place in the world. I've been to two places."},
	{"id": "glimmerdeep", "name": "The Glimmerdeep", "sub": "Chapter II",
		"text": "Crystal caves that drink light. Glimmer holds only while a lantern touches it. Shades drift in the deep tunnels.",
		"pell": "Shiny rocks that copy you. I trust them less than I would like to."},
	{"id": "drowned", "name": "The Drowned Halls", "sub": "Chapter III",
		"text": "The flooded halls of the Keepers. Hooks for the flame, eye-gates that watch for light, and black water that sends you back.",
		"pell": "Water. So much water. Moths and water are not friends."},
	{"id": "starwell", "name": "The Starwell", "sub": "Under the Lake",
		"text": "A Keeper observatory on the floor of the lake, sealed in a held breath of air. Down here a shadow stands still, if the light that throws it does.",
		"pell": "Glass all round, and the whole lake on the other side of it. I am being very calm about this."},
	{"id": "rootdark", "name": "The Rootdark", "sub": "Chapter IV",
		"text": "The roots of the whole forest, all the way down. The darkest place, where every shade wakes at once.",
		"pell": "I said I didn't like it. It's on record."},
	{"id": "hearth", "name": "The Hearth", "sub": "Chapter V",
		"text": "A bronze bridge between stone Keepers, over nothing at all. At the end, the cold Hearth, and a Cradle shaped exactly like you.",
		"pell": "The big light. It isn't very big right now."},
]

## People. Known once `met` holds. `gave` names the ember flag (if they can take one).
## `more` adds [condition, line] notes that appear as you learn things.
const PEOPLE := [
	{"id": "mossback", "name": "Mossback", "met": "met_mossback",
		"text": "An ancient totem, green with moss, at the edge of Mossgrave. Calls you 'little wick'. Has waited a very long time for something."},
	{"id": "tallow", "name": "Nan Tallow", "met": "met_tallow", "gave": "gave_tallow",
		"text": "An old candle-woman who keeps the Little Hearth in Old Hollow. Burned most of herself keeping it going.",
		"more": [["gave_tallow", "'Warmth never really leaves. It just moves house.'"]]},
	{"id": "pell", "name": "Pell", "met": "pell_follows",
		"text": "A moth. Follows your light everywhere. Not you, the light. Completely different, apparently."},
	{"id": "burrow", "name": "Burrow", "met": "met_burrow",
		"text": "A blind mole who mines the Glimmerdeep. Knows everything about glimmer, and nothing about hurrying."},
	{"id": "wisp", "name": "Wisp", "met": "met_wisp", "gave": "gave_wisp",
		"text": "A little glowworm who lost her glow, and her mama, in the Glimmerdeep.",
		"more": [["gave_wisp", "Glowing again, loudly, in Old Hollow."]]},
	{"id": "ash", "name": "Ash", "met": "met_ash", "gave": "gave_ash",
		"text": "A grey wanderer sitting in the Glimmerdeep. A wick whose lantern went out before they reached the bottom.",
		"more": [["knows_lark", "The Book of Wicks calls them Lark."], ["told_lark", "You told them. They kept both names."]]},
	{"id": "gudgeon", "name": "Old Gudgeon", "met": "met_gudgeon|met_gudgeon_cold", "gave": "gave_gudgeon",
		"text": "An enormous blind fish who ferries travellers through the black water. Fish have a long while.",
		"more": [["visited_starwell", "Knows the way down to the glass house under the lake."]]},
	{"id": "bell", "name": "Bell", "met": "met_bell", "gave": "gave_bell",
		"text": "A Keeper ghost child who rings the supper bell, so that everyone comes home.",
		"more": [["name:maud", "Her mama's name was Maud."]]},
	{"id": "archivist", "name": "The Archivist", "met": "gift_hook",
		"text": "The last Keeper awake in the Drowned Halls. Keeps the Book of Wicks, every one of you by name. Taught your lantern the Hook.",
		"more": [["archivist_heard_orrin", "Knows now that Orrin is awake, too."]]},
	{"id": "orrin", "name": "Orrin", "met": "met_orrin", "gave": "gave_orrin",
		"text": "A very old Keeper astronomer. Fell asleep counting stars beside the Great Orrery, the winter the water rose.",
		"more": [["orrery_lit", "You lit the Great Orrery. He saw the sky again."]]},
	{"id": "sprig", "name": "Sprig", "met": "met_sprig", "gave": "gave_sprig",
		"text": "A seedling growing under a crack in the Rootdark, where the sun once fell. Slowly is still growing.",
		"more": [["gave_sprig", "A young tree in Old Hollow now."]]},
	{"id": "rootmother", "name": "The Root-Mother", "met": "gift_flare",
		"text": "The heart of the forest's roots. She carried you up from the Hearth as a spark, and taught your lantern the Flare."},
	{"id": "hollow_one", "name": "The Hollow One", "met": "hollow_one_spoke", "gave": "gave_hollow_one",
		"text": "The cold that gathered around Vesper, the first wick, who walked all the way down and turned back.",
		"more": [["echo_vesper", "You have walked Vesper's road yourself. There is nothing to forgive."]]},
	{"id": "glim", "name": "Glim", "met": "met_glim", "gave": "gave_glim",
		"text": "Wisp's mama. Went down the old seam an age ago to lay her egg where it was warm, and could not find the way back up.",
		"more": [["gave_glim", "Home in Old Hollow, watching her little one glow."]]},
]

## Keepsakes: their frame in keepsake.png, title card, and the Echo they hold.
const KEEPSAKES := {
	"lantern": {"frame": 0, "name": "Lark's Lantern", "card": "Cold. It remembers being warm.", "echo": "lark"},
	"bell": {"frame": 1, "name": "Maud's Handbell", "card": "It rang everyone home for supper.", "echo": "maud"},
	"page": {"frame": 2, "name": "The First Page", "card": "Carved by Edda, after the first cold.", "echo": "vesper"},
}

## The Echoes, in the order you find them (each one further back in time).
## `hint` shows (before the keepsake is found) once `hint_if` holds.
const ECHOES := [
	{"id": "lark", "keepsake": "lantern", "name": "Lark's Song", "sub": "One age ago", "hint_if": "met_ash",
		"hint": "Ash's lantern is still in the Glimmerdeep, where it went out: up the violet glimmer above Ash's chamber. Violet glimmer needs a strong flame (3 embers).",
		"text": "Lark gave and gave, and the people they warmed lit the way down: Burrow by the eye-stone, a fish in a cold pool, Glim with her egg. The last ember went to the egg. The egg was Wisp."},
	{"id": "maud", "keepsake": "bell", "name": "The Last Winter", "sub": "The night of the flood", "hint_if": "met_bell",
		"hint": "Bell's mama had a handbell. It is in the sunk supper hall of the Drowned Halls: down the crack in the library floor, past an eye-gate that needs a light left by its eye-stone.",
		"text": "Maud rang everyone home as the water rose: Hollis, Fitch, Tobin, Pim and Wren. Then she went back down for Bell. The five who lived built Old Hollow, with forty doors."},
	{"id": "vesper", "keepsake": "page", "name": "Vesper", "sub": "The first wick", "hint_if": "gift_flare",
		"hint": "The Root-Mother has kept something since the night of the flood. Ask her for it.",
		"text": "Vesper walked down through a warm mountain full of people, reached the Hearth, and could not take the last step. The dark followed them back up. Edda carved the first page: no wick should walk down alone."},
]

## Keeper tablets and signs, in the order you pass them. Known once read.
const TABLETS := [
	["sign_start", "Mossgrave signpost"],
	["sign_hollow", "Old Hollow sign"],
	["sign_wickway_hollow", "The Wickway stone"],
	["tablet_hollow_secret", "Behind the thorns"],
	["tablet_glimmer_1", "Glimmerdeep, I"],
	["tablet_glimmer_2", "Glimmerdeep, II"],
	["tablet_glimmer_3", "Glimmerdeep, III"],
	["tablet_drowned_1", "Drowned Halls, I"],
	["tablet_drowned_2", "Drowned Halls, II"],
	["tablet_drowned_3", "Drowned Halls, III"],
	["tablet_drowned_4", "Drowned Halls, IV"],
	["tablet_starwell_1", "Starwell, I"],
	["tablet_starwell_2", "Starwell, II"],
	["tablet_starwell_3", "Starwell, III"],
	["tablet_root_1", "Rootdark, I"],
	["tablet_root_2", "Rootdark, II"],
	["tablet_hearth_1", "The Hearth, I"],
	["tablet_hearth_2", "The Hearth, II"],
]

## Keeper name-stones: id -> [name, who they were, where the stone lies].
const NAMES := {
	"hollis": ["Hollis", "who kept the bees", "mossgrave"],
	"fitch": ["Fitch", "who was always late, and came anyway", "old_hollow"],
	"tobin": ["Tobin", "who mended lanterns", "glimmerdeep"],
	"pim": ["Pim", "who swept the Wickways", "glimmerdeep"],
	"maud": ["Maud", "who called everyone home for supper", "drowned"],
	"wren": ["Wren", "who sang on the stairs", "drowned"],
	"agathe": ["Agathe", "who taught the shadow-plays", "starwell"],
	"corran": ["Corran", "who fell asleep in every lesson", "starwell"],
	"orrin": ["Orrin", "who counted the stars", "starwell"],
	"edda": ["Edda", "who carved the first page", "rootdark"],
}


## The display name of a place id.
static func place_name(id: String) -> String:
	for p: Dictionary in PLACES:
		if p["id"] == id:
			return p["name"]
	return id
