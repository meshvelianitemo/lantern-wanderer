class_name StoryDrowned
## Chapter III: The Drowned Halls. The Keepers' ruins, the Book of Wicks,
## Bell, Old Gudgeon, and the Hook.

const LINES := {
	"drowned_arrive": [
		{"who": "", "text": "Old Gudgeon sinks away beneath you with one slow, enormous blink."},
		{"who": "", "text": "You stand dripping in the Keepers' halls. Pale lights drift under the water, like someone forgot to blow them out."},
	],
	"tablet_drowned_1": [
		{"who": "", "text": "HERE THE KEEPERS LIVED. HERE WE TENDED, AND SANG, AND WERE WARM."},
	],
	"tablet_drowned_2": [
		{"who": "", "text": "THE FIRST WICK CAME BACK UP THE STAIRS. WE DID NOT ASK WHY."},
		{"who": "", "text": "THE WATER ROSE THAT WINTER."},
	],
	"tablet_drowned_3": [
		{"who": "", "text": "HOOKS FOR THE FLAME. LEAVE A LIGHT FOR THOSE BEHIND YOU."},
	],
	"tablet_drowned_4": [
		{"who": "", "text": "BEYOND: THE ROOTS. BEYOND THE ROOTS: THE HEARTH. GO GENTLY."},
	],
	"hook_no_gift": [
		{"who": "", "text": "An old iron hook on a stone foot, shaped to hold a lantern. It is cold, and empty."},
	],
	"rootdark_enter": [
		{"who": "", "text": "Beyond the last gate the masonry ends. Roots push through the walls, huge and black, like the fingers of something holding up the mountain."},
		{"who": "", "text": "You go down between them."},
	],

	# --- Bell -------------------------------------------------------------------
	"bell_intro": [
		{"who": "???", "text": "Ding... ding... Is it supper? Is somebody calling supper?"},
		{"who": "Bell", "text": "Oh. You're not Mama. You're a little lantern-person."},
		{"who": "Bell", "text": "I'm Bell. I ring for supper, so everybody comes home. I've been ringing a long time. Nobody comes."},
		{"who": "Bell", "text": "It's so cold in the water. Even ghosts get cold, did you know? Nobody tells you that."},
		{"set": "met_bell"},
		{"goto": "bell_ask"},
	],
	"bell_repeat": [
		{"who": "Bell", "text": "Ding... still nobody. Except you. You count."},
		{"goto": "bell_ask"},
	],
	"bell_ask": [
		{"if": "embers>=1", "who": "Bell", "text": "Your lantern looks so warm. Could I hold my hands near it? ...Could I keep a little bit?",
			"choices": [
				{"text": "Give Bell an ember.", "give": "bell", "goto": "bell_given"},
				{"text": "I can't.", "goto": "bell_refuse"},
				{"text": "...", "goto": "bell_refuse"},
			]},
		{"if": "!embers>=1", "who": "Bell", "text": "Your lantern's nearly empty too. Here, I'll ring for you. Ding. There. Now somebody's calling you home."},
	],
	"bell_given": [
		{"who": "", "text": "Bell cups the ember in her see-through hands, and the warmth soaks into her like dye into water."},
		{"who": "Bell", "text": "Oh! I'm warm! I'm all the way warm! I can feel my toes. I didn't know I still had toes!"},
		{"who": "Bell", "text": "There's a hollow up top? With a hearth? With people? ...Then I'll go and ring supper THERE."},
	],
	"bell_refuse": [
		{"who": "Bell", "text": "That's okay. I'll keep ringing. Somebody always comes, in the end. Mama said."},
	],
	"bell_thanks": [
		{"who": "Bell", "text": "I'm going up! I just have to remember how to float upwards. It's been ages."},
	],

	# --- The Archivist -----------------------------------------------------------
	"archivist_intro": [
		{"who": "???", "text": "Hush. Please. The books are sleeping. ...Ah. A wick. Of course it is a wick. Who else comes down here?"},
		{"who": "The Archivist", "text": "I am the Archivist. When the water rose, the other Keepers went to sleep in it. Someone had to stay awake and remember."},
		{"who": "The Archivist", "text": "I keep the Book of Wicks. Every one of you who ever came down the stairs. Would you like to see?",
			"choices": [
				{"text": "Show me.", "goto": "archivist_book"},
				{"text": "Why keep a book?", "goto": "archivist_why"},
				{"text": "...", "goto": "archivist_book"},
			]},
	],
	"archivist_why": [
		{"who": "The Archivist", "text": "Because the Hearth forgets. Fire always forgets. Somebody has to remember who it ate."},
		{"who": "The Archivist", "text": "...Forgive me. That was unkind. I have been alone with the water a long time."},
		{"goto": "archivist_book"},
	],
	"archivist_book": [
		{"sfx": "page", "who": "", "text": "The Archivist opens an enormous, swollen book. Page after page of names, in many different hands."},
		{"who": "The Archivist", "text": "Fenn, who sang. Ilse, who limped. Tamsin, who was afraid, and went anyway. Oriel. Bram. Little Coll..."},
		{"sfx": "page", "who": "The Archivist", "text": "And here. The last. 'Lark - who gave too much, too soon. Lantern went out in the Glimmerdeep.'"},
		{"set": "knows_lark"},
		{"if": "met_ash", "who": "The Archivist", "text": "You are looking at me strangely.",
			"choices": [
				{"text": "Lark is alive. They call themselves Ash.", "goto": "archivist_ash"},
				{"text": "...", "goto": "archivist_page"},
			]},
		{"goto": "archivist_page"},
	],
	"archivist_ash": [
		{"who": "The Archivist", "text": "...Alive? A wick whose flame went out, still walking about?"},
		{"who": "The Archivist", "text": "Then the book is wrong. I have never in my life been so glad to be wrong."},
		{"who": "", "text": "With a trembling hand, the Archivist crosses something out, and writes beside it."},
		{"goto": "archivist_page"},
	],
	"archivist_page": [
		{"who": "The Archivist", "text": "And this line, here, is blank. It is waiting for you. What shall I write?",
			"choices": [
				{"text": "Write 'Little Wick'.", "goto": "archivist_write_wick"},
				{"text": "I don't have a name.", "goto": "archivist_write_none"},
				{"text": "...", "goto": "archivist_write_quiet"},
			]},
	],
	"archivist_write_wick": [
		{"who": "The Archivist", "text": "'Little Wick.' Mossback's name for all of you. ...It is a good name. It has been a good name a hundred times."},
		{"goto": "archivist_gift"},
	],
	"archivist_write_none": [
		{"who": "The Archivist", "text": "Then I will write: 'The one who came after Lark.' And leave room for the rest."},
		{"goto": "archivist_gift"},
	],
	"archivist_write_quiet": [
		{"who": "The Archivist", "text": "Silence. Yes. Some of the best wicks had nothing to say. I will leave it blank, and you can fill it in at the bottom."},
		{"goto": "archivist_gift"},
	],
	"archivist_gift": [
		{"who": "The Archivist", "text": "Now. The Keepers left hooks all through these halls. Old iron, shaped to hold a flame. Let me show you the trick of it."},
		{"who": "", "text": "The Archivist touches your lantern with one cold finger. Something inside it learns a new shape."},
		{"set": "gift_hook", "sfx": "hook"},
		{"card": "Lantern Gift: Hook", "sub": "Press {key:interact} at a Keeper hook to leave your flame burning there", "hold": 3.0},
		{"who": "The Archivist", "text": "Leave your flame on a hook and it burns there as bright as in your lantern. Glimmer will hold. Eye-gates will see."},
		{"who": "The Archivist", "text": "But you walk on in the dark, with only a spark of yourself. Come back for it. Always come back for it."},
		{"who": "The Archivist", "text": "The way down is past the cistern, through the last eye-gate. Go gently, little one."},
	],
	"archivist_repeat": [
		{"who": "The Archivist", "text": "Leave a light for those behind you. That was the Keepers' whole philosophy. It is carved on half the walls."},
		{"who": "The Archivist", "text": "Eye-gates open for light held on them long enough. A hook will hold it for you."},
	],

	# --- Old Gudgeon in the cistern -------------------------------------------
	"gudgeon_cold": [
		{"who": "Old Gudgeon", "text": "Mm. Little light. You found your way through the halls. I heard you splashing."},
		{"who": "Old Gudgeon", "text": "The water grows colder every year. My old fins are stiff. I do not think I can carry anyone again."},
		{"who": "Old Gudgeon", "text": "There is a glass house on the floor of the lake. I would have liked to show you. Ah, well."},
		{"set": "met_gudgeon_cold"},
		{"goto": "gudgeon_ask"},
	],
	"gudgeon_cold_repeat": [
		{"who": "Old Gudgeon", "text": "Still cold, little light. Still here."},
		{"goto": "gudgeon_ask"},
	],
	"gudgeon_ask": [
		{"if": "embers>=1", "who": "Old Gudgeon", "text": "...A fish should not ask. But you smell warm.",
			"choices": [
				{"text": "Give Old Gudgeon an ember.", "give": "gudgeon", "goto": "gudgeon_given"},
				{"text": "I'm sorry.", "goto": "gudgeon_refuse"},
			]},
	],
	"gudgeon_given": [
		{"who": "", "text": "You lower an ember to the water. Old Gudgeon takes it as gently as a kiss."},
		{"who": "Old Gudgeon", "text": "Mmmmm. Oh. Oh, that is... the water remembers being warm."},
		{"who": "Old Gudgeon", "text": "I know the springs that run up under the mountain, all the way to the top. There is a well up there, I think. In a hollow full of lights."},
		{"who": "Old Gudgeon", "text": "I will find it. Fish have a long while."},
	],
	"gudgeon_refuse": [
		{"who": "Old Gudgeon", "text": "Mm. You are right. A fish is a small thing to spend a fire on. Go well, little light."},
	],
	"gudgeon_warm": [
		{"who": "Old Gudgeon", "text": "Mm. Warming my old bones before the long swim up. Go on, little light. Go on."},
		{"who": "Old Gudgeon", "text": "...Though. There is a glass house on the floor of the lake. I saw a light in it once, a very long time ago."},
		{"who": "Old Gudgeon", "text": "I am warm enough to dive now. Would you like to see it?",
			"choices": [
				{"text": "Take me down.", "goto": "gudgeon_dive"},
				{"text": "Not now.", "goto": "gudgeon_not_now"},
			]},
	],
	"gudgeon_dive_again": [
		{"who": "Old Gudgeon", "text": "Mm. The glass house again? I don't mind. The swim keeps me warm.",
			"choices": [
				{"text": "Take me down.", "goto": "gudgeon_dive"},
				{"text": "Not now.", "goto": "gudgeon_not_now"},
			]},
	],
	"gudgeon_dive": [
		{"who": "Old Gudgeon", "text": "Mm. Hold your breath, little light. And hold your flame closer."},
		{"event": "go:starwell:1"},
	],
	"gudgeon_not_now": [
		{"who": "Old Gudgeon", "text": "Mm. Whenever you like. Fish have a long while."},
	],

	# --- after the Starwell -----------------------------------------------------
	"bell_maud": [
		{"who": "Bell", "text": "You've got a stone with writing on. Can I see? I can read! A bit!"},
		{"who": "Bell", "text": "M... A... U... D. Maud! That's Mama! That's my mama's name!"},
		{"who": "Bell", "text": "I forgot it. I only ever called her Mama. Maud. Maud. I'll ring it so I don't forget again. Ding! Maud!"},
		{"set": "bell_heard_maud"},
		{"if": "!bell_asked_bell,!keepsake:bell,!echo_maud", "goto": "bell_ask_bell"},
	],
	"archivist_orrin": [
		{"who": "The Archivist", "text": "You smell of the lake bottom. And of brass. ...You went down to the Starwell."},
		{"who": "The Archivist", "text": "Orrin? Awake? That old star-counter always did fall asleep in the wrong places. ...I thought I was the last."},
		{"who": "The Archivist", "text": "Then I am not the only one remembering. How strange. How very light that feels."},
		{"set": "archivist_heard_orrin"},
	],
}
