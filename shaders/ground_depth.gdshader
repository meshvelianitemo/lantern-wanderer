shader_type canvas_item;
// Darkens ground tiles the further they are from open air, with ordered
// dithering so the falloff stays pixel-art crisp.

uniform sampler2D depth_map : filter_linear, repeat_disable;
uniform vec2 map_tiles = vec2(1.0);
uniform float tile_size = 16.0;
uniform float strength = 0.9;
uniform vec3 deep_tint = vec3(0.13, 0.09, 0.16);

varying vec2 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float bayer4(vec2 p) {
	ivec2 q = ivec2(mod(floor(p), 4.0));
	int i = q.x + q.y * 4;
	float m[16] = float[16](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	return (m[i] + 0.5) / 16.0;
}

void fragment() {
	vec4 c = COLOR;
	float d = texture(depth_map, world_pos / tile_size / map_tiles).r;
	float levels = 3.0;
	float q = clamp(floor(d * levels + bayer4(world_pos)) / levels, 0.0, 1.0);
	c.rgb = mix(c.rgb, c.rgb * deep_tint, q * strength);
	COLOR = c;
}
