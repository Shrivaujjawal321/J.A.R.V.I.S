/* Figma Plugin API simulator — faithful enough to catch real runtime bugs.
 * Enforces the gotchas that actually throw in Figma:
 *   - mutating TEXT.characters / fontName / fontSize without loadFontAsync  -> throw
 *   - combineAsVariants with duplicate variant names / mismatched prop keys -> throw
 *   - createPage() beyond the Starter 3-page cap                            -> throw
 *   - layoutSizing* on a child whose parent has no auto-layout              -> throw
 *   - unknown node property writes                                         -> recorded as WARN
 */
'use strict';

const LOADED = new Set();
const AVAILABLE_FONTS = new Set([
  'Inter|Regular', 'Inter|Medium', 'Inter|Semi Bold', 'Inter|Bold',
  'Barlow Semi Condensed|Medium', 'Barlow Semi Condensed|SemiBold', 'Barlow Semi Condensed|Bold',
  'IBM Plex Mono|Regular', 'IBM Plex Mono|Medium', 'IBM Plex Mono|SemiBold',
]);

const WARN = [];
let ID = 0;
const nid = (t) => `${++ID}:${Math.floor(Math.random() * 900 + 100)}`;

const VALID_PROPS = new Set([
  'name', 'visible', 'opacity', 'x', 'y', 'width', 'height', 'rotation', 'locked', 'type', 'id',
  'layoutMode', 'primaryAxisSizingMode', 'counterAxisSizingMode', 'itemSpacing', 'layoutWrap',
  'counterAxisSpacing', 'counterAxisAlignItems', 'primaryAxisAlignItems', 'layoutAlign',
  'layoutGrow', 'layoutSizingHorizontal', 'layoutSizingVertical', 'layoutPositioning',
  'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
  'fills', 'strokes', 'strokeAlign', 'strokeWeight', 'strokeTopWeight', 'strokeRightWeight',
  'strokeBottomWeight', 'strokeLeftWeight', 'dashPattern',
  'cornerRadius', 'topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius',
  'clipsContent', 'constraints', 'effects', 'blendMode', 'isMask',
  'characters', 'fontName', 'fontSize', 'lineHeight', 'letterSpacing', 'textCase',
  'textDecoration', 'textAlignHorizontal', 'textAlignVertical', 'textAutoResize',
  'paragraphSpacing', 'hyperlink', 'textStyleId', 'fillStyleId', 'strokeStyleId',
  'componentProperties', 'variantProperties', 'overflowDirection', 'reactions',
  'primaryAxisAlignContent', 'counterAxisAlignContent', 'itemReverseZIndex',
  'strokesIncludedInLayout', 'expanded', 'description', 'documentationLinks',
  'minWidth', 'maxWidth', 'minHeight', 'maxHeight', 'resizeToFit', 'sectionContentsHidden', 'flowStartingPoints', 'backgrounds', 'devStatus',
]);

function fontKey(f) { return `${f.family}|${f.style}`; }
function assertFontLoaded(node, what) {
  const f = node._fontName;
  if (!f) return;
  if (!LOADED.has(fontKey(f))) {
    throw new Error(`Cannot write to node with unloaded font "${f.family} ${f.style}" (while setting ${what})`);
  }
}

class Node {
  constructor(type) {
    this.type = type;
    this.id = nid(type);
    this._name = type;
    this._children = null;
    this.parent = null;
    this.visible = true;
    this.opacity = 1;
    this.x = 0; this.y = 0;
    this._w = 100; this._h = 100;
    this.removed = false;
    this._reactions = [];
    return new Proxy(this, {
      set(t, k, v) {
        if (typeof k === 'string' && typeof v !== 'function' && !k.startsWith('_') && !(k in t) && !VALID_PROPS.has(k)) {
          WARN.push(`UNKNOWN PROP set: ${t.type}.${k}`);
        }
        if (k === 'characters' || k === 'fontSize' || k === 'lineHeight' ||
            k === 'letterSpacing' || k === 'textCase' || k === 'fills') {
          if (t.type === 'TEXT') assertFontLoaded(t, k);
        }
        if (k === 'fontName') {
          if (!v || !v.family) throw new Error('fontName must be {family,style}');
          if (!LOADED.has(fontKey(v))) {
            throw new Error(`Cannot set fontName to unloaded font "${v.family} ${v.style}"`);
          }
          t._fontName = v;
          return true;
        }
        if (k === 'layoutSizingHorizontal' || k === 'layoutSizingVertical') {
          const p = t.parent;
          if (v === 'FILL') {
            if (!p || !p.layoutMode || p.layoutMode === 'NONE') {
              throw new Error(`layoutSizing${k.endsWith('Horizontal') ? 'Horizontal' : 'Vertical'}='FILL' requires an auto-layout parent (node "${t._name}")`);
            }
          }
        }
        if (k === 'name') { t._name = String(v); return true; }
        t[k] = v;
        return true;
      },
      get(t, k) {
        if (k === 'name') return t._name;
        if (k === 'fontName') return t._fontName;
        if (k === 'width') return t._w;
        if (k === 'height') return t._h;
        if (k === 'children') return t._children ? t._children.slice() : undefined;
        if (k === 'reactions') return t._reactions;
        if (k === 'absoluteBoundingBox') {
          let ax = 0, ay = 0, cur = t;
          while (cur && cur.type !== 'PAGE' && cur.type !== 'DOCUMENT') { ax += cur.x || 0; ay += cur.y || 0; cur = cur.parent; }
          return { x: ax, y: ay, width: t._w, height: t._h };
        }
        return t[k];
      },
    });
  }
}

function makeContainer(type) {
  const n = new Node(type);
  n._children = [];
  n.layoutMode = 'NONE';
  n.primaryAxisSizingMode = 'AUTO';
  n.counterAxisSizingMode = 'AUTO';
  n.itemSpacing = 0;
  n.paddingTop = n.paddingRight = n.paddingBottom = n.paddingLeft = 0;
  n.fills = []; n.strokes = [];
  n.clipsContent = false;
  n.cornerRadius = 0;
  n.effects = [];
  n.appendChild = function (c) {
    if (!c) throw new Error('appendChild(undefined)');
    if (c === n) throw new Error('appendChild: cannot append node to itself');
    if (c.removed) throw new Error(`appendChild: node "${c.name}" was removed`);
    if (c.parent && c.parent._children) {
      const i = c.parent._children.indexOf(c);
      if (i >= 0) c.parent._children.splice(i, 1);
    }
    n._children.push(c);
    c.parent = n;
    return c;
  };
  n.insertChild = function (i, c) { n.appendChild(c); const a = n._children; a.pop(); a.splice(i, 0, c); c.parent = n; };
  n.resize = function (w, h) {
    if (!(w > 0) || !(h > 0)) throw new Error(`resize(${w}, ${h}) — both dimensions must be > 0 (node "${n.name}")`);
    n._w = w; n._h = h;
  };
  n.resizeWithoutConstraints = n.resize;
  n.rescale = function (s) { if (!(s > 0)) throw new Error('rescale must be > 0'); n._w *= s; n._h *= s; };
  n.remove = function () { n.removed = true; if (n.parent && n.parent._children) { const i = n.parent._children.indexOf(n); if (i >= 0) n.parent._children.splice(i, 1); } };
  n.findOne = function (fn) { for (const c of walk(n)) if (c !== n && fn(c)) return c; return null; };
  n.findAll = function (fn) { const o = []; for (const c of walk(n)) if (c !== n && (!fn || fn(c))) o.push(c); return o; };
  n.findChild = function (fn) { return n._children.find(fn) || null; };
  n.setReactionsAsync = async function (r) {
    if (!Array.isArray(r)) throw new Error('setReactionsAsync expects an array');
    for (const x of r) {
      if (!x.trigger || !x.trigger.type) throw new Error('reaction.trigger.type required');
      if (x.action) throw new Error('`action` (singular) is deprecated — use `actions: [...]`');
      if (!Array.isArray(x.actions)) throw new Error('reaction.actions must be an array');
      for (const a of x.actions) {
        if (a.type === 'NODE' && !a.destinationId) throw new Error('NAVIGATE action needs destinationId');
        if (a.type === 'NODE' && !a.navigation) throw new Error('NODE action needs navigation');
      }
    }
    n._reactions = r;
  };
  n.clone = function () { const c = deepClone(n); if (n.parent) n.parent.appendChild(c); return c; };
  n.loadAsync = async function () { };
  n.screenshot = async function () { return { note: 'sim: no raster' }; };
  return n;
}

function* walk(n) {
  yield n;
  if (n._children) for (const c of n._children) yield* walk(c);
}
function deepClone(n) {
  const c = n._children ? makeContainer(n.type) : new Node(n.type);
  for (const k of Object.keys(n)) {
    if (k === '_children' || k === 'parent' || k === 'id' || typeof n[k] === 'function') continue;
    try { c[k] = n[k]; } catch (e) { /* fontName guard */ }
  }
  c._fontName = n._fontName;
  c._name = n._name; c._w = n._w; c._h = n._h;
  if (n._children) for (const ch of n._children) c.appendChild(deepClone(ch));
  return c;
}

function makeText() {
  const t = new Node('TEXT');
  t._fontName = { family: 'Inter', style: 'Regular' };
  t._w = 60; t._h = 16;
  t.characters = '';
  t.fontSize = 12;
  t.textAutoResize = 'NONE';
  t.resize = function (w, h) { if (!(w > 0) || !(h > 0)) throw new Error(`resize(${w},${h}) invalid on TEXT "${t.name}"`); t._w = w; t._h = h; };
  t.remove = function () { t.removed = true; if (t.parent && t.parent._children) { const i = t.parent._children.indexOf(t); if (i >= 0) t.parent._children.splice(i, 1); } };
  t.findOne = () => null; t.findAll = () => [];
  t.setReactionsAsync = async (r) => { t._reactions = r; };
  t.clone = function () { return deepClone(t); };
  t.getRangeFontName = () => t._fontName;
  return t;
}

/* ---- component / instance ---- */
function toComponent(frame) {
  if (!frame || (frame.type !== 'FRAME' && frame.type !== 'GROUP')) {
    throw new Error(`createComponentFromNode expects a FRAME, got ${frame && frame.type}`);
  }
  frame.type = 'COMPONENT';
  frame.createInstance = function () {
    const i = deepClone(frame);
    i.type = 'INSTANCE';
    i.mainComponent = frame;
    i._isInstance = true;
    stampInstance(i, frame);
    i.setProperties = function (props) {
      const set = frame.parent && frame.parent.type === 'COMPONENT_SET' ? frame.parent : null;
      if (!set) throw new Error(`setProperties on a non-variant instance ("${frame.name}")`);
      const target = findVariant(set, props, frame);
      if (!target) throw new Error(`setProperties: no variant matches ${JSON.stringify(props)} in set "${set.name}"`);
      return true;
    };
    i.swapComponent = function (c) { if (!c || c.type !== 'COMPONENT') throw new Error('swapComponent expects a COMPONENT'); return true; };
    i.detachInstance = function () { i.type = 'FRAME'; return i; };
    i.getMainComponentAsync = async () => frame;
    return i;
  };
  return frame;
}
function stampInstance(i, main) {
  for (const n of walk(i)) { if (n !== i && n.type === 'COMPONENT') n.type = 'INSTANCE'; }
}
function parseVariantName(nm) {
  const m = {};
  String(nm).split(',').forEach(p => { const s = p.trim().split('='); if (s.length === 2) m[s[0].trim()] = s[1].trim(); });
  return m;
}
function findVariant(set, props, fallback) {
  const keys = Object.keys(props || {});
  for (const ch of set._children) {
    const m = parseVariantName(ch.name);
    if (keys.every(k => m[k] === String(props[k]))) return ch;
  }
  return null;
}

/* ---- figma global ---- */
const paintStyles = [];
const textStyles = [];
const varCollections = [];

const rootNode = makeContainer('DOCUMENT');
rootNode._name = 'Document';

function makePage(name) {
  const p = makeContainer('PAGE');
  p._name = name;
  p.backgrounds = [];
  rootNode.appendChild(p);
  return p;
}

const PAGE_CAP = 3;
const page1 = makePage('01 Design System');
const page2 = makePage('02 Screens');
const page3 = makePage('03 Prototype');
page1.id = '0:1'; page2.id = '3:2'; page3.id = '3:3';

const figma = {
  root: rootNode,
  currentPage: page1,
  mixed: Symbol('mixed'),
  editorType: 'figma',
  createPage() {
    if (rootNode._children.length >= PAGE_CAP) {
      throw new Error(`Starter plan: cannot create more than ${PAGE_CAP} pages in a file (createPage #${rootNode._children.length + 1})`);
    }
    return makePage('Page ' + (rootNode._children.length + 1));
  },
  async setCurrentPageAsync(p) { if (!p || p.type !== 'PAGE') throw new Error('setCurrentPageAsync expects a PAGE'); figma.currentPage = p; },
  setCurrentPage(p) { figma.currentPage = p; },
  createFrame() { const f = makeContainer('FRAME'); f._name = 'Frame'; f._w = 100; f._h = 100; return f; },
  createSection() { const s = makeContainer('SECTION'); s._name = 'Section'; s._w = 400; s._h = 300; s.resizeWithoutConstraints = s.resize; return s; },
  createComponent() { const f = makeContainer('FRAME'); return toComponent(f); },
  createText() { return makeText(); },
  createRectangle() { const r = new Node('RECTANGLE'); r.fills = []; r.strokes = []; r.resize = (w, h) => { r._w = w; r._h = h; }; r.remove = () => { r.removed = true; }; r.findOne = () => null; r.findAll = () => []; return r; },
  createEllipse() { return figma.createRectangle(); },
  createVector() { const v = new Node('VECTOR'); v.resize = (w, h) => { v._w = w; v._h = h; }; v.findOne = () => null; v.findAll = () => []; return v; },
  createNodeFromSvg(svg) {
    if (typeof svg !== 'string' || svg.indexOf('<svg') !== 0) throw new Error('createNodeFromSvg needs an <svg ...> string');
    const g = makeContainer('FRAME');
    g.type = 'FRAME'; g._name = 'svg';
    const m = /width="(\d+(?:\.\d+)?)"/.exec(svg);
    const w = m ? parseFloat(m[1]) : 24;
    g._w = w; g._h = w;
    const v = figma.createVector(); v._w = w; v._h = w;
    g.appendChild(v);
    return g;
  },
  createComponentFromNode(n) { return toComponent(n); },
  combineAsVariants(comps, parent) {
    if (!Array.isArray(comps) || !comps.length) throw new Error('combineAsVariants needs a non-empty array');
    const names = new Set();
    let keysSig = null;
    for (const c of comps) {
      if (c.type !== 'COMPONENT') throw new Error(`combineAsVariants: node "${c.name}" is ${c.type}, not COMPONENT`);
      if (names.has(c.name)) throw new Error(`combineAsVariants: duplicate variant name "${c.name}"`);
      names.add(c.name);
      const sig = Object.keys(parseVariantName(c.name)).sort().join('|');
      if (!sig) throw new Error(`combineAsVariants: variant "${c.name}" has no "prop=value" name`);
      if (keysSig === null) keysSig = sig;
      else if (keysSig !== sig) throw new Error(`combineAsVariants: inconsistent variant props "${sig}" vs "${keysSig}"`);
    }
    const set = makeContainer('COMPONENT_SET');
    set._name = 'Component Set';
    if (parent) parent.appendChild(set);
    comps.forEach(c => set.appendChild(c));
    set.defaultVariant = comps[0];
    set.createInstance = () => comps[0].createInstance();
    return set;
  },
  createPaintStyle() { const s = { name: '', paints: [], id: nid('S'), type: 'PAINT', remove() { const i = paintStyles.indexOf(s); if (i >= 0) paintStyles.splice(i, 1); } }; paintStyles.push(s); return s; },
  createTextStyle() {
    const s = {
      _name: '', id: nid('S'), type: 'TEXT',
      set fontName(v) { if (!LOADED.has(fontKey(v))) throw new Error(`TextStyle fontName unloaded: ${v.family} ${v.style}`); s._fontName = v; },
      get fontName() { return s._fontName; },
      set name(v) { s._name = v; }, get name() { return s._name; },
      fontSize: 12, lineHeight: null, letterSpacing: null,
      remove() { const i = textStyles.indexOf(s); if (i >= 0) textStyles.splice(i, 1); },
    };
    textStyles.push(s); return s;
  },
  async getLocalPaintStylesAsync() { return paintStyles.slice(); },
  async getLocalTextStylesAsync() { return textStyles.slice(); },
  getLocalPaintStyles() { return paintStyles.slice(); },
  getLocalTextStyles() { return textStyles.slice(); },
  variables: {
    createVariableCollection(name) {
      const c = {
        name, id: nid('VC'), modes: [{ modeId: 'm1', name: 'Mode 1' }], variableIds: [],
        remove() { const i = varCollections.indexOf(c); if (i >= 0) varCollections.splice(i, 1); },
      };
      varCollections.push(c); return c;
    },
    createVariable(name, collection, type) {
      if (typeof collection === 'string') throw new Error('createVariable(name, collectionID:string, type) was removed — pass the collection object');
      if (!collection || !collection.modes) throw new Error('createVariable needs a VariableCollection');
      if (!['COLOR', 'FLOAT', 'STRING', 'BOOLEAN'].includes(type)) throw new Error('bad variable type ' + type);
      const v = { name, id: nid('VAR'), resolvedType: type, valuesByMode: {}, setValueForMode(m, val) { v.valuesByMode[m] = val; } };
      collection.variableIds.push(v.id);
      return v;
    },
    async getLocalVariableCollectionsAsync() { return varCollections.slice(); },
    getLocalVariableCollections() { return varCollections.slice(); },
    setBoundVariableForPaint(paint, field, variable) {
      if (!variable) throw new Error('setBoundVariableForPaint: null variable');
      return Object.assign({}, paint, { boundVariables: { [field]: { type: 'VARIABLE_ALIAS', id: variable.id } } });
    },
  },
  async loadFontAsync(f) {
    if (!f || !f.family || !f.style) throw new Error('loadFontAsync needs {family,style}');
    if (!AVAILABLE_FONTS.has(fontKey(f))) throw new Error(`Font "${f.family} ${f.style}" is not available`);
    LOADED.add(fontKey(f));
  },
  async listAvailableFontsAsync() { return [...AVAILABLE_FONTS].map(k => ({ fontName: { family: k.split('|')[0], style: k.split('|')[1] } })); },
  notify() { WARN.push('figma.notify() called — MUST be stripped for use_figma'); },
  closePlugin() { throw new Error('closePlugin() would abort the run'); },
  async getNodeByIdAsync(id) { for (const p of rootNode._children) for (const n of walk(p)) if (n.id === id) return n; return null; },
  getNodeById(id) { for (const p of rootNode._children) for (const n of walk(p)) if (n.id === id) return n; return null; },
  viewport: { scrollAndZoomIntoView() { } },
  ungroup(n) { return n._children.slice(); },
  group(nodes, parent) { const g = makeContainer('GROUP'); parent.appendChild(g); nodes.forEach(x => g.appendChild(x)); return g; },
};

module.exports = { figma, WARN, LOADED, walk, stats };

function stats() {
  const out = {};
  for (const p of rootNode._children) {
    const all = [...walk(p)];
    out[p.name] = {
      id: p.id,
      topLevel: p._children.length,
      sections: all.filter(n => n.type === 'SECTION').length,
      frames: all.filter(n => n.type === 'FRAME').length,
      components: all.filter(n => n.type === 'COMPONENT' && !(n.parent && n.parent.type === 'COMPONENT_SET')).length,
      componentSets: all.filter(n => n.type === 'COMPONENT_SET').length,
      variantsInSets: all.filter(n => n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET').length,
      instances: all.filter(n => n.type === 'INSTANCE').length,
      texts: all.filter(n => n.type === 'TEXT').length,
      reactions: all.filter(n => n._reactions && n._reactions.length).length,
      total: all.length - 1,
    };
  }
  out._styles = { paint: paintStyles.length, text: textStyles.length };
  out._variables = varCollections.map(c => c.name + ':' + c.variableIds.length);
  return out;
}
