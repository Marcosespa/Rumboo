const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const collection = JSON.parse(fs.readFileSync(path.join(__dirname, '../postman/satrack-service.postman_collection.json'), 'utf8'));
const requests = collection.item[0].item.filter(item => item.request.method === 'POST');

function sandbox(item, variables = {}, raw = item.request.body.raw, headers = {}) {
  const local = new Map();
  const shared = new Map(collection.variable.map(v => [v.key, v.value]));
  const get = name => local.has(name) ? local.get(name) : Object.hasOwn(variables, name) ? variables[name] : shared.get(name);
  let next;
  const pm = {
    request: { body: { raw }, headers: { get: name => headers[name] } },
    variables: {
      get,
      set: (name, value) => local.set(name, value),
      replaceIn: text => text.replace(/{{\s*([^{}]+?)\s*}}/g, (match, name) => name === '$guid' ? randomUUID() : get(name) ?? match),
    },
    collectionVariables: { get: name => shared.get(name), set: (name, value) => shared.set(name, value) },
    execution: { setNextRequest: value => { next = value; } },
    test: (name, fn) => fn(),
    response: { code: 202, json: () => ({ job_id: '7f1c2e9a-5b1d-4c1e-9a43-0f3f8c1f2a10' }), to: { have: { status: expected => assert.equal(expected, 202) } } },
  };
  return { pm, shared, next: () => next, run: listen => vm.runInNewContext(item.event.find(e => e.listen === listen).script.exec.join('\n'), { pm }) };
}

for (const item of requests) {
  test(`${item.name}: genera accountJson y escapa la contraseña`, () => {
    const password = 'demo"\\clave';
    const session = sandbox(item, { apiKey: 'demo-key', satrackUsername: 'demo-user', satrackPassword: password });
    session.run('prerequest');
    const body = JSON.parse(session.pm.variables.replaceIn(item.request.body.raw));
    assert.equal(body.account.password, password);
    assert.equal(body.account.id, 'satrack-local');
  });

  test(`${item.name}: admite usuario literal sin satrackUsername`, () => {
    const raw = '{"job_id":"{{$guid}}","type":"positions","account":{"id":"demo","username":"demo-user","password":"{{satrackPassword}}"},"plates":["ABC123"]}';
    const session = sandbox(item, { apiKey: 'demo-key', satrackPassword: 'demo-password' }, raw);
    session.run('prerequest');
    assert.equal(JSON.parse(session.pm.variables.replaceIn(raw)).account.username, 'demo-user');
    assert.equal(session.pm.request.body.raw, raw);
  });

  test(`${item.name}: identifica solo la contraseña faltante del body manual`, () => {
    const raw = '{"account":{"username":"demo-user","password":"{{satrackPassword}}"}}';
    const session = sandbox(item, { apiKey: 'demo-key' }, raw);
    assert.throws(() => session.run('prerequest'), error => {
      assert.match(error.message, /Faltan variables: satrackPassword\./);
      assert.ok(!error.message.includes('satrackUsername'));
      assert.ok(!error.message.includes('demo-key'));
      return true;
    });
    assert.equal(session.next(), null);
  });

  test(`${item.name}: acepta una API key en header explícito`, () => {
    const session = sandbox(item, {}, '{"account":{"username":"demo-user","password":"demo-password"}}', { 'X-Api-Key': 'demo-key' });
    session.run('prerequest');
  });

  test(`${item.name}: informa apiKey cuando el header es una variable vacía`, () => {
    const session = sandbox(item, {}, '{"account":{"username":"demo-user","password":"demo-password"}}', { 'X-Api-Key': '{{apiKey}}' });
    assert.throws(() => session.run('prerequest'), /Faltan variables: apiKey\./);
  });

  test(`${item.name}: usa el UUID que realmente devolvió el servicio`, () => {
    const session = sandbox(item, { apiKey: 'demo-key', satrackUsername: 'demo-user', satrackPassword: 'demo-password' });
    session.run('prerequest');
    session.run('test');
    const key = item.name.startsWith('2.') ? 'vehiclesJobId' : 'positionsJobId';
    assert.equal(session.shared.get(key), session.pm.response.json().job_id);
    assert.equal(session.pm.variables.get(key), session.pm.response.json().job_id);
  });
}
