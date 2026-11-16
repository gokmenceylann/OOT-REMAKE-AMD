const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { parse } = require(path.resolve(process.argv[2], 'node_modules/yaml'));

const folder = path.resolve(__dirname, '../.github/ISSUE_TEMPLATE');
function read(name) {
    return parse(fs.readFileSync(path.join(folder, name), 'utf8'));
}

const names = ['bug', 'gpu-compatibility', 'performance', 'visual-glitch', 'feature'];
for (const name of names) {
    const form = read(name + '.yml');
    assert.ok(form.name && form.description && Array.isArray(form.body) && form.body.length, name);
    const ids = form.body.map(field => field.id);
    assert.equal(new Set(ids).size, ids.length, name + ' duplicate field ID');
    for (const field of form.body) {
        assert.ok(/^[A-Za-z0-9_-]+$/.test(field.id || ''), name + ' invalid field ID');
        assert.ok(['textarea', 'checkboxes'].includes(field.type) && field.attributes?.label, name);
        if (field.type === 'checkboxes') {
            const options = field.attributes.options;
            assert.ok(Array.isArray(options) && options.length && options.every(option => option.label), name);
        }
    }
}

const config = read('config.yml');
assert.equal(typeof config.blank_issues_enabled, 'boolean');
assert.ok(Array.isArray(config.contact_links) && config.contact_links.length);
for (const link of config.contact_links) {
    const url = new URL(link.url);
    assert.ok(link.name && link.about && url.protocol === 'https:');
}
console.log('Validated five issue forms and the issue chooser configuration.');
