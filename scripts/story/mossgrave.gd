class_name StoryMossgrave
## Chapter I: Mossgrave Woods. Mossback the totem, who wakes every wick.

const LINES := {
	"sign_start": [
		{"who": "", "text": "MOSSGRAVE WOODS\n<- Old Hollow                 The Deep ->"},
	],
	"cave_enter": [
		{"who": "", "text": "Cold air breathes out of the dark. Somewhere far below, something faintly glows."},
		{"who": "", "text": "You lift your lantern a little higher, and step into the Deep..."},
	],

	"mossback_intro": [
		{"who": "???", "text": "...hm? A light. After so many dark nights... a light."},
		{"who": "???", "text": "Come closer, little wick. Let these old eyes have a look at you."},
		{"who": "Mossback", "text": "I am Mossback. I have stood in these woods for a thousand winters, and never have they felt this cold."},
		{"who": "Mossback", "text": "Deep beneath the mountain burns the Hearth. Its warmth is what keeps the forest breathing."},
		{"who": "Mossback", "text": "But the Hearth is going out. Each night the dark creeps a little further out of the caves."},
		{"who": "Mossback", "text": "And yet here you are... carrying an ember. Perhaps the very last one.",
			"choices": [
				{"text": "I'll take it to the Hearth.", "goto": "mossback_brave"},
				{"text": "Why me? I'm so small.", "goto": "mossback_small"},
				{"text": "...", "goto": "mossback_silent"},
			]},
	],
	"mossback_brave": [
		{"who": "Mossback", "text": "Ha! Brave words. These woods have not heard such in an age."},
		{"goto": "mossback_task"},
	],
	"mossback_small": [
		{"who": "Mossback", "text": "Small? So is a spark. And every great fire began as one."},
		{"goto": "mossback_task"},
	],
	"mossback_silent": [
		{"who": "Mossback", "text": "Not one for words? Good. The dark does not listen to them anyway."},
		{"goto": "mossback_task"},
	],
	"mossback_task": [
		{"who": "Mossback", "text": "Gather the drifting embers on your way. Each one will make your lantern burn brighter."},
		{"who": "Mossback", "text": "Light the old shrines. They will remember your warmth, should you stumble."},
		{"who": "Mossback", "text": "If your flame wants company, Old Hollow lies west. Nan Tallow still keeps a hearth there... or tries to."},
		{"who": "Mossback", "text": "The way down lies east, past the broken bridge, where the cave mouth swallows the light."},
		{"who": "Mossback", "text": "Go now, little wick. And keep your flame close."},
		{"set": "met_mossback"},
	],
	"mossback_repeat": [
		{"who": "Mossback", "text": "East, little wick. Past the broken bridge. The Deep is waiting... and so am I."},
	],

	"mossback_after_deep": [
		{"who": "Mossback", "text": "You have been below. I can smell the stone on your cloak."},
		{"who": "Mossback", "text": "The glimmer still sings down there, does it? It only ever sang back what it was given."},
		{"if": "given>=1", "who": "Mossback", "text": "Your flame is smaller than when you left. You have been giving it away."},
		{"if": "given>=1", "who": "Mossback", "text": "Good. A wick that keeps everything for itself only burns faster."},
		{"if": "!given>=1", "who": "Mossback", "text": "Your flame is bright. You have kept it close, as I told you."},
		{"if": "!given>=1", "who": "Mossback", "text": "...Perhaps I told you wrong. Warmth that is never shared goes cold all the same."},
		{"if": "met_ash", "who": "Mossback", "text": "And you found Ash. Grey now, I suppose. Ash was bright once. Brighter than you."},
		{"if": "met_ash", "who": "Mossback", "text": "I called that one 'little wick' too.",
			"choices": [
				{"text": "What happened to Ash?", "goto": "mossback_ash_what"},
				{"text": "Why do you call us 'wick'?", "goto": "mossback_ash_why"},
				{"text": "...", "goto": "mossback_ash_quiet"},
			]},
		{"set": "mossback_heard_deep"},
	],
	"mossback_ash_what": [
		{"who": "Mossback", "text": "Their lantern went out before they reached the Hearth. That is all. That is everything."},
		{"set": "mossback_heard_deep"},
	],
	"mossback_ash_why": [
		{"who": "Mossback", "text": "...Because that is what you are, little one. Go on. The Deep is waiting."},
		{"set": "mossback_heard_deep"},
	],
	"mossback_ash_quiet": [
		{"who": "Mossback", "text": "Yes. Silence is the right answer, sometimes."},
		{"set": "mossback_heard_deep"},
	],

	"mossback_after_drowned": [
		{"who": "Mossback", "text": "So. You have walked the Keepers' halls. Drowned, all of it, I suppose."},
		{"who": "Mossback", "text": "I remember when their lanterns lit this mountain from the inside, like a paper lamp."},
		{"who": "Mossback", "text": "They carved me, you know. Asked me to wait here, and wake each wick, and send them on."},
		{"who": "Mossback", "text": "I have woken a great many of you.",
			"choices": [
				{"text": "How many?", "goto": "mossback_many"},
				{"text": "What happened to them?", "goto": "mossback_what_happened"},
				{"text": "...", "goto": "mossback_drowned_quiet"},
			]},
	],
	"mossback_many": [
		{"who": "Mossback", "text": "More than I can count. Fewer than I can forget."},
		{"set": "mossback_heard_drowned"},
	],
	"mossback_what_happened": [
		{"who": "Mossback", "text": "They went down. They burned. The forest breathed. That is what happens, little wick."},
		{"who": "Mossback", "text": "...I am sorry. I am old, and I have only ever known the one way of telling it."},
		{"set": "mossback_heard_drowned"},
	],
	"mossback_drowned_quiet": [
		{"who": "Mossback", "text": "You are right not to ask. Some answers are heavier than lanterns."},
		{"set": "mossback_heard_drowned"},
	],

	"mossback_after_root": [
		{"who": "Mossback", "text": "You smell of roots and old dark. You have met the Root-Mother, then."},
		{"who": "Mossback", "text": "She carried you up to me, you know. A spark through her roots, the night the Hearth last flickered."},
		{"who": "Mossback", "text": "I held you in the moss until you woke. You were so very small. You still are."},
		{"who": "Mossback", "text": "Go on down, little wick. Whatever you choose at the bottom... I am glad it was you I woke."},
		{"set": "mossback_heard_root"},
	],
	"mossback_later": [
		{"if": "!visited_drowned", "who": "Mossback", "text": "Go gently, little wick. The Deep is listening."},
		{"if": "visited_drowned,!visited_rootdark", "who": "Mossback", "text": "Down and down. The Keepers built their roads for feet like yours."},
		{"if": "visited_rootdark", "who": "Mossback", "text": "Nearly there now. I can feel the Hearth listening for you."},
	],
}
