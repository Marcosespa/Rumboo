import {cp, mkdir, access} from 'node:fs/promises'
import {resolve} from 'node:path'
import {fileURLToPath} from 'node:url'

const root = fileURLToPath(new URL('.', import.meta.url))
const out = resolve(root, 'dist')
const files = ['index.html', 'styles.css', 'main.js', 'copy.js', 'config.js', 'icons.js', 'tokens.css', 'assets']
for (const file of files) await access(resolve(root, file))
await mkdir(out, {recursive: true})
for (const file of files) await cp(resolve(root, file), resolve(out, file), {recursive: true, force: true})
console.log(`Sitio estático listo en ${out}`)
