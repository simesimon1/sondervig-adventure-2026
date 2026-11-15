import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const directory = new URL('../assets/characters/', import.meta.url);
const manifest = JSON.parse(fs.readFileSync(new URL('manifest.json', directory)));
function glb(file) {
  const data = fs.readFileSync(new URL(file, directory));
  assert.equal(data.readUInt32LE(0), 0x46546c67); assert.equal(data.readUInt32LE(4), 2); assert.equal(data.readUInt32LE(8), data.length);
  const length = data.readUInt32LE(12); assert.equal(data.readUInt32LE(16), 0x4e4f534a);
  const json = JSON.parse(data.subarray(20, 20 + length).toString());
  assert.equal(data.readUInt32LE(24 + length), 0x004e4942);
  return { json, binary: data.subarray(28 + length), bytes: data.length };
}
function accessor(asset, index) {
  const a = asset.json.accessors[index], v = asset.json.bufferViews[a.bufferView];
  const width = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[a.type];
  assert.ok(width); const sizes = { 5121: 1, 5123: 2, 5125: 4, 5126: 4 }, size = sizes[a.componentType]; assert.ok(size);
  const values = [];
  for (let i = 0; i < a.count; i++) {
    const row = [];
    for (let j = 0; j < width; j++) {
      const offset = (v.byteOffset || 0) + (a.byteOffset || 0) + i * (v.byteStride || size * width) + j * size;
      const value = a.componentType === 5126 ? asset.binary.readFloatLE(offset) : a.componentType === 5125 ? asset.binary.readUInt32LE(offset) : a.componentType === 5123 ? asset.binary.readUInt16LE(offset) : asset.binary.readUInt8(offset);
      assert.ok(Number.isFinite(value)); row.push(value);
    }
    values.push(row);
  }
  return values;
}
for (const character of manifest.characters) {
  const asset = glb(character.file), j = asset.json;
  test(`${character.name}: self-contained GLB, mobile asset budget and actual height`, () => {
    assert.equal(asset.bytes, character.bytes); assert.ok(asset.bytes < 1_500_000);
    assert.ok(j.buffers.every(b => !b.uri)); assert.ok(j.images.every(i => !i.uri && i.bufferView !== undefined));
    assert.equal(j.skins.length, 1); assert.equal(j.skins[0].joints.length, 18);
    let min = Infinity, max = -Infinity, triangles = 0;
    for (const mesh of j.meshes) for (const primitive of mesh.primitives) {
      const pos = j.accessors[primitive.attributes.POSITION]; min = Math.min(min, pos.min[1]); max = Math.max(max, pos.max[1]);
      triangles += j.accessors[primitive.indices].count / 3;
    }
    assert.ok(Math.abs(min) < .001); assert.ok(Math.abs(max - character.height_m) < .003, `${max} vs ${character.height_m}`);
    assert.ok(triangles < 40_000); assert.equal(triangles, character.triangles);
  });
  test(`${character.name}: valid bone indices, normalized skin weights and looping clips`, () => {
    assert.deepEqual(j.animations.map(a => a.name).sort(), ['Idle', 'Walk']);
    for (const mesh of j.meshes) for (const primitive of mesh.primitives) {
      const joints = accessor(asset, primitive.attributes.JOINTS_0), weights = accessor(asset, primitive.attributes.WEIGHTS_0);
      assert.equal(joints.length, weights.length);
      for (let i = 0; i < joints.length; i++) {
        assert.ok(joints[i].every(n => n >= 0 && n < 18));
        assert.ok(Math.abs(weights[i].reduce((a,b) => a+b, 0) - 1) < .001);
      }
    }
    for (const clip of j.animations) {
      assert.ok(clip.channels.some(c => c.target.path === 'rotation'));
      for (const sampler of clip.samplers) {
        const times = accessor(asset, sampler.input).flat(), values = accessor(asset, sampler.output);
        assert.ok(times.at(-1) > .5); assert.ok(times.every((t,i) => !i || t > times[i-1]));
        assert.ok(values[0].every((v,i) => Math.abs(v-values.at(-1)[i]) < .001), `loop seam in ${clip.name}`);
      }
    }
  });
}
test('three original models together remain below 4 MB', () => {
  assert.equal(manifest.characters.length, 3); assert.ok(manifest.characters.reduce((s,c) => s+c.bytes,0) < 4_000_000);
});
