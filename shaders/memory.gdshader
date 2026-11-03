// The memory filter over an Echo: the world goes warm, faded and grainy at the edges,
// like something remembered. `fear` closes darkness in from the edges (Vesper).
shader_type canvas_item;

uniform sampler2D screen : hint_screen_texture, filter_nearest;
uniform float amount : hint_range(0.0, 1.0) = 1.0;
uniform vec3 tint = vec3(1.0, 0.86, 0.68);
uniform float fear : hint_range(0.0, 1.0) = 0.0;
uniform vec2 pixels = vec2(480.0, 270.0);

void fragment() {
	vec3 c = texture(screen, SCREEN_UV).rgb;
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	vec3 mem = mix(c, vec3(l) * tint * 1.12, 0.5);
	// film grain, one value per game pixel, a dozen times a second
	vec2 cell = floor(SCREEN_UV * pixels) + floor(TIME * 12.0) * vec2(17.0, 31.0);
	float n = fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
	mem += (n - 0.5) * 0.045;
	vec2 d = SCREEN_UV - 0.5;
	d.x *= pixels.x / pixels.y;
	float r = length(d);
	mem *= mix(0.7, 1.0, smoothstep(0.95, 0.35, r));
	vec3 col = mix(c, mem, amount);
	// fear: the dark closes in from the edges
	float open = smoothstep(0.95 - fear * 0.62, 0.62 - fear * 0.5, r);
	col *= mix(1.0, open, clamp(fear * 1.2, 0.0, 1.0));
	COLOR = vec4(col, 1.0);
}
