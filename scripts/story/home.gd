class_name StoryHome
## Old Hollow comes alive: the Little Hearth's keepsake menu, suppers (everyone
## gathered round the fire, talking to each other), each resident's thread, Glim
## coming home, the help residents give you, and the First Page ending.

## Suppers in story order: [id, condition]. Each plays once, when you rest at the
## Little Hearth with three or more people living in the Hollow (see hearth.gd).
const SUPPERS := [
	["first", ""],
	["lark", "echo_lark"],
	["glim", "gave_glim"],
	["stars", "gave_orrin"],
	["maud", "echo_maud"],
	["vesper", "echo_vesper"],
	["last", "visited_rootdark,home>=4"],
]


## The next supper to have, or "" (not enough people yet, or none left).
static func next_supper() -> String:
	if Game.echo != "" or not Game.check("gave_tallow,home>=3,!ending_many"):
		return ""
	for s: Array in SUPPERS:
		if not Game.has_flag("supper:" + s[0]) and Game.check(s[1]):
			return s[0]
	return ""


const LINES := {
	# --- the Little Hearth -----------------------------------------------------------
	"hearth_menu": [
		{"who": "", "text": "The Little Hearth crackles, warm and patient.", "choices": [
			{"text": "Lay Lark's lantern in the fire", "if": "keepsake:lantern,!echo_lark", "event": "echo:lark"},
			{"text": "Lay Maud's handbell in the fire", "if": "keepsake:bell,!echo_maud", "event": "echo:maud"},
			{"text": "Lay the first page in the fire", "if": "keepsake:page,!echo_vesper", "event": "echo:vesper"},
			{"text": "Just rest", "goto": "hearth_rest"},
			{"text": "Remember Lark again", "if": "echo_lark", "event": "echo:lark"},
			{"text": "Remember Maud again", "if": "echo_maud", "event": "echo:maud"},
			{"text": "Remember Vesper again", "if": "echo_vesper", "event": "echo:vesper"},
		]},
	],

	# --- suppers -------------------------------------------------------------------
	"supper_first": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Ding! SUPPER! Everybody home!"},
		{"who": "Nan Tallow", "text": "Supper. Sit, all of you. You too, little wick. Especially you."},
		{"who": "Nan Tallow", "text": "It's only root soup. But it's hot, and there's a lot of it, and that's two more things than we had last winter."},
		{"if": "gave_wisp", "who": "Wisp", "text": "I'm glowing on my soup! Look! It's green soup now!"},
		{"if": "gave_wisp", "who": "Nan Tallow", "text": "It was green before, dear."},
		{"if": "gave_ash", "who": "Ash", "text": "...This is nice. I'd forgotten this. Sitting with people. Being one of the people."},
		{"if": "gave_bell", "who": "Bell", "text": "Ghosts can't eat soup. I'm having a pretend bowl. It's the best soup I've ever pretended."},
		{"if": "gave_orrin", "who": "Orrin", "text": "Do you know, I haven't sat at a table since the lake came in. Pass the salt? There's no salt. Pass the idea of salt."},
		{"who": "Nan Tallow", "text": "Forty doors, this place had. Forty! And every one of them had somebody behind it, at supper time."},
		{"who": "Nan Tallow", "text": "We'll get there. One door at a time."},
	],
	"supper_lark": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Supper!"},
		{"who": "Nan Tallow", "text": "You've been very quiet since you sat at that fire, little wick. What did it show you?"},
		{"who": "", "text": "You tell them about Lark. The full lantern. Burrow by the eye-stone. The fish in the cold pool. The egg."},
		{"if": "gave_ash", "who": "Ash", "text": "I'd have kept a bit back. If I did it again. I'd keep enough to get home."},
		{"if": "gave_ash", "who": "Ash", "text": "...No. I wouldn't. I'd do every bit of it the same. Isn't that stupid?"},
		{"if": "gave_ash", "who": "Nan Tallow", "text": "It's the least stupid thing I've heard all year, dear. Eat your soup."},
		{"if": "gave_wisp", "who": "Wisp", "text": "An egg? A GREEN egg? That's me! Mama said a lantern-person warmed me before I hatched!"},
		{"if": "gave_wisp", "who": "Wisp", "text": "So it was you! Ash! It was you all along! Why didn't you SAY?"},
		{"if": "gave_wisp,gave_ash", "who": "Ash", "text": "I didn't know you made it, little one. I never knew."},
		{"if": "!gave_ash", "who": "Nan Tallow", "text": "Lark. Poor dear. Gave it all away and never got the thanks. Someone ought to thank them."},
	],
	"supper_glim": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Ding! Ding! Supper! And a NEW PERSON!"},
		{"who": "Glim", "text": "Oh, isn't this lovely. A table. Soup. My little one, sitting up straight for once."},
		{"who": "Wisp", "text": "I'm sitting up SO straight. Mama, look. Look how bright I got while you were gone."},
		{"who": "Glim", "text": "I see it, sweetheart. I could see it from the bottom of the world."},
		{"who": "Nan Tallow", "text": "She's been waiting for you a long while, you know. Never stopped talking about it."},
		{"who": "Glim", "text": "Has she been loud?"},
		{"who": "Nan Tallow", "text": "She has been extremely loud, dear."},
		{"who": "Glim", "text": "That's my girl."},
	],
	"supper_stars": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Supper! Orrin, come down off that barrow!"},
		{"who": "Orrin", "text": "Coming, coming. I've been naming stars after all of you. Do you want to hear?"},
		{"who": "Nan Tallow", "text": "Not if mine's a small one."},
		{"who": "Orrin", "text": "Yours is the steady orange one that never sets. I watched it for an hour. It didn't do anything clever. It just stayed."},
		{"who": "Nan Tallow", "text": "...Well. That's all right, then."},
		{"if": "gave_gudgeon", "who": "Old Gudgeon", "text": "Mm. Fish do not look up. Up is only the place where the water stops."},
		{"if": "gave_gudgeon", "who": "Orrin", "text": "Then I'll name one for you anyway, and you can not look at it. It'll be the one that's reflected in your well."},
		{"if": "gave_gudgeon", "who": "Old Gudgeon", "text": "...Mm. I will not look at it every night."},
		{"if": "gave_wisp", "who": "Wisp", "text": "Is there a green one? There has to be a green one."},
		{"if": "gave_wisp", "who": "Orrin", "text": "There is now."},
	],
	"supper_maud": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Ding! Supper! That's my bell. And that's Mama's bell. Ding!"},
		{"who": "Nan Tallow", "text": "Five Keepers, you said. Climbing up out of the water with nothing, and building doors under a fallen tree."},
		{"who": "Nan Tallow", "text": "My gran's gran's gran used to say we came from somewhere warm, a long way down. I thought she was telling stories."},
		{"who": "Nan Tallow", "text": "Forty doors. They built forty doors, for five of them. They must have meant to fill them."},
		{"if": "gave_bell", "who": "Bell", "text": "They did mean to. Mama always laid extra places. In case."},
		{"if": "gave_orrin", "who": "Orrin", "text": "Hollis. Fitch. Tobin. Pim. Wren. I knew all of them. Fitch was always late. I'm glad he wasn't late for that."},
		{"who": "Nan Tallow", "text": "Well. We'll lay extra places, then. In case."},
	],
	"supper_vesper": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "...Ding. Supper."},
		{"who": "", "text": "Nobody talks much tonight. You have told them about Vesper, and the Hearth, and the step that wouldn't come."},
		{"if": "gave_ash", "who": "Ash", "text": "I was afraid too. The whole way. I just didn't get far enough down to find out how afraid."},
		{"if": "gave_orrin", "who": "Orrin", "text": "We sent one child down alone and called it brave. We should have sent the whole mountain with them."},
		{"who": "Nan Tallow", "text": "Then that's what we'll do, isn't it. We'll not send you down alone, little wick. Not in any way that counts."},
		{"if": "gave_wisp", "who": "Wisp", "text": "I'll come! I'm VERY bright now. I'm brighter than a lot of things."},
		{"who": "Nan Tallow", "text": "Eat your soup. All of you. Fear's easier on a full stomach."},
	],
	"supper_last": [
		{"if": "gave_bell", "sfx": "bell_ring", "who": "Bell", "text": "Ding! Ding! The last supper before... before. Ding!"},
		{"who": "Nan Tallow", "text": "You're going down tomorrow. Don't argue, I can see it on you. Like flour."},
		{"if": "gave_ash", "who": "Ash", "text": "Don't give it all away. And don't keep it all, either. ...I said that before. It's still true."},
		{"if": "gave_wisp", "who": "Wisp", "text": "Come back! You have to come back! I'll keep your seat glowing."},
		{"if": "gave_glim", "who": "Glim", "text": "Be brave, love. And when you can't be brave, be stubborn. It looks the same from outside."},
		{"if": "gave_bell", "who": "Bell", "text": "I'll ring when it's supper. Wherever you are, you'll hear it. That's how bells work."},
		{"if": "gave_orrin", "who": "Orrin", "text": "Look up, now and then, even from down there. We'll all be looking down."},
		{"if": "gave_gudgeon", "who": "Old Gudgeon", "text": "Mm. Come back. Fish have a long while. I would rather not spend it waiting."},
		{"who": "Nan Tallow", "text": "And whatever you find at the bottom, little wick: you are not walking down there alone. You never were."},
	],

	# --- Ash and the lantern ---------------------------------------------------------
	"ash_lantern": [
		{"set": "ash_told_lantern"},
		{"if": "in:glimmerdeep", "who": "Ash", "text": "My lantern's still down here, you know. Up past the violet glimmer, over the black water, where it went out."},
		{"if": "!in:glimmerdeep", "who": "Ash", "text": "My lantern's still down in the Glimmerdeep, you know. Up past the violet glimmer above where you found me, where it went out."},
		{"who": "Ash", "text": "I left it. I couldn't carry it cold. It felt like carrying a sleeping thing that wouldn't wake up."},
		{"who": "Ash", "text": "Violet glimmer needs a strong flame. Three embers, at least. I didn't have three left, at the end."},
	],
	"ash_lantern_found": [
		{"set": "ash_saw_lantern"},
		{"who": "Ash", "text": "...You found it."},
		{"who": "Ash", "text": "Don't give it to me. Not yet. Take it to the Little Hearth first. Fire remembers things."},
		{"who": "Ash", "text": "I'd like to know if it remembers me kindly."},
	],
	"ash_after_echo": [
		{"set": "ash_heard_echo"},
		{"who": "", "text": "You hold out the old lantern. Ash takes it in both hands, very carefully, as if it might still be hot."},
		{"who": "Ash", "text": "It remembered the egg, didn't it. That's the last thing I remember too."},
		{"who": "Ash", "text": "Thank you for carrying it home. I'll keep it by the fire. Not to light. Just to sit with."},
		{"if": "in:old_hollow", "who": "Ash", "text": "And I've stopped feeding the hearth too much. A little at a time, now. Things last longer that way. Even fires."},
	],

	# --- the people Lark warmed -------------------------------------------------------
	"burrow_after_echo": [
		{"set": "burrow_heard_lark"},
		{"who": "Burrow", "text": "A lantern-person warmed me once. When I was a pup, by the old eye-stone. Gave me a warm I kept in a hole for years."},
		{"who": "Burrow", "text": "Lark? Was that their name? Huh. I never asked. You don't ask names when you're a pup. You just say thank you, very loud."},
		{"who": "Burrow", "text": "Tell them thank you. Very loud. From me."},
	],
	"gudgeon_after_echo": [
		{"set": "gudgeon_heard_lark"},
		{"who": "Old Gudgeon", "text": "Mm. That lantern, an age ago. The one who warmed my pool."},
		{"who": "Old Gudgeon", "text": "Lark? Mm. Fish do not ask names. I should have asked."},
		{"who": "Old Gudgeon", "text": "When you sat by my water in the Halls, cold as I was... I thought, it is the same lantern. It is not. It is the same kindness. That is better."},
	],

	# --- Wisp and Glim ------------------------------------------------------------------
	"wisp_after_echo": [
		{"set": "wisp_asked_glim"},
		{"who": "Wisp", "text": "Mama went down the old seam? Under the Glimmerdeep? To keep me warm?"},
		{"who": "Wisp", "text": "Then she's down there! She has to be! Mama always comes back. Eventually. Maybe she's just very, very eventually."},
		{"who": "Wisp", "text": "Will you look? Please? You're so good at looking. You found ME."},
	],
	"wisp_glim_home": [
		{"set": "wisp_heard_glim"},
		{"who": "Wisp", "text": "MAMA'S HOME! Mama's home! I TOLD everyone! Mama always comes back. Eventually!"},
		{"who": "Wisp", "text": "Eventually was a long time. But she came. She CAME."},
	],
	"glim_found": [
		{"set": "met_glim"},
		{"who": "", "text": "At the bottom of the old seam, a glow-grub so dim you nearly step on her."},
		{"who": "Glim", "text": "...Is somebody there? A light? Oh. Oh, you've a lantern. Just like the one who warmed me, an age ago."},
		{"who": "Glim", "text": "I came down to lay my egg where it was warm. And then it wasn't warm any more. And I couldn't find the way back up in the dark."},
		{"who": "Glim", "text": "My little one... is my little one alive? Is she bright?"},
		{"who": "", "text": "You tell her about Wisp, in Old Hollow. Very bright. Very loud.", "choices": [
			{"text": "Give Glim an ember", "give": "glim", "goto": "glim_given"},
			{"text": "Not yet", "goto": "glim_repeat"},
		]},
	],
	"glim_given": [
		{"who": "Glim", "text": "Oh! Oh, I'm glowing! I can see the way up! I can see ALL the ways up!"},
		{"who": "Glim", "text": "Old Hollow, you said? I'll follow the warm. I'll be there before you, you see if I'm not."},
	],
	"glim_repeat": [
		{"who": "Glim", "text": "Tell her Mama's coming. Mama always comes back. Eventually."},
	],
	"glim_hollow": [
		{"who": "Glim", "text": "Look at her. LOOK at her. She glows so loud."},
		{"who": "Glim", "text": "I missed every bit of her growing up. Now I'm going to sit right here and watch the rest."},
	],
	"glim_epilogue": [
		{"who": "Glim", "text": "Morning! Real morning. My little one's never seen one. She's trying to glow louder than it."},
	],

	# --- Bell and Maud's handbell ---------------------------------------------------------
	"bell_ask_bell": [
		{"set": "bell_asked_bell"},
		{"who": "Bell", "text": "Mama had a handbell. A big brass one. She rang it so everybody came home for supper."},
		{"who": "Bell", "text": "It's in the supper hall, under the water, past the eye that won't wake up. I can't go in. It's too dark, even for ghosts."},
		{"who": "Bell", "text": "If I had Mama's bell, maybe she'd hear it. Maybe she'd come."},
	],
	"bell_sees_bell": [
		{"set": "bell_saw_bell"},
		{"who": "Bell", "text": "That's Mama's bell! You found it! You found it!"},
		{"who": "Bell", "text": "It's so cold. Can you warm it up? Mama said the little fire up top could warm anything. Even a bell. Even a ghost."},
	],
	"bell_after_echo": [
		{"set": "bell_heard_echo"},
		{"who": "", "text": "You hold out Maud's handbell. Bell goes very still."},
		{"who": "Bell", "text": "That's Mama's. Was it... was it in the water?"},
		{"who": "", "text": "You tell her what you saw. All of it. The Long Stair. The five Keepers. The door at the top, and Maud turning round."},
		{"who": "Bell", "text": "...She came back for me."},
		{"who": "Bell", "text": "I thought she forgot. I rang and rang and I thought, she's forgotten me. But she was coming. She was coming the whole time."},
		{"who": "Bell", "text": "She did come."},
		{"who": "Bell", "text": "Can I keep it? I'll ring it for supper. Both bells. One for me, and one for Mama."},
		{"card": "Maud's Handbell", "sub": "Rung for supper again.", "hold": 2.4},
	],

	# --- Tallow and the forty doors ------------------------------------------------------
	"tallow_forty_doors": [
		{"set": "tallow_heard_maud"},
		{"who": "Nan Tallow", "text": "Five Keepers. Climbing out of the water with nothing, and building doors under a fallen tree."},
		{"who": "Nan Tallow", "text": "Forty doors, for five people. They meant to fill them. They meant for everyone to come home."},
		{"who": "Nan Tallow", "text": "Well. We're filling them, aren't we. Slowly. One door at a time. They'd like that."},
	],

	# --- help in return ---------------------------------------------------------------------
	"gudgeon_ferry": [
		{"who": "Old Gudgeon", "text": "Mm. The well goes down, you know. All the way down. Springs under springs.", "choices": [
			{"text": "Swim me to the Drowned Halls", "if": "visited_drowned", "event": "go:drowned:4"},
			{"text": "Swim me to the Starwell", "if": "visited_starwell", "event": "go:starwell:1"},
			{"text": "Just saying hello", "goto": "gudgeon_hollow"},
		]},
	],
	"orrin_telescope": [
		{"set": "orrin_looked"},
		{"who": "Orrin", "text": "Do you know, a telescope sees a long way if you point it at the ground instead of the sky. Nobody ever does."},
		{"who": "Orrin", "text": "Hold still. Hm. Hmm. There's a name-stone glinting somewhere down there... and another..."},
		{"who": "Orrin", "text": "I've marked roughly where in your Journal. Very roughly. The ground is much harder to read than stars."},
	],

	# --- The First Page ---------------------------------------------------------------------
	# After Many Hands, once all three Echoes are seen: the Hollow One asks to walk down with
	# you, and stepping into the Cradle again plays The First Page (great_hearth.gd).
	"hollow_one_walk": [
		{"who": "The Hollow One", "text": "Lark's lantern. Maud's bell. My page. You have sat at that little fire three times now, and watched three of us go down."},
		{"who": "The Hollow One", "text": "The Hearth is lit. Many hands lit it. And I stood at the edge of the bridge, the way I always stand at the edge."},
		{"who": "The Hollow One", "text": "I turned back once, little wick. I would like not to, this time. Will you walk down with me?", "choices": [
			{"text": "Walk down together", "goto": "hollow_one_walk_go"},
			{"text": "Not yet", "goto": "hollow_one_walk_wait"},
		]},
	],
	"hollow_one_walk_go": [
		{"set": "vesper_walk"},
		{"who": "", "text": "The Hollow One holds out a hand of night, and you take it. The stairs go by like a dream: roots, and stone, and the long warm dark."},
		{"event": "go:hearth:1"},
	],
	"hollow_one_walk_wait": [
		{"who": "The Hollow One", "text": "I have waited a very long time. I can wait a little longer. That part I am good at."},
	],
	"first_page_vesper": [
		{"who": "", "text": "The Hollow One does not stop at the edge of the bridge. It walks on, all the way to the Cradle, and stands beside you."},
		{"who": "The Hollow One", "text": "I turned back once. Not twice."},
		{"who": "The Hollow One", "text": "No wick should walk down alone. Edda carved that for me. It has taken me a very long time to read it."},
		{"event": "vesper_unveil", "who": "", "text": "It steps into the fire with you. The dark burns off it like mist off a morning, and underneath is a small hooded someone with a long gold scarf."},
		{"who": "Vesper", "text": "...Oh. It's warm. It was always warm. I was only afraid."},
	],
	"first_page_end": [
		{"music": "first_page", "who": "", "text": "Two wicks in the Cradle. The Hearth takes a little from each, and gives back more than it takes."},
		{"who": "", "text": "It roars up, gold and red and white, and the whole mountain breathes in. And neither of you burns out."},
		{"who": "", "text": "Far up the roots, in a village under a fallen tree, every one of forty doors swings open at once."},
		{"card": "The First Page", "sub": "Many flames together burn on.", "hold": 3.0},
		{"set": "ending_first_page"},
		{"set": "ending_many"},
		{"unset": "seen_epilogue_wake"},  # wake again, even after an earlier ending
		{"event": "go:old_hollow:epilogue"},
	],
	"vesper_epilogue": [
		{"who": "Vesper", "text": "So this is supper. I'd heard about it. Bell made me one, once. It was mostly bread."},
		{"who": "Vesper", "text": "Thank you for walking down with me, little wick. I'd been waiting a long time for someone to."},
	],
}
