//#region src/types.ts
var e = "_none", t = "未分组", n = "world", r = "legacy-percent";
function i(e) {
	return e === "world" || e === "legacy-percent";
}
//#endregion
//#region src/graph-node.ts
function a(e) {
	let t = e.source_path || e.path || e.source;
	if (t) return String(t);
	let n = e.id.endsWith(".md") ? e.id.slice(0, -3) : e.id;
	return `wiki/${o(e.type)}/${n}.md`;
}
function o(e) {
	let t = String(e || "");
	return t === "topic" ? "topics" : t === "source" ? "sources" : t === "comparison" ? "comparisons" : t === "synthesis" ? "synthesis" : t === "query" ? "queries" : "entities";
}
function s(e) {
	let t = String(e || "");
	return t === "topic" ? "主题" : t === "source" ? "来源" : t === "comparison" ? "对比" : t === "synthesis" ? "综合" : t === "query" ? "查询" : t === "entity" ? "实体" : t || "实体";
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/add.js
function c(e) {
	let t = +this._x.call(null, e), n = +this._y.call(null, e);
	return l(this.cover(t, n), t, n, e);
}
function l(e, t, n, r) {
	if (isNaN(t) || isNaN(n)) return e;
	var i, a = e._root, o = { data: r }, s = e._x0, c = e._y0, l = e._x1, u = e._y1, d, f, p, m, h, g, _, v;
	if (!a) return e._root = o, e;
	for (; a.length;) if ((h = t >= (d = (s + l) / 2)) ? s = d : l = d, (g = n >= (f = (c + u) / 2)) ? c = f : u = f, i = a, !(a = a[_ = g << 1 | h])) return i[_] = o, e;
	if (p = +e._x.call(null, a.data), m = +e._y.call(null, a.data), t === p && n === m) return o.next = a, i ? i[_] = o : e._root = o, e;
	do
		i = i ? i[_] = [
			,
			,
			,
			,
		] : e._root = [
			,
			,
			,
			,
		], (h = t >= (d = (s + l) / 2)) ? s = d : l = d, (g = n >= (f = (c + u) / 2)) ? c = f : u = f;
	while ((_ = g << 1 | h) == (v = (m >= f) << 1 | p >= d));
	return i[v] = a, i[_] = o, e;
}
function u(e) {
	var t, n, r = e.length, i, a, o = Array(r), s = Array(r), c = Infinity, u = Infinity, d = -Infinity, f = -Infinity;
	for (n = 0; n < r; ++n) isNaN(i = +this._x.call(null, t = e[n])) || isNaN(a = +this._y.call(null, t)) || (o[n] = i, s[n] = a, i < c && (c = i), i > d && (d = i), a < u && (u = a), a > f && (f = a));
	if (c > d || u > f) return this;
	for (this.cover(c, u).cover(d, f), n = 0; n < r; ++n) l(this, o[n], s[n], e[n]);
	return this;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/cover.js
function d(e, t) {
	if (isNaN(e = +e) || isNaN(t = +t)) return this;
	var n = this._x0, r = this._y0, i = this._x1, a = this._y1;
	if (isNaN(n)) i = (n = Math.floor(e)) + 1, a = (r = Math.floor(t)) + 1;
	else {
		for (var o = i - n || 1, s = this._root, c, l; n > e || e >= i || r > t || t >= a;) switch (l = (t < r) << 1 | e < n, c = [
			,
			,
			,
			,
		], c[l] = s, s = c, o *= 2, l) {
			case 0:
				i = n + o, a = r + o;
				break;
			case 1:
				n = i - o, a = r + o;
				break;
			case 2:
				i = n + o, r = a - o;
				break;
			case 3:
				n = i - o, r = a - o;
				break;
		}
		this._root && this._root.length && (this._root = s);
	}
	return this._x0 = n, this._y0 = r, this._x1 = i, this._y1 = a, this;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/data.js
function f() {
	var e = [];
	return this.visit(function(t) {
		if (!t.length) do
			e.push(t.data);
		while (t = t.next);
	}), e;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/extent.js
function p(e) {
	return arguments.length ? this.cover(+e[0][0], +e[0][1]).cover(+e[1][0], +e[1][1]) : isNaN(this._x0) ? void 0 : [[this._x0, this._y0], [this._x1, this._y1]];
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/quad.js
function m(e, t, n, r, i) {
	this.node = e, this.x0 = t, this.y0 = n, this.x1 = r, this.y1 = i;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/find.js
function h(e, t, n) {
	var r, i = this._x0, a = this._y0, o, s, c, l, u = this._x1, d = this._y1, f = [], p = this._root, h, g;
	for (p && f.push(new m(p, i, a, u, d)), n == null ? n = Infinity : (i = e - n, a = t - n, u = e + n, d = t + n, n *= n); h = f.pop();) if (!(!(p = h.node) || (o = h.x0) > u || (s = h.y0) > d || (c = h.x1) < i || (l = h.y1) < a)) if (p.length) {
		var _ = (o + c) / 2, v = (s + l) / 2;
		f.push(new m(p[3], _, v, c, l), new m(p[2], o, v, _, l), new m(p[1], _, s, c, v), new m(p[0], o, s, _, v)), (g = (t >= v) << 1 | e >= _) && (h = f[f.length - 1], f[f.length - 1] = f[f.length - 1 - g], f[f.length - 1 - g] = h);
	} else {
		var y = e - +this._x.call(null, p.data), b = t - +this._y.call(null, p.data), x = y * y + b * b;
		if (x < n) {
			var S = Math.sqrt(n = x);
			i = e - S, a = t - S, u = e + S, d = t + S, r = p.data;
		}
	}
	return r;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/remove.js
function g(e) {
	if (isNaN(u = +this._x.call(null, e)) || isNaN(d = +this._y.call(null, e))) return this;
	var t, n = this._root, r, i, a, o = this._x0, s = this._y0, c = this._x1, l = this._y1, u, d, f, p, m, h, g, _;
	if (!n) return this;
	if (n.length) for (;;) {
		if ((m = u >= (f = (o + c) / 2)) ? o = f : c = f, (h = d >= (p = (s + l) / 2)) ? s = p : l = p, t = n, !(n = n[g = h << 1 | m])) return this;
		if (!n.length) break;
		(t[g + 1 & 3] || t[g + 2 & 3] || t[g + 3 & 3]) && (r = t, _ = g);
	}
	for (; n.data !== e;) if (i = n, !(n = n.next)) return this;
	return (a = n.next) && delete n.next, i ? (a ? i.next = a : delete i.next, this) : t ? (a ? t[g] = a : delete t[g], (n = t[0] || t[1] || t[2] || t[3]) && n === (t[3] || t[2] || t[1] || t[0]) && !n.length && (r ? r[_] = n : this._root = n), this) : (this._root = a, this);
}
function _(e) {
	for (var t = 0, n = e.length; t < n; ++t) this.remove(e[t]);
	return this;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/root.js
function v() {
	return this._root;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/size.js
function y() {
	var e = 0;
	return this.visit(function(t) {
		if (!t.length) do
			++e;
		while (t = t.next);
	}), e;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/visit.js
function b(e) {
	var t = [], n, r = this._root, i, a, o, s, c;
	for (r && t.push(new m(r, this._x0, this._y0, this._x1, this._y1)); n = t.pop();) if (!e(r = n.node, a = n.x0, o = n.y0, s = n.x1, c = n.y1) && r.length) {
		var l = (a + s) / 2, u = (o + c) / 2;
		(i = r[3]) && t.push(new m(i, l, u, s, c)), (i = r[2]) && t.push(new m(i, a, u, l, c)), (i = r[1]) && t.push(new m(i, l, o, s, u)), (i = r[0]) && t.push(new m(i, a, o, l, u));
	}
	return this;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/visitAfter.js
function x(e) {
	var t = [], n = [], r;
	for (this._root && t.push(new m(this._root, this._x0, this._y0, this._x1, this._y1)); r = t.pop();) {
		var i = r.node;
		if (i.length) {
			var a, o = r.x0, s = r.y0, c = r.x1, l = r.y1, u = (o + c) / 2, d = (s + l) / 2;
			(a = i[0]) && t.push(new m(a, o, s, u, d)), (a = i[1]) && t.push(new m(a, u, s, c, d)), (a = i[2]) && t.push(new m(a, o, d, u, l)), (a = i[3]) && t.push(new m(a, u, d, c, l));
		}
		n.push(r);
	}
	for (; r = n.pop();) e(r.node, r.x0, r.y0, r.x1, r.y1);
	return this;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/x.js
function S(e) {
	return e[0];
}
function C(e) {
	return arguments.length ? (this._x = e, this) : this._x;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/y.js
function w(e) {
	return e[1];
}
function T(e) {
	return arguments.length ? (this._y = e, this) : this._y;
}
//#endregion
//#region ../../node_modules/d3-quadtree/src/quadtree.js
function E(e, t, n) {
	var r = new D(t ?? S, n ?? w, NaN, NaN, NaN, NaN);
	return e == null ? r : r.addAll(e);
}
function D(e, t, n, r, i, a) {
	this._x = e, this._y = t, this._x0 = n, this._y0 = r, this._x1 = i, this._y1 = a, this._root = void 0;
}
function O(e) {
	for (var t = { data: e.data }, n = t; e = e.next;) n = n.next = { data: e.data };
	return t;
}
var k = E.prototype = D.prototype;
k.copy = function() {
	var e = new D(this._x, this._y, this._x0, this._y0, this._x1, this._y1), t = this._root, n, r;
	if (!t) return e;
	if (!t.length) return e._root = O(t), e;
	for (n = [{
		source: t,
		target: e._root = [
			,
			,
			,
			,
		]
	}]; t = n.pop();) for (var i = 0; i < 4; ++i) (r = t.source[i]) && (r.length ? n.push({
		source: r,
		target: t.target[i] = [
			,
			,
			,
			,
		]
	}) : t.target[i] = O(r));
	return e;
}, k.add = c, k.addAll = u, k.cover = d, k.data = f, k.extent = p, k.find = h, k.remove = g, k.removeAll = _, k.root = v, k.size = y, k.visit = b, k.visitAfter = x, k.x = C, k.y = T;
//#endregion
//#region src/model/legacy-helpers.ts
var A = 15, j = 8.5, M = 22, N = 72, P = 180, F = "…", ee = 8, I = 1e3, L = 680, te = .62, R = 3.2, z = {
	x: 5,
	y: 3,
	width: 150,
	height: 48
}, ne = typeof Intl < "u" && Intl.Segmenter ? new Intl.Segmenter("zh", { granularity: "grapheme" }) : null;
function re(e) {
	var t = e.codePointAt(0);
	return t >= 65024 && t <= 65039;
}
function ie(e) {
	var t = e.codePointAt(0);
	return t >= 768 && t <= 879 || t >= 6832 && t <= 6911 || t >= 7616 && t <= 7679 || t >= 8400 && t <= 8447 || t >= 65056 && t <= 65071;
}
function ae(e) {
	var t = e.codePointAt(0);
	return t >= 127995 && t <= 127999;
}
function B(e) {
	if (ne) return Array.from(ne.segment(e), function(e) {
		return e.segment;
	});
	var t = Array.from(e);
	if (!t.length) return [];
	for (var n = [t[0]], r = 1; r < t.length; r++) {
		var i = t[r], a = t[r - 1];
		i === "‍" || a === "‍" || re(i) || ie(i) || ae(i) ? n[n.length - 1] += i : n.push(i);
	}
	return n;
}
function V(e) {
	return /[一-鿿]/.test(e) ? A : j;
}
function oe(e) {
	for (var t = 0, n = 0; n < e.length; n++) t += V(e[n]);
	return t;
}
function se(e, t) {
	if (!e || typeof e != "string") return {
		text: "",
		truncated: !1
	};
	var n = B(e);
	if (oe(n) + M <= t) return {
		text: e,
		truncated: !1
	};
	for (var r = "", i = 0, a = 0; a < n.length; a++) {
		var o = V(n[a]);
		if (i + o + ee + M > t) break;
		r += n[a], i += o;
	}
	return {
		text: r + F,
		truncated: !0
	};
}
function ce(e) {
	var t = oe(B(e.label || e.id)), n = Math.max(N, Math.min(P, t + M)), r = 36;
	return e.type === "topic" && (r = 40, n += 6), e.type === "source" && (r = 32), {
		w: n,
		h: r
	};
}
function le(e, t) {
	return {
		get: function(n) {
			try {
				return e.getItem(n);
			} catch (e) {
				return t && t("[wiki] storage.get failed:", n, e), null;
			}
		},
		set: function(n, r) {
			try {
				e.setItem(n, r);
			} catch (e) {
				t && t("[wiki] storage.set failed:", n, e);
			}
		}
	};
}
function ue(e) {
	return String(e ?? "").trim().toLowerCase().replace(/[^a-z0-9一-鿿]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48);
}
function de(e) {
	for (var t = String(e ?? ""), n = 0, r = 0; r < t.length; r++) n = (n << 5) - n + t.charCodeAt(r) >>> 0;
	return n.toString(36);
}
function fe(e, t) {
	var n = ue(e && e.wiki_title ? e.wiki_title : ""), r = typeof t == "string" && t ? t : e && e.wiki_title || n || "default";
	return "llm-wiki:" + (n || "default") + ":" + de(r);
}
function pe() {
	return {
		version: 1,
		favorites: [],
		notes: [],
		recentNoteIds: []
	};
}
function me(e) {
	if (!e || typeof e != "object") return pe();
	for (var t = pe(), n = Array.isArray(e.favorites) ? e.favorites : t.favorites, r = Array.isArray(e.notes) ? e.notes : t.notes, i = Array.isArray(e.recentNoteIds) ? e.recentNoteIds : t.recentNoteIds, a = {}, o = n.map(function(e) {
		return e == null ? null : String(e);
	}).filter(function(e) {
		return !e || a[e] ? !1 : (a[e] = !0, !0);
	}), s = r.map(function(e) {
		return !e || typeof e != "object" || e.id == null || e.node_id == null ? null : {
			id: String(e.id),
			node_id: String(e.node_id),
			label: e.label == null ? String(e.node_id) : String(e.label),
			text: e.text == null ? "" : String(e.text),
			created_at: e.created_at == null ? null : String(e.created_at)
		};
	}).filter(function(e) {
		return !!e;
	}), c = {}, l = 0; l < s.length; l++) c[s[l].id] = !0;
	var u = {}, d = i.map(function(e) {
		return e == null ? null : String(e);
	}).filter(function(e) {
		return !e || !c[e] || u[e] ? !1 : (u[e] = !0, !0);
	});
	return !d.length && s.length && (d = s.map(function(e) {
		return e.id;
	})), {
		version: t.version,
		favorites: o,
		notes: s,
		recentNoteIds: d
	};
}
function he(e, t) {
	var n = me(e), r = t == null ? "" : String(t);
	if (!r) return n;
	var i = n.favorites.slice(), a = i.indexOf(r);
	return a === -1 ? i.unshift(r) : i.splice(a, 1), {
		version: n.version,
		favorites: i,
		notes: n.notes.slice(),
		recentNoteIds: n.recentNoteIds.slice()
	};
}
function ge(e, t, n) {
	var r = me(e);
	if (!t || typeof t != "object" || t.id == null || t.node_id == null) return r;
	var i = Number.isFinite(Number(n)) ? Math.max(1, Math.round(Number(n))) : 50, a = {
		id: String(t.id),
		node_id: String(t.node_id),
		label: t.label == null ? String(t.node_id) : String(t.label),
		text: t.text == null ? "" : String(t.text),
		created_at: t.created_at == null ? null : String(t.created_at)
	}, o = [a].concat(r.notes.filter(function(e) {
		return e.id !== a.id;
	})).slice(0, i), s = [a.id].concat(r.recentNoteIds.filter(function(e) {
		return e !== a.id;
	})).slice(0, Math.min(i, 12));
	return {
		version: r.version,
		favorites: r.favorites.slice(),
		notes: o,
		recentNoteIds: s
	};
}
function _e(e, t, n) {
	var r = me(e), i = Number.isFinite(Number(n)) ? Math.max(1, Math.round(Number(n))) : 4, a = t && typeof t == "object" ? t : {}, o = {}, s = [], c;
	for (c = 0; c < r.notes.length; c++) o[r.notes[c].id] = r.notes[c];
	for (c = 0; c < r.recentNoteIds.length && s.length < i; c++) {
		var l = o[r.recentNoteIds[c]];
		if (l) {
			var u = a[l.node_id];
			s.push({
				kind: "note",
				node_id: l.node_id,
				label: l.label || u && (u.label || u.id) || l.node_id,
				text: l.text || ""
			});
		}
	}
	for (c = 0; c < r.favorites.length && s.length < i; c++) {
		var d = r.favorites[c], f = a[d];
		s.push({
			kind: "favorite",
			node_id: d,
			label: f && (f.label || f.id) ? f.label || f.id : d,
			text: ""
		});
	}
	return {
		favorite_count: r.favorites.length,
		note_count: r.notes.length,
		recent_items: s
	};
}
function ve() {
	return {
		version: 1,
		entry: {
			recommended_start_node_id: null,
			recommended_start_reason: null,
			default_mode: "global"
		},
		views: {
			path: {
				enabled: !1,
				start_node_id: null,
				node_ids: [],
				degraded: !0
			},
			community: {
				enabled: !1,
				community_id: null,
				label: null,
				node_ids: [],
				is_weak: !1,
				degraded: !0
			},
			global: {
				enabled: !0,
				node_ids: [],
				degraded: !1
			}
		},
		communities: [],
		degraded: {
			path_to_community: !0,
			community_to_global: !0
		}
	};
}
function ye(e) {
	if (!e || typeof e != "object") return ve();
	var t = ve();
	function n(e, t, n) {
		return e && e[t] != null ? e[t] : n;
	}
	return {
		version: n(e, "version", t.version),
		entry: {
			recommended_start_node_id: n(e.entry, "recommended_start_node_id", t.entry.recommended_start_node_id),
			recommended_start_reason: n(e.entry, "recommended_start_reason", t.entry.recommended_start_reason),
			default_mode: n(e.entry, "default_mode", t.entry.default_mode)
		},
		views: {
			path: {
				enabled: n(e.views && e.views.path, "enabled", t.views.path.enabled),
				start_node_id: n(e.views && e.views.path, "start_node_id", t.views.path.start_node_id),
				node_ids: Array.isArray(e.views && e.views.path && e.views.path.node_ids) ? e.views.path.node_ids : t.views.path.node_ids,
				degraded: n(e.views && e.views.path, "degraded", t.views.path.degraded)
			},
			community: {
				enabled: n(e.views && e.views.community, "enabled", t.views.community.enabled),
				community_id: n(e.views && e.views.community, "community_id", t.views.community.community_id),
				label: n(e.views && e.views.community, "label", t.views.community.label),
				node_ids: Array.isArray(e.views && e.views.community && e.views.community.node_ids) ? e.views.community.node_ids : t.views.community.node_ids,
				is_weak: n(e.views && e.views.community, "is_weak", t.views.community.is_weak),
				degraded: n(e.views && e.views.community, "degraded", t.views.community.degraded)
			},
			global: {
				enabled: n(e.views && e.views.global, "enabled", t.views.global.enabled),
				node_ids: Array.isArray(e.views && e.views.global && e.views.global.node_ids) ? e.views.global.node_ids : t.views.global.node_ids,
				degraded: n(e.views && e.views.global, "degraded", t.views.global.degraded)
			}
		},
		communities: Array.isArray(e.communities) ? e.communities : t.communities,
		degraded: {
			path_to_community: n(e.degraded, "path_to_community", t.degraded.path_to_community),
			community_to_global: n(e.degraded, "community_to_global", t.degraded.community_to_global)
		}
	};
}
function be(e) {
	return "global";
}
function xe(e, t) {
	return !Array.isArray(e) || !t ? [] : e.filter(function(e) {
		return e && e.community != null && String(e.community) === String(t);
	}).map(function(e) {
		return e.id;
	}).sort();
}
function Se(e, t) {
	if (!e || !e.views) return [];
	var n = e.views[t];
	return !n || !n.enabled ? [] : Array.isArray(n.node_ids) ? n.node_ids : [];
}
function Ce(e, t) {
	if (!t || !t.length) return e;
	for (var n = {}, r = 0; r < t.length; r++) n[t[r]] = !0;
	return e.filter(function(e) {
		var t = e.source.id || e.source, r = e.target.id || e.target;
		return n[t] && n[r];
	});
}
function we(e) {
	return ((e && (e.label || e.id || "")) + "\n" + (e && e.content || "").slice(0, 500)).toLowerCase();
}
function Te(e) {
	return Array.isArray(e) ? e.map(function(e) {
		return {
			node: e,
			haystack: we(e)
		};
	}) : [];
}
function Ee(e, t) {
	return Array.isArray(e) ? !t || typeof t != "object" ? e.slice() : e.filter(function(e) {
		return t[e && e.type ? e.type : "EXTRACTED"] !== !1;
	}) : [];
}
function De(e, t) {
	if (!Array.isArray(e)) return [];
	var n = typeof t == "string" ? t.trim().toLowerCase() : "";
	return (n ? e.filter(function(e) {
		return e && typeof e.haystack == "string" && e.haystack.indexOf(n) !== -1;
	}) : e).map(function(e) {
		return e && e.node ? e.node.id : null;
	}).filter(function(e) {
		return e != null;
	});
}
function Oe(e) {
	return {
		sourceId: e && e.source && e.source.id ? e.source.id : e && e.source,
		targetId: e && e.target && e.target.id ? e.target.id : e && e.target
	};
}
function ke(e, t, n) {
	return e.slice().sort(function(e, r) {
		var i = (t[r] || 0) - (t[e] || 0);
		if (i) return i;
		var a = n[e] && Number.isFinite(Number(n[e].degree)) ? Number(n[e].degree) : 0, o = n[r] && Number.isFinite(Number(n[r].degree)) ? Number(n[r].degree) : 0;
		return o === a ? String(e).localeCompare(String(r)) : o - a;
	});
}
function Ae(e) {
	var t = e && typeof e == "object" ? e : {}, n = Array.isArray(t.nodes) ? t.nodes : [], r = Array.isArray(t.links) ? t.links : [], i = Array.isArray(t.nodeIds) ? t.nodeIds.slice() : [], a = t.mode || "all", o = t.anchorNodeId == null ? null : String(t.anchorNodeId), s = Number.isFinite(Number(t.highConfidenceThreshold)) ? Number(t.highConfidenceThreshold) : .75, c = {}, l = {}, u;
	for (u = 0; u < n.length; u++) n[u] && n[u].id != null && (c[n[u].id] = n[u]);
	for (u = 0; u < i.length; u++) l[i[u]] = !0;
	if (!i.length) return {
		node_ids: [],
		links: []
	};
	var d = Ce(r, i);
	if (a === "all") return {
		node_ids: i.slice(),
		links: d
	};
	if (a === "high_confidence") {
		var f = d.filter(function(e) {
			var t = Number(e && e.weight);
			return Number.isFinite(t) && t >= s;
		}), p = {};
		for (u = 0; u < f.length; u++) {
			var m = Oe(f[u]);
			l[m.sourceId] && (p[m.sourceId] = !0), l[m.targetId] && (p[m.targetId] = !0);
		}
		o && l[o] && (p[o] = !0);
		var h = i.filter(function(e) {
			return !!p[e];
		});
		return {
			node_ids: h,
			links: Ce(f, h)
		};
	}
	if (a === "one_hop") {
		var g = o && l[o] ? o : i[0] || null;
		if (!g) return {
			node_ids: [],
			links: []
		};
		var _ = {};
		for (_[g] = !0, u = 0; u < d.length; u++) {
			var v = Oe(d[u]);
			v.sourceId === g && l[v.targetId] && (_[v.targetId] = !0), v.targetId === g && l[v.sourceId] && (_[v.sourceId] = !0);
		}
		var y = i.filter(function(e) {
			return !!_[e];
		});
		return {
			node_ids: y,
			links: Ce(d, y)
		};
	}
	if (a === "core") {
		if (i.length <= 3) return {
			node_ids: i.slice(),
			links: d
		};
		var b = {};
		for (u = 0; u < i.length; u++) b[i[u]] = 0;
		for (u = 0; u < d.length; u++) {
			var x = Oe(d[u]), S = Number(d[u] && d[u].weight), C = Number.isFinite(S) ? 1 + S : 1.5;
			b[x.sourceId] != null && (b[x.sourceId] += C), b[x.targetId] != null && (b[x.targetId] += C);
		}
		var w = Number.isFinite(Number(t.coreLimit)) ? Number(t.coreLimit) : Math.max(3, Math.min(8, Math.round(i.length * .5)));
		w = Math.max(1, Math.min(i.length, Math.round(w)));
		var T = ke(i, b, c).slice(0, w);
		return {
			node_ids: T,
			links: Ce(d, T)
		};
	}
	return {
		node_ids: i.slice(),
		links: d
	};
}
function je(e) {
	var t = e && typeof e == "object" ? e : {}, n = Array.isArray(t.nodes) ? t.nodes : [], r = Array.isArray(t.links) ? t.links : [], i = Array.isArray(t.baseNodeIds) ? t.baseNodeIds.slice() : n.map(function(e) {
		return e.id;
	}), a = Ce(Ee(r, t.filters), i), o = Ae({
		mode: t.focusMode,
		nodes: n,
		links: a,
		nodeIds: i,
		anchorNodeId: t.anchorNodeId,
		highConfidenceThreshold: t.highConfidenceThreshold,
		coreLimit: t.coreLimit
	}), s = o.node_ids || [];
	if (!s.length && t.focusMode && t.focusMode !== "all") return {
		node_ids: [],
		nodes: [],
		links: [],
		searchIndex: []
	};
	s.length || (s = i);
	for (var c = Te(n.filter(function(e) {
		return s.indexOf(e.id) !== -1;
	})), l = typeof t.searchQuery == "string" ? t.searchQuery.trim() : "", u = l ? De(c, l) : s, d = {}, f = 0; f < u.length; f++) d[u[f]] = !0;
	return {
		node_ids: u,
		nodes: n.filter(function(e) {
			return !!d[e.id];
		}),
		links: u.length ? Ce(o.links && o.links.length ? o.links : a, u) : [],
		searchIndex: c
	};
}
function Me(e) {
	return e === "path";
}
var Ne = {
	EXTRACTED: "直接提取",
	INFERRED: "推断关联",
	AMBIGUOUS: "存在歧义",
	UNVERIFIED: "未核实"
}, Pe = {
	topic: "主题",
	entity: "实体",
	source: "来源",
	comparison: "对比",
	synthesis: "综合",
	query: "查询"
}, Fe = {
	topic: "TOPIC",
	entity: "ENTITY",
	source: "SOURCE",
	comparison: "COMPARISON",
	synthesis: "SYNTHESIS",
	query: "QUERY"
};
function Ie(e) {
	var t = String(e || "entity").toLowerCase();
	return Pe[t] ? t : "entity";
}
function Le(e) {
	var t = String(e || "EXTRACTED").toUpperCase();
	return Ne[t] ? t : "EXTRACTED";
}
function Re(e) {
	return Ne[Le(e)];
}
function ze(e) {
	return String(e || "依赖").trim() || "依赖";
}
function Be(e) {
	return Pe[Ie(e)];
}
function Ve(e) {
	return Fe[Ie(e)];
}
function H(e, t, n, r) {
	var i = Number(e);
	return Number.isFinite(i) || (i = t), Number.isFinite(Number(n)) && (i = Math.max(Number(n), i)), Number.isFinite(Number(r)) && (i = Math.min(Number(r), i)), i;
}
function He(e) {
	var t = e && typeof e == "object" ? e : {};
	return {
		width: H(t.width, I, 1, 1e5),
		height: H(t.height, L, 1, 1e5)
	};
}
function Ue(e) {
	var t = e && typeof e == "object" ? e : {};
	return {
		x: H(t.x, 0, -1e6, 1e6),
		y: H(t.y, 0, -1e6, 1e6),
		scale: H(t.scale, 1, te, R)
	};
}
function We(e) {
	var t = e && typeof e == "object" ? e : {};
	return {
		x: H(t.x, 50, 0, 100) / 100 * I,
		y: H(t.y, 50, 0, 100) / 100 * L
	};
}
function Ge(e, t) {
	var n = Array.isArray(e) ? e : [], r = Number.isFinite(Number(t)) ? Math.max(0, Number(t)) : 48;
	if (!n.length) return {
		x: 0,
		y: 0,
		width: I,
		height: L,
		minX: 0,
		minY: 0,
		maxX: I,
		maxY: L
	};
	var i = I, a = L, o = 0, s = 0;
	return n.forEach(function(e) {
		var t = We(e);
		i = Math.min(i, t.x), a = Math.min(a, t.y), o = Math.max(o, t.x), s = Math.max(s, t.y);
	}), i = H(i - r, 0, 0, I), a = H(a - r, 0, 0, L), o = H(o + r, I, 0, I), s = H(s + r, L, 0, L), {
		x: i,
		y: a,
		width: Math.max(1, o - i),
		height: Math.max(1, s - a),
		minX: i,
		minY: a,
		maxX: o,
		maxY: s
	};
}
function Ke(e, t, n) {
	var r = He(t), i = Ue(e), a = n && typeof n == "object" ? n : {}, o = H(a.minScale, te, .1, R), s = H(a.maxScale, R, o, 10), c = H(a.marginX, r.width * .38, 0, r.width), l = H(a.marginY, r.height * .38, 0, r.height), u = H(i.scale, 1, o, s), d = r.width * u, f = r.height * u, p = r.width - d - c, m = c, h = r.height - f - l, g = l;
	if (d <= r.width) {
		var _ = (r.width - d) / 2;
		p = _ - c, m = _ + c;
	}
	if (f <= r.height) {
		var v = (r.height - f) / 2;
		h = v - l, g = v + l;
	}
	return {
		x: H(i.x, 0, p, m),
		y: H(i.y, 0, h, g),
		scale: u
	};
}
function qe(e, t, n) {
	var r = e && typeof e == "object" ? e : Ge([]), i = He(t), a = n && typeof n == "object" ? n : {}, o = H(a.padding, .84, .2, 1), s = H(a.minScale, te, .1, R), c = H(a.maxScale, 2.15, s, R), l = I * o / Math.max(1, r.width || 1), u = L * o / Math.max(1, r.height || 1), d = H(Math.min(l, u), 1, s, c), f = r.minX != null && r.maxX != null ? (r.minX + r.maxX) / 2 : (r.x || 0) + (r.width || I) / 2, p = r.minY != null && r.maxY != null ? (r.minY + r.maxY) / 2 : (r.y || 0) + (r.height || L) / 2;
	return Ke({
		x: i.width / 2 - d * (f / I * i.width),
		y: i.height / 2 - d * (p / L * i.height),
		scale: d
	}, i, a);
}
function Je(e, t, n, r) {
	var i = e && typeof e == "object" ? e : {
		x: I / 2,
		y: L / 2
	}, a = He(t), o = H(n, 1, te, R);
	return Ke({
		x: a.width / 2 - o * (i.x / I * a.width),
		y: a.height / 2 - o * (i.y / L * a.height),
		scale: o
	}, a, r);
}
function Ye(e, t, n, r, i) {
	var a = He(r), o = Ue(e), s = n && typeof n == "object" ? {
		x: H(n.x, a.width / 2, 0, a.width),
		y: H(n.y, a.height / 2, 0, a.height)
	} : {
		x: a.width / 2,
		y: a.height / 2
	}, c = H(t, 1, .2, 5), l = i && typeof i == "object" ? i : {}, u = H(l.minScale, te, .1, R), d = H(l.maxScale, R, u, 10), f = H(o.scale * c, o.scale, u, d), p = f / o.scale;
	return Ke({
		x: s.x - (s.x - o.x) * p,
		y: s.y - (s.y - o.y) * p,
		scale: f
	}, a, l);
}
function Xe(e, t) {
	var n = He(t), r = Ue(e), i = (0 - r.x) / r.scale / n.width * I, a = (0 - r.y) / r.scale / n.height * L, o = n.width / r.scale / n.width * I, s = n.height / r.scale / n.height * L, c = H(i, 0, 0, I), l = H(a, 0, 0, L), u = H(i + o, I, 0, I), d = H(a + s, L, 0, L);
	return {
		x: c,
		y: l,
		width: Math.max(1, u - c),
		height: Math.max(1, d - l),
		minX: c,
		minY: l,
		maxX: u,
		maxY: d
	};
}
function Ze(e) {
	var t = e && typeof e == "object" ? e : {
		x: 0,
		y: 0
	};
	return {
		x: z.x + H(t.x, 0, 0, I) / I * z.width,
		y: z.y + H(t.y, 0, 0, L) / L * z.height
	};
}
function Qe(e) {
	var t = e && typeof e == "object" ? e : {
		x: z.x,
		y: z.y
	};
	return {
		x: H((t.x - z.x) / z.width * I, 0, 0, I),
		y: H((t.y - z.y) / z.height * L, 0, 0, L)
	};
}
function $e(e, t) {
	var n = Xe(e, t), r = Ze({
		x: n.x,
		y: n.y
	}), i = Ze({
		x: n.x + n.width,
		y: n.y + n.height
	});
	return {
		x: r.x,
		y: r.y,
		width: Math.max(2, i.x - r.x),
		height: Math.max(2, i.y - r.y)
	};
}
function et(e) {
	return e && typeof e == "object" && e.id != null ? String(e.id) : e == null ? "" : String(e);
}
function tt(e) {
	return String(e || "").replace(/^---[\s\S]*?---\s*/m, "").replace(/```[\s\S]*?```/g, " ").replace(/!\[[^\]]*\]\([^)]+\)/g, " ").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\[\[([^\]|]+)\|?([^\]]*)\]\]/g, function(e, t, n) {
		return n || t;
	}).replace(/^#{1,6}\s+/gm, "").replace(/^[-*+]\s+/gm, "").replace(/^\d+\.\s+/gm, "").replace(/[*_`>#]/g, "").replace(/\s+/g, " ").trim();
}
function nt(e, t) {
	var n = e && e.summary != null ? String(e.summary).trim() : "";
	if (n) return n.length > 170 ? n.slice(0, 170).trim() + "…" : n;
	var r = tt(String(t || e && e.content || "").replace(/^#\s+.*(?:\r?\n)+/, ""));
	return r ? r.length > 170 ? r.slice(0, 170).trim() + "…" : r : "";
}
function rt(e, t) {
	var n = e && typeof e == "object" ? e : {}, r = n.id == null ? "node-" + t : String(n.id), i = n.label == null || String(n.label).trim() === "" ? r : String(n.label).trim(), a = n.content == null ? "" : String(n.content), o = Ie(n.type), s = n.community == null || n.community === "" ? "_none" : String(n.community), c = Number(n.x), l = Number(n.y), u = (typeof n.x == "number" || typeof n.x == "string" && n.x.trim() !== "") && Number.isFinite(c), d = (typeof n.y == "number" || typeof n.y == "string" && n.y.trim() !== "") && Number.isFinite(l);
	return {
		id: r,
		label: i,
		type: o,
		type_label: Be(o),
		kind: Ve(o),
		community: s,
		source_path: n.source_path || n.source || n.path || "",
		confidence: Le(n.confidence || n.type_confidence),
		confidence_label: Re(n.confidence || n.type_confidence),
		content: a,
		summary: nt(n, a),
		unavailable: n.unavailable === !0 || n.available === !1,
		degree: 0,
		weight: H(n.weight == null ? n.score : n.weight, 50, 0, 100),
		priority: 0,
		idx: t,
		x: u ? c : null,
		y: d ? l : null
	};
}
function it(e, t) {
	var n = e && typeof e == "object" ? e : {}, r = et(n.from == null ? n.source : n.from), i = et(n.to == null ? n.target : n.to), a = Le(n.confidence || n.type || n.type_confidence);
	return {
		id: n.id == null ? "edge-" + t : String(n.id),
		source: r,
		target: i,
		from: r,
		to: i,
		type: a,
		confidence: a,
		confidence_label: Re(a),
		relation_type: ze(n.relation_type || n.relationship_type || n.relation),
		weight: H(n.weight, .6, 0, 1),
		signals: n.signals && typeof n.signals == "object" ? n.signals : {},
		source_signal_available: n.source_signal_available === !0
	};
}
function at(e) {
	return [
		e && e.label,
		e && e.id,
		e && e.type_label,
		e && e.source_path,
		e && e.summary,
		e && tt(e.content)
	].join("\n").toLowerCase();
}
function ot(e) {
	return Array.isArray(e) ? e.map(function(e) {
		return {
			node: e,
			haystack: at(e)
		};
	}) : [];
}
function st(e, t, n) {
	var r = ye(e && e.learning), i = Array.isArray(r.communities) ? r.communities : [], a = [], o = {};
	return i.forEach(function(e) {
		if (!(!e || e.id == null)) {
			var t = String(e.id), r = n[t] || { nodes: [] };
			o[t] = !0, a.push({
				id: t,
				label: e.label || t,
				node_count: Number.isFinite(Number(e.node_count)) ? Number(e.node_count) : r.nodes.length,
				source_count: Number.isFinite(Number(e.source_count)) ? Number(e.source_count) : 0,
				is_primary: e.is_primary === !0,
				recommended_start_node_id: e.recommended_start_node_id || null,
				color_index: a.length
			});
		}
	}), Object.keys(n).sort().forEach(function(e) {
		if (!o[e]) {
			var t = n[e], r = t.nodes.find(function(e) {
				return e.type === "topic";
			});
			a.push({
				id: e,
				label: e === "_none" ? "未分组" : r && r.label || e,
				node_count: t.nodes.length,
				source_count: t.nodes.filter(function(e) {
					return e.type === "source";
				}).length,
				is_primary: a.length === 0,
				recommended_start_node_id: null,
				color_index: a.length
			});
		}
	}), a.sort(function(e, t) {
		return !!t.is_primary == !!e.is_primary ? (t.node_count || 0) === (e.node_count || 0) ? String(e.label || e.id).localeCompare(String(t.label || t.id)) : (t.node_count || 0) - (e.node_count || 0) : t.is_primary ? 1 : -1;
	}), a.forEach(function(e, t) {
		e.color_index = t;
	}), a;
}
function ct(e, t, n, r) {
	var i = [], a = {};
	function o(e, t) {
		if (e != null) {
			var r = String(e);
			!n[r] || a[r] || (a[r] = !0, i.push({
				node: n[r],
				reason: t || ""
			}));
		}
	}
	var s = ye(e && e.learning);
	return o(s.entry && s.entry.recommended_start_node_id, "全局推荐起点"), r.forEach(function(e) {
		o(e.recommended_start_node_id, e.label + " · 推荐起点");
	}), t.slice().sort(function(e, t) {
		return (t.priority || 0) - (e.priority || 0);
	}).forEach(function(e) {
		i.length < 6 && o(e.id, Be(e.type) + " · " + Re(e.confidence));
	}), i.slice(0, 6);
}
function lt(e) {
	var t = e && typeof e == "object" ? e : {};
	return {
		surprising_connections: Array.isArray(t.surprising_connections) ? t.surprising_connections : [],
		isolated_nodes: Array.isArray(t.isolated_nodes) ? t.isolated_nodes : [],
		bridge_nodes: Array.isArray(t.bridge_nodes) ? t.bridge_nodes : [],
		sparse_communities: Array.isArray(t.sparse_communities) ? t.sparse_communities : [],
		meta: t.meta && typeof t.meta == "object" ? t.meta : { degraded: !1 }
	};
}
function ut(e) {
	var t = e && typeof e == "object" ? e : {}, n = Array.isArray(t.nodes) ? t.nodes.map(rt) : [], r = {}, i = {};
	n.forEach(function(e) {
		r[e.id] = e, i[e.community] || (i[e.community] = {
			id: e.community,
			nodes: []
		}), i[e.community].nodes.push(e);
	});
	var a = (Array.isArray(t.edges) ? t.edges : []).map(it).filter(function(e) {
		return !!(r[e.source] && r[e.target]);
	});
	a.forEach(function(e) {
		r[e.source].degree += 1, r[e.target].degree += 1;
	}), n.forEach(function(e) {
		e.priority = e.degree * 12 + e.weight + (e.type === "topic" ? 12 : e.type === "source" ? 6 : 0);
	});
	var o = st(t, n, i), s = {};
	return o.forEach(function(e) {
		s[e.id] = e;
	}), {
		meta: {
			wiki_title: t.meta && t.meta.wiki_title ? String(t.meta.wiki_title) : "知识库",
			total_nodes: n.length,
			total_edges: a.length,
			build_date: t.meta && t.meta.build_date ? String(t.meta.build_date) : ""
		},
		nodes: n,
		edges: a,
		byId: r,
		communities: o,
		communityById: s,
		starts: ct(t, n, r, o),
		searchIndex: ot(n),
		insights: lt(t.insights)
	};
}
function dt(e) {
	var t = e && typeof e == "object" ? e : {
		nodes: [],
		communities: []
	}, n = [
		{
			x: 50,
			y: 48
		},
		{
			x: 30,
			y: 34
		},
		{
			x: 70,
			y: 36
		},
		{
			x: 30,
			y: 72
		},
		{
			x: 72,
			y: 70
		},
		{
			x: 18,
			y: 52
		},
		{
			x: 84,
			y: 52
		},
		{
			x: 50,
			y: 78
		}
	], r = {};
	(t.communities || []).forEach(function(e, t) {
		r[e.id] = t;
	});
	var i = {};
	return (t.nodes || []).forEach(function(e) {
		i[e.community] || (i[e.community] = []), i[e.community].push(e);
	}), Object.keys(i).forEach(function(e) {
		i[e].sort(function(e, t) {
			return (t.priority || 0) - (e.priority || 0);
		});
		var t = n[(r[e] || 0) % n.length], a = i[e].length;
		i[e].forEach(function(e, n) {
			if (e.x != null && e.y != null && Number.isFinite(Number(e.x)) && Number.isFinite(Number(e.y))) {
				e.x = H(e.x, t.x, 5, 95), e.y = H(e.y, t.y, 8, 92);
				return;
			}
			var r = Math.floor(n / 8), i = n % 8 / Math.min(8, Math.max(1, a)) * Math.PI * 2 + r * .42, o = 7 + r * 5 + Math.min(5, a * .16), s = 5 + r * 4 + Math.min(4, a * .12);
			e.x = H(t.x + Math.cos(i) * o, t.x, 5, 95), e.y = H(t.y + Math.sin(i) * s, t.y, 8, 92);
		});
	}), {
		nodes: (t.nodes || []).slice(),
		edges: (t.edges || []).slice(),
		nodePositions: (t.nodes || []).reduce(function(e, t) {
			return e[t.id] = {
				x: t.x,
				y: t.y
			}, e;
		}, {})
	};
}
function ft(e) {
	var t = Number.isFinite(Number(e)) ? Number(e) : 0;
	return t > 500 ? "overview" : t > 200 ? "point-plus-focus" : t > 80 ? "compact-card" : "card";
}
function pt(e, t) {
	return e === "overview" ? 40 : e === "point-plus-focus" ? 60 : e === "compact-card" ? Math.min(120, t) : t;
}
function mt(e, t) {
	return e === "overview" ? 1e3 : e === "point-plus-focus" ? 800 : t;
}
function ht(e, t, n) {
	var r = e && typeof e == "object" ? e : ut({}), i = n && typeof n == "object" ? n : {}, a = i.activeCommunityId == null ? "all" : String(i.activeCommunityId), o = typeof i.query == "string" ? i.query.trim().toLowerCase() : "", s = i.focusMode || "all", c = i.selectedNodeId == null ? null : String(i.selectedNodeId), l = i.filters && typeof i.filters == "object" ? i.filters : {}, u = r.nodes.filter(function(e) {
		return !(a !== "all" && e.community !== a || s === "source" && e.type !== "source");
	});
	if (s === "core" && u.length > 8) {
		var d = Math.max(8, Math.ceil(u.length * .45)), f = {};
		u.slice().sort(function(e, t) {
			return (t.priority || 0) - (e.priority || 0);
		}).slice(0, d).forEach(function(e) {
			f[e.id] = !0;
		}), c && r.byId[c] && (f[c] = !0), u = u.filter(function(e) {
			return !!f[e.id];
		});
	}
	var p = {};
	u.forEach(function(e) {
		p[e.id] = !0;
	});
	var m = ot(u), h = {}, g = o ? m.filter(function(e) {
		return e.haystack.indexOf(o) !== -1;
	}).map(function(e) {
		return h[e.node.id] = !0, e.node;
	}) : u, _ = {};
	g.forEach(function(e) {
		_[e.id] = !0;
	});
	var v = r.edges.filter(function(e) {
		return l[e.type || "EXTRACTED"] === !1 ? !1 : !!(_[e.source] && _[e.target]);
	}), y = ft(g.length), b = pt(y, g.length), x = {}, S = {}, C = {}, w = r.starts.filter(function(e) {
		return !!(e && e.node && _[e.node.id]) && (a === "all" || e.node.community === a);
	});
	w.forEach(function(e) {
		S[e.node.id] = !0, C[e.node.id] = !0;
	}), g.slice().sort(function(e, t) {
		return (t.priority || 0) - (e.priority || 0);
	}).slice(0, Math.max(0, Math.min(8, Math.ceil(g.length * .08)))).forEach(function(e) {
		C[e.id] = !0;
	}), g.slice().sort(function(e, t) {
		var n = c === e.id || h[e.id] || C[e.id] ? 1 : 0, r = c === t.id || h[t.id] || C[t.id] ? 1 : 0;
		return r === n ? (t.priority || 0) - (e.priority || 0) : r - n;
	}).slice(0, b).forEach(function(e) {
		x[e.id] = !0;
	}), c && _[c] && (x[c] = !0), Object.keys(h).forEach(function(e) {
		_[e] && (x[e] = !0, C[e] = !0);
	}), Object.keys(S).forEach(function(e) {
		_[e] && (x[e] = !0);
	}), c && _[c] && (C[c] = !0);
	var T = mt(y, v.length);
	return v = v.slice().sort(function(e, t) {
		var n = c && (e.source === c || e.target === c) ? 1 : 0, r = c && (t.source === c || t.target === c) ? 1 : 0;
		return r === n ? (t.weight || 0) - (e.weight || 0) : r - n;
	}).slice(0, T), {
		node_ids: g.map(function(e) {
			return e.id;
		}),
		nodes: g,
		edges: v,
		links: v,
		searchIndex: m,
		densityMode: y,
		labelNodeIds: x,
		matchedNodeIds: h,
		importantNodeIds: C,
		startNodeIds: S,
		starts: w,
		counts: {
			visible_nodes: g.length,
			visible_edges: v.length,
			total_nodes: r.nodes.length,
			total_edges: r.edges.length,
			total_communities: r.communities.length
		}
	};
}
function gt(e, t, n) {
	var r = e && typeof e == "object" ? e : ut({}), i = n == null ? null : String(n), a = t && typeof t == "object" ? t : null, o = {};
	return a && Array.isArray(a.node_ids) && a.node_ids.forEach(function(e) {
		o[String(e)] = !0;
	}), i && r.byId && r.byId[i] && (!a || o[i]) ? i : null;
}
//#endregion
//#region src/layout/edge-geometry.ts
var _t = 22;
function vt(e, t, n) {
	return {
		x: (e.x + t.x) / 2 + n,
		y: (e.y + t.y) / 2 - _t
	};
}
//#endregion
//#region src/layout/spatial-index.ts
var yt = 10, bt = 32, xt = class e {
	nodes;
	edges;
	communities;
	aggregationContainers;
	nodeTree;
	edgeGrid;
	maxNodeRadius;
	edgeHitTolerance;
	nodeFallbackRadius;
	constructor(e = {}) {
		this.edgeHitTolerance = Ht(e.edgeHitTolerance, 10), this.nodeFallbackRadius = Ht(e.nodeFallbackRadius, 32), this.nodes = Ct(e.nodes || [], this.nodeFallbackRadius), this.maxNodeRadius = this.nodes.reduce((e, t) => Math.max(e, t.radius), this.nodeFallbackRadius), this.nodeTree = E(this.nodes, (e) => e.point.x, (e) => e.point.y);
		let t = new Map(this.nodes.map((e) => [e.id, e]));
		this.edges = wt(e.edges || [], t, this.edgeHitTolerance), this.edgeGrid = new qt(this.edges, this.edgeHitTolerance), this.communities = Tt(e.communities || []), this.aggregationContainers = Et(e.aggregationContainers || []);
	}
	rebuild(t) {
		return new e(t);
	}
	hitTest(e) {
		let t = Vt(e), n = this.findNode(t);
		if (n) return {
			kind: "node",
			id: n.id
		};
		let r = this.findEdge(t);
		if (r) return {
			kind: "edge",
			id: r.id
		};
		let i = this.findAggregationContainer(t);
		if (i) return {
			kind: "aggregation-container",
			id: i.id,
			communityId: i.communityId
		};
		let a = this.findCommunity(t);
		return a ? {
			kind: "community-wash",
			id: a.id
		} : { kind: "graph-blank" };
	}
	findNode(e) {
		let t = Vt(e), n = this.collectNodeCandidates(t);
		return n.length && n.sort((e, n) => {
			let r = Mt(t, e.bounds) - Mt(t, n.bounds);
			return r === 0 ? e.order - n.order : r;
		})[0] || null;
	}
	findEdge(e) {
		let t = Vt(e), n = null, r = Infinity;
		return this.visitEdgeCandidates(t, (e) => {
			let i = Pt(t, e.source, e.target, e.curveOffset);
			i > this.edgeHitTolerance || (!n || i < r || i === r && e.order < n.order) && (n = e, r = i);
		}), n;
	}
	findCommunity(e) {
		let t = Vt(e);
		return this.communities.map((e) => ({
			community: e,
			score: Rt(t, e)
		})).filter((e) => e.score <= 1).sort((e, t) => e.score - t.score || e.community.order - t.community.order)[0]?.community || null;
	}
	findAggregationContainer(e) {
		let t = Vt(e);
		return this.aggregationContainers.filter((e) => Gt(t, e.point) <= e.radius).sort((e, n) => Gt(t, e.point) - Gt(t, n.point) || e.order - n.order)[0] || null;
	}
	nearestNode(e, t = this.maxNodeRadius) {
		return this.nodeTree.find(Ut(e.x, 0), Ut(e.y, 0), Ht(t, this.maxNodeRadius)) || null;
	}
	edgeCandidateCount(e) {
		let t = Vt(e), n = 0;
		return this.visitEdgeCandidates(t, () => {
			n += 1;
		}), n;
	}
	collectNodeCandidates(e) {
		let t = [], n = this.maxNodeRadius;
		return this.nodeTree.visit((r, i, a, o, s) => {
			if (i > e.x + n || o < e.x - n || a > e.y + n || s < e.y - n) return !0;
			let c = zt(r);
			if (!c) return !1;
			let l = c;
			for (; l;) jt(l.data.bounds, e) && t.push(l.data), l = l.next;
			return !1;
		}), t;
	}
	visitEdgeCandidates(e, t) {
		this.edgeGrid.visit(e, t);
	}
};
function St(e = {}) {
	return new xt(e);
}
function Ct(e, t) {
	return e.flatMap((e, n) => {
		let r = Dt(e);
		if (!r) return [];
		let i = e.hitBounds ? kt(e.hitBounds, r, t) : Ot(e, r, t);
		return [{
			id: String(e.id),
			point: r,
			bounds: i,
			radius: Nt(i, r),
			order: n
		}];
	});
}
function wt(e, t, n) {
	return e.flatMap((e, r) => {
		let i = t.get(String(e.source)), a = t.get(String(e.target));
		if (!i || !a) return [];
		let o = Bt(i.point), s = Bt(a.point), c = Ut(e.curveOffset, 0), l = Ft(o, s, c, n);
		return [{
			id: String(e.id),
			source: o,
			target: s,
			curveOffset: c,
			bounds: l,
			order: r
		}];
	});
}
function Tt(e) {
	return e.flatMap((e, t) => {
		let n = e.wash;
		if (!n) return [];
		let r = Ht(n.rx, 0), i = Ht(n.ry, 0);
		return r <= 0 || i <= 0 ? [] : [{
			id: String(e.id),
			cx: Ut(n.cx, 0),
			cy: Ut(n.cy, 0),
			rx: r,
			ry: i,
			order: t
		}];
	});
}
function Et(e) {
	return e.flatMap((e, t) => e.point ? [{
		id: String(e.id),
		communityId: e.communityId ? String(e.communityId) : null,
		point: Vt(e.point),
		radius: Ht(e.radius, 32),
		order: t
	}] : []);
}
function Dt(e) {
	return e.point ? Vt(e.point) : typeof e.x == "number" && typeof e.y == "number" ? Vt({
		x: e.x,
		y: e.y
	}) : null;
}
function Ot(e, t, n) {
	if (e.displayMode === "point" || e.displayMode === "overview" || e.visualRole === "map-pin") return At(t, 28, 28);
	if (e.displayMode === "compact-card" || e.visualRole === "landmark") return At(t, 130, 42);
	if (e.label || e.type || e.id) {
		let n = ce({
			id: e.id,
			label: e.label || e.id,
			type: e.type || "entity"
		});
		return At(t, Math.max(72, Math.min(182, n.w)), Math.max(46, n.h));
	}
	return At(t, n * 2, n * 2);
}
function kt(e, t, n) {
	let r = Ht(e.width, n * 2), i = Ht(e.height, n * 2);
	return {
		x: Ut(e.x, t.x - r / 2),
		y: Ut(e.y, t.y - i / 2),
		width: r,
		height: i
	};
}
function At(e, t, n) {
	return {
		x: e.x - t / 2,
		y: e.y - n / 2,
		width: t,
		height: n
	};
}
function jt(e, t) {
	return t.x >= e.x && t.x <= e.x + e.width && t.y >= e.y && t.y <= e.y + e.height;
}
function Mt(e, t) {
	let n = Math.max(t.x - e.x, 0, e.x - (t.x + t.width)), r = Math.max(t.y - e.y, 0, e.y - (t.y + t.height));
	return Math.hypot(n, r);
}
function Nt(e, t) {
	let n = [
		{
			x: e.x,
			y: e.y
		},
		{
			x: e.x + e.width,
			y: e.y
		},
		{
			x: e.x,
			y: e.y + e.height
		},
		{
			x: e.x + e.width,
			y: e.y + e.height
		}
	];
	return Math.max(...n.map((e) => Wt(t, e)));
}
function Pt(e, t, n, r) {
	let i = vt(t, n, r), a = t, o = Infinity;
	for (let r = 1; r <= 24; r += 1) {
		let s = It(t, i, n, r / 24);
		o = Math.min(o, Lt(e, a, s)), a = s;
	}
	return o;
}
function Ft(e, t, n, r) {
	let i = vt(e, t, n), a = r + Math.abs(n) + 24, o = Math.min(e.x, t.x, i.x) - a, s = Math.max(e.x, t.x, i.x) + a, c = Math.min(e.y, t.y, i.y) - a, l = Math.max(e.y, t.y, i.y) + a;
	return {
		x: o,
		y: c,
		width: s - o,
		height: l - c
	};
}
function It(e, t, n, r) {
	let i = 1 - r;
	return {
		x: i * i * e.x + 2 * i * r * t.x + r * r * n.x,
		y: i * i * e.y + 2 * i * r * t.y + r * r * n.y
	};
}
function Lt(e, t, n) {
	let r = n.x - t.x, i = n.y - t.y, a = r * r + i * i;
	if (a <= 0) return Wt(e, t);
	let o = Math.max(0, Math.min(1, ((e.x - t.x) * r + (e.y - t.y) * i) / a));
	return Wt(e, {
		x: t.x + o * r,
		y: t.y + o * i
	});
}
function Rt(e, t) {
	let n = (e.x - t.cx) / t.rx, r = (e.y - t.cy) / t.ry;
	return n * n + r * r;
}
function zt(e) {
	return Array.isArray(e) ? null : e;
}
function Bt(e) {
	return {
		x: e.x,
		y: e.y
	};
}
function Vt(e) {
	return {
		x: Ut(e.x, 0),
		y: Ut(e.y, 0)
	};
}
function Ht(e, t) {
	let n = Ut(e, t);
	return n > 0 ? n : t;
}
function Ut(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function Wt(e, t) {
	return Math.hypot(t.x - e.x, t.y - e.y);
}
function Gt(e, t) {
	return Wt(e, t);
}
var Kt = 96, qt = class {
	cellSize;
	buckets = /* @__PURE__ */ new Map();
	constructor(e, t) {
		this.cellSize = Math.max(Kt, Ht(t, 10) * 8);
		for (let t of e) this.add(t);
	}
	visit(e, t) {
		let n = this.buckets.get(this.key(this.cellCoord(e.x), this.cellCoord(e.y)));
		if (!n?.length) return;
		let r = /* @__PURE__ */ new Set();
		for (let i of n) r.has(i.id) || (r.add(i.id), jt(i.bounds, e) && t(i));
	}
	add(e) {
		let t = this.cellCoord(e.bounds.x), n = this.cellCoord(e.bounds.x + e.bounds.width), r = this.cellCoord(e.bounds.y), i = this.cellCoord(e.bounds.y + e.bounds.height);
		for (let a = t; a <= n; a += 1) for (let t = r; t <= i; t += 1) {
			let n = this.key(a, t), r = this.buckets.get(n);
			r ? r.push(e) : this.buckets.set(n, [e]);
		}
	}
	cellCoord(e) {
		return Math.floor(Ut(e, 0) / this.cellSize);
	}
	key(e, t) {
		return `${e}:${t}`;
	}
}, Jt = 1e6, Yt = 1e3;
function Xt(e) {
	let t = e && typeof e == "object" ? e : {}, i = t.version === 1 ? r : n;
	return {
		version: 2,
		pins: Qt(t.pins, {
			defaultCoordinateSpace: i,
			acceptKey: $t
		}),
		updatedAt: typeof t.updatedAt == "string" ? t.updatedAt : ""
	};
}
function Zt(e) {
	return Qt(e);
}
function Qt(e, t = {}) {
	let n = {};
	if (!e || typeof e != "object") return n;
	let r = t.defaultCoordinateSpace || "world";
	for (let [i, a] of Object.entries(e)) {
		if (t.acceptKey && !t.acceptKey(i)) continue;
		let e = en(a, r);
		e && (n[i] = e);
	}
	return n;
}
function $t(e) {
	return e.startsWith("wiki/") && !e.includes("..") && !e.startsWith("/") && !e.startsWith("\\") && !/^[A-Za-z]:[\\/]/.test(e);
}
function en(e, t) {
	if (!e || typeof e != "object") return null;
	let n = e, r = Number(n.x), a = Number(n.y);
	if (!Number.isFinite(r) || !Number.isFinite(a)) return null;
	let o = i(n.coordinateSpace) ? n.coordinateSpace : t;
	return o === "world" && tn(r, a) || o === "legacy-percent" && nn(r, a) ? null : {
		x: r,
		y: a,
		coordinateSpace: o
	};
}
function tn(e, t) {
	return Math.abs(e) > Jt || Math.abs(t) > Jt;
}
function nn(e, t) {
	return Math.abs(e) > Yt || Math.abs(t) > Yt;
}
//#endregion
//#region src/themes/tokens.ts
function rn(e) {
	return `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='620' height='620'%3E%3Cfilter id='m'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.014' numOctaves='3' seed='11' stitchTiles='stitch'/%3E%3CfeColorMatrix values='${e}'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23m)'/%3E%3C/svg%3E")`;
}
var an = `
  color-scheme: light;
  --bg: #f4efe4;
  --surface: #fffdf7;
  --surface-2: #f8f1e4;
  --vellum: #e9ddc9;
  --mist: #ece5d8;
  --ink: #241f1a;
  --muted: #6f6559;
  --faint: #9b8f7e;
  --rule: #d8cdbb;
  --line: #cfc4b1;
  --cinnabar: #8b2e24;
  --cinnabar-2: #a23b2a;
  --jade: #4b7564;
  --green: #3e6b4b;
  --night: #315f72;
  --amber: #b7791f;
  --violet: #6f557f;
  --shadow: 0 18px 36px rgba(36, 31, 26, .11);
  --soft-shadow: 0 10px 24px rgba(36, 31, 26, .08);
  --radius: 12px;
  --paper-glow: radial-gradient(140% 95% at 50% -25%, rgba(255, 251, 240, .7), rgba(255, 251, 240, 0) 55%);
  --paper-vignette: radial-gradient(ellipse 105% 92% at 50% 40%, rgba(255, 255, 255, 0) 52%, rgba(120, 98, 70, .05) 100%);
  --paper-mottle: ${rn("0 0 0 0 0.55 0 0 0 0 0.45 0 0 0 0 0.33 0 0 0 0.13 0")};
  --font-serif: "Noto Serif SC", "Songti SC", "STSong", Georgia, serif;
  --font-ui: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
`, on = `
  color-scheme: dark;
  --bg: #0d0f0e;
  --surface: #181a18;
  --surface-2: #21231f;
  --vellum: #2c2d28;
  --mist: #20241f;
  --ink: #f5f0e6;
  --muted: #c6bbab;
  --faint: #8f8677;
  --rule: #3b3932;
  --line: #8e8778;
  --cinnabar: #e45d4a;
  --cinnabar-2: #ff8066;
  --jade: #8ab6a2;
  --green: #8bae78;
  --night: #a9bfcb;
  --amber: #e0b35e;
  --violet: #c1a8d5;
  --shadow: 0 22px 44px rgba(0, 0, 0, .48);
  --soft-shadow: 0 12px 28px rgba(0, 0, 0, .36);
  --radius: 12px;
  --paper-glow: radial-gradient(140% 95% at 50% -25%, rgba(40, 46, 42, .55), rgba(40, 46, 42, 0) 55%);
  --paper-vignette: radial-gradient(ellipse 105% 92% at 50% 40%, rgba(0, 0, 0, 0) 52%, rgba(0, 0, 0, .22) 100%);
  --paper-mottle: ${rn("0 0 0 0 0.7 0 0 0 0 0.72 0 0 0 0 0.68 0 0 0 0.1 0")};
  --font-serif: "Noto Serif SC", "Songti SC", "STSong", Georgia, serif;
  --font-ui: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
`;
function sn(e) {
	let t = {};
	for (let n of e.split(";")) {
		let e = n.trim();
		if (!e) continue;
		let r = e.indexOf(":");
		if (r < 1) continue;
		let i = e.slice(0, r).trim(), a = e.slice(r + 1).trim();
		!i.startsWith("--") || !a || (t[i] = a);
	}
	return t;
}
var cn = {
	"shan-shui": {
		id: "shan-shui",
		colorScheme: "light",
		vars: sn(an),
		communityColors: [
			"#dd9c82",
			"#8fb0c9",
			"#a6c187",
			"#d8b563",
			"#b9a3cf",
			"#8ec4b3",
			"#cda37e",
			"#d9a0ad",
			"#bdb389"
		]
	},
	"mo-ye": {
		id: "mo-ye",
		colorScheme: "dark",
		vars: sn(on),
		communityColors: [
			"#e45d4a",
			"#a9bfcb",
			"#8ab6a2",
			"#e0b35e",
			"#c1a8d5",
			"#8bae78",
			"#d19966",
			"#aeb8e4"
		]
	}
};
function ln(e) {
	return cn[e] || cn["shan-shui"];
}
function un(e) {
	return { ...(typeof e == "string" ? ln(e) : e).vars };
}
function dn(e, t) {
	let n = typeof e == "string" ? ln(e) : e, r = n.communityColors.length ? n.communityColors : cn["shan-shui"].communityColors;
	return r[Math.abs(Math.trunc(t)) % r.length];
}
//#endregion
//#region src/render/geometry.ts
var U = {
	width: 1e3,
	height: 680
}, W = {
	minX: 0,
	minY: 0,
	maxX: U.width,
	maxY: U.height,
	width: U.width,
	height: U.height
}, fn = {
	x: 5,
	y: 3,
	width: 150,
	height: 48
};
function pn(e, t) {
	return {
		x: G(e.x, 0) - G(t.left, 0),
		y: G(e.y, 0) - G(t.top, 0)
	};
}
function mn(e, t, n = W) {
	let r = Nn(t), i = Pn(n);
	return {
		x: (G(e.x, i.minX) - i.minX) / i.width * r.width,
		y: (G(e.y, i.minY) - i.minY) / i.height * r.height
	};
}
function hn(e, t = W) {
	let n = Pn(t);
	return {
		x: (G(e.x, n.minX) - n.minX) / n.width * 100,
		y: (G(e.y, n.minY) - n.minY) / n.height * 100
	};
}
function gn(e, t, n = W) {
	let r = Nn(t), i = Pn(n);
	return {
		x: i.minX + G(e.x, 0) / r.width * i.width,
		y: i.minY + G(e.y, 0) / r.height * i.height
	};
}
function _n(e, t, n, r = W) {
	let i = mn(e, n, r), a = Mn(t);
	return {
		x: a.x + a.scale * i.x,
		y: a.y + a.scale * i.y
	};
}
function vn(e, t, n, r = W) {
	let i = Mn(t), a = Math.max(1e-6, i.scale);
	return gn({
		x: (G(e.x, 0) - i.x) / a,
		y: (G(e.y, 0) - i.y) / a
	}, n, r);
}
function yn(e, t, n = W) {
	let r = Nn(t), i = Pn(n);
	return {
		x: G(e.x, 0) / i.width * r.width,
		y: G(e.y, 0) / i.height * r.height
	};
}
function bn(e, t, n, r = W) {
	return yn({
		x: G(t.x, 0) - G(e.x, 0),
		y: G(t.y, 0) - G(e.y, 0)
	}, n, r);
}
function xn(e, t, n = W) {
	let r = Nn(t), i = Pn(n);
	return {
		x: G(e.x, 0) / r.width * i.width,
		y: G(e.y, 0) / r.height * i.height
	};
}
function Sn(e) {
	return {
		x: G(e.x, 0),
		y: G(e.y, 0)
	};
}
function Cn(e) {
	return {
		x: G(e.x, 0),
		y: G(e.y, 0)
	};
}
function wn(e, t = fn, n = W) {
	let r = Fn(t), i = Pn(n);
	return {
		x: r.x + (In(G(e.x, i.minX), i.minX, i.maxX) - i.minX) / i.width * r.width,
		y: r.y + (In(G(e.y, i.minY), i.minY, i.maxY) - i.minY) / i.height * r.height
	};
}
function Tn(e, t = fn, n = W) {
	let r = Fn(t), i = Pn(n);
	return {
		x: In(i.minX + (G(e.x, r.x) - r.x) / r.width * i.width, i.minX, i.maxX),
		y: In(i.minY + (G(e.y, r.y) - r.y) / r.height * i.height, i.minY, i.maxY)
	};
}
function En(e, t, n = W) {
	let r = Pn(n), i = vn({
		x: 0,
		y: 0
	}, e, t, r), a = Nn(t), o = vn({
		x: a.width,
		y: a.height
	}, e, t, r);
	return {
		x: In(i.x, r.minX, r.maxX),
		y: In(i.y, r.minY, r.maxY),
		width: Math.max(0, In(o.x, r.minX, r.maxX) - In(i.x, r.minX, r.maxX)),
		height: Math.max(0, In(o.y, r.minY, r.maxY) - In(i.y, r.minY, r.maxY))
	};
}
function Dn(e, t = fn, n = W) {
	let r = wn({
		x: e.x,
		y: e.y
	}, t, n), i = wn({
		x: e.x + e.width,
		y: e.y + e.height
	}, t, n);
	return {
		x: r.x,
		y: r.y,
		width: Math.max(0, i.x - r.x),
		height: Math.max(0, i.y - r.y)
	};
}
function On(e) {
	return {
		x: G(e.x, 0),
		y: G(e.y, 0)
	};
}
function kn() {
	return {
		width: U.width,
		height: U.height
	};
}
function An(e, t = 80, n = W) {
	let r = Pn(n), i = Math.max(0, G(t, 80));
	return {
		x: G(e.x, r.minX) < r.minX + r.width / 2 ? r.minX - i : r.maxX + i,
		y: In(G(e.y, r.minY), r.minY + i, Math.max(r.minY + i, r.maxY - i))
	};
}
function jn(e, t = {}) {
	let n = Math.max(0, G(t.padding, 80)), r = Math.max(1, G(t.minWidth, U.width)), i = Math.max(1, G(t.minHeight, U.height)), a = 0, o = 0, s = r, c = i;
	for (let t of e) {
		let e = G(t.x, 0), r = G(t.y, 0);
		a = Math.min(a, e - n), o = Math.min(o, r - n), s = Math.max(s, e + n), c = Math.max(c, r + n);
	}
	let l = s - a, u = c - o, d = Number(t.aspectRatio);
	if (Number.isFinite(d) && d > 0 && l > 0 && u > 0) {
		let e = (a + s) / 2, t = (o + c) / 2;
		l / u < d ? l = u * d : u = l / d, a = e - l / 2, s = e + l / 2, o = t - u / 2, c = t + u / 2;
	}
	return Pn({
		minX: a,
		minY: o,
		maxX: s,
		maxY: c,
		width: l,
		height: c - o
	});
}
function Mn(e) {
	return {
		x: G(e.x, 0),
		y: G(e.y, 0),
		scale: Math.max(1e-6, G(e.scale, 1))
	};
}
function Nn(e) {
	return {
		width: Math.max(1, G(e.width, U.width)),
		height: Math.max(1, G(e.height, U.height))
	};
}
function Pn(e) {
	if ("minX" in e || "maxX" in e || "minY" in e || "maxY" in e) {
		let t = e, n = G(t.minX, 0), r = G(t.minY, 0), i = Math.max(n + 1, G(t.maxX, n + G(t.width, U.width))), a = Math.max(r + 1, G(t.maxY, r + G(t.height, U.height)));
		return {
			minX: n,
			minY: r,
			maxX: i,
			maxY: a,
			width: Math.max(1, i - n),
			height: Math.max(1, a - r)
		};
	}
	return {
		minX: 0,
		minY: 0,
		maxX: Math.max(1, G(e.width, U.width)),
		maxY: Math.max(1, G(e.height, U.height)),
		width: Math.max(1, G(e.width, U.width)),
		height: Math.max(1, G(e.height, U.height))
	};
}
function Fn(e) {
	return {
		x: G(e.x, fn.x),
		y: G(e.y, fn.y),
		width: Math.max(1, G(e.width, fn.width)),
		height: Math.max(1, G(e.height, fn.height))
	};
}
function G(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function In(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
//#endregion
//#region src/render/community-wash.ts
var Ln = 54, Rn = 36, zn = 46, Bn = 34, Vn = 240, Hn = U.width * .19, Un = ir(U.height * .21);
function Wn(e, t = {}) {
	if (!e.length) return null;
	let n = e.map((e) => tr(e.point)), r = Gn(t), { core: i, outliers: a } = Kn(n), o = Zn(Jn(i, r), r.maxRadiusX * 2, r.maxRadiusY * 2), s = a.length ? Yn(o, Jn([...i, ...a], r), r) : o;
	return {
		cx: ir((s.minX + s.maxX) / 2),
		cy: ir((s.minY + s.maxY) / 2),
		rx: ir((s.maxX - s.minX) / 2),
		ry: ir((s.maxY - s.minY) / 2),
		opacity: e.length > 1 ? .11 : .06
	};
}
function Gn(e) {
	return {
		minRadiusX: nr(e.minRadiusX, Ln),
		minRadiusY: nr(e.minRadiusY, Rn),
		paddingX: nr(e.paddingX, zn),
		paddingY: nr(e.paddingY, Bn),
		maxRadiusX: nr(e.maxRadiusX, Hn),
		maxRadiusY: nr(e.maxRadiusY, Un)
	};
}
function Kn(e) {
	if (e.length <= 3) return {
		core: e,
		outliers: []
	};
	let t = e.length > Vn ? qn(e, Vn) : e, n = t.map((e) => ({
		point: e,
		neighborScore: $n(e, t)
	})).sort((e, t) => e.neighborScore - t.neighborScore), r = Math.max(2, Math.ceil(n.length * .75)), i = n.slice(0, r), a = n.slice(r), o = Math.max(...i.map((e) => e.neighborScore)), s = Math.min(...a.map((e) => e.neighborScore));
	return !Number.isFinite(s) || s <= Math.max(180, o * 2.5) ? {
		core: e,
		outliers: []
	} : {
		core: i.map((e) => e.point),
		outliers: a.map((e) => e.point)
	};
}
function qn(e, t) {
	if (e.length <= t) return e;
	let n = e.length - 1, r = [], i = /* @__PURE__ */ new Set();
	for (let a = 0; a < t; a += 1) {
		let o = Math.round(a * n / Math.max(1, t - 1));
		i.has(o) || (i.add(o), r.push(e[o]));
	}
	return r;
}
function Jn(e, t) {
	let n = Math.min(...e.map((e) => e.x)), r = Math.max(...e.map((e) => e.x)), i = Math.min(...e.map((e) => e.y)), a = Math.max(...e.map((e) => e.y)), o = (n + r) / 2, s = (i + a) / 2, c = Math.max(t.minRadiusX, (r - n) / 2 + t.paddingX), l = Math.max(t.minRadiusY, (a - i) / 2 + t.paddingY);
	return {
		minX: o - c,
		maxX: o + c,
		minY: s - l,
		maxY: s + l
	};
}
function Yn(e, t, n) {
	let r = Xn(e.minX, e.maxX, t.minX, t.maxX, n.maxRadiusX * 2), i = Xn(e.minY, e.maxY, t.minY, t.maxY, n.maxRadiusY * 2);
	return {
		minX: r.min,
		maxX: r.max,
		minY: i.min,
		maxY: i.max
	};
}
function Xn(e, t, n, r, i) {
	let a = Qn(e, t, i), o = Math.max(0, a.min - n), s = Math.max(0, r - a.max), c = Math.max(0, i - (a.max - a.min)), l = o + s;
	if (l <= 0 || c <= 0) return a;
	let u = Math.min(c, l);
	return {
		min: a.min - o / l * u,
		max: a.max + s / l * u
	};
}
function Zn(e, t, n) {
	let r = Qn(e.minX, e.maxX, t), i = Qn(e.minY, e.maxY, n);
	return {
		minX: r.min,
		maxX: r.max,
		minY: i.min,
		maxY: i.max
	};
}
function Qn(e, t, n) {
	if (t - e <= n) return {
		min: e,
		max: t
	};
	let r = (e + t) / 2, i = n / 2;
	return {
		min: r - i,
		max: r + i
	};
}
function $n(e, t) {
	let n = Infinity, r = Infinity, i = 0;
	for (let a of t) {
		if (a === e) continue;
		i += 1;
		let t = er(e, a);
		t < n ? (r = n, n = t) : t < r && (r = t);
	}
	return i === 0 ? 0 : i === 1 ? n : (n + r) / 2;
}
function er(e, t) {
	return Math.hypot(t.x - e.x, t.y - e.y);
}
function tr(e) {
	return {
		x: rr(e.x, 0),
		y: rr(e.y, 0)
	};
}
function nr(e, t) {
	let n = rr(e, t);
	return n > 0 ? n : t;
}
function rr(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function ir(e) {
	return Math.round(e * 1e3) / 1e3;
}
//#endregion
//#region src/render/pin-position.ts
function ar(e) {
	let t = {
		x: cr(e.x),
		y: cr(e.y)
	};
	return i(e.coordinateSpace) && (t.coordinateSpace = e.coordinateSpace), t;
}
function or(e) {
	return {
		x: cr(e.x),
		y: cr(e.y),
		coordinateSpace: n
	};
}
function sr(e) {
	let t = ar(e);
	return (t.coordinateSpace || "world") === "legacy-percent" ? {
		x: t.x / 100 * U.width,
		y: t.y / 100 * U.height
	} : {
		x: t.x,
		y: t.y
	};
}
function cr(e) {
	let t = Number(e);
	return Number.isFinite(t) ? t : 0;
}
//#endregion
//#region src/render/model.ts
var lr = "M8 40 C34 20 54 36 76 22 C98 8 118 24 150 12", ur = {
	global: {
		maxVisibleNodes: 1e4,
		maxVisibleEdges: 1e3,
		maxLabels: 40,
		maxCards: 0,
		maxInteractionUpdates: 1200
	},
	community: {
		maxVisibleNodes: 2500,
		maxVisibleEdges: 1500,
		maxLabels: 120,
		maxCards: 60,
		maxInteractionUpdates: 1800
	}
}, dr = {
	smallMax: 40,
	mediumMax: 250,
	largeMax: 1e3
}, fr = {
	small: {
		maxVisibleNodes: 2500,
		maxVisibleEdges: 1500,
		maxLabels: 8,
		maxCards: 0,
		maxInteractionUpdates: 1800
	},
	medium: {
		maxVisibleNodes: 2500,
		maxVisibleEdges: 1500,
		maxLabels: 14,
		maxCards: 0,
		maxInteractionUpdates: 1800
	},
	large: {
		maxVisibleNodes: 2500,
		maxVisibleEdges: 1200,
		maxLabels: 18,
		maxCards: 0,
		maxInteractionUpdates: 1500
	},
	oversized: {
		maxVisibleNodes: 2500,
		maxVisibleEdges: 800,
		maxLabels: 24,
		maxCards: 0,
		maxInteractionUpdates: 1200
	}
};
function pr() {
	let e = /* @__PURE__ */ new Map();
	return {
		getEdgeCurve(t, n, r) {
			let i = t.id || `${t.source}->${t.target}`, a = e.get(i);
			if (a != null) return a;
			let o = zr(n, r, t);
			return e.set(i, o), o;
		},
		clear() {
			e.clear();
		}
	};
}
function mr(e, t = {}) {
	let n = t.theme || "shan-shui", r = ut(e), i = dt(r), o = Vr(r, t), s = new Set(o), c = o.length === 1 ? o[0] : null, l = jr(t.focus, r), u = l?.kind === "community" ? r.nodes.filter((e) => e.community === l.id).length : 0, d = xr(l, u), f = hr(e), p = br(l, u), m = l?.kind === "community" ? "community" : "global", h = Mr(t.typeFilters, r.nodes), g = ht(r, i, {
		activeCommunityId: l?.kind === "community" ? l.id : "all",
		selectedNodeId: c
	}), _ = c ? null : Hr(g), v = g.importantNodeIds || {}, y = g.labelNodeIds || {}, b = g.startNodeIds || {}, x = Nr(g.nodes, h), S = new Set(x.map((e) => e.id)), C = g.edges.filter((e) => S.has(e.source) && S.has(e.target)), w = ft(x.length), T = {
		visible_nodes: x.length,
		visible_edges: C.length,
		total_nodes: g.counts.total_nodes,
		total_edges: g.counts.total_edges,
		total_communities: g.counts.total_communities
	}, E = Nr(r.nodes, h), D = new Map(E.map((e) => [e.id, Rr(e, t)])), O = new Map(r.communities.map((e, t) => [e.id, dn(n, Number(e.color_index ?? t))])), k = l?.kind === "community" && t.viewportSize && t.viewportSize.width > 0 && t.viewportSize.height > 0 ? t.viewportSize.width / t.viewportSize.height : void 0, A = jn([...D.values()], k ? { aspectRatio: k } : {}), j = li(r.nodes, t.pins), M = new Set(t.searchResultIds || []);
	t.aggregationMarkers;
	let N = Zr(x, p.maxLabels, {
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		previewNodeId: _
	}), P = new Set(N), F = Jr(C, p.maxVisibleEdges, (e) => ci(e, {
		importantNodeIds: v,
		coreNodeIds: P
	})), ee = new Set(x.filter((e) => si(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M
	}) > 0).map((e) => e.id)), I = Jr(x, p.maxVisibleNodes, (e) => Yr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		previewNodeId: _,
		coreNodeIds: P
	})), L = x.filter((e) => I.has(e.id)), te = L.filter((e) => y[e.id] === !0 || s.has(e.id) || j.has(e.id) || M.has(e.id) || v[e.id] === !0 || b[e.id] === !0 || e.id === _), R = Jr(te, p.maxLabels, (e) => Yr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		previewNodeId: _,
		coreNodeIds: P
	})), z = p.maxCards > 0 ? L.filter((e) => qr(e, m, w, s, j, M, v, _)) : [], ne = Jr(z, p.maxCards, (e) => Yr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		previewNodeId: _,
		coreNodeIds: P
	})), re = new Set([
		...P,
		...s,
		...j,
		...M
	]), ie = Math.max(4, Math.min(R.size, Math.ceil(p.maxLabels * .35))), ae = Jr(L.filter((e) => re.has(e.id)), ie, (e) => Yr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		previewNodeId: _,
		coreNodeIds: P
	})), B = $r(L, {
		labelNodeIds: y,
		importantNodeIds: v,
		startNodeIds: b,
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		coreNodeIds: P
	}), V = L.map((e) => {
		let r = s.has(e.id), i = Ur(e, {
			view: m,
			densityMode: w,
			selectedNodeIds: s,
			cardNodeIds: ne,
			labelNodeIds: R
		}), o = D.get(e.id) || Rr(e, t), l = hn(o, A);
		return {
			id: e.id,
			label: e.label,
			type: e.type,
			kind: e.kind,
			community: e.community,
			communityColor: O.get(e.community) ?? dn(n, 0),
			sourcePath: a(e),
			x: K(l.x),
			y: K(l.y),
			point: o,
			displayMode: i,
			visualRole: di(e, i, r ? e.id : c, _, v),
			priority: Number(e.priority || 0),
			weight: Number(e.weight || 0),
			stableImportance: Qr(e, {
				labelNodeIds: y,
				importantNodeIds: v,
				startNodeIds: b,
				previewNodeId: _,
				coreNodeIds: P
			}),
			temporaryBoost: si(e, {
				selectedNodeIds: s,
				pinnedNodeIds: j,
				searchResultIds: M
			}),
			coreAnchor: P.has(e.id),
			unavailable: e.unavailable === !0,
			selected: r,
			startNode: b[e.id] === !0,
			previewStart: e.id === _,
			labelVisible: R.has(e.id),
			interactionLabelVisible: ae.has(e.id),
			communityMapImportance: B.get(e.id) ?? 0,
			communityMapDotSize: ei(B.get(e.id) ?? 0),
			communityMapLabelSide: ti(l),
			communityMapRelationLabel: ni(e, { labelNodeSet: R }),
			communityMapTier: ri(e, {
				coreNodeIds: P,
				selectedNodeIds: s,
				pinnedNodeIds: j,
				searchResultIds: M,
				labelNodeIds: R,
				importantNodeIds: v,
				startNodeIds: b
			})
		};
	}), oe = new Map(V.map((e) => [e.id, e])), se = l?.kind === "community", ce = C.filter((e) => oe.has(e.source) && oe.has(e.target)), le = Jr(ce, p.maxVisibleEdges, (e) => Xr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		importantNodeIds: v,
		coreNodeIds: P
	})), ue = Math.max(8, Math.min(le.size, Math.ceil(p.maxVisibleEdges * .22))), de = Jr(ce.filter((e) => le.has(e.id) && (re.has(e.source) || re.has(e.target) || F.has(e.id))), ue, (e) => Xr(e, {
		selectedNodeIds: s,
		pinnedNodeIds: j,
		searchResultIds: M,
		importantNodeIds: v,
		coreNodeIds: P
	})), fe = ce.filter((e) => le.has(e.id)).flatMap((e) => {
		let n = oe.get(e.source), r = oe.get(e.target);
		if (!n || !r) return [];
		let i = t.pathCache?.getEdgeCurve(e, n.point, r.point) ?? zr(n.point, r.point, e, A), a = Pr(e), o = Fr(e), s = ii(e, {
			skeletonEdgeIds: F,
			interactionEdgeIds: de
		});
		return [{
			id: e.id,
			source: e.source,
			target: e.target,
			type: a,
			confidence: a,
			relationType: o,
			relationClass: Or(o),
			path: Cr(n.point, r.point, i),
			curveOffset: i,
			strokeWidth: Er(e, se),
			opacity: Dr(e, se),
			simulationWeight: wr(e),
			skeleton: F.has(e.id),
			traceable: de.has(e.id),
			communityMapLayer: s
		}];
	}), pe = new Set(fe.map((e) => e.id)), me = r.communities.map((e, t) => {
		let r = V.filter((t) => t.community === e.id), i = E.filter((t) => t.community === e.id), a = Wn(r);
		return {
			id: e.id,
			label: e.label || e.id,
			color: O.get(e.id) ?? dn(n, t),
			nodeCount: Number(e.node_count ?? i.length),
			boundaryCertainty: f.boundaryCertainty,
			wash: a ? {
				...a,
				opacity: gr(a.opacity, f.boundaryCertainty)
			} : null
		};
	}), he = new Map(me.map((e) => [e.id, e])), ge = [], _e = V.filter((e) => e.labelVisible).length, ve = V.filter((e) => e.displayMode === "card").length, ye = V.length + fe.length + _e + ve, be = Math.min(ye, p.maxInteractionUpdates), xe = V.filter((e) => e.interactionLabelVisible).length, Se = fe.filter((e) => e.traceable).length, Ce = V.length + Se + xe, we = Math.min(Ce, p.maxInteractionUpdates), Te = l?.kind === "community", Ee = l?.kind === "community" ? l.id : t.sourceCommunityId ? t.sourceCommunityId : null, De = new Set(Ee ? V.filter((e) => e.community === Ee).map((e) => e.id) : []), Oe = V.filter((e) => De.has(e.id)), ke = fe.filter((e) => De.has(e.source) && De.has(e.target)), Ae = Oe.filter((e) => e.labelVisible).length, je = ai(ke), Me = Ee ? {
		communityId: Ee,
		source: Te ? "focus" : "source-context",
		nodeRulesById: Object.fromEntries(Oe.map((e) => [e.id, {
			nodeId: e.id,
			tier: e.communityMapTier,
			basePoint: e.point,
			labelVisible: e.labelVisible,
			labelSide: e.communityMapLabelSide,
			relationLabel: e.communityMapRelationLabel,
			importance: e.communityMapImportance,
			dotSize: e.communityMapDotSize
		}])),
		edgeRulesById: Object.fromEntries(ke.map((e) => [e.id, {
			edgeId: e.id,
			layer: e.communityMapLayer,
			skeleton: e.skeleton,
			traceable: e.traceable
		}])),
		layout: oi(Oe, { viewportSize: t.viewportSize }),
		labelBudget: {
			limit: p.maxLabels,
			visible: Ae,
			hidden: Math.max(0, Oe.length - Ae)
		},
		edgeLayers: je
	} : null;
	return {
		model: r,
		layout: i,
		worldBounds: A,
		selectedNodeId: c,
		focus: l,
		typeFilters: h,
		densityMode: w,
		counts: {
			visibleNodes: T.visible_nodes,
			visibleEdges: T.visible_edges,
			totalNodes: T.total_nodes,
			totalEdges: T.total_edges,
			totalCommunities: T.total_communities
		},
		nodes: V,
		edges: fe,
		communities: me,
		aggregationContainers: ge,
		minimap: {
			path: lr,
			nodes: V.slice(0, 60).map((e) => {
				let t = wn(e.point, void 0, A);
				return {
					id: e.id,
					x: t.x,
					y: t.y,
					r: e.selected ? 3.2 : 2.2,
					fill: he.get(e.community)?.color || dn(n, 0),
					selected: e.selected
				};
			})
		},
		budget: {
			view: m,
			limits: { ...p },
			usage: {
				maxVisibleNodes: V.length,
				maxVisibleEdges: fe.length,
				maxLabels: _e,
				maxCards: ve,
				maxInteractionUpdates: be
			}
		},
		overflow: {
			nodes: ui(x.map((e) => e.id), new Set(V.map((e) => e.id))),
			edges: ui(C.map((e) => e.id), pe),
			labels: ui(te.map((e) => e.id), R),
			cards: ui(z.map((e) => e.id), ne),
			interactionUpdates: {
				total: ye,
				hidden: Math.max(0, ye - p.maxInteractionUpdates)
			}
		},
		interaction: {
			mode: "idle",
			maxUpdatedObjects: p.maxInteractionUpdates,
			updateCandidates: Ce,
			updatedObjects: we,
			hiddenObjects: Math.max(0, Ce - p.maxInteractionUpdates),
			labelsVisibleDuringInteraction: xe,
			edgesVisibleDuringInteraction: Se,
			preservedNodeIds: V.filter((e) => re.has(e.id)).map((e) => e.id)
		},
		importance: {
			stableCoreNodeIds: N,
			stableSkeletonEdgeIds: C.filter((e) => F.has(e.id)).map((e) => e.id),
			temporaryBoostNodeIds: x.filter((e) => ee.has(e.id)).map((e) => e.id)
		},
		communityFocus: d,
		communityQuality: f,
		communityMap: {
			active: Te,
			sourceCommunityId: t.sourceCommunityId || null,
			motionMode: Te ? "frozen" : "live",
			maxNodeDriftRatio: +!Te,
			current: Me,
			rulesByCommunityId: Me ? { [Me.communityId]: Me } : {}
		}
	};
}
function hr(e) {
	let t = e.nodes.length, n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map();
	for (let t of e.nodes) {
		let e = _r(t.community);
		e && n.set(e, (n.get(e) || 0) + 1);
	}
	for (let t of e.learning?.communities || []) n.set(t.id, Math.max(n.get(t.id) || 0, Number(t.node_count) || 0)), r.set(t.id, t.label || "");
	let i = n.size, a = Math.max(0, ...n.values()), o = [...n.values()].filter((e) => e <= 2).length, s = [...n.keys()].filter((e) => vr(r.get(e), e)).length, c = yr(e), l = [];
	(a > dr.largeMax || t >= 80 && a / Math.max(1, t) >= .72) && l.push({
		id: "oversized-community",
		severity: "poor",
		value: a,
		threshold: dr.largeMax
	}), i >= 8 && o / i >= .55 && l.push({
		id: "many-tiny-communities",
		severity: "moderate",
		value: K(o / i),
		threshold: .55
	}), e.edges.length >= 6 && c >= .42 && l.push({
		id: "mixed-cross-community-edges",
		severity: "poor",
		value: K(c),
		threshold: .42
	}), i > 0 && s / i >= .35 && l.push({
		id: "weak-community-labels",
		severity: "moderate",
		value: K(s / i),
		threshold: .35
	}), (t >= 60 && i <= 1 || i > Math.max(48, Math.ceil(Math.sqrt(Math.max(1, t)) * 4))) && l.push({
		id: "abnormal-community-count",
		severity: "moderate",
		value: i,
		threshold: t >= 60 && i <= 1 ? 1 : Math.max(48, Math.ceil(Math.sqrt(Math.max(1, t)) * 4))
	});
	let u = l.reduce((e, t) => e + (t.severity === "poor" ? 2 : 1), 0), d = u >= 3 ? "poor" : u >= 1 ? "moderate" : "good";
	return {
		level: d,
		boundaryCertainty: d === "poor" ? "low" : d === "moderate" ? "reduced" : "high",
		warning: d === "poor" ? "poor-community-quality" : d === "moderate" ? "moderate-community-quality" : null,
		signals: l,
		auxiliaryViews: d === "poor" ? [{
			id: "core-structure-connectivity",
			label: "核心结构 / 连通性"
		}] : []
	};
}
function gr(e, t) {
	return t === "low" ? K(e * .48) : t === "reduced" ? K(e * .72) : e;
}
function _r(e) {
	return String(e || "").trim() || null;
}
function vr(e, t) {
	let n = String(e || "").trim().toLowerCase(), r = t.trim().toLowerCase();
	return !n || n === r ? !0 : /^(community|cluster|group|社区|社群|群组)[\s:_-]*[a-z0-9._-]*$/i.test(n);
}
function yr(e) {
	let t = new Map(e.nodes.map((e) => [e.id, _r(e.community)])), n = 0, r = 0;
	for (let i of e.edges) {
		let e = t.get(i.from), a = t.get(i.to);
		!e || !a || (n += 1, e !== a && (r += 1));
	}
	return n ? r / n : 0;
}
function br(e, t = 0) {
	return e?.kind === "community" ? { ...fr[Wr(t)] } : { ...ur.global };
}
function xr(e, t) {
	if (e?.kind !== "community") return null;
	let n = Math.max(0, Math.floor(Number(t) || 0)), r = Wr(n);
	return {
		communityId: e.id,
		nodeCount: n,
		sizeBand: r,
		representation: Gr(r),
		completePresence: Kr(r),
		thresholds: { ...dr }
	};
}
function Sr(e, t, n) {
	let r = We(e), i = We(t);
	return Cr(r, i, zr(r, i, n));
}
function Cr(e, t, n) {
	let r = e.x, i = e.y, a = t.x, o = t.y, s = vt(e, t, n);
	return `M ${K(r)} ${K(i)} Q ${K(s.x)} ${K(s.y)} ${K(a)} ${K(o)}`;
}
function wr(e) {
	return K(1.1 + fi(e.weight) * 1.8);
}
function Tr(e) {
	return K(.32 + fi(e.weight) * .44);
}
function Er(e, t) {
	return t ? wr(e) : K(.95 + fi(e.weight) * .75);
}
function Dr(e, t) {
	return t ? Tr(e) : K(.2 + fi(e.weight) * .22);
}
function Or(e) {
	switch (Ir(e)) {
		case "实现": return "relation-implementation";
		case "依赖": return "relation-dependency";
		case "衍生": return "relation-derivation";
		case "对比": return "relation-contrast";
		case "矛盾": return "relation-conflict";
		default: return "relation-dependency";
	}
}
function kr(e, t) {
	let n = Number.isFinite(Number(e)) ? Math.max(0, Number(e)) : 0, r = Number.isFinite(Number(t)) ? pi(Number(t), .25, 4) : 1;
	return ft(Math.ceil(n / (r * r)));
}
function Ar(e, t) {
	if (e.selected || t === "card") return "card";
	if (t === "compact-card") return "compact-card";
	let n = e.labelVisible || e.visualRole !== "map-pin";
	return t === "point-plus-focus" ? n ? "compact-card" : "point" : n ? "compact-card" : "overview";
}
function jr(e, t) {
	if (!e || e.kind !== "community") return null;
	let n = String(e.id || "");
	return n && t.communityById[n] ? {
		kind: "community",
		id: n
	} : null;
}
function Mr(e, t) {
	let n = {};
	for (let r of t) n[r.type] = e?.[r.type] !== !1;
	return n;
}
function Nr(e, t) {
	return e.filter((e) => t[e.type] !== !1);
}
function Pr(e) {
	let t = String(e.confidence || e.type || "EXTRACTED").toUpperCase();
	return t === "INFERRED" || t === "AMBIGUOUS" || t === "UNVERIFIED" ? t.toLowerCase() : "extracted";
}
function Fr(e) {
	return Ir(e.relation_type || "依赖");
}
function Ir(e) {
	return String(e || "依赖").trim() || "依赖";
}
function Lr(e) {
	return a(e);
}
function Rr(e, t) {
	let n = t.positions?.[e.id];
	if (n) return {
		x: Br(n.x),
		y: Br(n.y)
	};
	let r = t.pins?.[Lr(e)];
	return r ? sr(r) : We(e);
}
function zr(e, t, n, r = {
	minX: 0,
	minY: 0,
	maxX: U.width,
	maxY: U.height,
	width: U.width,
	height: U.height
}) {
	let i = (e.y - r.minY) / r.height * 100, a = (t.y - r.minY) / r.height * 100;
	return Math.max(-76, Math.min(76, (i - a) * 1.8 + (fi(n.weight) - .5) * 24));
}
function Br(e) {
	let t = Number(e);
	return Number.isFinite(t) ? t : 0;
}
function Vr(e, t) {
	if (t.selection?.kind === "node" && e.byId[t.selection.id]) return [t.selection.id];
	if (t.selection?.kind === "community") {
		let n = t.selection.id;
		return e.nodes.filter((e) => e.community === n).map((e) => e.id);
	}
	if (t.selection?.kind === "nodes") {
		let n = new Set(t.selection.ids);
		return e.nodes.map((e) => e.id).filter((e) => n.has(e));
	}
	return t.selectedNodeId && e.byId[t.selectedNodeId] ? [t.selectedNodeId] : [];
}
function Hr(e) {
	let t = e.starts.find((e) => e?.node);
	if (t?.node) return t.node.id;
	let n = e.nodes.slice().sort((e, t) => Number(t.priority || 0) - Number(e.priority || 0))[0];
	return n ? n.id : null;
}
function Ur(e, t) {
	return t.cardNodeIds.has(e.id) ? "card" : t.labelNodeIds.has(e.id) ? "compact-card" : (t.view, t.densityMode === "overview" ? "overview" : "point");
}
function Wr(e) {
	let t = Math.max(0, Math.floor(Number(e) || 0));
	return t <= dr.smallMax ? "small" : t <= dr.mediumMax ? "medium" : t <= dr.largeMax ? "large" : "oversized";
}
function Gr(e) {
	return e === "small" ? "cards-and-labels" : e === "medium" ? "points-with-cards" : e === "large" ? "outline-with-caps" : "internal-map-entry";
}
function Kr(e) {
	return e === "large" ? "outline" : e === "oversized" ? "internal-map" : "nodes";
}
function qr(e, t, n, r, i, a, o, s) {
	return t === "global" ? !1 : n === "card" || r.has(e.id) || i.has(e.id) || a.has(e.id) || o[e.id] === !0 || e.id === s;
}
function Jr(e, t, n) {
	return t <= 0 || e.length === 0 ? /* @__PURE__ */ new Set() : e.length <= t ? new Set(e.map((e) => e.id)) : new Set(e.map((e, t) => ({
		item: e,
		index: t,
		score: n(e, t)
	})).sort((e, t) => t.score - e.score || e.index - t.index).slice(0, t).map((e) => e.item.id));
}
function Yr(e, t) {
	return Qr(e, t) + si(e, t);
}
function Xr(e, t) {
	let n = [e.source, e.target], r = ci(e, t);
	for (let e of n) t.selectedNodeIds.has(e) && (r += 1e5), t.searchResultIds.has(e) && (r += 5e4), t.pinnedNodeIds.has(e) && (r += 4e4), t.importantNodeIds[e] && (r += 12e3);
	return r;
}
function Zr(e, t, n) {
	if (t <= 0) return [];
	let r = /* @__PURE__ */ new Set(), i = /* @__PURE__ */ new Map();
	e.forEach((e, t) => {
		let r = Qr(e, {
			...n,
			coreNodeIds: /* @__PURE__ */ new Set()
		}), a = i.get(e.community);
		(!a || r > a.score || r === a.score && t < a.index) && i.set(e.community, {
			node: e,
			score: r,
			index: t
		});
	});
	for (let e of [...i.values()].sort((e, t) => t.score - e.score || e.index - t.index)) {
		if (r.size >= t) break;
		r.add(e.node.id);
	}
	let a = Jr(e, t, (e) => Qr(e, {
		...n,
		coreNodeIds: r
	})), o = new Set([...r, ...a]);
	return e.filter((e) => o.has(e.id)).slice(0, t).map((e) => e.id);
}
function Qr(e, t) {
	let n = Number(e.priority || 0) * 10 + Number(e.weight || 0);
	return t.coreNodeIds.has(e.id) && (n += 2e4), n;
}
function $r(e, t) {
	let n = e.map((e) => ({
		id: e.id,
		value: Math.max(Number(e.priority || 0), Number(e.weight || 0))
	})), r = Math.max(0, ...n.map((e) => e.value)), i = r <= 1 ? 10 : r > 10 ? 10 / r : 1, a = /* @__PURE__ */ new Map();
	for (let n of e) {
		let e = Math.max(Number(n.priority || 0), Number(n.weight || 0)) * i;
		(t.selectedNodeIds.has(n.id) || t.pinnedNodeIds.has(n.id) || t.searchResultIds.has(n.id)) && (e += 1.5), t.coreNodeIds.has(n.id) && (e += 1), (t.startNodeIds[n.id] || t.importantNodeIds[n.id] || t.labelNodeIds[n.id]) && (e += .7), a.set(n.id, K(pi(e, 0, 10)));
	}
	return a;
}
function ei(e) {
	return K(9 + Math.max(0, Math.min(10, e || 0)) * 1.45);
}
function ti(e) {
	return e.x > 72 ? "left" : e.x < 24 ? "right" : e.y > 68 ? "top" : e.y < 24 ? "bottom" : "right";
}
function ni(e, t) {
	return t.labelNodeSet.has(e.id);
}
function ri(e, t) {
	return t.coreNodeIds.has(e.id) || t.selectedNodeIds.has(e.id) || t.startNodeIds[e.id] === !0 ? "core" : t.pinnedNodeIds.has(e.id) || t.searchResultIds.has(e.id) || t.labelNodeIds.has(e.id) || t.importantNodeIds[e.id] === !0 ? "related" : "peripheral";
}
function ii(e, t) {
	return t.skeletonEdgeIds.has(e.id) ? "skeleton" : t.interactionEdgeIds.has(e.id) ? "related" : "background";
}
function ai(e) {
	return e.reduce((e, t) => (e[t.communityMapLayer] += 1, e), {
		skeleton: 0,
		related: 0,
		background: 0
	});
}
function oi(e, t) {
	let n = jn(e.map((e) => e.point)), r = t.viewportSize, i = r && r.width > 0 && r.height > 0 ? r.width / r.height : null;
	return {
		coordinateSpace: "world",
		bounds: {
			minX: n.minX,
			minY: n.minY,
			maxX: n.maxX,
			maxY: n.maxY,
			width: n.width,
			height: n.height
		},
		viewportAspectRatio: i
	};
}
function si(e, t) {
	let n = 0;
	return t.selectedNodeIds.has(e.id) && (n += 1e5), t.searchResultIds.has(e.id) && (n += 5e4), t.pinnedNodeIds.has(e.id) && (n += 4e4), n;
}
function ci(e, t) {
	let n = [e.source, e.target], r = fi(e.weight) * 1e3;
	for (let e of n) t.coreNodeIds.has(e) && (r += 1e4);
	return r;
}
function li(e, t) {
	if (!t) return /* @__PURE__ */ new Set();
	let n = new Set(Object.keys(t));
	return new Set(e.filter((e) => n.has(Lr(e))).map((e) => e.id));
}
function ui(e, t) {
	let n = e.filter((e) => !t.has(e));
	return {
		total: e.length,
		hidden: n.length,
		ids: n
	};
}
function di(e, t, n, r, i) {
	return e.id === n ? "cinnabar-note" : t === "point" || t === "overview" ? "map-pin" : r && e.id === r || i[e.id] ? "index-slip" : "landmark";
}
function fi(e) {
	let t = Number(e);
	return Number.isFinite(t) ? pi(t, 0, 1) : .6;
}
function pi(e, t, n) {
	return Math.max(t, Math.min(n, e));
}
function K(e) {
	return Math.round(e * 1e3) / 1e3;
}
//#endregion
//#region src/render/legend.ts
function mi(e, t) {
	return e.filter((e) => e.nodeCount > 0).map((e) => ({
		id: e.id,
		label: e.label || e.id,
		color: e.color,
		pageCount: e.nodeCount,
		nodeIds: t.filter((t) => t.community === e.id).map((e) => e.id)
	}));
}
//#endregion
//#region src/select/index.ts
var q = {
	summarizePage: {
		id: "summarize_page",
		label: "总结这一页",
		tone: "digest"
	},
	findRelatedPages: {
		id: "find_related_pages",
		label: "它和谁有关",
		tone: "bridge"
	},
	quotePage: {
		id: "quote_page",
		label: "在对话中引用",
		tone: "write"
	},
	summarizeCluster: {
		id: "summarize_cluster",
		label: "总结这一簇",
		tone: "digest"
	},
	summarizeGroup: {
		id: "summarize_group",
		label: "总结这一组",
		tone: "digest"
	},
	exploreGroupRelationships: {
		id: "explore_group_relationships",
		label: "探索它们的关系",
		tone: "bridge"
	},
	findKnowledgeGaps: {
		id: "find_knowledge_gaps",
		label: "找知识缺口",
		tone: "lint"
	},
	createTopicPage: {
		id: "create_topic_page",
		label: "生成主题页",
		tone: "write"
	},
	whyNoConnection: {
		id: "why_no_connection",
		label: "为什么没联系",
		tone: "bridge"
	},
	findPotentialBridges: {
		id: "find_potential_bridges",
		label: "找潜在桥梁",
		tone: "bridge"
	},
	compareCommunities: {
		id: "compare_communities",
		label: "对比这两块",
		tone: "compare"
	},
	explorePotentialLinks: {
		id: "explore_potential_links",
		label: "探索潜在联系",
		tone: "bridge"
	},
	compareDifferences: {
		id: "compare_differences",
		label: "对比异同",
		tone: "compare"
	},
	linkIsland: {
		id: "link_island",
		label: "把它链入知识库",
		tone: "repair"
	}
};
function hi(e = !1) {
	let t = [
		q.summarizePage,
		q.findRelatedPages,
		q.quotePage
	];
	return e ? [...t, q.linkIsland] : t;
}
function gi() {
	return [q.quotePage, q.findRelatedPages].map((e) => ({
		id: e.id,
		label: e.label
	}));
}
function _i(e, t) {
	return yi(e, t, { canAsk: !0 });
}
function vi(e, t, n) {
	let r = Ti(e);
	if (!r.nodeById.has(n)) return t ?? null;
	let i = t ? Ei(r, t) : [], a = new Set(i);
	a.has(n) ? a.delete(n) : a.add(n);
	let o = r.nodes.map((e) => e.id).filter((e) => a.has(e));
	return o.length === 0 ? null : o.length === 1 ? {
		kind: "node",
		id: o[0]
	} : {
		kind: "nodes",
		ids: o
	};
}
function yi(e, t, n) {
	let r = Ti(e), i = Ei(r, t), a = Di(r, i), o = Oi(r, i);
	return {
		id: Ai(t, i),
		nodeIds: i,
		communityIds: o,
		facts: a,
		input: t,
		actions: n.canAsk === !1 ? [] : bi(a, t)
	};
}
function bi(e, t) {
	return e.pageCount === 0 ? [] : e.pageCount === 1 ? hi(e.isolatedCount === 1) : e.pageCount > 1 && e.internalLinkCount > 0 && t?.kind !== "community" && t?.kind !== "neighbors" ? [q.summarizeGroup, q.exploreGroupRelationships] : e.communityCount === 1 && e.internalLinkCount > 0 ? [
		q.summarizeCluster,
		q.findKnowledgeGaps,
		q.createTopicPage
	] : e.communityCount === 2 ? [
		q.whyNoConnection,
		q.findPotentialBridges,
		q.compareCommunities
	] : e.pageCount > 1 && e.internalLinkCount === 0 || e.pageCount > 1 ? [q.explorePotentialLinks, q.compareDifferences] : [q.explorePotentialLinks];
}
function xi() {
	return [
		q.summarizeCluster,
		q.findKnowledgeGaps,
		q.createTopicPage,
		{
			...q.explorePotentialLinks,
			label: "探索潜在关系"
		}
	];
}
function Si(e) {
	return e ? xi().find((t) => t.id === e) ?? null : null;
}
function Ci(e) {
	return e === "ungrouped" ? "explore_potential_links" : e === "loose" ? "find_knowledge_gaps" : "summarize_cluster";
}
function wi(e) {
	return e.internalLinkCount === 0 || e.communityCount > 1 ? "explore_potential_links" : "summarize_cluster";
}
function Ti(e) {
	let t = e.nodes.map(ji), n = new Map(t.map((e) => [e.id, e])), r = new Map(t.map((e) => [e.id, /* @__PURE__ */ new Set()])), i = [];
	for (let t of e.edges) {
		let e = Mi(t.from), a = Mi(t.to);
		if (!e || !a || e === a || !n.has(e) || !n.has(a)) continue;
		let o = {
			id: t.id || `${e}->${a}`,
			source: e,
			target: a
		};
		i.push(o), r.get(e)?.add(a), r.get(a)?.add(e);
	}
	return {
		nodes: t,
		nodeById: n,
		edges: i,
		neighborsById: r
	};
}
function Ei(e, t) {
	return t.kind === "node" ? e.nodeById.has(t.id) ? [t.id] : [] : t.kind === "community" ? ki(e.nodes.filter((e) => e.community === t.id).map((e) => e.id), e) : t.kind === "neighbors" ? e.nodeById.has(t.id) ? ki([t.id, ...Array.from(e.neighborsById.get(t.id) ?? [])], e) : [] : ki(t.ids.filter((t) => e.nodeById.has(t)), e);
}
function Di(e, t) {
	let n = new Set(t), r = e.edges.filter((e) => n.has(e.source) && n.has(e.target)).length, i = t.filter((t) => (e.neighborsById.get(t)?.size ?? 0) === 0).length;
	return {
		pageCount: t.length,
		internalLinkCount: r,
		communityCount: Oi(e, t).length,
		isolatedCount: i
	};
}
function Oi(e, t) {
	let n = /* @__PURE__ */ new Set(), r = [];
	for (let i of t) {
		let t = e.nodeById.get(i)?.community;
		!t || n.has(t) || (n.add(t), r.push(t));
	}
	return r;
}
function ki(e, t) {
	let n = new Set(e);
	return t.nodes.map((e) => e.id).filter((e) => n.has(e));
}
function Ai(e, t) {
	return `${e.kind}:${t.join(",")}`;
}
function ji(e) {
	return {
		id: e.id,
		label: e.label || e.id,
		community: String(e.community || "_none"),
		sourcePath: a(e)
	};
}
function Mi(e) {
	return e == null || e === "" ? null : String(e);
}
//#endregion
//#region src/render/adapter.ts
var Ni = [
	"dom-svg",
	"candidate-global",
	"aggregation-fallback"
];
function Pi(e, t = {}) {
	let n = mr(e, {
		theme: t.theme,
		pins: t.pins,
		selection: t.selection,
		focus: t.focus,
		typeFilters: t.typeFilters,
		positions: t.positions,
		searchResultIds: t.searchResultIds,
		sourceCommunityId: t.sourceCommunityId
	}), r = new Map(e.nodes.map((e) => [e.id, e])), i = new Map(n.nodes.map((e) => [e.id, e])), a = t.searchResultIds ?? [], o = new Set(a), s = Ii(e, t.selection), c = new Set(s.selectedNodeIds), l = new Set(s.selectedCommunityIds), u = t.aggregationMarkers ?? [], d = n.nodes.map((e) => {
		let n = r.get(e.id), i = n?.community ?? e.community ?? null, a = Li(n, e.id, e.sourcePath, t.pins);
		return {
			id: e.id,
			object: {
				kind: "node",
				nodeId: e.id
			},
			label: e.label,
			type: e.type,
			communityId: i,
			sourcePath: e.sourcePath,
			point: e.point,
			selected: c.has(e.id),
			searchHit: o.has(e.id),
			pinHint: a,
			aggregationIds: zi(u, e.id).map((e) => e.id),
			drawerTarget: {
				summaryKind: "node-summary",
				object: {
					kind: "node",
					nodeId: e.id
				}
			},
			render: {
				displayMode: e.displayMode,
				visualRole: e.visualRole,
				priority: e.priority,
				labelVisible: e.labelVisible,
				communityMapTier: e.communityMapTier,
				communityMapImportance: e.communityMapImportance,
				communityMapDotSize: e.communityMapDotSize,
				communityMapLabelSide: e.communityMapLabelSide,
				communityMapRelationLabel: e.communityMapRelationLabel
			}
		};
	}), f = n.communities.map((e) => {
		let i = n.nodes.filter((t) => t.community === e.id).map((e) => e.id), o = Bi(u, e.id), s = i.map((e) => Li(r.get(e), e, null, t.pins)).filter((e) => e.pinned);
		return {
			id: e.id,
			object: {
				kind: "community",
				communityId: e.id
			},
			label: e.label,
			nodeIds: i,
			nodeCount: e.nodeCount,
			selected: l.has(e.id),
			searchResultIds: Vi(i, a),
			pinHints: s,
			aggregationIds: o.map((e) => e.id),
			drawerTarget: {
				summaryKind: "community-summary",
				object: {
					kind: "community",
					communityId: e.id
				}
			},
			commands: e.id === "_none" ? [] : [Hi(e.id)]
		};
	}), p = n.edges.map((t) => {
		let n = r.get(t.source), i = r.get(t.target), a = e.edges.find((e) => e.id === t.id);
		return {
			id: t.id,
			sourceNodeId: t.source,
			targetNodeId: t.target,
			sourceCommunityId: n?.community ?? null,
			targetCommunityId: i?.community ?? null,
			relationType: a?.relation_type ?? t.relationType ?? null,
			confidence: a?.confidence ?? a?.type ?? t.confidence ?? null,
			weight: Ui(a?.weight),
			render: {
				strokeWidth: t.strokeWidth,
				opacity: t.opacity,
				communityMapLayer: t.communityMapLayer,
				skeleton: t.skeleton,
				traceable: t.traceable
			}
		};
	}), m = u.map((e) => {
		let n = {
			kind: "aggregation",
			aggregationId: e.id,
			nodeIds: [...e.nodeIds],
			communityId: e.communityId ?? null
		}, i = e.communityId ? {
			summaryKind: "community-summary",
			object: {
				kind: "community",
				communityId: e.communityId
			}
		} : {
			summaryKind: "excluded-object",
			object: n,
			reason: "aggregation"
		}, o = Vi(e.nodeIds, e.selectedNodeIds ?? s.selectedNodeIds), c = Vi(e.nodeIds, e.pinnedNodeIds ?? Ri(e, r, t.pins)), u = c.map((e) => Li(r.get(e), e, null, t.pins)).filter((e) => e.pinned);
		return {
			id: e.id,
			object: n,
			label: e.label ?? e.id,
			communityId: e.communityId ?? null,
			nodeIds: [...e.nodeIds],
			selectedNodeIds: o,
			searchResultIds: Vi(e.nodeIds, e.searchResultIds ?? a),
			pinnedNodeIds: c,
			totalCount: e.totalCount ?? e.nodeIds.length,
			selected: o.length > 0 || !!(e.communityId && l.has(e.communityId)),
			pinHints: u,
			drawerTarget: i,
			commands: [{
				kind: "show-this-object",
				object: n,
				label: "显示这个对象"
			}, {
				kind: "clear-temporary-object-display",
				label: "清除临时显示"
			}]
		};
	});
	return {
		renderable: n,
		counts: n.counts,
		selection: s,
		sourceCommunityId: t.sourceCommunityId ?? null,
		nodes: d,
		edges: p.filter((e) => i.has(e.sourceNodeId) && i.has(e.targetNodeId)),
		communities: f,
		aggregations: m
	};
}
function Fi(t, n) {
	return {
		route: n,
		pointSelect: t.nodes.map((e) => ({
			nodeId: e.id,
			object: e.object,
			drawerTarget: e.drawerTarget,
			selected: e.selected,
			searchHit: e.searchHit,
			pinHint: e.pinHint,
			aggregationIds: e.aggregationIds
		})),
		containerSelect: [...t.communities.map((e) => ({
			containerId: e.id,
			object: e.object,
			drawerTarget: e.drawerTarget,
			selected: e.selected,
			searchResultIds: e.searchResultIds,
			pinHintNodeIds: e.pinHints.map((e) => e.nodeId)
		})), ...t.aggregations.map((e) => ({
			containerId: e.id,
			object: e.object,
			drawerTarget: e.drawerTarget,
			selected: e.selected,
			searchResultIds: e.searchResultIds,
			pinHintNodeIds: e.pinHints.map((e) => e.nodeId)
		}))],
		searchHighlight: t.nodes.filter((e) => e.searchHit).map((e) => ({
			nodeId: e.id,
			object: e.object,
			aggregationIds: e.aggregationIds,
			drawerTarget: e.drawerTarget
		})),
		selectedObjectInsideAggregation: t.aggregations.filter((e) => e.selectedNodeIds.length > 0).map((e) => ({
			aggregationId: e.id,
			object: e.object,
			selectedNodeIds: e.selectedNodeIds,
			selected: e.selected,
			drawerTarget: e.drawerTarget
		})),
		pinInsideAggregation: t.aggregations.filter((e) => e.pinnedNodeIds.length > 0).map((e) => ({
			aggregationId: e.id,
			pinnedNodeIds: e.pinnedNodeIds,
			pinHints: e.pinHints,
			drawerTarget: e.drawerTarget
		})),
		enterCommunity: t.communities.filter((t) => t.id !== e).map((e) => ({
			communityId: e.id,
			command: Hi(e.id)
		}))
	};
}
function Ii(e, t) {
	if (!t) return {
		input: null,
		selectionId: null,
		selectedNodeIds: [],
		selectedCommunityIds: [],
		containsCurrentObject: !1
	};
	let n = yi(e, t, { canAsk: !1 });
	return {
		input: t,
		selectionId: n.id,
		selectedNodeIds: n.nodeIds,
		selectedCommunityIds: n.communityIds,
		containsCurrentObject: n.nodeIds.length > 0 || n.communityIds.length > 0
	};
}
function Li(e, t, n, r) {
	let i = e ? a(e) : n ?? t, o = r?.[i] ?? null;
	return {
		nodeId: t,
		wikiPath: i,
		pinned: !!o,
		position: o
	};
}
function Ri(e, t, n) {
	return n ? e.nodeIds.filter((e) => {
		let r = t.get(e);
		return r ? !!n[a(r)] : !1;
	}) : [];
}
function zi(e, t) {
	return e.filter((e) => e.nodeIds.includes(t));
}
function Bi(e, t) {
	return e.filter((e) => e.communityId === t);
}
function Vi(e, t) {
	let n = new Set(t);
	return e.filter((e) => n.has(e));
}
function Hi(e) {
	return {
		kind: "enter-community",
		communityId: e,
		label: "进入社区"
	};
}
function Ui(e) {
	return typeof e == "number" && Number.isFinite(e) ? e : 0;
}
//#endregion
//#region src/render/toolbar.ts
var Wi = "llm-wiki:graph:toolbar:panel";
function Gi(e) {
	return e === "filters" || e === "legend" ? e : "closed";
}
function Ki(e) {
	try {
		return Gi(e?.getItem(Wi));
	} catch {
		return "closed";
	}
}
function qi(e, t) {
	try {
		e?.setItem(Wi, t);
	} catch {}
}
function Ji(e, t) {
	return e === t ? "closed" : t;
}
function Yi(e) {
	return e !== "closed";
}
function Xi(e) {
	return Yi(e) ? "closed" : e;
}
//#endregion
//#region ../../node_modules/d3-force/src/constant.js
function J(e) {
	return function() {
		return e;
	};
}
//#endregion
//#region ../../node_modules/d3-force/src/jiggle.js
function Zi(e) {
	return (e() - .5) * 1e-6;
}
//#endregion
//#region ../../node_modules/d3-force/src/collide.js
function Qi(e) {
	return e.x + e.vx;
}
function $i(e) {
	return e.y + e.vy;
}
function ea(e) {
	var t, n, r, i = 1, a = 1;
	typeof e != "function" && (e = J(e == null ? 1 : +e));
	function o() {
		for (var e, o = t.length, c, l, u, d, f, p, m = 0; m < a; ++m) for (c = E(t, Qi, $i).visitAfter(s), e = 0; e < o; ++e) l = t[e], f = n[l.index], p = f * f, u = l.x + l.vx, d = l.y + l.vy, c.visit(h);
		function h(e, t, n, a, o) {
			var s = e.data, c = e.r, m = f + c;
			if (s) {
				if (s.index > l.index) {
					var h = u - s.x - s.vx, g = d - s.y - s.vy, _ = h * h + g * g;
					_ < m * m && (h === 0 && (h = Zi(r), _ += h * h), g === 0 && (g = Zi(r), _ += g * g), _ = (m - (_ = Math.sqrt(_))) / _ * i, l.vx += (h *= _) * (m = (c *= c) / (p + c)), l.vy += (g *= _) * m, s.vx -= h * (m = 1 - m), s.vy -= g * m);
				}
				return;
			}
			return t > u + m || a < u - m || n > d + m || o < d - m;
		}
	}
	function s(e) {
		if (e.data) return e.r = n[e.data.index];
		for (var t = e.r = 0; t < 4; ++t) e[t] && e[t].r > e.r && (e.r = e[t].r);
	}
	function c() {
		if (t) {
			var r, i = t.length, a;
			for (n = Array(i), r = 0; r < i; ++r) a = t[r], n[a.index] = +e(a, r, t);
		}
	}
	return o.initialize = function(e, n) {
		t = e, r = n, c();
	}, o.iterations = function(e) {
		return arguments.length ? (a = +e, o) : a;
	}, o.strength = function(e) {
		return arguments.length ? (i = +e, o) : i;
	}, o.radius = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : J(+t), c(), o) : e;
	}, o;
}
//#endregion
//#region ../../node_modules/d3-force/src/link.js
function ta(e) {
	return e.index;
}
function na(e, t) {
	var n = e.get(t);
	if (!n) throw Error("node not found: " + t);
	return n;
}
function ra(e) {
	var t = ta, n = d, r, i = J(30), a, o, s, c, l, u = 1;
	e ??= [];
	function d(e) {
		return 1 / Math.min(s[e.source.index], s[e.target.index]);
	}
	function f(t) {
		for (var n = 0, i = e.length; n < u; ++n) for (var o = 0, s, d, f, p, m, h, g; o < i; ++o) s = e[o], d = s.source, f = s.target, p = f.x + f.vx - d.x - d.vx || Zi(l), m = f.y + f.vy - d.y - d.vy || Zi(l), h = Math.sqrt(p * p + m * m), h = (h - a[o]) / h * t * r[o], p *= h, m *= h, f.vx -= p * (g = c[o]), f.vy -= m * g, d.vx += p * (g = 1 - g), d.vy += m * g;
	}
	function p() {
		if (o) {
			var n, i = o.length, l = e.length, u = new Map(o.map((e, n) => [t(e, n, o), e])), d;
			for (n = 0, s = Array(i); n < l; ++n) d = e[n], d.index = n, typeof d.source != "object" && (d.source = na(u, d.source)), typeof d.target != "object" && (d.target = na(u, d.target)), s[d.source.index] = (s[d.source.index] || 0) + 1, s[d.target.index] = (s[d.target.index] || 0) + 1;
			for (n = 0, c = Array(l); n < l; ++n) d = e[n], c[n] = s[d.source.index] / (s[d.source.index] + s[d.target.index]);
			r = Array(l), m(), a = Array(l), h();
		}
	}
	function m() {
		if (o) for (var t = 0, i = e.length; t < i; ++t) r[t] = +n(e[t], t, e);
	}
	function h() {
		if (o) for (var t = 0, n = e.length; t < n; ++t) a[t] = +i(e[t], t, e);
	}
	return f.initialize = function(e, t) {
		o = e, l = t, p();
	}, f.links = function(t) {
		return arguments.length ? (e = t, p(), f) : e;
	}, f.id = function(e) {
		return arguments.length ? (t = e, f) : t;
	}, f.iterations = function(e) {
		return arguments.length ? (u = +e, f) : u;
	}, f.strength = function(e) {
		return arguments.length ? (n = typeof e == "function" ? e : J(+e), m(), f) : n;
	}, f.distance = function(e) {
		return arguments.length ? (i = typeof e == "function" ? e : J(+e), h(), f) : i;
	}, f;
}
//#endregion
//#region ../../node_modules/d3-dispatch/src/dispatch.js
var ia = { value: () => {} };
function aa() {
	for (var e = 0, t = arguments.length, n = {}, r; e < t; ++e) {
		if (!(r = arguments[e] + "") || r in n || /[\s.]/.test(r)) throw Error("illegal type: " + r);
		n[r] = [];
	}
	return new oa(n);
}
function oa(e) {
	this._ = e;
}
function sa(e, t) {
	return e.trim().split(/^|\s+/).map(function(e) {
		var n = "", r = e.indexOf(".");
		if (r >= 0 && (n = e.slice(r + 1), e = e.slice(0, r)), e && !t.hasOwnProperty(e)) throw Error("unknown type: " + e);
		return {
			type: e,
			name: n
		};
	});
}
oa.prototype = aa.prototype = {
	constructor: oa,
	on: function(e, t) {
		var n = this._, r = sa(e + "", n), i, a = -1, o = r.length;
		if (arguments.length < 2) {
			for (; ++a < o;) if ((i = (e = r[a]).type) && (i = ca(n[i], e.name))) return i;
			return;
		}
		if (t != null && typeof t != "function") throw Error("invalid callback: " + t);
		for (; ++a < o;) if (i = (e = r[a]).type) n[i] = la(n[i], e.name, t);
		else if (t == null) for (i in n) n[i] = la(n[i], e.name, null);
		return this;
	},
	copy: function() {
		var e = {}, t = this._;
		for (var n in t) e[n] = t[n].slice();
		return new oa(e);
	},
	call: function(e, t) {
		if ((i = arguments.length - 2) > 0) for (var n = Array(i), r = 0, i, a; r < i; ++r) n[r] = arguments[r + 2];
		if (!this._.hasOwnProperty(e)) throw Error("unknown type: " + e);
		for (a = this._[e], r = 0, i = a.length; r < i; ++r) a[r].value.apply(t, n);
	},
	apply: function(e, t, n) {
		if (!this._.hasOwnProperty(e)) throw Error("unknown type: " + e);
		for (var r = this._[e], i = 0, a = r.length; i < a; ++i) r[i].value.apply(t, n);
	}
};
function ca(e, t) {
	for (var n = 0, r = e.length, i; n < r; ++n) if ((i = e[n]).name === t) return i.value;
}
function la(e, t, n) {
	for (var r = 0, i = e.length; r < i; ++r) if (e[r].name === t) {
		e[r] = ia, e = e.slice(0, r).concat(e.slice(r + 1));
		break;
	}
	return n != null && e.push({
		name: t,
		value: n
	}), e;
}
//#endregion
//#region ../../node_modules/d3-timer/src/timer.js
var ua = 0, da = 0, fa = 0, pa = 1e3, ma, ha, ga = 0, _a = 0, va = 0, ya = typeof performance == "object" && performance.now ? performance : Date, ba = typeof window == "object" && window.requestAnimationFrame ? window.requestAnimationFrame.bind(window) : function(e) {
	setTimeout(e, 17);
};
function xa() {
	return _a ||= (ba(Sa), ya.now() + va);
}
function Sa() {
	_a = 0;
}
function Ca() {
	this._call = this._time = this._next = null;
}
Ca.prototype = wa.prototype = {
	constructor: Ca,
	restart: function(e, t, n) {
		if (typeof e != "function") throw TypeError("callback is not a function");
		n = (n == null ? xa() : +n) + (t == null ? 0 : +t), !this._next && ha !== this && (ha ? ha._next = this : ma = this, ha = this), this._call = e, this._time = n, ka();
	},
	stop: function() {
		this._call && (this._call = null, this._time = Infinity, ka());
	}
};
function wa(e, t, n) {
	var r = new Ca();
	return r.restart(e, t, n), r;
}
function Ta() {
	xa(), ++ua;
	for (var e = ma, t; e;) (t = _a - e._time) >= 0 && e._call.call(void 0, t), e = e._next;
	--ua;
}
function Ea() {
	_a = (ga = ya.now()) + va, ua = da = 0;
	try {
		Ta();
	} finally {
		ua = 0, Oa(), _a = 0;
	}
}
function Da() {
	var e = ya.now(), t = e - ga;
	t > pa && (va -= t, ga = e);
}
function Oa() {
	for (var e, t = ma, n, r = Infinity; t;) t._call ? (r > t._time && (r = t._time), e = t, t = t._next) : (n = t._next, t._next = null, t = e ? e._next = n : ma = n);
	ha = e, ka(r);
}
function ka(e) {
	ua || (da &&= clearTimeout(da), e - _a > 24 ? (e < Infinity && (da = setTimeout(Ea, e - ya.now() - va)), fa &&= clearInterval(fa)) : (fa ||= (ga = ya.now(), setInterval(Da, pa)), ua = 1, ba(Ea)));
}
//#endregion
//#region ../../node_modules/d3-force/src/lcg.js
var Aa = 1664525, ja = 1013904223, Ma = 4294967296;
function Na() {
	let e = 1;
	return () => (e = (Aa * e + ja) % Ma) / Ma;
}
//#endregion
//#region ../../node_modules/d3-force/src/simulation.js
function Pa(e) {
	return e.x;
}
function Fa(e) {
	return e.y;
}
var Ia = 10, La = Math.PI * (3 - Math.sqrt(5));
function Ra(e) {
	var t, n = 1, r = .001, i = 1 - r ** (1 / 300), a = 0, o = .6, s = /* @__PURE__ */ new Map(), c = wa(d), l = aa("tick", "end"), u = Na();
	e ??= [];
	function d() {
		f(), l.call("tick", t), n < r && (c.stop(), l.call("end", t));
	}
	function f(r) {
		var c, l = e.length, u;
		r === void 0 && (r = 1);
		for (var d = 0; d < r; ++d) for (n += (a - n) * i, s.forEach(function(e) {
			e(n);
		}), c = 0; c < l; ++c) u = e[c], u.fx == null ? u.x += u.vx *= o : (u.x = u.fx, u.vx = 0), u.fy == null ? u.y += u.vy *= o : (u.y = u.fy, u.vy = 0);
		return t;
	}
	function p() {
		for (var t = 0, n = e.length, r; t < n; ++t) {
			if (r = e[t], r.index = t, r.fx != null && (r.x = r.fx), r.fy != null && (r.y = r.fy), isNaN(r.x) || isNaN(r.y)) {
				var i = Ia * Math.sqrt(.5 + t), a = t * La;
				r.x = i * Math.cos(a), r.y = i * Math.sin(a);
			}
			(isNaN(r.vx) || isNaN(r.vy)) && (r.vx = r.vy = 0);
		}
	}
	function m(t) {
		return t.initialize && t.initialize(e, u), t;
	}
	return p(), t = {
		tick: f,
		restart: function() {
			return c.restart(d), t;
		},
		stop: function() {
			return c.stop(), t;
		},
		nodes: function(n) {
			return arguments.length ? (e = n, p(), s.forEach(m), t) : e;
		},
		alpha: function(e) {
			return arguments.length ? (n = +e, t) : n;
		},
		alphaMin: function(e) {
			return arguments.length ? (r = +e, t) : r;
		},
		alphaDecay: function(e) {
			return arguments.length ? (i = +e, t) : +i;
		},
		alphaTarget: function(e) {
			return arguments.length ? (a = +e, t) : a;
		},
		velocityDecay: function(e) {
			return arguments.length ? (o = 1 - e, t) : 1 - o;
		},
		randomSource: function(e) {
			return arguments.length ? (u = e, s.forEach(m), t) : u;
		},
		force: function(e, n) {
			return arguments.length > 1 ? (n == null ? s.delete(e) : s.set(e, m(n)), t) : s.get(e);
		},
		find: function(t, n, r) {
			var i = 0, a = e.length, o, s, c, l, u;
			for (r == null ? r = Infinity : r *= r, i = 0; i < a; ++i) l = e[i], o = t - l.x, s = n - l.y, c = o * o + s * s, c < r && (u = l, r = c);
			return u;
		},
		on: function(e, n) {
			return arguments.length > 1 ? (l.on(e, n), t) : l.on(e);
		}
	};
}
//#endregion
//#region ../../node_modules/d3-force/src/manyBody.js
function za() {
	var e, t, n, r, i = J(-30), a, o = 1, s = Infinity, c = .81;
	function l(n) {
		var i, a = e.length, o = E(e, Pa, Fa).visitAfter(d);
		for (r = n, i = 0; i < a; ++i) t = e[i], o.visit(f);
	}
	function u() {
		if (e) {
			var t, n = e.length, r;
			for (a = Array(n), t = 0; t < n; ++t) r = e[t], a[r.index] = +i(r, t, e);
		}
	}
	function d(e) {
		var t = 0, n, r, i = 0, o, s, c;
		if (e.length) {
			for (o = s = c = 0; c < 4; ++c) (n = e[c]) && (r = Math.abs(n.value)) && (t += n.value, i += r, o += r * n.x, s += r * n.y);
			e.x = o / i, e.y = s / i;
		} else {
			n = e, n.x = n.data.x, n.y = n.data.y;
			do
				t += a[n.data.index];
			while (n = n.next);
		}
		e.value = t;
	}
	function f(e, i, l, u) {
		if (!e.value) return !0;
		var d = e.x - t.x, f = e.y - t.y, p = u - i, m = d * d + f * f;
		if (p * p / c < m) return m < s && (d === 0 && (d = Zi(n), m += d * d), f === 0 && (f = Zi(n), m += f * f), m < o && (m = Math.sqrt(o * m)), t.vx += d * e.value * r / m, t.vy += f * e.value * r / m), !0;
		if (!(e.length || m >= s)) {
			(e.data !== t || e.next) && (d === 0 && (d = Zi(n), m += d * d), f === 0 && (f = Zi(n), m += f * f), m < o && (m = Math.sqrt(o * m)));
			do
				e.data !== t && (p = a[e.data.index] * r / m, t.vx += d * p, t.vy += f * p);
			while (e = e.next);
		}
	}
	return l.initialize = function(t, r) {
		e = t, n = r, u();
	}, l.strength = function(e) {
		return arguments.length ? (i = typeof e == "function" ? e : J(+e), u(), l) : i;
	}, l.distanceMin = function(e) {
		return arguments.length ? (o = e * e, l) : Math.sqrt(o);
	}, l.distanceMax = function(e) {
		return arguments.length ? (s = e * e, l) : Math.sqrt(s);
	}, l.theta = function(e) {
		return arguments.length ? (c = e * e, l) : Math.sqrt(c);
	}, l;
}
//#endregion
//#region ../../node_modules/d3-force/src/x.js
function Ba(e) {
	var t = J(.1), n, r, i;
	typeof e != "function" && (e = J(e == null ? 0 : +e));
	function a(e) {
		for (var t = 0, a = n.length, o; t < a; ++t) o = n[t], o.vx += (i[t] - o.x) * r[t] * e;
	}
	function o() {
		if (n) {
			var a, o = n.length;
			for (r = Array(o), i = Array(o), a = 0; a < o; ++a) r[a] = isNaN(i[a] = +e(n[a], a, n)) ? 0 : +t(n[a], a, n);
		}
	}
	return a.initialize = function(e) {
		n = e, o();
	}, a.strength = function(e) {
		return arguments.length ? (t = typeof e == "function" ? e : J(+e), o(), a) : t;
	}, a.x = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : J(+t), o(), a) : e;
	}, a;
}
//#endregion
//#region ../../node_modules/d3-force/src/y.js
function Va(e) {
	var t = J(.1), n, r, i;
	typeof e != "function" && (e = J(e == null ? 0 : +e));
	function a(e) {
		for (var t = 0, a = n.length, o; t < a; ++t) o = n[t], o.vy += (i[t] - o.y) * r[t] * e;
	}
	function o() {
		if (n) {
			var a, o = n.length;
			for (r = Array(o), i = Array(o), a = 0; a < o; ++a) r[a] = isNaN(i[a] = +e(n[a], a, n)) ? 0 : +t(n[a], a, n);
		}
	}
	return a.initialize = function(e) {
		n = e, o();
	}, a.strength = function(e) {
		return arguments.length ? (t = typeof e == "function" ? e : J(+e), o(), a) : t;
	}, a.y = function(t) {
		return arguments.length ? (e = typeof t == "function" ? t : J(+t), o(), a) : e;
	}, a;
}
//#endregion
//#region src/sim/pins.ts
var Ha = class {
	nodePathById = /* @__PURE__ */ new Map();
	nodeIdByPath = /* @__PURE__ */ new Map();
	pins;
	constructor(e, t = {}) {
		for (let t of e.nodes) {
			let e = Ga(t);
			this.nodePathById.set(t.id, e), this.nodeIdByPath.set(e, t.id);
		}
		this.pins = Wa(t, this.nodeIdByPath);
	}
	isPinned(e) {
		let t = this.nodePathById.get(e);
		return !!(t && this.pins[t]);
	}
	pin(e, t) {
		let n = this.nodePathById.get(e);
		if (!n) throw Error(`Cannot pin unknown graph node: ${e}`);
		return this.pins = {
			...this.pins,
			[n]: or(t)
		}, this.snapshot();
	}
	unpin(e) {
		let t = this.nodePathById.get(e);
		if (!t || !this.pins[t]) return this.snapshot();
		let n = { ...this.pins };
		return delete n[t], this.pins = n, this.snapshot();
	}
	reset() {
		return this.pins = {}, this.snapshot();
	}
	snapshot() {
		return {
			pins: { ...this.pins },
			pinnedNodeIds: Object.keys(this.pins).map((e) => this.nodeIdByPath.get(e)).filter((e) => !!e)
		};
	}
};
function Ua(e, t) {
	let n = {};
	for (let r of e.nodes) {
		let e = t[Ga(r)];
		e && (n[r.id] = sr(e));
	}
	return n;
}
function Wa(e, t) {
	let n = {};
	for (let [r, i] of Object.entries(e)) t.has(r) && (n[r] = ar(i));
	return n;
}
function Ga(e) {
	return e.sourcePath || e.id;
}
//#endregion
//#region src/sim/index.ts
var Ka = {
	minX: 0,
	minY: 0,
	maxX: 1e3,
	maxY: 680
}, qa = 4, Ja = class {
	options;
	nodes;
	simulation;
	nodeById;
	directNeighbors;
	dragBounds;
	onTick;
	draggedNodeId = null;
	destroyed = !1;
	constructor(e, t = {}) {
		this.options = t, this.nodes = e.nodes.map((e) => Qa(e)), this.nodeById = new Map(this.nodes.map((e) => [e.id, e])), this.directNeighbors = $a(e), this.dragBounds = ro(t.dragBounds || Za(e)), this.onTick = t.onTick;
		let n = e.edges.filter((e) => this.nodeById.has(e.source) && this.nodeById.has(e.target)).map((e) => ({
			id: e.id,
			source: e.source,
			target: e.target,
			weight: Number.isFinite(Number(e.simulationWeight)) ? Number(e.simulationWeight) : 1
		}));
		this.simulation = Ra(this.nodes).force("link", ra(n).id((e) => e.id).distance((e) => eo(e)).strength((e) => to(e))).force("charge", za().strength(-34).distanceMax(220)).force("x", Ba((e) => e.baseX).strength(.052)).force("y", Va((e) => e.baseY).strength(.052)).force("collide", ea((e) => no(e)).strength(.64).iterations(2)).alpha(this.coldStartAlpha).alphaMin(this.alphaMin).alphaDecay(this.alphaDecay).velocityDecay(this.velocityDecay).on("tick", () => this.emitTick()).stop();
	}
	get alpha() {
		return this.simulation.alpha();
	}
	get coldStartAlpha() {
		return io(this.options.coldStartAlpha, .08, .01, .4);
	}
	get lowHeatAlphaTarget() {
		return io(this.options.lowHeatAlphaTarget, .15, .05, .3);
	}
	get alphaMin() {
		return io(this.options.alphaMin, .003, 1e-4, .02);
	}
	get alphaDecay() {
		return io(this.options.alphaDecay, .14, .02, .6);
	}
	get velocityDecay() {
		return io(this.options.velocityDecay, .58, .2, .9);
	}
	startCold() {
		this.assertActive(), this.simulation.alpha(this.coldStartAlpha).alphaTarget(0).restart();
	}
	tick(e = 1) {
		this.assertActive(), this.simulation.tick(Math.max(1, Math.floor(e)));
		let t = this.snapshot();
		return this.onTick?.(t), t;
	}
	settle(e = 240) {
		this.assertActive();
		let t = 0;
		for (; this.simulation.alpha() > this.alphaMin && t < e;) this.simulation.tick(), t += 1;
		this.simulation.alpha(0).alphaTarget(0).stop();
		let n = this.snapshot();
		return this.onTick?.(n), n;
	}
	beginDrag(e) {
		this.assertActive();
		let t = this.requireNode(e);
		return this.draggedNodeId = e, this.freezeFarNodes(e), t.fx = t.x ?? t.baseX, t.fy = t.y ?? t.baseY, this.simulation.alpha(Math.max(this.simulation.alpha(), this.lowHeatAlphaTarget)).alphaTarget(this.lowHeatAlphaTarget).restart(), t;
	}
	dragTo(e, t) {
		this.assertActive();
		let n = this.requireNode(e), r = Xa(t, {
			bounds: this.dragBounds,
			fallback: {
				x: n.baseX,
				y: n.baseY
			}
		});
		return n.fx = r.x, n.fy = r.y, n;
	}
	setFixed(e, t) {
		this.assertActive();
		let n = this.requireNode(e);
		return t === null ? (n.fx = null, n.fy = null, n) : (n.fx = ao(t.x, n.baseX), n.fy = ao(t.y, n.baseY), n.x = n.fx, n.y = n.fy, n);
	}
	endDrag(e = {}) {
		this.assertActive();
		let t = this.draggedNodeId ? this.nodeById.get(this.draggedNodeId) : null;
		if (t) if (e.restore) {
			let n = ao(e.restore.position.x, t.baseX), r = ao(e.restore.position.y, t.baseY);
			t.x = n, t.y = r, t.fx = e.restore.fixed ? n : null, t.fy = e.restore.fixed ? r : null;
		} else e.keepFixed || (t.fx = null, t.fy = null);
		return this.unfreezeFarNodes(), this.draggedNodeId = null, this.simulation.alphaTarget(0), this.snapshot();
	}
	snapshot() {
		return {
			alpha: this.simulation.alpha(),
			positions: Object.fromEntries(this.nodes.map((e) => [e.id, {
				x: oo(e.fx ?? e.x ?? e.baseX),
				y: oo(e.fy ?? e.y ?? e.baseY)
			}]))
		};
	}
	destroy() {
		this.destroyed || (this.destroyed = !0, this.simulation.stop(), this.simulation.on("tick", null));
	}
	requireNode(e) {
		let t = this.nodeById.get(e);
		if (!t) throw Error(`Unknown graph node: ${e}`);
		return t;
	}
	freezeFarNodes(e) {
		let t = this.directNeighbors.get(e) ?? /* @__PURE__ */ new Set();
		for (let n of this.nodes) n.id === e || t.has(n.id) || (n.fixedByDrag = !0, n.savedFx = n.fx ?? null, n.savedFy = n.fy ?? null, n.fx = n.x ?? n.baseX, n.fy = n.y ?? n.baseY);
	}
	unfreezeFarNodes() {
		for (let e of this.nodes) e.fixedByDrag && (e.fx = e.savedFx ?? null, e.fy = e.savedFy ?? null, delete e.fixedByDrag, delete e.savedFx, delete e.savedFy);
	}
	emitTick() {
		this.onTick?.(this.snapshot());
	}
	assertActive() {
		if (this.destroyed) throw Error("Graph simulation has been destroyed");
	}
};
function Ya(e, t) {
	return new Ja(e, t);
}
function Xa(e, t = {}) {
	let n = ro(t.bounds), r = t.fallback || {
		x: (n.minX + n.maxX) / 2,
		y: (n.minY + n.maxY) / 2
	};
	return {
		x: io(e.x, r.x, n.minX, n.maxX),
		y: io(e.y, r.y, n.minY, n.maxY)
	};
}
function Za(e) {
	let t = ro(e.worldBounds), n = Math.max(Ka.maxX - Ka.minX, t.maxX - t.minX, 1), r = Math.max(Ka.maxY - Ka.minY, t.maxY - t.minY, 1);
	return {
		minX: t.minX - n * qa,
		minY: t.minY - r * qa,
		maxX: t.maxX + n * qa,
		maxY: t.maxY + r * qa
	};
}
function Qa(e) {
	return {
		id: e.id,
		sourcePath: e.sourcePath,
		baseX: e.point.x,
		baseY: e.point.y,
		x: e.point.x,
		y: e.point.y
	};
}
function $a(e) {
	let t = /* @__PURE__ */ new Map();
	for (let n of e.nodes) t.set(n.id, /* @__PURE__ */ new Set());
	for (let n of e.edges) t.get(n.source)?.add(n.target), t.get(n.target)?.add(n.source);
	return t;
}
function eo(e) {
	return 118 - io(e.weight, 1.6, .8, 3.4) * 10;
}
function to(e) {
	return io(.032 + e.weight * .012, .052, .02, .09);
}
function no(e) {
	return Math.max(14, Math.min(58, 24 + Math.abs(e.baseX - 500) / 44));
}
function ro(e = Ka) {
	let t = ao(e.minX, Ka.minX), n = ao(e.minY, Ka.minY);
	return {
		minX: t,
		minY: n,
		maxX: Math.max(t, ao(e.maxX, Ka.maxX)),
		maxY: Math.max(n, ao(e.maxY, Ka.maxY))
	};
}
function io(e, t, n, r) {
	let i = Number(e);
	return Number.isFinite(i) ? Math.max(n, Math.min(r, i)) : t;
}
function ao(e, t) {
	let n = Number(e);
	return Number.isFinite(n) ? n : t;
}
function oo(e) {
	return Math.round(e * 1e3) / 1e3;
}
//#endregion
//#region src/render/viewport.ts
var so = {
	x: 0,
	y: 0,
	scale: 1
}, co = 18, lo = 720, uo = .0016, fo = .18, po = .78, mo = .18, ho = .82, go = {
	minScale: .5,
	maxScale: 4,
	worldBounds: W
};
function _o(e) {
	return {
		x: Y(e?.x, so.x),
		y: Y(e?.y, so.y),
		scale: Math.max(.01, Y(e?.scale, so.scale))
	};
}
function vo(e) {
	let t = _o(e);
	return `translate(${Mo(t.x)}px, ${Mo(t.y)}px) scale(${Mo(t.scale)})`;
}
function yo(e, t) {
	let n = _o(t);
	e.style.transformOrigin = "0 0", e.style.transform = vo(n), e.dataset.viewportX = String(Mo(n.x)), e.dataset.viewportY = String(Mo(n.y)), e.dataset.viewportScale = String(Mo(n.scale));
}
function bo(e) {
	let t = Y(e.deltaY, 0);
	return e.deltaMode === 1 ? t * co : e.deltaMode === 2 ? t * lo : t;
}
function xo(e, t, n, r, i = {}) {
	let a = bo(t), o = jo(Math.exp(-a * uo), .2, 5), s = _o(e), c = Oo(r), l = Ao(n, c), u = No(i), d = jo(s.scale * o, u.minScale, u.maxScale), f = mn(vn(l, s, c, u.worldBounds), c, u.worldBounds);
	return Ke({
		x: l.x - d * f.x,
		y: l.y - d * f.y,
		scale: d
	}, c, u);
}
function So(e, t, n, r = {}) {
	let i = _o(e);
	return Ke({
		x: i.x + Y(t.x, 0),
		y: i.y + Y(t.y, 0),
		scale: i.scale
	}, n, No(r));
}
function Co(e, t, n = {}) {
	let r = Po(e), i = Oo(t), a = No(n), o = jo(Math.min(a.worldBounds.width * .82 / Math.max(1, r.width || 1), a.worldBounds.height * .82 / Math.max(1, r.height || 1)), a.minScale, a.maxScale), s = mn({
		x: (r.minX + r.maxX) / 2,
		y: (r.minY + r.maxY) / 2
	}, i, a.worldBounds);
	return Ke({
		x: i.width / 2 - o * s.x,
		y: i.height / 2 - o * s.y,
		scale: o
	}, i, a);
}
function wo(e, t, n, r = {}) {
	let i = _o(t), a = Oo(n), o = No(r), s = jo(i.scale, o.minScale, o.maxScale), c = mn(e, a, o.worldBounds);
	return Ke({
		x: a.width / 2 - s * c.x,
		y: a.height / 2 - s * c.y,
		scale: s
	}, a, o);
}
function To(e, t, n, r = {}) {
	let i = _o(e), a = Oo(t), o = Oo(n), s = No(r), c = r.anchorPoint || ko(i, a, s.worldBounds), l = _n(c, i, a, s.worldBounds), u = jo(l.x / a.width, fo, po), d = jo(l.y / a.height, mo, ho), f = mn(c, o, s.worldBounds);
	return Ke({
		x: o.width * u - i.scale * f.x,
		y: o.height * d - i.scale * f.y,
		scale: i.scale
	}, o, s);
}
function Eo(e, t, n = {}) {
	let r = No(n), i = Dn(En(_o(e), Oo(t), r.worldBounds), void 0, r.worldBounds);
	return {
		x: i.x,
		y: i.y,
		width: Math.max(2, i.width),
		height: Math.max(2, i.height)
	};
}
function Do(e, t = Fo()) {
	let n = !1, r = null, i = null;
	return { schedule(a, o = {}) {
		r = _o(a), i = { lightweight: i === null ? !!o.lightweight : !!(i.lightweight && o.lightweight) }, !n && (n = !0, t.requestAnimationFrame(() => {
			n = !1;
			let t = r, a = i || {};
			r = null, i = null, t && e(t, a);
		}));
	} };
}
function Y(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function Oo(e) {
	return {
		width: Math.max(1, Y(e.width, U.width)),
		height: Math.max(1, Y(e.height, U.height))
	};
}
function ko(e, t, n) {
	let r = vn({
		x: t.width / 2,
		y: t.height / 2
	}, e, t, n);
	return {
		x: jo(r.x, n.minX, n.maxX),
		y: jo(r.y, n.minY, n.maxY)
	};
}
function Ao(e, t) {
	return {
		x: jo(Y(e.x, t.width / 2), 0, t.width),
		y: jo(Y(e.y, t.height / 2), 0, t.height)
	};
}
function jo(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
function Mo(e) {
	return Math.round(e * 1e3) / 1e3;
}
function No(e) {
	return {
		minScale: Y(e.minScale, go.minScale),
		maxScale: Y(e.maxScale, go.maxScale),
		worldBounds: e.worldBounds || go.worldBounds
	};
}
function Po(e) {
	if (!e.length) return {
		minX: 0,
		minY: 0,
		maxX: U.width,
		maxY: U.height,
		width: U.width,
		height: U.height
	};
	let t = U.width, n = U.height, r = 0, i = 0;
	for (let a of e) {
		let e = Y(a.x, 0), o = Y(a.y, 0);
		t = Math.min(t, e), n = Math.min(n, o), r = Math.max(r, e), i = Math.max(i, o);
	}
	return {
		minX: t,
		minY: n,
		maxX: r,
		maxY: i,
		width: Math.max(1, r - t),
		height: Math.max(1, i - n)
	};
}
function Fo() {
	let e = globalThis;
	return { requestAnimationFrame(t) {
		return typeof e.requestAnimationFrame == "function" ? e.requestAnimationFrame(t) : setTimeout(t, 16);
	} };
}
//#endregion
//#region src/render/state.ts
var Io = class {
	snapshotValue;
	listeners = /* @__PURE__ */ new Set();
	constructor(e = {}) {
		this.snapshotValue = Ro(e);
	}
	snapshot() {
		return zo(this.snapshotValue);
	}
	subscribe(e) {
		return this.listeners.add(e), () => {
			this.listeners.delete(e);
		};
	}
	setViewport(e) {
		return this.update({ viewport: _o(e) });
	}
	setPositions(e) {
		return this.update({ positions: Bo(e) });
	}
	commitPosition(e, t) {
		return this.update({ positions: {
			...this.snapshotValue.positions,
			[e]: {
				x: X(t.x, 0),
				y: X(t.y, 0)
			}
		} });
	}
	setPins(e) {
		return this.update({ pins: Vo(e) });
	}
	setHover(e) {
		return this.update({ hover: Ho(e) });
	}
	setSelection(e, t) {
		let n = Wo(e);
		return this.update({
			selection: n,
			selectionSurface: Ko(n, t)
		});
	}
	setFocus(e) {
		return this.update({ focus: Uo(e) });
	}
	setActiveGesture(e) {
		return this.update({ activeGesture: Go(e) });
	}
	clearInteraction() {
		return this.update({
			hover: null,
			selection: null,
			selectionSurface: null,
			focus: null,
			activeGesture: null
		});
	}
	update(e) {
		this.snapshotValue = {
			...this.snapshotValue,
			...e
		};
		let t = this.snapshot();
		for (let e of this.listeners) e(t);
		return t;
	}
};
function Lo(e = {}) {
	return new Io(e);
}
function Ro(e) {
	return {
		viewport: _o(e.viewport || so),
		positions: Bo(e.positions || {}),
		pins: Vo(e.pins || {}),
		hover: Ho(e.hover ?? null),
		selection: Wo(e.selection ?? null),
		selectionSurface: Ko(e.selection ?? null, e.selectionSurface),
		focus: Uo(e.focus ?? null),
		activeGesture: Go(e.activeGesture ?? null)
	};
}
function zo(e) {
	return {
		viewport: { ...e.viewport },
		positions: Bo(e.positions),
		pins: Vo(e.pins),
		hover: Ho(e.hover),
		selection: Wo(e.selection),
		selectionSurface: e.selectionSurface,
		focus: Uo(e.focus),
		activeGesture: Go(e.activeGesture)
	};
}
function Bo(e) {
	return Object.fromEntries(Object.entries(e).map(([e, t]) => [e, {
		x: X(t.x, 0),
		y: X(t.y, 0)
	}]));
}
function Vo(e) {
	return Object.fromEntries(Object.entries(e).map(([e, t]) => [e, {
		x: X(t.x, 0),
		y: X(t.y, 0),
		...t.coordinateSpace ? { coordinateSpace: t.coordinateSpace } : {}
	}]));
}
function Ho(e) {
	return e ? { ...e } : null;
}
function Uo(e) {
	return e ? { ...e } : null;
}
function Wo(e) {
	return e ? e.kind === "nodes" ? {
		kind: "nodes",
		ids: [...e.ids]
	} : { ...e } : null;
}
function Go(e) {
	return e ? e.kind === "node-drag" ? {
		kind: "node-drag",
		pointerId: X(e.pointerId, 0),
		nodeId: e.nodeId,
		grabOffset: {
			x: X(e.grabOffset.x, 0),
			y: X(e.grabOffset.y, 0)
		},
		startWorldPoint: {
			x: X(e.startWorldPoint.x, 0),
			y: X(e.startWorldPoint.y, 0)
		},
		wasPinned: !!e.wasPinned,
		locked: !!e.locked
	} : e.kind === "viewport-pan" ? {
		kind: "viewport-pan",
		pointerId: X(e.pointerId, 0),
		lastScreenPoint: {
			x: X(e.lastScreenPoint.x, 0),
			y: X(e.lastScreenPoint.y, 0)
		},
		locked: !!e.locked
	} : {
		kind: "community-click",
		pointerId: X(e.pointerId, 0),
		communityId: e.communityId,
		locked: !!e.locked
	} : null;
}
function Ko(e, t) {
	return e ? t ?? "selection-panel" : null;
}
function X(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/host-dom.ts
function qo(e) {
	let t = (e.ownerDocument || document).createElement("div");
	return t.className = "llm-wiki-graph-engine", t.dataset.llmWikiGraphRoot = "true", t.tabIndex = 0, e.replaceChildren(t), t;
}
//#endregion
//#region src/render/gestures.ts
var Jo = [
	"graph-blank",
	"node",
	"community-wash",
	"aggregation-container",
	"edge"
], Yo = [
	"minimap",
	"toolbar",
	"search",
	"legend",
	"drawer",
	"text-control",
	"unknown"
], Xo = {
	textControl: "textarea, select, [contenteditable=\"true\"], [data-graph-text-control=\"true\"]",
	search: ".graph-search",
	toolbar: ".graph-toolbar",
	legend: ".community-legend",
	drawer: ".graph-reader, .graph-selection-panel, [data-graph-drawer=\"true\"]",
	minimap: ".mini-map",
	node: ".node",
	aggregationContainer: ".aggregation-container",
	communityWash: ".community-wash",
	edge: ".edge",
	blank: "[data-graph-blank=\"true\"]"
};
function Zo(e) {
	if (!e) return { kind: "unknown" };
	if (us(e) || cs(e, Xo.textControl)) return { kind: "text-control" };
	if (cs(e, Xo.search)) return { kind: "search" };
	if (cs(e, Xo.legend)) return { kind: "legend" };
	if (cs(e, Xo.toolbar)) return { kind: "toolbar" };
	if (cs(e, Xo.drawer)) return { kind: "drawer" };
	if (cs(e, Xo.minimap)) return { kind: "minimap" };
	let t = cs(e, Xo.node);
	if (t) return {
		kind: "node",
		id: ls(t, "id", "nodeId")
	};
	let n = cs(e, Xo.aggregationContainer);
	if (n) return {
		kind: "aggregation-container",
		id: ls(n, "aggregationId", "id"),
		communityId: ls(n, "communityId")
	};
	let r = cs(e, Xo.communityWash);
	if (r) return {
		kind: "community-wash",
		id: ls(r, "communityId", "id")
	};
	let i = cs(e, Xo.edge);
	return i ? {
		kind: "edge",
		id: ls(i, "edgeId", "id")
	} : (cs(e, Xo.blank), { kind: "graph-blank" });
}
function Qo(e) {
	return $o(e) ? "graph-owned" : "graph-blocker";
}
function $o(e) {
	return Jo.includes(e.kind);
}
function es(e) {
	return !$o(e);
}
function ts(e, t = {}) {
	return ns(Zo(e), t);
}
function ns(e, t = {}) {
	return $o(e) ? {
		intent: "zoom",
		target: e
	} : {
		intent: "blocked",
		target: e
	};
}
function rs(e) {
	return as(Zo(e));
}
function is(e) {
	if (!e) return { kind: "unknown" };
	switch (e.kind) {
		case "node": return {
			kind: "node",
			id: e.id
		};
		case "edge": return {
			kind: "edge",
			id: e.id
		};
		case "community-wash": return {
			kind: "community-wash",
			id: e.id
		};
		case "aggregation-container": return {
			kind: "aggregation-container",
			id: e.id,
			communityId: e.communityId
		};
		case "graph-blank": return { kind: "graph-blank" };
		default: return { kind: "unknown" };
	}
}
function as(e) {
	switch (e.kind) {
		case "node": return {
			intent: "node-drag-candidate",
			target: e
		};
		case "community-wash": return {
			intent: "community-click-candidate",
			target: e
		};
		case "aggregation-container": return {
			intent: "community-click-candidate",
			target: {
				kind: "community-wash",
				id: e.communityId
			}
		};
		case "edge": return {
			intent: "blank-pan-candidate",
			target: e
		};
		case "graph-blank": return {
			intent: "blank-pan-candidate",
			target: e
		};
		default: return {
			intent: "blocked",
			target: e
		};
	}
}
var os = class {
	dragThreshold;
	active = null;
	constructor(e = {}) {
		this.dragThreshold = ms(e.dragThreshold, 4);
	}
	snapshot() {
		return ds(this.active);
	}
	pointerDown(e, t) {
		return this.active = null, e.intent === "node-drag-candidate" ? (this.active = {
			kind: "node",
			pointerId: t.pointerId,
			nodeId: e.target.id,
			startScreenPoint: Z(t.screenPoint),
			lastScreenPoint: Z(t.screenPoint),
			additive: !!t.shiftKey,
			locked: !1
		}, []) : e.intent === "community-click-candidate" ? (this.active = {
			kind: "community-wash",
			pointerId: t.pointerId,
			communityId: e.target.id,
			startScreenPoint: Z(t.screenPoint),
			lastScreenPoint: Z(t.screenPoint),
			locked: !1,
			cancelled: !1
		}, []) : (e.intent === "blank-pan-candidate" && (this.active = {
			kind: "blank-pan",
			pointerId: t.pointerId,
			startScreenPoint: Z(t.screenPoint),
			lastScreenPoint: Z(t.screenPoint),
			locked: !1
		}), []);
	}
	pointerMove(e) {
		if (!this.active || this.active.pointerId !== e.pointerId) return [];
		let t = this.active, n = ps(t.startScreenPoint, e.screenPoint), r = fs(t.lastScreenPoint, e.screenPoint);
		if (t.lastScreenPoint = Z(e.screenPoint), t.kind === "node") {
			let i = [];
			return !t.locked && n > this.dragThreshold && (t.locked = !0, i.push({
				kind: "node-drag-start",
				nodeId: t.nodeId,
				pointerId: t.pointerId,
				screenPoint: Z(e.screenPoint)
			})), t.locked && i.push({
				kind: "node-drag-move",
				nodeId: t.nodeId,
				pointerId: t.pointerId,
				screenPoint: Z(e.screenPoint),
				delta: r
			}), i;
		}
		if (t.kind === "community-wash") return !t.locked && n > this.dragThreshold ? (t.locked = !0, t.cancelled = !0, [{
			kind: "community-click-cancelled",
			communityId: t.communityId,
			pointerId: t.pointerId,
			reason: "moved"
		}]) : [];
		let i = [];
		return !t.locked && n > this.dragThreshold && (t.locked = !0, i.push({
			kind: "blank-pan-start",
			pointerId: t.pointerId,
			screenPoint: Z(e.screenPoint)
		})), t.locked && i.push({
			kind: "blank-pan-move",
			pointerId: t.pointerId,
			screenPoint: Z(e.screenPoint),
			delta: r
		}), i;
	}
	pointerUp(e) {
		if (!this.active || this.active.pointerId !== e.pointerId) return [];
		let t = this.active;
		return this.active = null, t.kind === "node" ? t.locked ? [{
			kind: "node-drag-end",
			nodeId: t.nodeId,
			pointerId: t.pointerId,
			screenPoint: Z(e.screenPoint)
		}] : [{
			kind: "node-click",
			nodeId: t.nodeId,
			additive: t.additive,
			pointerId: t.pointerId
		}] : t.kind === "community-wash" ? t.cancelled || t.locked ? [] : [{
			kind: "community-click",
			communityId: t.communityId,
			pointerId: t.pointerId
		}] : t.locked ? [{
			kind: "blank-pan-end",
			pointerId: t.pointerId,
			screenPoint: Z(e.screenPoint)
		}] : [{
			kind: "blank-click",
			pointerId: t.pointerId
		}];
	}
	pointerCancel(e) {
		return this.cancel(e.pointerId, "pointercancel");
	}
	lostPointerCapture(e) {
		return this.cancel(e.pointerId, "lostpointercapture");
	}
	escape() {
		return this.active ? this.cancel(this.active.pointerId, "escape") : [];
	}
	cancel(e, t) {
		if (!this.active || this.active.pointerId !== e) return [];
		let n = this.active;
		return this.active = null, n.kind === "node" ? n.locked ? [{
			kind: "node-drag-cancel",
			nodeId: n.nodeId,
			pointerId: e,
			reason: t
		}] : [] : n.kind === "community-wash" ? n.cancelled ? [] : [{
			kind: "community-click-cancelled",
			communityId: n.communityId,
			pointerId: e,
			reason: t
		}] : n.locked ? [{
			kind: "blank-pan-cancel",
			pointerId: e,
			reason: t
		}] : [];
	}
}, ss = class {
	root;
	options;
	stateMachine;
	lastBlankDoubleClick = null;
	recentPointerDownTargets = [];
	destroyed = !1;
	constructor(e, t) {
		this.root = e, this.options = t, this.stateMachine = t.stateMachine || new os(), this.root.addEventListener("wheel", this.handleWheel, { passive: !1 }), this.root.addEventListener("pointerdown", this.handlePointerDown), this.root.addEventListener("pointermove", this.handlePointerMove), this.root.addEventListener("pointerup", this.handlePointerUp), this.root.addEventListener("pointercancel", this.handlePointerCancel), this.root.addEventListener("lostpointercapture", this.handleLostPointerCapture), this.root.addEventListener("click", this.handleClick), this.root.addEventListener("dblclick", this.handleDoubleClick);
	}
	destroy() {
		this.destroyed || (this.destroyed = !0, this.root.removeEventListener("wheel", this.handleWheel), this.root.removeEventListener("pointerdown", this.handlePointerDown), this.root.removeEventListener("pointermove", this.handlePointerMove), this.root.removeEventListener("pointerup", this.handlePointerUp), this.root.removeEventListener("pointercancel", this.handlePointerCancel), this.root.removeEventListener("lostpointercapture", this.handleLostPointerCapture), this.root.removeEventListener("click", this.handleClick), this.root.removeEventListener("dblclick", this.handleDoubleClick));
	}
	snapshot() {
		return this.stateMachine.snapshot();
	}
	escape() {
		let e = this.stateMachine.escape();
		return this.emitActiveState(), e;
	}
	handleWheel = (e) => {
		let t = this.screenPointFromMouseEvent(e), n = ns(this.graphTargetForEvent(e.target, t), e);
		n.intent === "zoom" && (e.preventDefault(), this.options.onWheelZoom(e, n, t));
	};
	handlePointerDown = (e) => {
		if (e.button !== 0) return;
		let t = this.screenPointFromMouseEvent(e), n = as(this.graphTargetForEvent(e.target, t));
		n.intent !== "blocked" && (this.recordPointerDown(n.target, t, e.timeStamp), e.preventDefault(), this.options.onPointerDown?.(e, n), this.stateMachine.pointerDown(n, this.pointerEventFromPointerEvent(e)), this.emitActiveState(), this.root.setPointerCapture(e.pointerId));
	};
	handlePointerMove = (e) => {
		this.stateMachine.snapshot() && e.preventDefault(), this.applyIntents(this.stateMachine.pointerMove(this.pointerEventFromPointerEvent(e)), e);
	};
	handlePointerUp = (e) => {
		this.stateMachine.snapshot() && e.preventDefault(), this.applyIntents(this.stateMachine.pointerUp(this.pointerEventFromPointerEvent(e)), e), this.root.hasPointerCapture(e.pointerId) && this.root.releasePointerCapture(e.pointerId);
	};
	handlePointerCancel = (e) => {
		this.stateMachine.snapshot() && e.preventDefault(), this.applyIntents(this.stateMachine.pointerCancel({ pointerId: e.pointerId }), e), this.root.hasPointerCapture(e.pointerId) && this.root.releasePointerCapture(e.pointerId);
	};
	handleLostPointerCapture = (e) => {
		let t = Number(e.pointerId);
		Number.isFinite(t) && this.applyIntents(this.stateMachine.lostPointerCapture({ pointerId: t }), null);
	};
	handleClick = (e) => {
		e.detail < 2 || this.triggerBlankDoubleClick(e);
	};
	handleDoubleClick = (e) => {
		this.isDuplicateBlankDoubleClick(e) || this.triggerBlankDoubleClick(e);
	};
	triggerBlankDoubleClick(e) {
		this.isTrueBlankDoubleClick(e) && (e.preventDefault(), e.stopPropagation(), this.lastBlankDoubleClick = {
			x: e.clientX,
			y: e.clientY,
			timeStamp: e.timeStamp
		}, this.options.onBlankDoubleClick?.(e));
	}
	isDuplicateBlankDoubleClick(e) {
		return this.lastBlankDoubleClick ? Math.abs(this.lastBlankDoubleClick.x - e.clientX) < 1 && Math.abs(this.lastBlankDoubleClick.y - e.clientY) < 1 && e.timeStamp - this.lastBlankDoubleClick.timeStamp < 500 : !1;
	}
	isTrueBlankDoubleClick(e) {
		let t = this.recentPointerDownTargets.filter((t) => e.timeStamp - t.timeStamp < 500);
		return t.length ? t.every((e) => e.target.kind === "graph-blank") : Zo(this.eventTarget(e.target)).kind === "graph-blank";
	}
	recordPointerDown(e, t, n) {
		this.recentPointerDownTargets.push({
			target: e,
			x: t.x,
			y: t.y,
			timeStamp: n
		}), this.recentPointerDownTargets.length > 8 && this.recentPointerDownTargets.shift();
	}
	applyIntents(e, t) {
		this.options.onGestureIntents(e, t), this.emitActiveState();
	}
	emitActiveState() {
		this.options.onActiveStateChange?.(this.stateMachine.snapshot());
	}
	eventTarget(e) {
		return this.options.targetFromEventTarget ? this.options.targetFromEventTarget(e) : e;
	}
	graphTargetForEvent(e, t) {
		let n = Zo(this.eventTarget(e));
		return es(n) || n.kind === "aggregation-container" ? n : this.options.graphTargetFromScreenPoint?.(t) || n;
	}
	pointerEventFromPointerEvent(e) {
		return {
			pointerId: e.pointerId,
			screenPoint: this.screenPointFromMouseEvent(e),
			shiftKey: e.shiftKey
		};
	}
	screenPointFromMouseEvent(e) {
		return pn({
			x: e.clientX,
			y: e.clientY
		}, this.root.getBoundingClientRect());
	}
};
function cs(e, t) {
	return typeof e.closest == "function" ? e.closest(t) : null;
}
function ls(e, ...t) {
	for (let n of t) {
		let t = e.dataset?.[n];
		if (t) return t;
	}
	return null;
}
function us(e) {
	if (e.isContentEditable) return !0;
	let t = e.tagName?.toLowerCase();
	if (!t) return !1;
	if (t === "textarea" || t === "select") return !0;
	if (t !== "input") return !1;
	let n = String(e.type || "text").toLowerCase();
	return ![
		"button",
		"checkbox",
		"radio",
		"range",
		"submit",
		"reset"
	].includes(n);
}
function ds(e) {
	return e ? (e.kind === "node" || e.kind, {
		...e,
		startScreenPoint: Z(e.startScreenPoint),
		lastScreenPoint: Z(e.lastScreenPoint)
	}) : null;
}
function Z(e) {
	return {
		x: hs(e.x, 0),
		y: hs(e.y, 0)
	};
}
function fs(e, t) {
	return {
		x: hs(t.x, 0) - hs(e.x, 0),
		y: hs(t.y, 0) - hs(e.y, 0)
	};
}
function ps(e, t) {
	return Math.hypot(hs(t.x, 0) - hs(e.x, 0), hs(t.y, 0) - hs(e.y, 0));
}
function ms(e, t) {
	let n = hs(e, t);
	return n > 0 ? n : t;
}
function hs(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/hit-testing.ts
function gs(e) {
	let t = null, n = null;
	function r() {
		let r = e.graph();
		return t !== r || !n ? i(r) : n;
	}
	function i(r = e.graph()) {
		let i = St(_s(r));
		return t = r, n = i, i;
	}
	return {
		targetFromScreenPoint(t) {
			let n = e.graph(), i = vn(t, e.viewport(), e.viewportSize(), n.worldBounds);
			return is(r().hitTest(i));
		},
		index: r,
		refresh: i
	};
}
function _s(e) {
	return {
		nodes: e.nodes,
		edges: e.edges,
		communities: e.communities,
		aggregationContainers: e.aggregationContainers
	};
}
//#endregion
//#region src/render/keyboard.ts
function vs(e) {
	let t = e.key.toLowerCase();
	return e.graphFocused || e.activeGesture ? (e.metaKey || e.ctrlKey) && t === "f" ? e.graphFocused && !e.textEditingTarget ? "open-search" : "blocked" : e.key === "Escape" ? e.graphFocused && e.searchActive ? "close-search" : e.graphFocused && e.toolbarOpen ? "close-toolbar" : e.activeGesture ? "cancel-active-gesture" : e.graphFocused && e.interactionActive ? "clear-interaction" : "blocked" : "blocked" : "blocked";
}
function ys(e) {
	if (!e) return !1;
	let t = e.tagName.toLowerCase();
	if (t === "textarea") return !0;
	if (t === "input") {
		let t = e.type.toLowerCase();
		return ![
			"button",
			"checkbox",
			"radio",
			"range",
			"submit",
			"reset"
		].includes(t);
	}
	return typeof HTMLElement < "u" && e instanceof HTMLElement && e.isContentEditable;
}
//#endregion
//#region src/render/node-drag-lifecycle.ts
function bs(e) {
	e.finalWorldPoint && e.simulation.dragTo(e.nodeId, Ts(e.finalWorldPoint));
	let t = e.simulation.endDrag({ keepFixed: !0 }), n = ws(t.positions, e.nodeId), r = e.pinState.pin(e.nodeId, n);
	return {
		kind: "committed",
		nodeId: e.nodeId,
		pinPosition: n,
		positions: t.positions,
		pins: r.pins,
		pinnedNodeIds: r.pinnedNodeIds
	};
}
function xs(e) {
	let t = Ts(e.session.startWorldPoint), n = e.simulation.endDrag({ restore: {
		position: t,
		fixed: e.session.wasPinned
	} }), r = e.pinState.snapshot();
	return {
		kind: "cancelled",
		nodeId: e.session.nodeId,
		restoredPosition: t,
		restoredFixed: e.session.wasPinned,
		positions: n.positions,
		pins: r.pins,
		pinnedNodeIds: r.pinnedNodeIds
	};
}
function Ss(e) {
	let t = Ts(e.finalWorldPoint || e.startWorldPoint), n = e.pinState.pin(e.nodeId, t);
	return {
		kind: "committed",
		nodeId: e.nodeId,
		pinPosition: t,
		positions: {
			...e.currentPositions,
			[e.nodeId]: {
				x: t.x,
				y: t.y
			}
		},
		pins: n.pins,
		pinnedNodeIds: n.pinnedNodeIds
	};
}
function Cs(e) {
	let t = Ts(e.startWorldPoint), n = e.wasPinned ? e.pinState.snapshot() : e.pinState.unpin(e.nodeId);
	return {
		kind: "cancelled",
		nodeId: e.nodeId,
		restoredPosition: t,
		restoredFixed: e.wasPinned,
		positions: {
			...e.currentPositions,
			[e.nodeId]: {
				x: t.x,
				y: t.y
			}
		},
		pins: n.pins,
		pinnedNodeIds: n.pinnedNodeIds
	};
}
function ws(e, t) {
	let n = e[t];
	if (!n) throw Error(`Cannot finish drag for unknown graph node: ${t}`);
	return Ts(n);
}
function Ts(e) {
	return {
		x: Es(e.x, 0),
		y: Es(e.y, 0)
	};
}
function Es(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/search.ts
function Ds(e, t, n) {
	let r = n ?? Te(e), i = t.trim(), a = i ? De(r, i) : [], o = new Set(a);
	return {
		query: i,
		matchIds: a,
		nodes: e.map((e) => ({
			id: e.id,
			searchState: i ? o.has(e.id) ? "match" : "faded" : "none"
		})),
		searchIndex: r
	};
}
function Os(e, t) {
	if (!e.length) return {
		id: null,
		index: -1
	};
	let n = ((t ? e.indexOf(t) : -1) + 1) % e.length;
	return {
		id: e[n],
		index: n
	};
}
function ks(e, t) {
	if (!e.length) return {
		id: null,
		index: -1
	};
	let n = t ? e.indexOf(t) : -1, r = n <= 0 ? e.length - 1 : n - 1;
	return {
		id: e[r],
		index: r
	};
}
//#endregion
//#region src/render/simulation-bridge.ts
function As(e) {
	let t = vn(e.pointerScreenPoint, e.viewport, e.viewportSize, e.worldBounds), n = Ms(e.nodeWorldPoint);
	return {
		pointerWorldPoint: t,
		grabOffset: {
			x: t.x - n.x,
			y: t.y - n.y
		},
		targetWorldPoint: n
	};
}
function js(e) {
	let t = vn(e.pointerScreenPoint, e.viewport, e.viewportSize, e.worldBounds), n = Ms(e.grabOffset);
	return {
		x: t.x - n.x,
		y: t.y - n.y
	};
}
function Ms(e) {
	return {
		x: Ns(e.x, 0),
		y: Ns(e.y, 0)
	};
}
function Ns(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/controller.ts
function Ps(e, t) {
	function n() {
		return new ss(e.root, {
			stateMachine: e.gestureMachine,
			targetFromEventTarget: L,
			graphTargetFromScreenPoint: e.hitTargetResolver.targetFromScreenPoint,
			onWheelZoom: (n, r, i) => {
				t.setViewportAnimating(!1), t.setInteractionDegraded(!0, { restoreDelayMs: 200 }), e.viewportCommitter.schedule(xo(e.runtimeState.snapshot().viewport, {
					deltaY: n.deltaY,
					deltaMode: n.deltaMode
				}, i, t.viewportSize(), { worldBounds: e.graph.worldBounds }), { lightweight: !0 });
			},
			onPointerDown: (n, r) => {
				r.intent !== "node-drag-candidate" && e.rendererSurface.focusRoot({ preventScroll: !0 }), t.setViewportAnimating(!1), t.setInteractionDegraded(!0, { restoreDelayMs: 200 });
			},
			onGestureIntents: i,
			onActiveStateChange: ee,
			onBlankDoubleClick: () => {
				P();
			}
		});
	}
	function r(t) {
		let n = vs({
			key: t.key,
			ctrlKey: t.ctrlKey,
			metaKey: t.metaKey,
			graphFocused: x(),
			activeGesture: !!e.gestureMachine.snapshot(),
			textEditingTarget: ys(e.ownerDocument.activeElement),
			searchActive: !!(e.searchOpen || e.searchQuery || e.searchFocusedNodeId),
			toolbarOpen: Yi(e.toolbarPanelState),
			interactionActive: y()
		});
		if (n === "blocked") return;
		if (n === "open-search") {
			t.preventDefault(), S();
			return;
		}
		if (t.preventDefault(), t.stopPropagation(), n === "close-search") {
			O();
			return;
		}
		if (n === "close-toolbar") {
			k();
			return;
		}
		if (n === "cancel-active-gesture") {
			let t = e.gestureMachine.escape();
			t.length && (i(t, null), ee());
			return;
		}
		let r = e.runtimeState.snapshot();
		if (r.selection || r.hover || e.searchFocusedNodeId || e.previewTimer || e.root.dataset.focus) {
			h();
			return;
		}
		if (r.focus) {
			P();
			return;
		}
		_();
	}
	function i(n, r) {
		for (let r of n) switch (r.kind) {
			case "node-click":
				r.nodeId && e.rendererSurface.focusNode(r.nodeId, { preventScroll: !0 }), r.nodeId && a(r.nodeId, r.additive);
				break;
			case "node-drag-start":
				r.nodeId && l(r.nodeId, r.screenPoint), t.setInteractionDegraded(!0, { restoreDelayMs: 220 });
				break;
			case "node-drag-move":
				r.nodeId && u(r.nodeId, r.pointerId, r.screenPoint), t.setInteractionDegraded(!0, { restoreDelayMs: 220 });
				break;
			case "node-drag-end":
				r.nodeId && d(r.nodeId, r.pointerId, r.screenPoint), t.setInteractionDegraded(!0, { restoreDelayMs: 160 });
				break;
			case "node-drag-cancel":
				r.nodeId && f(r.nodeId, r.pointerId), t.setInteractionDegraded(!1);
				break;
			case "community-click":
				r.communityId && A(r.communityId);
				break;
			case "community-click-cancelled": break;
			case "blank-click":
				m();
				break;
			case "blank-pan-start":
				e.rendererSurface.setViewportDragging(!0), t.setInteractionDegraded(!0, { restoreDelayMs: 220 });
				break;
			case "blank-pan-move":
				e.rendererSurface.setViewportDragging(!0), t.setInteractionDegraded(!0, { restoreDelayMs: 220 }), e.viewportCommitter.schedule(So(e.runtimeState.snapshot().viewport, r.delta, t.viewportSize(), { worldBounds: e.graph.worldBounds }), { lightweight: !0 });
				break;
			case "blank-pan-end":
			case "blank-pan-cancel":
				e.rendererSurface.setViewportDragging(!1), t.setInteractionDegraded(!0, { restoreDelayMs: 160 });
				break;
		}
	}
	function a(n, r) {
		let i = r ? Ls(n, Is(e.runtimeState.snapshot().selection)) : {
			kind: "node",
			id: n
		};
		e.runtimeState.setSelection(i, "selection-panel"), e.callbacks.onSelectionInput?.(i), t.render(), c(n);
	}
	function o(t) {
		return !!e.graph.nodes.find((e) => e.id === t);
	}
	function s(n, r) {
		let i = e.graph.nodes.find((e) => e.id === n);
		if (!i) return !1;
		let a = r === "fix" ? e.pinState.pin(n, re(n) || i.point) : e.pinState.unpin(n);
		return e.runtimeState.setPins(a.pins), e.simulation?.setFixed(n, r === "fix" ? Ua(e.graph, a.pins)[n] || i.point : null), t.render(), e.callbacks.onPinsChanged?.(a.pins), !0;
	}
	function c(t) {
		e.rendererSurface.focusNode(t, { preventScroll: !0 });
	}
	function l(t, n) {
		let r = e.simulation;
		if (!r) {
			e.graph.focus?.kind === "community" ? (e.rendererSurface.setNodeDragging(t, !0), e.rendererSurface.setDragTarget(t), e.callbacks.onDragActiveChange?.(!0)) : e.runtimeState.setActiveGesture(null);
			return;
		}
		let i = e.runtimeState.snapshot().activeGesture;
		if (i?.kind !== "node-drag" || i.nodeId !== t) return;
		let a = i.grabOffset;
		e.rendererSurface.setNodeDragging(t, !0), r.beginDrag(t), r.dragTo(t, V(n, a)), e.rendererSurface.setDragTarget(t), e.callbacks.onDragActiveChange?.(!0);
	}
	function u(n, r, i) {
		let a = e.simulation;
		if (!a) {
			if (e.graph.focus?.kind === "community" && B(n, r, !0)) {
				let a = V(i, R(n, r));
				t.applyMotionFrame({
					...e.runtimeState.snapshot().positions,
					[n]: a
				});
			}
			return;
		}
		B(n, r, !0) && a.dragTo(n, V(i, R(n, r)));
	}
	function d(t, n, r) {
		let i = e.simulation;
		if (!i) {
			if (e.graph.focus?.kind !== "community" || !B(t, n, !0)) return;
			let i = te(t, n);
			p(t, Ss({
				nodeId: t,
				startWorldPoint: i.startWorldPoint,
				wasPinned: i.wasPinned,
				finalWorldPoint: V(r, R(t, n)),
				currentPositions: e.runtimeState.snapshot().positions,
				pinState: e.pinState
			}));
			return;
		}
		B(t, n, !0) && p(t, bs({
			nodeId: t,
			simulation: i,
			pinState: e.pinState,
			finalWorldPoint: V(r, R(t, n))
		}));
	}
	function f(t, n) {
		let r = e.simulation;
		if (!r) {
			if (e.graph.focus?.kind !== "community" || !B(t, n, !0)) return;
			let r = te(t, n);
			p(t, Cs({
				nodeId: t,
				startWorldPoint: r.startWorldPoint,
				wasPinned: r.wasPinned,
				currentPositions: e.runtimeState.snapshot().positions,
				pinState: e.pinState
			}));
			return;
		}
		B(t, n, !0) && p(t, xs({
			session: te(t, n),
			simulation: r,
			pinState: e.pinState
		}));
	}
	function p(n, r) {
		e.runtimeState.setPins(r.pins), t.applyMotionFrame(r.positions), t.markPinnedNodes(r.pinnedNodeIds), e.callbacks.onPinsChanged?.(r.pins), e.rendererSurface.setNodeDragging(n, !1), e.rendererSurface.setDragTarget(null), e.runtimeState.setActiveGesture(null), e.callbacks.onDragActiveChange?.(!1);
	}
	function m() {
		if (e.rendererSurface.setViewportDragging(!1), Yi(e.toolbarPanelState)) {
			k();
			return;
		}
		b() && h();
	}
	function h() {
		g(), t.setGraphHover(null), e.runtimeState.setSelection(null), e.rendererSurface.setFocusDataset(!1), e.callbacks.onSelectionClearRequested?.(), t.render();
	}
	function g() {
		e.searchFocusedNodeId = null, e.previewTimer &&= (clearTimeout(e.previewTimer), null);
	}
	function _() {
		g(), e.runtimeState.clearInteraction(), e.rendererSurface.setFocusDataset(!1), e.callbacks.onSelectionClearRequested?.(), t.render();
	}
	function v() {
		g(), e.rendererSurface.clearNodeDragging(), e.rendererSurface.setDragTarget(null), e.rendererSurface.setViewportDragging(!1), e.simulation?.endDrag(), e.gestureMachine.escape(), e.runtimeState.setHover(null), e.callbacks.onDragActiveChange?.(!1);
	}
	function y() {
		let t = e.runtimeState.snapshot();
		return !!(t.selection || t.focus || e.root.dataset.focus);
	}
	function b() {
		let t = e.runtimeState.snapshot();
		return !!(t.selection || t.hover || e.searchFocusedNodeId || e.previewTimer);
	}
	function x() {
		let t = e.ownerDocument.activeElement;
		return !!(t === e.root || t && e.root.contains(t));
	}
	function S() {
		e.searchOpen = !0, e.rendererSurface.setSearchOpen(!0), e.dom.searchInput && (e.dom.searchInput.focus(), e.dom.searchInput.select());
	}
	function C(n) {
		n !== e.searchQuery && (e.searchFocusedNodeId = null), e.searchQuery = n, t.setInteractionDegraded(!!n, { restoreDelayMs: 180 });
		let r = Ds(e.data.nodes, e.searchQuery, e.searchIndex);
		if (e.searchIndex = r.searchIndex, r.matchIds.includes(e.searchFocusedNodeId || "") || (e.searchFocusedNodeId = null), e.rendererSurface.setSearchState({
			query: r.query,
			focusedNodeId: e.searchFocusedNodeId,
			nodes: r.nodes
		}), e.dom.searchInput && e.dom.searchInput.value !== e.searchQuery && (e.dom.searchInput.value = e.searchQuery), e.dom.searchStatusElement) {
			let t = e.searchFocusedNodeId ? r.matchIds.indexOf(e.searchFocusedNodeId) : -1;
			e.dom.searchStatusElement.textContent = r.query ? t >= 0 ? `${t + 1}/${r.matchIds.length}` : `${r.matchIds.length} 个结果` : "输入关键词";
		}
		e.callbacks.onVisibilityStateChange?.({
			searchQuery: r.query,
			searchResultIds: r.matchIds,
			typeFilters: e.typeFilters,
			temporaryObject: e.temporaryObject
		});
	}
	function w() {
		E("next");
	}
	function T() {
		E("previous");
	}
	function E(n) {
		let r = Ds(e.data.nodes, e.searchQuery, e.searchIndex);
		e.searchIndex = r.searchIndex;
		let i = n === "next" ? Os(r.matchIds, e.searchFocusedNodeId) : ks(r.matchIds, e.searchFocusedNodeId);
		if (e.searchFocusedNodeId = i.id, !i.id) {
			C(e.searchQuery);
			return;
		}
		let a = e.graph.nodes.find((e) => e.id === i.id);
		a && (t.setViewportAnimating(!0), e.viewportCommitter.schedule(wo(a.point, e.runtimeState.snapshot().viewport, t.viewportSize(), { worldBounds: e.graph.worldBounds }))), C(e.searchQuery);
	}
	function D() {
		let t = Ds(e.data.nodes, e.searchQuery, e.searchIndex);
		e.searchIndex = t.searchIndex;
		let n = e.searchFocusedNodeId && t.matchIds.includes(e.searchFocusedNodeId) ? e.searchFocusedNodeId : Os(t.matchIds, e.searchFocusedNodeId).id;
		if (e.searchFocusedNodeId = n, !n) {
			C(e.searchQuery);
			return;
		}
		C(e.searchQuery), a(n, !1);
	}
	function O() {
		e.searchOpen = !1, e.searchFocusedNodeId = null, e.rendererSurface.setSearchOpen(!1), t.setInteractionDegraded(!1), C(""), e.rendererSurface.focusRoot({ preventScroll: !0 });
	}
	function k() {
		e.toolbarPanelState = Xi(e.toolbarPanelState), qi(e.ownerDocument.defaultView?.localStorage, e.toolbarPanelState), e.dom.toolbarPanelElement && (e.dom.toolbarPanelElement.dataset.state = e.toolbarPanelState), e.dom.toolbarElement && (e.dom.toolbarElement.dataset.panel = e.toolbarPanelState), e.root.dataset.toolbarPanel = e.toolbarPanelState, e.root.dataset.toolbarOpen = "false", e.toolbarContainer.dataset.toolbarPanel = e.toolbarPanelState, e.toolbarContainer.dataset.toolbarOpen = "false";
	}
	function A(n) {
		let r = {
			kind: "community",
			id: n
		};
		e.runtimeState.setSelection(r, "selection-panel"), e.callbacks.onSelectionInput?.(r), t.render();
	}
	function j(t) {
		e.runtimeState.setHover(t ? {
			kind: "community",
			id: t
		} : null);
	}
	function M(n) {
		e.runtimeState.setFocus({
			kind: "community",
			id: n
		}), t.render();
		let r = e.graph.nodes.map((e) => e.point);
		r.length && (t.setViewportAnimating(!0), e.viewportCommitter.schedule(Co(r, t.viewportSize(), {
			maxScale: t.focusFitMaxScale,
			worldBounds: e.graph.worldBounds
		})));
	}
	function N() {
		t.setGraphHover(null), e.runtimeState.setFocus(null), e.runtimeState.setActiveGesture(null), e.rendererSurface.setFocusDataset(!1), e.callbacks.onViewReset?.(), t.render(), t.setViewportAnimating(!0), e.viewportCommitter.schedule(Co(e.graph.nodes.map((e) => e.point), t.viewportSize(), { worldBounds: e.graph.worldBounds }));
	}
	function P() {
		if (e.callbacks.onGlobalResetRequested) {
			e.callbacks.onGlobalResetRequested();
			return;
		}
		N();
	}
	function F() {
		e.searchFocusedNodeId = null, t.setGraphHover(null), e.runtimeState.setSelection(null), e.rendererSurface.setFocusDataset(!1), e.callbacks.onSelectionClearRequested?.(), t.render();
	}
	function ee() {
		let t = e.gestureMachine.snapshot();
		e.runtimeState.setActiveGesture(I(t));
	}
	function I(e) {
		return e ? e.kind === "node" ? e.nodeId ? {
			kind: "node-drag",
			pointerId: e.pointerId,
			nodeId: e.nodeId,
			grabOffset: z(e),
			startWorldPoint: ne(e.nodeId),
			wasPinned: ie(e.nodeId),
			locked: e.locked
		} : null : e.kind === "community-wash" ? e.communityId ? {
			kind: "community-click",
			pointerId: e.pointerId,
			communityId: e.communityId,
			locked: e.locked
		} : null : {
			kind: "viewport-pan",
			pointerId: e.pointerId,
			lastScreenPoint: e.lastScreenPoint,
			locked: e.locked
		} : null;
	}
	function L(e) {
		return Fs(e) ? e : null;
	}
	function te(t, n) {
		let r = e.runtimeState.snapshot().activeGesture;
		return r?.kind === "node-drag" && r.nodeId === t && r.pointerId === n ? {
			pointerId: n,
			nodeId: t,
			startWorldPoint: r.startWorldPoint,
			wasPinned: r.wasPinned
		} : {
			pointerId: n,
			nodeId: t,
			startWorldPoint: e.graph.nodes.find((e) => e.id === t)?.point || {
				x: 0,
				y: 0
			},
			wasPinned: e.pinState.isPinned(t)
		};
	}
	function R(t, n) {
		let r = e.runtimeState.snapshot().activeGesture;
		return r?.kind === "node-drag" && r.nodeId === t && r.pointerId === n ? r.grabOffset : {
			x: 0,
			y: 0
		};
	}
	function z(t) {
		let n = e.runtimeState.snapshot().activeGesture;
		return n?.kind === "node-drag" && n.nodeId === t.nodeId && n.pointerId === t.pointerId ? n.grabOffset : t.nodeId ? ae(t).grabOffset : {
			x: 0,
			y: 0
		};
	}
	function ne(t) {
		let n = e.runtimeState.snapshot().activeGesture;
		return n?.kind === "node-drag" && n.nodeId === t ? n.startWorldPoint : Ua(e.graph, e.runtimeState.snapshot().pins)[t] || e.graph.nodes.find((e) => e.id === t)?.point || {
			x: 0,
			y: 0
		};
	}
	function re(t) {
		return e.runtimeState.snapshot().positions[t] || Ua(e.graph, e.runtimeState.snapshot().pins)[t] || e.graph.nodes.find((e) => e.id === t)?.point || null;
	}
	function ie(t) {
		let n = e.runtimeState.snapshot().activeGesture;
		return n?.kind === "node-drag" && n.nodeId === t ? n.wasPinned : !!Ua(e.graph, e.runtimeState.snapshot().pins)[t] || e.pinState.isPinned(t);
	}
	function ae(n) {
		if (!n.nodeId) return {
			grabOffset: {
				x: 0,
				y: 0
			},
			startWorldPoint: {
				x: 0,
				y: 0
			},
			wasPinned: !1
		};
		let r = e.graph.nodes.find((e) => e.id === n.nodeId);
		if (!r) return {
			grabOffset: {
				x: 0,
				y: 0
			},
			startWorldPoint: {
				x: 0,
				y: 0
			},
			wasPinned: !1
		};
		let i = As({
			nodeWorldPoint: r.point,
			pointerScreenPoint: n.startScreenPoint,
			viewport: e.runtimeState.snapshot().viewport,
			viewportSize: t.viewportSize(),
			worldBounds: e.graph.worldBounds
		}), a = Ua(e.graph, e.runtimeState.snapshot().pins)[n.nodeId];
		return {
			grabOffset: i.grabOffset,
			startWorldPoint: a || i.targetWorldPoint,
			wasPinned: !!a || e.pinState.isPinned(n.nodeId)
		};
	}
	function B(t, n, r) {
		let i = e.runtimeState.snapshot().activeGesture;
		return i?.kind !== "node-drag" || i.nodeId !== t || i.pointerId !== n ? !1 : r === void 0 ? !0 : i.locked === r;
	}
	function V(n, r) {
		return js({
			pointerScreenPoint: n,
			viewport: e.runtimeState.snapshot().viewport,
			viewportSize: t.viewportSize(),
			worldBounds: e.graph.worldBounds,
			grabOffset: r
		});
	}
	return {
		bindViewportHandlers: n,
		onGestureIntents: i,
		syncRuntimeGestureState: ee,
		handleDocumentKeydown: r,
		isGraphKeyboardFocusActive: x,
		handleNodeClick: a,
		handleNodeDoubleClick: o,
		setNodeFixed: s,
		handleBlankClick: m,
		openSearch: S,
		applySearchQuery: C,
		focusNextSearchResult: w,
		focusPreviousSearchResult: T,
		activateSearchResult: D,
		closeSearch: O,
		selectCommunity: A,
		setCommunityHover: j,
		focusCommunity: M,
		resetViewState: N,
		requestGlobalReset: P,
		retreatFocusedView: F,
		clearSelectionOnly: h,
		closeToolbarPanel: k,
		clearInteractionState: _,
		clearTransientInteractionForDataRefresh: v,
		hasInteractionState: y
	};
}
function Fs(e) {
	if (!e || typeof e != "object") return !1;
	let t = e;
	return typeof t.closest == "function" || !!t.dataset || typeof t.tagName == "string";
}
function Is(e) {
	return e ? e.kind === "node" || e.kind === "neighbors" ? [e.id] : e.kind === "nodes" ? e.ids : [] : [];
}
function Ls(e, t) {
	let n = new Set(t);
	n.has(e) ? n.delete(e) : n.add(e);
	let r = Array.from(n);
	return r.length === 1 ? {
		kind: "node",
		id: r[0]
	} : {
		kind: "nodes",
		ids: r
	};
}
//#endregion
//#region src/render/nodes.ts
function Rs(e, t, n, r = {}) {
	let i = e.createElement("button");
	if (i.className = "node", t.unavailable && i.classList.add("is-disabled"), zs(i, t.displayMode), t.previewStart && i.classList.add("is-preview-start"), t.labelVisible || i.classList.add("is-label-hidden"), i.type = "button", i.dataset.id = t.id, i.dataset.type = t.type, i.dataset.community = t.community, i.dataset.visualRole = t.visualRole, i.dataset.startNode = t.startNode ? "true" : "false", i.dataset.previewStart = t.previewStart ? "true" : "false", i.dataset.coreAnchor = t.coreAnchor ? "true" : "false", i.dataset.temporaryBoost = t.temporaryBoost > 0 ? "true" : "false", i.dataset.interactionLabelVisible = t.interactionLabelVisible ? "true" : "false", i.dataset.traceable = t.selected || t.coreAnchor || t.interactionLabelVisible ? "true" : "false", i.dataset.worldX = String(t.point.x), i.dataset.worldY = String(t.point.y), i.dataset.communityMapTier = t.communityMapTier, i.dataset.communityMapImportance = String(t.communityMapImportance), i.style.left = `${t.x}%`, i.style.top = `${t.y}%`, i.title = t.label, i.setAttribute("aria-pressed", t.selected ? "true" : "false"), i.addEventListener("dblclick", (e) => {
		e.stopPropagation(), n.onNodeDoubleClick(t.id);
	}), i.addEventListener("pointerenter", () => n.onNodePreviewEnter(t.id)), i.addEventListener("pointerleave", () => n.onNodePreviewLeave()), i.addEventListener("focus", () => n.onNodePreviewEnter(t.id)), i.addEventListener("blur", () => n.onNodePreviewLeave()), Bs(i, t.id, n), r.communityMap) {
		i.dataset.labelSide = t.communityMapLabelSide, i.dataset.relationLabel = t.communityMapRelationLabel ? "true" : "false", i.style.setProperty("--node-size", `${t.communityMapDotSize}px`), i.style.setProperty("--node-community-color", t.communityColor);
		let n = e.createElement("span");
		n.className = "node-pin", n.setAttribute("aria-hidden", "true");
		let r = e.createElement("span");
		r.className = "dot-core", n.appendChild(r), i.appendChild(n);
	}
	let a = e.createElement("span");
	a.className = "node-kind", a.textContent = t.kind, i.appendChild(a);
	let o = e.createElement("span");
	o.className = "node-name", o.textContent = t.label, i.appendChild(o);
	let s = e.createElement("span");
	s.className = "node-meta";
	let c = e.createElement("i");
	return c.className = "spark", s.appendChild(c), s.append(t.unavailable ? "来源暂不可用" : String(Math.round(t.priority || t.weight || 0))), i.appendChild(s), i;
}
function zs(e, t) {
	e.classList.toggle("is-compact", t === "compact-card"), e.classList.toggle("is-point", t === "point"), e.classList.toggle("is-overview", t === "overview"), e.dataset.densityMode = t;
}
function Bs(e, t, n) {
	e.addEventListener("click", (e) => {
		e.detail === 0 && (e.stopPropagation(), n.onNodeClick(t, e.shiftKey));
	});
}
//#endregion
//#region src/render/aggregation-containers.ts
function Vs(e, t, n) {
	let r = e.createElement("button");
	r.type = "button", r.className = "aggregation-container", r.dataset.aggregationId = t.id, r.dataset.communityId = t.communityId ?? "", r.dataset.role = t.role, r.dataset.nodeCount = String(t.nodeCount), r.dataset.searchHitCount = String(t.searchHitCount), r.dataset.pinnedCount = String(t.pinnedCount), r.dataset.selectedCount = String(t.selectedCount), r.dataset.selected = t.selected ? "true" : "false", r.dataset.searchInside = t.searchHitCount > 0 ? "true" : "false", r.dataset.pinnedInside = t.pinnedCount > 0 ? "true" : "false", r.dataset.worldX = String(t.point.x), r.dataset.worldY = String(t.point.y), r.style.left = `${t.x}%`, r.style.top = `${t.y}%`, r.style.setProperty("--aggregation-color", t.color), r.style.setProperty("--aggregation-radius", `${t.radius}px`), r.title = t.label, r.setAttribute("aria-pressed", t.selected ? "true" : "false"), r.addEventListener("click", (e) => {
		e.stopPropagation(), n.onAggregationContainerClick(t);
	});
	let i = e.createElement("span");
	i.className = "aggregation-container-count", i.textContent = String(t.nodeCount), r.appendChild(i);
	let a = e.createElement("span");
	a.className = "aggregation-container-label", a.textContent = t.label, r.appendChild(a);
	let o = e.createElement("span");
	return o.className = "aggregation-container-markers", Hs(e, o, "命中", t.searchHitCount), Hs(e, o, "固定", t.pinnedCount), Hs(e, o, "选中", t.selectedCount), r.appendChild(o), r;
}
function Hs(e, t, n, r) {
	if (r <= 0) return;
	let i = e.createElement("span");
	i.className = "aggregation-container-marker", i.textContent = `${n} ${r}`, t.appendChild(i);
}
//#endregion
//#region src/render/community-washes.ts
var Us = "http://www.w3.org/2000/svg";
function Ws(e, t) {
	if (!t.wash) return null;
	let n = e.createElementNS(Us, "ellipse");
	return n.setAttribute("class", "community-wash"), n.setAttribute("cx", String(t.wash.cx)), n.setAttribute("cy", String(t.wash.cy)), n.setAttribute("rx", String(t.wash.rx)), n.setAttribute("ry", String(t.wash.ry)), n.setAttribute("fill", t.color), n.setAttribute("opacity", String(t.wash.opacity)), n.dataset.communityId = t.id, n.dataset.boundaryCertainty = t.boundaryCertainty, n.style.cursor = "pointer", n;
}
//#endregion
//#region src/render/edges.ts
var Gs = "http://www.w3.org/2000/svg";
function Ks(e, t, n) {
	let r = e.createElementNS(Gs, "path");
	r.setAttribute("d", t.path), r.setAttribute("class", `edge confidence-${t.confidence} ${t.relationClass}`), r.setAttribute("data-from", t.source), r.setAttribute("data-to", t.target), r.setAttribute("data-edge-id", t.id), r.setAttribute("data-confidence", t.confidence), r.setAttribute("data-relation-type", t.relationType), r.setAttribute("data-skeleton", t.skeleton ? "true" : "false"), r.setAttribute("data-traceable", t.traceable ? "true" : "false"), r.setAttribute("data-community-map-layer", t.communityMapLayer), r.setAttribute("aria-label", `${t.relationType} · ${qs(t.confidence)}`), r.setAttribute("tabindex", "0"), r.addEventListener("pointerenter", () => n.onEdgePreviewEnter(t.id)), r.addEventListener("pointerleave", () => n.onEdgePreviewLeave()), r.addEventListener("focus", () => n.onEdgePreviewEnter(t.id)), r.addEventListener("blur", () => n.onEdgePreviewLeave()), r.style.strokeWidth = String(t.strokeWidth), r.style.setProperty("--edge-map-width", `${t.strokeWidth}px`), r.style.opacity = String(t.opacity);
	let i = e.createElementNS(Gs, "title");
	return i.textContent = `${t.relationType} · ${qs(t.confidence)}`, r.appendChild(i), r;
}
function qs(e) {
	switch (e) {
		case "inferred": return "推断";
		case "ambiguous": return "待确认";
		case "unverified": return "未验证";
		default: return "原文";
	}
}
//#endregion
//#region src/render/minimap.ts
var Js = "http://www.w3.org/2000/svg";
function Ys(e, t) {
	let n = e.createElement("div");
	n.className = "mini-map";
	let r = e.createElementNS(Js, "svg");
	r.setAttribute("viewBox", "0 0 160 54"), r.setAttribute("aria-hidden", "true");
	let i = e.createElementNS(Js, "path");
	i.setAttribute("d", t.path), i.setAttribute("fill", "none"), i.setAttribute("stroke", "var(--line)"), i.setAttribute("stroke-width", "1.4"), r.appendChild(i);
	let a = e.createElementNS(Js, "rect");
	a.setAttribute("class", "mini-map-viewport"), a.setAttribute("data-mini-map-viewport", "true"), a.setAttribute("x", "0"), a.setAttribute("y", "0"), a.setAttribute("width", "160"), a.setAttribute("height", "54"), r.appendChild(a);
	let o = /* @__PURE__ */ new Map();
	for (let n of t.nodes) {
		let t = e.createElementNS(Js, "circle");
		t.setAttribute("cx", String(n.x)), t.setAttribute("cy", String(n.y)), t.setAttribute("r", String(n.r)), t.setAttribute("fill", n.fill), n.selected && t.classList.add("is-selected"), r.appendChild(t), o.set(n.id, t);
	}
	return n.appendChild(r), {
		element: n,
		nodeElements: o,
		viewportElement: a
	};
}
//#endregion
//#region src/render/dom-svg-renderer.ts
var Xs = "http://www.w3.org/2000/svg";
function Zs(e) {
	let { ownerDocument: t, root: n, graph: r, handlers: i } = e;
	n.replaceChildren(), n.dataset.theme = e.theme, n.dataset.baseDensity = r.densityMode, n.dataset.interactionMode = n.dataset.interactionMode || "idle", n.dataset.interactionMaxUpdates = String(r.interaction.maxUpdatedObjects), n.dataset.interactionUpdatedObjects = String(r.interaction.updatedObjects), n.dataset.interactionHiddenObjects = String(r.interaction.hiddenObjects), n.dataset.interactionPreservedNodes = String(r.interaction.preservedNodeIds.length), n.dataset.communityQuality = r.communityQuality.level, n.dataset.communityBoundaryCertainty = r.communityQuality.boundaryCertainty, n.dataset.communityAuxiliaryViews = r.communityQuality.auxiliaryViews.map((e) => e.id).join(","), n.dataset.communityMapState = r.focus?.kind === "community" ? "lightweight" : "none", n.dataset.communityMapMotion = r.communityMap.motionMode, n.dataset.communityMapSourceCommunityId = r.communityMap.sourceCommunityId || "", n.dataset.communityMapCommunityId = r.communityMap.current?.communityId || "", n.dataset.communityMapLabelLimit = String(r.communityMap.current?.labelBudget.limit ?? 0), n.dataset.communityMapVisibleLabels = String(r.communityMap.current?.labelBudget.visible ?? 0), n.dataset.communityMapSkeletonEdges = String(r.communityMap.current?.edgeLayers.skeleton ?? 0), n.dataset.communityMapRelatedEdges = String(r.communityMap.current?.edgeLayers.related ?? 0), n.dataset.communityMapBackgroundEdges = String(r.communityMap.current?.edgeLayers.background ?? 0), n.dataset.communityMapBounds = r.communityMap.current ? JSON.stringify(r.communityMap.current.layout.bounds) : "";
	let a = ec(), o = t.createElement("div");
	o.className = "graph-content-layer", o.dataset.viewportLayer = "true", a.contentLayer = o;
	let s = t.createElementNS(Xs, "svg");
	s.setAttribute("class", "llm-wiki-graph-svg"), s.dataset.graphBlank = "true", $s(s, r), s.setAttribute("preserveAspectRatio", "none"), s.setAttribute("aria-hidden", "true"), a.svgElement = s;
	let c = t.createElementNS(Xs, "g");
	c.setAttribute("class", "community-wash-layer");
	for (let e of r.communities) {
		let n = Ws(t, e);
		n && (c.appendChild(n), a.communityWashElements.set(e.id, n));
	}
	s.appendChild(c);
	let l = t.createElementNS(Xs, "g");
	l.setAttribute("class", "edge-layer");
	for (let e of r.edges) {
		let n = Ks(t, e, i);
		l.appendChild(n), a.edgeElements.set(e.id, n);
	}
	s.appendChild(l), o.appendChild(s);
	let u = t.createElement("div");
	u.className = "node-layer";
	for (let e of r.aggregationContainers) {
		let n = Vs(t, e, i);
		a.aggregationContainerElements.set(e.id, n), u.appendChild(n);
	}
	for (let e of r.nodes) {
		let n = Rs(t, e, i, { communityMap: r.focus?.kind === "community" });
		a.nodeElements.set(e.id, n), a.basePoints.set(e.id, e.point), u.appendChild(n);
	}
	o.appendChild(u), n.appendChild(o);
	let d = t.createElement("aside");
	d.className = "graph-hover-preview", d.dataset.state = "closed", d.setAttribute("aria-live", "polite"), n.appendChild(d), a.previewElement = d;
	let f = Qs(t, r);
	f && n.appendChild(f);
	let p = Ys(t, r.minimap);
	if (a.miniViewportElement = p.viewportElement, a.miniNodeElements = p.nodeElements, n.appendChild(p.element), !e.hasHostReader) {
		let e = t.createElement("aside");
		e.className = "graph-reader", e.dataset.state = r.selectedNodeId ? "open" : "closed", n.appendChild(e), a.readerElement = e;
		let i = t.createElement("aside");
		i.className = "graph-selection-panel", i.dataset.state = "closed", n.appendChild(i), a.selectionElement = i;
	}
	return a;
}
function Qs(e, t) {
	if (!t.communityQuality.warning) return null;
	let n = e.createElement("aside");
	n.className = "graph-quality-notice", n.dataset.qualityLevel = t.communityQuality.level, n.dataset.boundaryCertainty = t.communityQuality.boundaryCertainty, n.setAttribute("aria-live", "polite");
	let r = e.createElement("span");
	r.className = "graph-quality-notice-label", r.textContent = t.communityQuality.level === "poor" ? "社区划分可信度低" : "社区划分可信度偏弱", n.appendChild(r);
	for (let r of t.communityQuality.auxiliaryViews) {
		let t = e.createElement("button");
		t.type = "button", t.className = "graph-quality-notice-action", t.dataset.auxiliaryViewId = r.id, t.textContent = r.label, n.appendChild(t);
	}
	return n;
}
function $s(e, t) {
	let n = t.worldBounds;
	e.setAttribute("viewBox", `${n.minX} ${n.minY} ${n.width} ${n.height}`);
}
function ec() {
	return {
		contentLayer: null,
		svgElement: null,
		edgeElements: /* @__PURE__ */ new Map(),
		communityWashElements: /* @__PURE__ */ new Map(),
		aggregationContainerElements: /* @__PURE__ */ new Map(),
		nodeElements: /* @__PURE__ */ new Map(),
		miniNodeElements: /* @__PURE__ */ new Map(),
		miniViewportElement: null,
		basePoints: /* @__PURE__ */ new Map(),
		readerElement: null,
		selectionElement: null,
		searchElement: null,
		searchInput: null,
		searchStatusElement: null,
		toolbarElement: null,
		toolbarPanelElement: null,
		legendElement: null,
		legendRows: /* @__PURE__ */ new Map(),
		previewElement: null
	};
}
//#endregion
//#region src/render/controls.ts
function tc(e, t) {
	let n = e.createElement("nav");
	n.className = "graph-toolbar", n.dataset.panel = t.panelState, n.setAttribute("aria-label", "图谱控制"), n.addEventListener("click", (e) => e.stopPropagation());
	let r = e.createElement("div");
	r.className = "graph-toolbar-actions";
	let i = dc(e, "筛选", t.panelState === "filters");
	i.addEventListener("click", () => t.onPanelToggle("filters"));
	let a = dc(e, "图例", t.panelState === "legend");
	a.addEventListener("click", () => t.onPanelToggle("legend"));
	let o = dc(e, "回全图", !1);
	o.addEventListener("click", t.onReset), r.append(i, a, o);
	let s = e.createElement("section");
	s.className = "graph-toolbar-panel", s.dataset.state = t.panelState;
	let c = e.createElement("div");
	c.className = "graph-toolbar-section graph-toolbar-filters", c.appendChild(lc(e, t.typeFilters, t.onTypeFilterToggle));
	let l = e.createElement("div");
	l.className = "graph-toolbar-section graph-toolbar-legend";
	let u = e.createElement("div");
	return u.className = "graph-toolbar-section-title", u.textContent = "边", l.appendChild(u), l.appendChild(ac(e)), s.append(c, l), n.append(r, s), {
		element: n,
		panel: s,
		filtersPanel: c,
		buttons: {
			filters: i,
			legend: a
		}
	};
}
function nc(e, t) {
	let n = e.createElement("nav");
	n.className = "graph-zoom-controls", n.dataset.control = "sigma-zoom", n.setAttribute("aria-label", "图谱缩放"), n.addEventListener("click", (e) => e.stopPropagation());
	let r = fc(e, "+", "放大图谱");
	r.addEventListener("click", (e) => {
		e.stopPropagation(), t.onZoomIn();
	});
	let i = fc(e, "-", "缩小图谱");
	return i.addEventListener("click", (e) => {
		e.stopPropagation(), t.onZoomOut();
	}), n.append(r, i), {
		element: n,
		buttons: {
			zoomIn: r,
			zoomOut: i
		}
	};
}
function rc(e, t) {
	let n = e.createElement("aside");
	n.className = "community-legend", n.dataset.state = t.collapsed ? "collapsed" : "open";
	let r = e.createElement("button");
	r.type = "button", r.className = "community-legend-toggle", r.setAttribute("aria-expanded", t.collapsed ? "false" : "true"), r.textContent = "社区", r.addEventListener("click", (e) => {
		e.stopPropagation(), t.onToggle();
	}), n.appendChild(r);
	let i = e.createElement("div");
	i.className = "community-legend-list";
	let a = /* @__PURE__ */ new Map();
	for (let n of t.rows) {
		let r = e.createElement("button");
		r.type = "button", r.className = "community-legend-row", r.dataset.communityId = n.id, r.addEventListener("pointerenter", () => t.onHover(n.id)), r.addEventListener("pointerleave", () => t.onHover(null)), r.addEventListener("click", (e) => {
			e.stopPropagation(), t.onSelect(n.id);
		});
		let o = e.createElement("span");
		o.className = "community-legend-swatch", o.style.background = n.color;
		let s = e.createElement("span");
		s.className = "community-legend-label", s.textContent = n.label;
		let c = e.createElement("span");
		c.className = "community-legend-count", c.textContent = `${n.pageCount} 页`, r.append(o, s, c), i.appendChild(r), a.set(n.id, r);
	}
	return n.appendChild(i), {
		element: n,
		rows: a
	};
}
function ic(e, t) {
	let n = e.createElement("div");
	n.className = "graph-search", n.dataset.state = t.open ? "open" : "closed";
	let r = e.createElement("input");
	r.type = "search", r.className = "graph-search-input", r.placeholder = "搜索图谱", r.setAttribute("aria-label", "搜索图谱"), r.value = t.query, r.addEventListener("focus", t.onOpen), r.addEventListener("input", () => t.onQuery(r.value)), r.addEventListener("keydown", (e) => {
		e.key === "ArrowDown" && (e.preventDefault(), t.onNext()), e.key === "ArrowUp" && (e.preventDefault(), t.onPrevious()), e.key === "Enter" && (e.preventDefault(), t.onActivate()), e.key === "Escape" && (e.preventDefault(), e.stopPropagation(), t.onClose());
	});
	let i = e.createElement("span");
	return i.className = "graph-search-status", i.textContent = t.query ? "0 个结果" : "输入关键词", n.append(r, i), {
		element: n,
		input: r,
		status: i
	};
}
function ac(e) {
	let t = e.createElement("div");
	t.className = "graph-edge-legend";
	let n = e.createElement("div");
	n.className = "graph-edge-legend-group", n.appendChild(oc(e, "关系类型"));
	for (let t of [
		{
			label: "实现 / 依赖 / 衍生",
			className: "relation-dependency"
		},
		{
			label: "对比",
			className: "relation-contrast"
		},
		{
			label: "矛盾",
			className: "relation-conflict"
		}
	]) n.appendChild(sc(e, t.label, t.className));
	let r = e.createElement("div");
	r.className = "graph-edge-legend-group", r.appendChild(oc(e, "置信度"));
	for (let t of [
		{
			label: "原文",
			className: "confidence-extracted"
		},
		{
			label: "推断",
			className: "confidence-inferred"
		},
		{
			label: "待确认",
			className: "confidence-ambiguous"
		}
	]) r.appendChild(cc(e, t.label, t.className));
	return t.append(n, r), t;
}
function oc(e, t) {
	let n = e.createElement("div");
	return n.className = "graph-edge-legend-heading", n.textContent = t, n;
}
function sc(e, t, n) {
	let r = e.createElement("div");
	r.className = `graph-edge-legend-row graph-edge-legend-relation ${n}`;
	let i = e.createElement("span");
	i.className = "graph-edge-legend-swatch";
	let a = e.createElement("span");
	return a.textContent = t, r.append(i, a), r;
}
function cc(e, t, n) {
	let r = e.createElement("div");
	r.className = `graph-edge-legend-row graph-edge-legend-confidence ${n}`;
	let i = e.createElement("span");
	i.className = "graph-edge-legend-line";
	let a = e.createElement("span");
	return a.textContent = t, r.append(i, a), r;
}
function lc(e, t, n) {
	let r = e.createElement("fieldset");
	r.className = "graph-type-filter";
	let i = e.createElement("legend");
	i.className = "graph-toolbar-section-title", i.textContent = "类型筛选", r.appendChild(i);
	for (let i of uc(t)) {
		let a = e.createElement("label");
		a.className = "graph-type-filter-option";
		let o = e.createElement("input");
		o.type = "checkbox", o.checked = t[i] !== !1, o.dataset.type = i, o.addEventListener("change", () => n(i, o.checked));
		let c = e.createElement("span");
		c.textContent = s(i), a.append(o, c), r.appendChild(a);
	}
	return r;
}
function uc(e) {
	let t = [
		"entity",
		"topic",
		"source"
	], n = /* @__PURE__ */ new Set(), r = [];
	for (let i of t) Object.hasOwn(e, i) && (r.push(i), n.add(i));
	for (let t of Object.keys(e).sort()) n.has(t) || r.push(t);
	return r;
}
function dc(e, t, n) {
	let r = e.createElement("button");
	return r.type = "button", r.className = "graph-toolbar-button", r.dataset.active = n ? "true" : "false", r.textContent = t, r;
}
function fc(e, t, n) {
	let r = e.createElement("button");
	return r.type = "button", r.className = "graph-zoom-button", r.textContent = t, r.setAttribute("aria-label", n), r;
}
//#endregion
//#region src/render/render-styles.ts
function pc(e) {
	if (e.getElementById("llm-wiki-graph-engine-static-styles")) return;
	let t = e.createElement("style");
	t.id = "llm-wiki-graph-engine-static-styles", t.textContent = mc, e.head.appendChild(t);
}
var mc = "\n.llm-wiki-graph-engine {\n  position: relative;\n  width: 100%;\n  min-height: 520px;\n  height: 100%;\n  overflow: hidden;\n  overscroll-behavior: contain;\n  touch-action: none;\n  user-select: none;\n  -webkit-user-select: none;\n  -webkit-user-drag: none;\n  color: var(--ink);\n  font-family: var(--font-ui);\n  background:\n    var(--paper-glow, radial-gradient(ellipse at 28% 55%, color-mix(in srgb, var(--surface) 56%, transparent), transparent 56%)),\n    var(--paper-vignette, radial-gradient(ellipse at 70% 48%, color-mix(in srgb, var(--mist) 60%, transparent), transparent 58%)),\n    var(--paper-mottle, none),\n    var(--bg);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] {\n  background:\n    var(--paper-glow, radial-gradient(140% 95% at 50% -25%, color-mix(in srgb, var(--surface-2) 38%, transparent), transparent 55%)),\n    linear-gradient(180deg, color-mix(in srgb, var(--surface-2) 38%, transparent), transparent 34%),\n    radial-gradient(ellipse at 28% 56%, color-mix(in srgb, var(--night) 13%, transparent), transparent 58%),\n    radial-gradient(ellipse at 76% 38%, color-mix(in srgb, var(--cinnabar) 9%, transparent), transparent 54%),\n    var(--paper-vignette, radial-gradient(ellipse 105% 92% at 50% 40%, transparent 52%, rgba(0, 0, 0, .22) 100%)),\n    var(--paper-mottle, none),\n    var(--bg);\n}\n[data-llm-wiki-graph-route-transition] > .sigma-global-route,\n[data-llm-wiki-graph-route-transition] > [data-llm-wiki-graph-root=\"true\"],\n[data-llm-wiki-graph-route-transition] > .graph-over-limit-notice-view {\n  animation: graph-route-continuity .16s ease-out both;\n}\n@media (prefers-reduced-motion: reduce) {\n  [data-llm-wiki-graph-route-transition] > .sigma-global-route,\n  [data-llm-wiki-graph-route-transition] > [data-llm-wiki-graph-root=\"true\"],\n  [data-llm-wiki-graph-route-transition] > .graph-over-limit-notice-view {\n    animation: none;\n  }\n}\n@keyframes graph-route-continuity {\n  from {\n    opacity: .82;\n    transform: scale(.996);\n  }\n  to {\n    opacity: 1;\n    transform: scale(1);\n  }\n}\n.sigma-global-route,\n.sigma-global-renderer {\n  position: absolute;\n  inset: 0;\n  width: 100%;\n  height: 100%;\n}\n.sigma-global-route.llm-wiki-graph-engine {\n  min-height: 0;\n}\n.sigma-global-renderer canvas {\n  position: absolute;\n  inset: 0;\n}\n.sigma-global-overlay {\n  position: absolute;\n  inset: 0;\n  z-index: 3;\n  pointer-events: none;\n}\n.sigma-global-node-hit-target,\n.sigma-global-community-region,\n.sigma-global-community-label {\n  position: absolute;\n  pointer-events: none;\n}\n.sigma-global-node-hit-target {\n  border: 1px solid currentColor;\n  cursor: pointer;\n  pointer-events: auto;\n  z-index: 2;\n  border-radius: 999px;\n  opacity: 0;\n  touch-action: none;\n  user-select: none;\n  -webkit-user-select: none;\n  -webkit-user-drag: none;\n}\n.sigma-global-node-hit-target:focus-visible {\n  outline: 2px solid var(--cinnabar);\n  outline-offset: 2px;\n  opacity: .2;\n}\n.sigma-global-community-label {\n  max-width: 160px;\n  overflow: hidden;\n  transform: translate(-50%, -50%);\n  border-radius: 4px;\n  background: color-mix(in srgb, var(--surface) 58%, transparent);\n  box-shadow: 0 1px 2px color-mix(in srgb, var(--ink) 10%, transparent);\n  padding: 1px 5px;\n  color: var(--muted);\n  font: 600 12px/1.35 var(--font-ui);\n  text-align: center;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.sigma-global-community-label[data-selected=\"true\"] {\n  background: color-mix(in srgb, var(--surface) 72%, transparent);\n  color: var(--ink);\n  font-weight: 600;\n}\n.sigma-global-community-label[data-dim=\"true\"] {\n  opacity: .45;\n}\n.graph-content-layer {\n  position: absolute;\n  inset: 0;\n  z-index: 2;\n  transform-origin: 0 0;\n  will-change: transform;\n}\n.graph-search {\n  position: absolute;\n  top: 64px;\n  left: 14px;\n  z-index: 7;\n  display: grid;\n  grid-template-columns: minmax(180px, 260px) auto;\n  align-items: center;\n  gap: 8px;\n  opacity: 0;\n  pointer-events: none;\n  transform: translateY(-6px);\n  transition: opacity .16s ease, transform .16s ease;\n}\n.graph-search[data-state=\"open\"],\n.graph-search:focus-within {\n  opacity: 1;\n  pointer-events: auto;\n  transform: translateY(0);\n}\n.graph-search-input {\n  touch-action: auto;\n  user-select: text;\n  -webkit-user-select: text;\n  min-width: 0;\n  border: 1px solid color-mix(in srgb, var(--rule) 78%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 92%, transparent);\n  padding: 8px 10px;\n  color: var(--ink);\n  font: 13px/1.3 var(--font-ui);\n  outline: none;\n  box-shadow: 0 12px 24px rgba(36, 24, 12, .08);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-search-input {\n  background: color-mix(in srgb, var(--surface) 88%, transparent);\n}\n.graph-search-input:focus {\n  border-color: color-mix(in srgb, var(--cinnabar) 70%, transparent);\n}\n.graph-search-status {\n  border: 1px solid color-mix(in srgb, var(--rule) 68%, transparent);\n  border-radius: 999px;\n  background: color-mix(in srgb, var(--surface) 84%, transparent);\n  padding: 5px 8px;\n  color: var(--muted);\n  font-size: 11px;\n  white-space: nowrap;\n}\n.graph-toolbar {\n  position: absolute;\n  top: 14px;\n  left: 14px;\n  right: 14px;\n  z-index: 8;\n  display: grid;\n  justify-items: start;\n  pointer-events: none;\n}\n.graph-toolbar-actions {\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  max-width: 100%;\n  border: 1px solid color-mix(in srgb, var(--rule) 62%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 64%, transparent);\n  box-shadow: 0 14px 30px rgba(36, 24, 12, .08);\n  backdrop-filter: blur(14px);\n  padding: 4px;\n  pointer-events: auto;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-toolbar-actions {\n  background: color-mix(in srgb, var(--surface) 58%, transparent);\n}\n.graph-toolbar-button {\n  user-select: none;\n  -webkit-user-select: none;\n  min-height: 28px;\n  border: 0;\n  border-radius: 6px;\n  background: transparent;\n  color: var(--muted);\n  font: 12px/1.2 var(--font-ui);\n  padding: 0 10px;\n  cursor: pointer;\n  white-space: nowrap;\n}\n.graph-toolbar-button:hover,\n.graph-toolbar-button[data-active=\"true\"] {\n  background: color-mix(in srgb, var(--cinnabar) 10%, transparent);\n  color: var(--ink);\n}\n.graph-toolbar-panel {\n  width: min(320px, calc(100vw - 28px));\n  max-height: min(58vh, 420px);\n  margin-top: 8px;\n  border: 1px solid color-mix(in srgb, var(--rule) 62%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 70%, transparent);\n  box-shadow: 0 20px 42px rgba(36, 24, 12, .12);\n  backdrop-filter: blur(16px);\n  overflow: auto;\n  pointer-events: auto;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-toolbar-panel {\n  background: color-mix(in srgb, var(--surface) 62%, transparent);\n}\n.graph-toolbar-panel[data-state=\"closed\"] {\n  display: none;\n}\n.graph-zoom-controls {\n  position: absolute;\n  left: 14px;\n  bottom: 14px;\n  z-index: 8;\n  display: inline-flex;\n  flex-direction: column;\n  gap: 5px;\n  border: 1px solid color-mix(in srgb, var(--rule) 62%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 64%, transparent);\n  box-shadow: 0 14px 30px rgba(36, 24, 12, .08);\n  backdrop-filter: blur(14px);\n  padding: 4px;\n  pointer-events: auto;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-zoom-controls {\n  background: color-mix(in srgb, var(--surface) 58%, transparent);\n}\n.graph-zoom-button {\n  user-select: none;\n  -webkit-user-select: none;\n  width: 30px;\n  height: 30px;\n  border: 0;\n  border-radius: 6px;\n  background: transparent;\n  color: var(--muted);\n  font: 600 18px/1 var(--font-ui);\n  cursor: pointer;\n}\n.graph-zoom-button:hover,\n.graph-zoom-button:focus-visible {\n  background: color-mix(in srgb, var(--cinnabar) 10%, transparent);\n  color: var(--ink);\n  outline: none;\n}\n.graph-toolbar-section {\n  display: none;\n}\n.graph-toolbar-panel[data-state=\"filters\"] .graph-toolbar-filters,\n.graph-toolbar-panel[data-state=\"legend\"] .graph-toolbar-legend {\n  display: block;\n}\n.graph-toolbar-section-title {\n  padding: 10px 12px;\n  color: var(--muted);\n  font: 12px/1.3 var(--font-ui);\n}\n.graph-type-filter {\n  display: grid;\n  grid-template-columns: repeat(3, minmax(0, 1fr));\n  gap: 6px;\n  margin: 0;\n  border: 0;\n  border-bottom: 1px solid color-mix(in srgb, var(--rule) 52%, transparent);\n  padding: 0 10px 10px;\n}\n.graph-type-filter .graph-toolbar-section-title {\n  grid-column: 1 / -1;\n  padding: 10px 2px 2px;\n}\n.graph-type-filter-option {\n  display: inline-flex;\n  align-items: center;\n  gap: 6px;\n  min-width: 0;\n  min-height: 28px;\n  border: 1px solid color-mix(in srgb, var(--rule) 52%, transparent);\n  border-radius: 6px;\n  background: color-mix(in srgb, var(--surface) 48%, transparent);\n  padding: 0 8px;\n  color: var(--ink);\n  font: 12px/1.2 var(--font-ui);\n  cursor: pointer;\n}\n.graph-type-filter-option input {\n  margin: 0;\n  accent-color: var(--cinnabar);\n}\n.graph-type-filter-option span {\n  min-width: 0;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-edge-legend {\n  display: grid;\n  gap: 12px;\n  padding: 0 12px 12px;\n}\n.graph-edge-legend-group {\n  display: grid;\n  gap: 7px;\n}\n.graph-edge-legend-heading {\n  color: var(--muted);\n  font: 11px/1.2 var(--font-ui);\n}\n.graph-edge-legend-row {\n  display: grid;\n  grid-template-columns: 38px minmax(0, 1fr);\n  align-items: center;\n  gap: 8px;\n  min-height: 24px;\n  color: var(--ink);\n  font: 12px/1.2 var(--font-ui);\n}\n.graph-edge-legend-swatch,\n.graph-edge-legend-line {\n  display: block;\n  width: 34px;\n  height: 0;\n  border-top: 2px solid color-mix(in srgb, var(--night) 66%, transparent);\n}\n.graph-edge-legend-relation.relation-contrast .graph-edge-legend-swatch {\n  border-top-color: color-mix(in srgb, var(--amber) 82%, transparent);\n}\n.graph-edge-legend-relation.relation-conflict .graph-edge-legend-swatch {\n  border-top-color: color-mix(in srgb, #d94693 78%, transparent);\n}\n.graph-edge-legend-confidence.confidence-inferred .graph-edge-legend-line {\n  border-top-style: dashed;\n}\n.graph-edge-legend-confidence.confidence-ambiguous .graph-edge-legend-line {\n  border-top-style: dotted;\n}\n.sigma-global-route .graph-edge-legend-group:has(.graph-edge-legend-confidence) {\n  display: none;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-edge-legend-swatch,\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-edge-legend-line {\n  border-top-color: color-mix(in srgb, var(--line) 70%, transparent);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-edge-legend-relation.relation-contrast .graph-edge-legend-swatch {\n  border-top-color: color-mix(in srgb, var(--amber) 76%, transparent);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-edge-legend-relation.relation-conflict .graph-edge-legend-swatch {\n  border-top-color: color-mix(in srgb, #f472b6 78%, transparent);\n}\n.community-legend {\n  width: 100%;\n  border: 0;\n  border-radius: 0;\n  background: transparent;\n  box-shadow: none;\n  overflow: hidden;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .community-legend {\n  background: transparent;\n}\n.community-legend-toggle {\n  width: 100%;\n  border: 0;\n  border-bottom: 1px solid color-mix(in srgb, var(--rule) 64%, transparent);\n  background: transparent;\n  padding: 8px 10px;\n  color: var(--ink);\n  font: 12px/1.3 var(--font-ui);\n  text-align: left;\n  cursor: pointer;\n}\n.community-legend[data-state=\"collapsed\"] .community-legend-toggle {\n  border-bottom: 0;\n}\n.community-legend-list {\n  display: grid;\n}\n.community-legend[data-state=\"collapsed\"] .community-legend-list {\n  display: none;\n}\n.community-legend-row {\n  display: grid;\n  grid-template-columns: 12px minmax(0, 1fr) auto;\n  align-items: center;\n  gap: 8px;\n  border: 0;\n  border-top: 1px solid color-mix(in srgb, var(--rule) 48%, transparent);\n  background: transparent;\n  padding: 8px 10px;\n  color: var(--ink);\n  font: 12px/1.3 var(--font-ui);\n  cursor: pointer;\n  text-align: left;\n}\n.community-legend-row:first-child {\n  border-top: 0;\n}\n.community-legend-row:hover,\n.community-legend-row[data-community-state=\"active\"] {\n  background: color-mix(in srgb, var(--cinnabar) 8%, transparent);\n}\n.community-legend-row[data-community-state=\"faded\"] {\n  opacity: .42;\n}\n.community-legend-swatch {\n  width: 12px;\n  height: 12px;\n  border-radius: 999px;\n  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, .12);\n}\n.community-legend-label {\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.community-legend-count {\n  color: var(--muted);\n  font-size: 11px;\n  white-space: nowrap;\n}\n.graph-selection-panel {\n  position: absolute;\n  right: 16px;\n  bottom: 16px;\n  z-index: 7;\n  display: grid;\n  gap: 12px;\n  width: min(360px, calc(100% - 32px));\n  max-height: min(520px, calc(100% - 32px));\n  overflow: auto;\n  border: 1px solid color-mix(in srgb, var(--rule) 72%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 92%, transparent);\n  box-shadow: 0 18px 36px rgba(36, 24, 12, .14);\n  padding: 14px;\n  opacity: 0;\n  pointer-events: none;\n  touch-action: auto;\n  user-select: text;\n  -webkit-user-select: text;\n  transform: translateY(8px);\n  transition: opacity .16s ease, transform .16s ease;\n}\n.graph-selection-panel[data-state=\"open\"] {\n  opacity: 1;\n  pointer-events: auto;\n  transform: translateY(0);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-selection-panel {\n  background: color-mix(in srgb, var(--surface) 88%, transparent);\n}\n.graph-selection-header {\n  display: grid;\n  grid-template-columns: minmax(0, 1fr) 28px;\n  align-items: center;\n  gap: 8px;\n}\n.graph-selection-title {\n  overflow: hidden;\n  color: var(--ink);\n  font: 600 14px/1.35 var(--font-ui);\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-selection-close {\n  width: 28px;\n  height: 28px;\n  border: 1px solid color-mix(in srgb, var(--rule) 72%, transparent);\n  border-radius: 999px;\n  background: transparent;\n  color: var(--ink);\n  cursor: pointer;\n  font-size: 17px;\n  line-height: 1;\n}\n.graph-selection-hint,\n.graph-selection-empty {\n  margin: 0;\n  color: var(--muted);\n  font-size: 12px;\n  line-height: 1.45;\n}\n.graph-selection-facts {\n  display: grid;\n  grid-template-columns: repeat(4, minmax(0, 1fr));\n  gap: 6px;\n}\n.graph-selection-fact {\n  min-width: 0;\n  border: 1px solid color-mix(in srgb, var(--rule) 58%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--mist) 52%, transparent);\n  padding: 8px 6px;\n}\n.graph-selection-fact strong,\n.graph-selection-fact span {\n  display: block;\n  overflow: hidden;\n  text-align: center;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-selection-fact strong {\n  color: var(--ink);\n  font-size: 15px;\n}\n.graph-selection-fact span {\n  margin-top: 2px;\n  color: var(--muted);\n  font-size: 11px;\n}\n.graph-selection-pages {\n  display: grid;\n  gap: 6px;\n  margin: 0;\n  padding: 0;\n  list-style: none;\n}\n.graph-selection-page {\n  min-width: 0;\n  border-top: 1px solid color-mix(in srgb, var(--rule) 46%, transparent);\n  padding-top: 7px;\n}\n.graph-selection-page:first-child {\n  border-top: 0;\n  padding-top: 0;\n}\n.graph-selection-page-title,\n.graph-selection-page-path {\n  display: block;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-selection-page-title {\n  color: var(--ink);\n  font-size: 13px;\n}\n.graph-selection-page-path {\n  margin-top: 2px;\n  color: var(--muted);\n  font-size: 11px;\n}\n.graph-content-layer.is-viewport-animating {\n  transition: transform .2s ease-out;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node {\n  box-shadow: 0 8px 16px rgba(36, 31, 26, .06);\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"]) {\n  border-color: color-mix(in srgb, var(--rule) 88%, transparent);\n  box-shadow: 0 8px 14px rgba(36, 31, 26, .04);\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"])::before {\n  opacity: .12;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"]) .node-name,\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"]) .node-meta {\n  display: none;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"]).is-point,\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"]).is-overview,\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node:not([data-traceable=\"true\"])[data-visual-role=\"map-pin\"] {\n  box-shadow: 0 0 0 2px color-mix(in srgb, var(--night) 8%, transparent);\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .edge:not([data-traceable=\"true\"]) {\n  opacity: .08 !important;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .edge[data-traceable=\"true\"] {\n  opacity: .46;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .community-wash {\n  opacity: .08;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node[data-traceable=\"true\"] .node-name,\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node[aria-pressed=\"true\"] .node-name {\n  display: block;\n}\n.llm-wiki-graph-engine[data-interaction-mode=\"active\"] .node[data-traceable=\"true\"] .node-meta {\n  display: flex;\n}\n.llm-wiki-graph-svg {\n  position: absolute;\n  inset: 0;\n  width: 100%;\n  height: 100%;\n  overflow: visible;\n}\n.edge {\n  fill: none;\n  stroke-linecap: round;\n  opacity: .74;\n  pointer-events: stroke;\n}\n.edge[data-filter-state=\"hidden\"],\n.community-wash[data-filter-state=\"hidden\"] {\n  opacity: .04 !important;\n  pointer-events: none;\n}\n.edge.is-diff-added {\n  stroke-dasharray: var(--diff-edge-length, 180);\n  stroke-dashoffset: var(--diff-edge-length, 180);\n  animation: llm-wiki-edge-draw 1.15s ease forwards;\n}\n.edge.is-diff-removed {\n  animation: llm-wiki-fade-out .72s ease forwards;\n}\n.edge.relation-implementation,\n.edge.relation-dependency,\n.edge.relation-derivation {\n  stroke: color-mix(in srgb, var(--night) 66%, transparent);\n}\n.edge.relation-contrast {\n  stroke: color-mix(in srgb, var(--amber) 82%, transparent);\n}\n.edge.relation-conflict {\n  stroke: color-mix(in srgb, #d94693 78%, transparent);\n}\n.edge.confidence-inferred { stroke-dasharray: 6 8; }\n.edge.confidence-ambiguous { stroke-dasharray: 2 7; }\n.edge.confidence-unverified { stroke-dasharray: 1 8; }\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge {\n  opacity: .82;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge.relation-implementation,\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge.relation-dependency,\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge.relation-derivation {\n  stroke: color-mix(in srgb, var(--line) 70%, transparent);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge.relation-contrast {\n  stroke: color-mix(in srgb, var(--amber) 76%, transparent);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .edge.relation-conflict {\n  stroke: color-mix(in srgb, #f472b6 78%, transparent);\n}\n.community-wash {\n  transition: opacity .16s ease, cx .24s ease, cy .24s ease, rx .24s ease, ry .24s ease;\n}\n.llm-wiki-graph-engine[data-community-boundary-certainty=\"reduced\"] .community-wash {\n  stroke-dasharray: 12 8;\n  stroke-width: .95;\n}\n.llm-wiki-graph-engine[data-community-boundary-certainty=\"low\"] .community-wash {\n  stroke-dasharray: 7 10;\n  stroke-width: .75;\n  filter: grayscale(.18);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .community-wash {\n  mix-blend-mode: screen;\n  filter: saturate(.9);\n}\n.community-wash.is-diff-new-community {\n  animation: llm-wiki-community-emerge .85s ease both;\n}\n.llm-wiki-graph-engine[data-dragging] .community-wash {\n  opacity: .035;\n}\n.graph-quality-notice {\n  position: absolute;\n  left: 14px;\n  bottom: 14px;\n  z-index: 7;\n  display: inline-flex;\n  align-items: center;\n  gap: 8px;\n  max-width: min(420px, calc(100% - 28px));\n  border: 1px solid color-mix(in srgb, var(--rule) 58%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 76%, transparent);\n  box-shadow: 0 14px 28px rgba(36, 24, 12, .08);\n  backdrop-filter: blur(14px);\n  padding: 7px 8px 7px 10px;\n  color: var(--muted);\n  font: 12px/1.25 var(--font-ui);\n  pointer-events: auto;\n}\n.graph-quality-notice[data-quality-level=\"poor\"] {\n  border-color: color-mix(in srgb, var(--cinnabar) 42%, transparent);\n  color: var(--ink);\n}\n.graph-quality-notice-label {\n  min-width: 0;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-quality-notice-action {\n  flex: 0 0 auto;\n  border: 1px solid color-mix(in srgb, var(--rule) 58%, transparent);\n  border-radius: 6px;\n  background: color-mix(in srgb, var(--surface) 62%, transparent);\n  padding: 5px 8px;\n  color: var(--ink);\n  font: 12px/1.2 var(--font-ui);\n  cursor: pointer;\n}\n.graph-quality-notice-action:hover {\n  border-color: color-mix(in srgb, var(--cinnabar) 54%, transparent);\n}\n.node-layer {\n  position: absolute;\n  inset: 0;\n  z-index: 3;\n  pointer-events: none;\n}\n.aggregation-container {\n  position: absolute;\n  z-index: 2;\n  display: grid;\n  place-items: center;\n  gap: 2px;\n  width: calc(var(--aggregation-radius, 48px) * 2);\n  height: calc(var(--aggregation-radius, 48px) * 2);\n  border: 1px solid color-mix(in srgb, var(--aggregation-color, var(--cinnabar)) 58%, transparent);\n  border-radius: 999px;\n  background:\n    radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--aggregation-color, var(--cinnabar)) 18%, transparent), transparent 62%),\n    color-mix(in srgb, var(--surface) 58%, transparent);\n  box-shadow: inset 0 0 0 10px color-mix(in srgb, var(--aggregation-color, var(--cinnabar)) 7%, transparent), 0 18px 34px rgba(36, 31, 26, .08);\n  color: var(--ink);\n  cursor: pointer;\n  pointer-events: auto;\n  text-align: center;\n  translate: -50% -50%;\n}\n.aggregation-container:hover,\n.aggregation-container:focus-visible,\n.aggregation-container[aria-pressed=\"true\"] {\n  border-color: color-mix(in srgb, var(--aggregation-color, var(--cinnabar)) 84%, transparent);\n  box-shadow: inset 0 0 0 10px color-mix(in srgb, var(--aggregation-color, var(--cinnabar)) 12%, transparent), 0 18px 34px rgba(36, 31, 26, .14);\n}\n.aggregation-container[data-selected=\"true\"] {\n  outline: 2px solid color-mix(in srgb, var(--cinnabar) 72%, transparent);\n  outline-offset: 3px;\n}\n.aggregation-container[data-community-state=\"faded\"] {\n  opacity: .34;\n}\n.aggregation-container[data-community-state=\"active\"] {\n  opacity: 1;\n}\n.aggregation-container-count {\n  font: 700 18px/1 var(--font-ui);\n}\n.aggregation-container-label {\n  max-width: 78%;\n  overflow: hidden;\n  color: var(--muted);\n  font: 11px/1.2 var(--font-ui);\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.aggregation-container-markers {\n  display: flex;\n  justify-content: center;\n  gap: 3px;\n  max-width: 92%;\n  min-height: 14px;\n  overflow: hidden;\n}\n.aggregation-container-marker {\n  border-radius: 999px;\n  background: color-mix(in srgb, var(--surface) 76%, transparent);\n  padding: 1px 4px;\n  color: var(--muted);\n  font: 9px/1.2 var(--font-ui);\n  white-space: nowrap;\n}\n.graph-hover-preview {\n  position: absolute;\n  z-index: 9;\n  width: min(300px, calc(100% - 32px));\n  pointer-events: none;\n  opacity: 0;\n  transition: opacity .14s ease;\n}\n.graph-hover-preview[data-state=\"open\"] {\n  opacity: 1;\n}\n.graph-hover-preview-card {\n  border: 1px solid color-mix(in srgb, var(--rule) 74%, transparent);\n  border-radius: 8px;\n  background: color-mix(in srgb, var(--surface) 94%, transparent);\n  box-shadow: 0 18px 34px rgba(36, 31, 26, .16);\n  padding: 11px 12px;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-hover-preview-card {\n  border-color: color-mix(in srgb, var(--line) 38%, transparent);\n  background: color-mix(in srgb, var(--surface) 90%, transparent);\n  box-shadow: 0 18px 36px rgba(0, 0, 0, .38);\n}\n.graph-hover-preview-type {\n  color: var(--muted);\n  font-size: 11px;\n  line-height: 1.2;\n}\n.graph-hover-preview-title {\n  margin-top: 3px;\n  overflow: hidden;\n  color: var(--ink);\n  font-family: var(--font-serif);\n  font-size: 15px;\n  font-weight: 700;\n  line-height: 1.25;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-hover-preview-summary {\n  display: -webkit-box;\n  margin: 7px 0 0;\n  overflow: hidden;\n  color: var(--muted);\n  font-size: 12px;\n  line-height: 1.45;\n  -webkit-box-orient: vertical;\n  -webkit-line-clamp: 3;\n}\n.node {\n  position: absolute;\n  z-index: 3;\n  pointer-events: auto;\n  min-height: 46px;\n  max-width: 178px;\n  padding: 8px 11px;\n  border-radius: 12px;\n  border: 1px solid color-mix(in srgb, var(--rule) 98%, transparent);\n  background: color-mix(in srgb, var(--surface) 88%, transparent);\n  box-shadow: 0 12px 22px rgba(36, 31, 26, .09), inset 0 0 0 1px rgba(255, 255, 255, .32);\n  translate: -50% -50%;\n  text-align: left;\n  color: var(--ink);\n  transition:\n    opacity .16s ease,\n    width .16s ease,\n    height .16s ease,\n    min-width .16s ease,\n    min-height .16s ease,\n    max-width .16s ease,\n    padding .16s ease,\n    border-radius .16s ease,\n    border-color .16s ease,\n    background-color .16s ease,\n    box-shadow .16s ease;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .node {\n  border-color: color-mix(in srgb, var(--rule) 84%, transparent);\n  background: color-mix(in srgb, var(--surface) 86%, transparent);\n  box-shadow: 0 16px 30px rgba(0, 0, 0, .34), inset 0 0 0 1px rgba(245, 240, 230, .07);\n}\n.node::before {\n  content: \"\";\n  position: absolute;\n  inset: -7px;\n  border-radius: 17px;\n  background: radial-gradient(circle, color-mix(in srgb, var(--night) 18%, transparent), transparent 66%);\n  z-index: -1;\n  opacity: .46;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .node::before {\n  background: radial-gradient(circle, color-mix(in srgb, var(--night) 24%, transparent), transparent 68%);\n  opacity: .4;\n}\n.node[data-type=\"topic\"] { border-left: 5px solid var(--cinnabar); }\n.node[data-type=\"entity\"] { border-left: 5px solid var(--night); }\n.node[data-type=\"source\"] { border-left: 5px solid var(--jade); }\n.node[aria-pressed=\"true\"] {\n  border-color: color-mix(in srgb, var(--cinnabar) 74%, transparent);\n  box-shadow: 0 16px 28px color-mix(in srgb, var(--cinnabar) 16%, transparent), 0 0 0 4px color-mix(in srgb, var(--cinnabar) 10%, transparent);\n  transform: translateY(-2px);\n}\n.node[data-search-state=\"match\"] {\n  border-color: color-mix(in srgb, var(--cinnabar) 78%, transparent);\n  box-shadow: 0 16px 28px color-mix(in srgb, var(--cinnabar) 15%, transparent), 0 0 0 4px color-mix(in srgb, var(--cinnabar) 9%, transparent);\n}\n.node[data-search-focus=\"true\"] {\n  outline: 3px solid color-mix(in srgb, var(--cinnabar) 68%, transparent);\n  outline-offset: 4px;\n}\n.node[data-search-state=\"faded\"] {\n  opacity: .28;\n}\n.node[data-filter-state=\"hidden\"] {\n  opacity: .08;\n  pointer-events: none;\n}\n.node[data-community-state=\"faded\"] {\n  opacity: .24;\n}\n.edge[data-community-state=\"faded\"],\n.community-wash[data-community-state=\"faded\"] {\n  opacity: .12 !important;\n}\n.community-wash[data-community-state=\"active\"] {\n  opacity: .2;\n}\n.node.is-dragging {\n  cursor: grabbing;\n  z-index: 8;\n  box-shadow: 0 18px 34px color-mix(in srgb, var(--cinnabar) 18%, transparent), 0 0 0 4px color-mix(in srgb, var(--cinnabar) 10%, transparent);\n}\n.node.is-pinned::after {\n  content: \"\";\n  position: absolute;\n  right: -5px;\n  top: -5px;\n  width: 10px;\n  height: 10px;\n  border: 2px solid color-mix(in srgb, var(--surface) 92%, transparent);\n  border-radius: 99px;\n  background: var(--cinnabar);\n  box-shadow: 0 0 0 3px color-mix(in srgb, var(--cinnabar) 13%, transparent);\n}\n.node-kind {\n  display: none;\n  color: var(--muted);\n  font-family: var(--font-mono);\n  font-size: 10px;\n  letter-spacing: .04em;\n  text-transform: uppercase;\n}\n.node-name {\n  display: block;\n  max-width: 146px;\n  margin-top: 0;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n  font-family: var(--font-serif);\n  font-size: 14px;\n  font-weight: 700;\n  line-height: 1.25;\n}\n.node-meta {\n  display: none;\n  align-items: center;\n  gap: 6px;\n  margin-top: 6px;\n  color: var(--faint);\n  font-size: 11px;\n}\n.node:hover .node-kind,\n.node[aria-pressed=\"true\"] .node-kind {\n  display: block;\n}\n.node:hover .node-name,\n.node[aria-pressed=\"true\"] .node-name {\n  margin-top: 3px;\n}\n.node:hover .node-meta,\n.node[aria-pressed=\"true\"] .node-meta {\n  display: flex;\n}\n.spark {\n  width: 5px;\n  height: 5px;\n  border-radius: 99px;\n  background: var(--night);\n  box-shadow: 0 0 10px color-mix(in srgb, var(--night) 70%, transparent);\n}\n.node.is-compact {\n  min-height: 34px;\n  max-width: 130px;\n  padding: 6px 9px;\n  border-radius: 10px;\n}\n.node.is-compact .node-kind,\n.node.is-compact .node-meta { display: none; }\n.node.is-compact .node-name {\n  max-width: 104px;\n  font-size: 12px;\n}\n.node.is-point,\n.node.is-overview,\n.node[data-visual-role=\"map-pin\"] {\n  width: 14px;\n  height: 14px;\n  min-width: 14px;\n  min-height: 14px;\n  max-width: 14px;\n  padding: 0;\n  border: 0;\n  border-radius: 999px;\n  background: var(--night);\n  box-shadow: 0 0 0 4px color-mix(in srgb, var(--night) 14%, transparent);\n}\n.node.is-point[data-type=\"topic\"],\n.node.is-overview[data-type=\"topic\"] { background: var(--cinnabar); }\n.node.is-point[data-type=\"source\"],\n.node.is-overview[data-type=\"source\"] { background: var(--jade); }\n.node.is-point .node-kind,\n.node.is-point .node-name,\n.node.is-point .node-meta,\n.node.is-overview .node-kind,\n.node.is-overview .node-name,\n.node.is-overview .node-meta { display: none; }\n.node.is-label-hidden .node-name { display: none; }\n.node[data-visual-role=\"landmark\"] {\n  min-height: 30px;\n  max-width: 150px;\n  padding: 5px 10px 5px 24px;\n  border: 1px solid color-mix(in srgb, var(--rule) 78%, transparent);\n  border-radius: 999px 8px 8px 999px;\n  background: color-mix(in srgb, var(--surface) 70%, transparent);\n  box-shadow: 0 8px 16px rgba(36, 31, 26, .06);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .node[data-visual-role=\"landmark\"] {\n  border-color: color-mix(in srgb, var(--line) 38%, transparent);\n  background: color-mix(in srgb, var(--surface) 64%, transparent);\n  box-shadow: 0 10px 20px rgba(0, 0, 0, .22);\n}\n.node[data-visual-role=\"landmark\"]::before {\n  inset: auto auto auto 9px;\n  top: 50%;\n  width: 8px;\n  height: 8px;\n  border-radius: 999px;\n  background: var(--night);\n  opacity: .78;\n  translate: 0 -50%;\n}\n.node[data-visual-role=\"landmark\"][data-type=\"topic\"]::before { background: var(--cinnabar); }\n.node[data-visual-role=\"landmark\"][data-type=\"source\"]::before { background: var(--jade); }\n.node[data-visual-role=\"landmark\"] .node-kind,\n.node[data-visual-role=\"landmark\"] .node-meta { display: none; }\n.node[data-visual-role=\"landmark\"] .node-name {\n  max-width: 116px;\n  margin-top: 0;\n  font-size: 12px;\n  line-height: 1.2;\n}\n.node[data-visual-role=\"index-slip\"],\n.node[data-visual-role=\"cinnabar-note\"] {\n  min-height: 42px;\n  max-width: 182px;\n  padding: 8px 11px 8px 13px;\n  border-radius: 8px 12px 12px 8px;\n  background: color-mix(in srgb, var(--surface) 92%, transparent);\n  box-shadow: 0 13px 24px rgba(36, 31, 26, .1), inset 0 0 0 1px rgba(255, 255, 255, .32);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .node[data-visual-role=\"index-slip\"],\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .node[data-visual-role=\"cinnabar-note\"] {\n  background: color-mix(in srgb, var(--surface-2) 88%, transparent);\n  box-shadow: 0 16px 30px rgba(0, 0, 0, .38), inset 0 0 0 1px rgba(245, 240, 230, .09);\n}\n.node[data-visual-role=\"cinnabar-note\"] {\n  border-color: color-mix(in srgb, var(--cinnabar) 78%, transparent);\n  box-shadow: 0 17px 30px color-mix(in srgb, var(--cinnabar) 18%, transparent), 0 0 0 4px color-mix(in srgb, var(--cinnabar) 11%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] {\n  --community-map-label-bg: rgba(255, 252, 246, .68);\n  --community-map-label-border: rgba(121, 102, 80, .14);\n  --community-map-label-shadow: rgba(58, 42, 26, .06);\n  background:\n    var(--paper-glow),\n    var(--bg);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .community-wash {\n  fill: rgba(113, 152, 164, .055);\n  stroke: rgba(113, 152, 164, .16);\n  stroke-width: 1.4;\n  stroke-dasharray: 10 8;\n  opacity: .68;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .community-wash {\n  opacity: .42;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge {\n  stroke-width: max(1.1px, min(1.65px, var(--edge-map-width, 1.45px))) !important;\n  opacity: .32 !important;\n  transition: opacity .18s ease, stroke-width .18s ease, stroke .18s ease;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge.relation-implementation {\n  stroke: color-mix(in srgb, var(--night) 34%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge.relation-dependency {\n  stroke: color-mix(in srgb, var(--night) 36%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge.relation-derivation {\n  stroke: color-mix(in srgb, var(--night) 34%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge.relation-contrast {\n  stroke: color-mix(in srgb, var(--amber) 40%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge.relation-conflict {\n  stroke: rgba(183, 96, 112, .42); /* conflict 色 token 化待 ADR-23 关系边系统整体演进，spec §3.4 */\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .edge[data-relation-focus-depth=\"first\"] {\n  opacity: .74 !important;\n  stroke-width: max(2px, var(--edge-map-width, 2px)) !important;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .edge[data-relation-focus-depth=\"second\"] {\n  opacity: .12 !important;\n  stroke-width: 1.15px !important;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .edge[data-relation-focus-depth=\"unrelated\"] {\n  opacity: .018 !important;\n  pointer-events: none;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node {\n  width: 44px;\n  height: 44px;\n  min-width: 44px;\n  min-height: 44px;\n  max-width: 44px;\n  padding: 0;\n  border: 0;\n  border-radius: 999px;\n  background: transparent;\n  box-shadow: none;\n  transform: none;\n  overflow: visible;\n}\n.llm-wiki-graph-engine .node-pin,\n.llm-wiki-graph-engine .dot-core {\n  display: none;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node-pin {\n  position: relative;\n  display: grid;\n  width: 44px;\n  height: 44px;\n  min-width: 44px;\n  min-height: 44px;\n  place-items: center;\n  pointer-events: none;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .dot-core {\n  display: block;\n  width: var(--node-size, 13px);\n  height: var(--node-size, 13px);\n  border: 1px solid rgba(255, 252, 246, .82);\n  border-radius: 999px;\n  background: var(--node-community-color, var(--night));\n  transition: transform .16s ease, box-shadow .16s ease, background .16s ease, opacity .16s ease;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"topic\"] .dot-core {\n  background: var(--cinnabar);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node:hover .dot-core {\n  box-shadow: 0 0 8px 1px color-mix(in srgb, var(--night) 45%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"topic\"]:hover .dot-core {\n  box-shadow: 0 0 8px 1px color-mix(in srgb, var(--cinnabar) 45%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"source\"]:hover .dot-core {\n  box-shadow: 0 0 8px 1px color-mix(in srgb, var(--jade) 45%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"synthesis\"]:hover .dot-core,\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"comparison\"]:hover .dot-core {\n  box-shadow: 0 0 8px 1px color-mix(in srgb, var(--amber) 45%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-type=\"query\"]:hover .dot-core {\n  box-shadow: 0 0 8px 1px color-mix(in srgb, var(--violet) 45%, transparent);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[aria-pressed=\"true\"] .dot-core,\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-relation-focus-depth=\"focus\"] .dot-core {\n  transform: scale(1.32);\n  box-shadow: 0 0 0 6px color-mix(in srgb, var(--cinnabar) 18%, transparent), 0 8px 18px rgba(58, 42, 26, .16);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .node[data-relation-focus-depth=\"first\"] .dot-core {\n  transform: scale(1.12);\n  opacity: .96;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .node[data-relation-focus-depth=\"second\"] .dot-core {\n  opacity: .38;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .node[data-relation-focus-depth=\"unrelated\"] .dot-core {\n  opacity: .16;\n  transform: scale(.82);\n  box-shadow: none;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node-kind,\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node-meta {\n  display: none !important;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node-name {\n  position: absolute;\n  top: 50%;\n  left: calc(50% + 15px);\n  z-index: 2;\n  display: none !important;\n  max-width: 158px;\n  margin: 0;\n  overflow: hidden;\n  border: 1px solid var(--community-map-label-border);\n  border-radius: 5px;\n  background: var(--community-map-label-bg);\n  box-shadow: 0 5px 16px var(--community-map-label-shadow);\n  padding: 3px 7px;\n  color: var(--ink);\n  font-family: var(--font-serif);\n  font-size: 12px;\n  font-weight: 700;\n  line-height: 1.22;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n  pointer-events: none;\n  transform: translateY(-50%);\n  backdrop-filter: blur(10px);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-label-side=\"left\"] .node-name {\n  right: calc(50% + 15px);\n  left: auto;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-label-side=\"top\"] .node-name {\n  top: auto;\n  bottom: calc(50% + 13px);\n  left: 50%;\n  transform: translateX(-50%);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-label-side=\"bottom\"] .node-name {\n  top: calc(50% + 13px);\n  left: 50%;\n  transform: translateX(-50%);\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node:not(.is-label-hidden) .node-name,\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-relation-focus-depth=\"focus\"] .node-name,\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-relation-focus-depth=\"first\"][data-relation-label=\"true\"] .node-name {\n  display: block !important;\n}\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .node[data-filter-state=\"hidden\"],\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"] .edge[data-filter-state=\"hidden\"],\n.llm-wiki-graph-engine[data-community-map-state=\"lightweight\"][data-relation-focus=\"active\"] .edge[data-filter-state=\"hidden\"] {\n  opacity: .035 !important;\n  pointer-events: none;\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"][data-community-map-state=\"lightweight\"] .node-name {\n  border-color: color-mix(in srgb, var(--line) 34%, transparent);\n  background: color-mix(in srgb, var(--surface-2) 88%, transparent);\n  box-shadow: 0 10px 22px rgba(0, 0, 0, .28);\n}\n.node.is-disabled { opacity: .72; }\n.node.is-diff-added {\n  animation: llm-wiki-node-grow .96s cubic-bezier(.18,.82,.22,1) both;\n  animation-delay: var(--diff-delay, 0ms);\n}\n.node.is-diff-removed {\n  animation: llm-wiki-fade-out .72s ease forwards;\n}\n.node.is-diff-recolored {\n  animation: llm-wiki-node-recolor .92s ease both;\n}\n.mini-map {\n  position: absolute;\n  right: 16px;\n  bottom: 16px;\n  z-index: 4;\n  width: 160px;\n  height: 54px;\n  border: 1px solid color-mix(in srgb, var(--rule) 86%, transparent);\n  border-radius: var(--radius);\n  background: color-mix(in srgb, var(--surface) 74%, transparent);\n  box-shadow: var(--soft-shadow);\n}\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .mini-map,\n.llm-wiki-graph-engine[data-theme=\"mo-ye\"] .graph-reader {\n  border-color: color-mix(in srgb, var(--line) 34%, transparent);\n  background: color-mix(in srgb, var(--surface) 88%, transparent);\n  box-shadow: var(--soft-shadow), inset 0 0 0 1px rgba(245, 240, 230, .05);\n}\n.mini-map svg {\n  width: 100%;\n  height: 100%;\n  display: block;\n}\n.mini-map .is-selected {\n  stroke: var(--cinnabar);\n  stroke-width: 1.5;\n}\n.mini-map-viewport {\n  fill: color-mix(in srgb, var(--cinnabar) 7%, transparent);\n  stroke: color-mix(in srgb, var(--cinnabar) 78%, transparent);\n  stroke-width: 1.2;\n  rx: 3;\n  pointer-events: none;\n}\n.graph-reader {\n  position: absolute;\n  top: 16px;\n  right: 16px;\n  z-index: 6;\n  display: flex;\n  flex-direction: column;\n  width: min(360px, calc(100% - 32px));\n  max-height: calc(100% - 100px);\n  border: 1px solid color-mix(in srgb, var(--rule) 82%, transparent);\n  border-radius: var(--radius);\n  background: color-mix(in srgb, var(--surface) 92%, transparent);\n  box-shadow: var(--soft-shadow);\n  opacity: 0;\n  pointer-events: none;\n  touch-action: auto;\n  user-select: text;\n  -webkit-user-select: text;\n  transform: translateY(-4px);\n  transition: opacity .18s ease, transform .18s ease;\n}\n.graph-reader[data-state=\"open\"] {\n  opacity: 1;\n  pointer-events: auto;\n  transform: translateY(0);\n}\n.graph-reader-header {\n  position: relative;\n  padding: 14px 42px 10px 14px;\n  border-bottom: 1px solid color-mix(in srgb, var(--rule) 72%, transparent);\n}\n.graph-reader-title {\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n  font-family: var(--font-serif);\n  font-size: 16px;\n  font-weight: 700;\n}\n.graph-reader-meta {\n  margin-top: 4px;\n  display: flex;\n  flex-wrap: wrap;\n  gap: 4px 8px;\n  overflow: hidden;\n  color: var(--muted);\n  font-size: 11px;\n}\n.graph-reader-meta span {\n  max-width: 100%;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.graph-reader-close {\n  position: absolute;\n  top: 9px;\n  right: 10px;\n  width: 26px;\n  height: 26px;\n  border: 1px solid color-mix(in srgb, var(--rule) 78%, transparent);\n  border-radius: 999px;\n  background: color-mix(in srgb, var(--bg) 72%, transparent);\n  color: var(--ink);\n}\n.graph-reader-body {\n  min-height: 0;\n  overflow: auto;\n  touch-action: auto;\n  user-select: text;\n  -webkit-user-select: text;\n  padding: 12px 14px 14px;\n}\n.graph-reader-source {\n  display: inline-block;\n  max-width: 100%;\n  margin-bottom: 10px;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  vertical-align: top;\n  white-space: nowrap;\n  color: var(--cinnabar);\n  font-size: 12px;\n}\n.graph-reader-body pre {\n  margin: 0;\n  white-space: pre-wrap;\n  overflow-wrap: anywhere;\n  font-family: var(--font-serif);\n  font-size: 13px;\n  line-height: 1.65;\n}\n.graph-reader-empty {\n  margin: 0;\n  padding: 12px 14px;\n  color: var(--muted);\n  font-size: 13px;\n}\n@keyframes llm-wiki-node-grow {\n  0% {\n    opacity: 0;\n    translate: calc(-50% + var(--diff-anchor-dx, 0px)) calc(-50% + var(--diff-anchor-dy, 0px));\n    transform: scale(.68);\n  }\n  100% {\n    opacity: 1;\n    translate: -50% -50%;\n    transform: scale(1);\n  }\n}\n@keyframes llm-wiki-edge-draw {\n  to { stroke-dashoffset: 0; }\n}\n@keyframes llm-wiki-fade-out {\n  to { opacity: 0; transform: scale(.82); }\n}\n@keyframes llm-wiki-node-recolor {\n  0% { filter: saturate(.55) brightness(1.18); }\n  100% { filter: saturate(1) brightness(1); }\n}\n@keyframes llm-wiki-community-emerge {\n  0% { opacity: 0; transform: scale(.82); }\n  100% { transform: scale(1); }\n}\n";
//#endregion
//#region src/render/relation-focus.ts
function hc(e) {
	let t = new Set(e.nodes.map((e) => e.id)), n = e.activeNodeId && t.has(e.activeNodeId) ? e.activeNodeId : null, r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Map(), a = /* @__PURE__ */ new Set(), o = /* @__PURE__ */ new Set(), s = /* @__PURE__ */ new Set();
	if (!n) {
		for (let t of e.nodes) r.set(t.id, "none");
		for (let t of e.edges) i.set(t.id, "none");
		return {
			activeNodeId: null,
			nodeDepthById: r,
			edgeDepthById: i,
			firstNodeIds: a,
			secondNodeIds: o,
			directEdgeIds: s
		};
	}
	for (let r of e.edges) r.source === n && t.has(r.target) && (a.add(r.target), s.add(r.id)), r.target === n && t.has(r.source) && (a.add(r.source), s.add(r.id));
	for (let r of e.edges) {
		let e = a.has(r.source), i = a.has(r.target);
		e && r.target !== n && !a.has(r.target) && t.has(r.target) && o.add(r.target), i && r.source !== n && !a.has(r.source) && t.has(r.source) && o.add(r.source);
	}
	o.delete(n);
	for (let e of a) o.delete(e);
	for (let t of e.nodes) t.id === n ? r.set(t.id, "focus") : a.has(t.id) ? r.set(t.id, "first") : o.has(t.id) ? r.set(t.id, "second") : r.set(t.id, "unrelated");
	for (let t of e.edges) {
		if (s.has(t.id)) {
			i.set(t.id, "first");
			continue;
		}
		let e = r.get(t.source), n = r.get(t.target), a = e === "first" || n === "first", o = e === "second" || n === "second", c = (e === "first" || e === "second") && (n === "first" || n === "second");
		i.set(t.id, a && (o || c) ? "second" : "unrelated");
	}
	return {
		activeNodeId: n,
		nodeDepthById: r,
		edgeDepthById: i,
		firstNodeIds: a,
		secondNodeIds: o,
		directEdgeIds: s
	};
}
//#endregion
//#region src/render/render-pipeline.ts
var gc = "llm-wiki:graph:community-legend:collapsed";
function _c(e, t) {
	return !(!t || !e.nodes.length || e.focus?.kind === "community");
}
function vc(e, t) {
	pc(e.ownerDocument);
	let n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map();
	function i() {
		let i = e.runtimeState.snapshot(), s = bc(i);
		e.graph = mr(e.data, {
			pins: i.pins,
			theme: e.theme,
			selectedNodeId: s.selectedNodeId,
			selection: s.selection,
			focus: i.focus,
			typeFilters: {},
			aggregationMarkers: e.aggregationMarkers,
			pathCache: e.pathCache,
			viewportSize: A(),
			sourceCommunityId: e.sourceCommunityId
		}), e.runtimeState.setPositions(Sc(e.graph)), e.baseTypeFilters = e.graph.typeFilters, e.typeFilters = yc(e.typeFilters, e.baseTypeFilters), e.availableTypeFilters = e.typeFilters, e.graph.typeFilters = e.typeFilters, e.searchIndex = void 0, f(), e.pinState = new Ha(e.graph, e.runtimeState.snapshot().pins), e.hitTargetResolver.refresh(), Ac(e.root, e.theme), e.dom = a(e.graph, {
			hasHostReader: t.hasHostReader,
			handlers: {
				onNodeClick: (e, n) => {
					t.commands.handleNodeClick(e, n);
				},
				onNodeDoubleClick: (e) => t.commands.handleNodeDoubleClick(e),
				onNodePreviewEnter: (n) => {
					t.commands.setNodeHover(n), e.graph.focus?.kind !== "community" && t.commands.scheduleHoverPreview(n);
				},
				onEdgePreviewEnter: (e) => {
					t.commands.showEdgeHoverPreview(e);
				},
				onEdgePreviewLeave: () => {
					t.commands.clearHoverPreview();
				},
				onNodePreviewLeave: () => {
					if (e.graph.focus?.kind !== "community") {
						t.commands.clearHoverPreview(), t.commands.setNodeHover(null);
						return;
					}
					t.commands.cancelHoverPreviewOnly(), e.relationFocusClearTimer && clearTimeout(e.relationFocusClearTimer), e.relationFocusClearTimer = setTimeout(() => {
						e.relationFocusClearTimer = null, t.commands.setNodeHover(null);
					}, 80);
				},
				onAggregationContainerClick: (e) => {
					t.commands.selectAggregationContainer(e.communityId);
				}
			}
		}), delete e.root.dataset.relationFocusApplied, n.clear(), r.clear(), e.lastEffectiveDensityMode = null, o(), c(), t.commands.applySearchQuery(e.searchQuery), l(e.typeFilters), g(), _(), x(e.pinState.snapshot().pinnedNodeIds), C(e.runtimeState.snapshot().viewport), e.activeDiff && e.root.dataset.diffState === "playing" && N(e.activeDiff), t.overlays.renderReader(), t.overlays.renderSelectionPanel(), t.overlays.renderHoverPreview(), y();
	}
	function a(t, n) {
		return Zs({
			ownerDocument: e.ownerDocument,
			root: e.root,
			graph: t,
			theme: e.theme,
			hasHostReader: n.hasHostReader,
			handlers: n.handlers
		});
	}
	function o() {
		let n = ic(e.ownerDocument, {
			open: e.searchOpen,
			query: e.searchQuery,
			onOpen: () => t.commands.openSearch(),
			onQuery: (e) => t.commands.applySearchQuery(e),
			onNext: () => t.commands.focusNextSearchResult(),
			onPrevious: () => t.commands.focusPreviousSearchResult(),
			onActivate: () => t.commands.activateSearchResult(),
			onClose: () => t.commands.closeSearch()
		});
		e.dom.searchElement = n.element, e.dom.searchInput = n.input, e.dom.searchStatusElement = n.status, e.root.prepend(n.element), e.root.dataset.searchOpen = e.searchOpen ? "true" : "false";
	}
	function s() {
		let n = mi(e.graph.communities, e.graph.nodes), r = rc(e.ownerDocument, {
			rows: n,
			collapsed: e.legendCollapsed,
			onToggle: () => {
				e.legendCollapsed = !e.legendCollapsed, Oc(e.ownerDocument, e.legendCollapsed), s();
			},
			onHover: (e) => {
				t.commands.setCommunityHover(e), g();
			},
			onSelect: (e) => t.commands.selectCommunity(e)
		});
		e.dom.legendElement = r.element, e.dom.legendRows = r.rows, e.root.dataset.legendCollapsed = e.legendCollapsed ? "true" : "false";
	}
	function c() {
		s();
		let n = tc(e.ownerDocument, {
			panelState: e.toolbarPanelState,
			typeFilters: e.graph.typeFilters,
			onPanelToggle: (t) => {
				e.toolbarPanelState = Ji(e.toolbarPanelState, t), qi(e.ownerDocument.defaultView?.localStorage, e.toolbarPanelState), h(n);
			},
			onTypeFilterToggle: (t, n) => {
				l({
					...e.typeFilters,
					[t]: n
				});
			},
			onReset: () => {
				t.commands.requestGlobalReset();
			}
		});
		e.dom.legendElement && n.filtersPanel.appendChild(e.dom.legendElement), e.dom.toolbarElement = n.element, e.dom.toolbarPanelElement = n.panel, e.hasExternalToolbarContainer ? e.toolbarContainer.replaceChildren(n.element) : e.root.prepend(n.element), h(n);
	}
	function l(t) {
		e.typeFilters = yc(t, e.baseTypeFilters), e.graph.typeFilters = e.typeFilters;
		let n = p(e.temporaryObject, e.graph), r = /* @__PURE__ */ new Set();
		for (let [t, i] of e.dom.nodeElements) {
			let a = e.typeFilters[i.dataset.type || ""] === !1 && !n.has(t);
			i.dataset.filterState = a ? "hidden" : "visible", i.setAttribute("aria-hidden", a ? "true" : "false"), a && r.add(t);
		}
		for (let [t, i] of e.dom.edgeElements) {
			let a = e.graph.edges.find((e) => e.id === t), o = !a || !n.has(a.source) && !n.has(a.target) && (r.has(a.source) || r.has(a.target));
			i.dataset.filterState = o ? "hidden" : "visible", i.setAttribute("aria-hidden", o ? "true" : "false");
		}
		for (let [t, i] of e.dom.communityWashElements) {
			let a = e.graph.nodes.some((e) => e.community === t && (!r.has(e.id) || n.has(e.id)));
			i.dataset.filterState = a ? "visible" : "hidden", i.setAttribute("aria-hidden", a ? "false" : "true");
		}
		m(), f(), e.root.dataset.filteredNodeCount = String(r.size), e.root.dataset.typeFiltersActive = Object.values(e.typeFilters).some((e) => e === !1) ? "true" : "false", g(), _(), E();
	}
	function u(t) {
		e.temporaryObject = t, l(e.typeFilters);
	}
	function d() {
		e.temporaryObject = null, l(e.typeFilters);
	}
	function f() {
		let t = Ds(e.data.nodes, e.searchQuery, e.searchIndex);
		e.searchIndex = t.searchIndex, e.callbacks.onVisibilityStateChange?.({
			searchQuery: t.query,
			searchResultIds: t.matchIds,
			typeFilters: e.typeFilters,
			temporaryObject: e.temporaryObject
		});
	}
	function p(e, t) {
		if (!e || e.kind !== "node") return /* @__PURE__ */ new Set();
		let n = new Set([e.nodeId]);
		for (let r of t.edges) r.source === e.nodeId && n.add(r.target), r.target === e.nodeId && n.add(r.source);
		return n;
	}
	function m() {
		if (!e.dom.toolbarElement) return;
		let t = Array.from(e.dom.toolbarElement.querySelectorAll(".graph-type-filter input[data-type]"));
		for (let n of t) {
			let t = n.dataset.type || "";
			n.checked = e.typeFilters[t] !== !1;
		}
	}
	function h(t) {
		let n = e.toolbarPanelState !== "closed";
		t.element.dataset.panel = e.toolbarPanelState, t.panel.dataset.state = e.toolbarPanelState, t.buttons.filters.dataset.active = e.toolbarPanelState === "filters" ? "true" : "false", t.buttons.legend.dataset.active = e.toolbarPanelState === "legend" ? "true" : "false", e.root.dataset.toolbarPanel = e.toolbarPanelState, e.root.dataset.toolbarOpen = n ? "true" : "false", e.toolbarContainer.dataset.toolbarPanel = e.toolbarPanelState, e.toolbarContainer.dataset.toolbarOpen = n ? "true" : "false";
	}
	function g() {
		let t = e.runtimeState.snapshot().hover, n = t?.kind === "community" ? t.id : null;
		e.root.dataset.legendHover = n || "";
		for (let [t, r] of e.dom.legendRows) r.dataset.communityState = n ? t === n ? "active" : "faded" : "none";
		let r = /* @__PURE__ */ new Map();
		for (let [t, i] of e.dom.nodeElements) {
			let e = i.dataset.community || "";
			r.set(t, e), i.dataset.communityState = n ? e === n ? "active" : "faded" : "none";
		}
		for (let [t, r] of e.dom.communityWashElements) r.dataset.communityState = n ? t === n ? "active" : "faded" : "none";
		for (let t of e.dom.aggregationContainerElements.values()) {
			let e = t.dataset.communityId || "";
			t.dataset.communityState = n ? e === n ? "active" : "faded" : "none";
		}
		for (let t of e.graph.edges) {
			let i = e.dom.edgeElements.get(t.id);
			if (!i) continue;
			let a = r.get(t.source) === n && r.get(t.target) === n;
			i.dataset.communityState = n ? a ? "active" : "faded" : "none";
		}
	}
	function _() {
		let t = v();
		if (e.root.dataset.relationFocusNode === (t || "") && e.root.dataset.relationFocusApplied === "true") return;
		let i = hc({
			activeNodeId: t,
			nodes: e.graph.nodes,
			edges: e.graph.edges
		});
		e.root.dataset.relationFocus = i.activeNodeId ? "active" : "idle", e.root.dataset.relationFocusNode = i.activeNodeId || "", e.root.dataset.relationFocusApplied = "true";
		for (let [t, r] of e.dom.nodeElements) {
			let e = i.nodeDepthById.get(t) || "none";
			n.get(t) !== e && (r.dataset.relationFocusDepth = e, n.set(t, e));
		}
		for (let t of n.keys()) e.dom.nodeElements.has(t) || n.delete(t);
		for (let [t, n] of e.dom.edgeElements) {
			let e = i.edgeDepthById.get(t) || "none";
			r.get(t) !== e && (n.dataset.relationFocusDepth = e, r.set(t, e));
		}
		for (let t of r.keys()) e.dom.edgeElements.has(t) || r.delete(t);
	}
	function v() {
		if (e.graph.focus?.kind !== "community") return null;
		let t = e.runtimeState.snapshot().hover;
		return t?.kind === "node" && e.dom.nodeElements.has(t.id) ? t.id : e.graph.selectedNodeId;
	}
	function y() {
		if (e.simulation?.destroy(), e.simulation = null, _c(e.graph, t.live)) {
			e.simulation = Ya(e.graph, { onTick: (e) => b(e.positions) });
			for (let [t, n] of Object.entries(Ua(e.graph, e.runtimeState.snapshot().pins))) e.simulation.setFixed(t, n);
			e.simulation.startCold(), x(e.pinState.snapshot().pinnedNodeIds);
		}
	}
	function b(t) {
		if (e.destroyed) return;
		let n = e.runtimeState.setPositions(t), r = bc(n), i = e.graph.worldBounds, a = A();
		e.graph = mr(e.data, {
			pins: n.pins,
			theme: e.theme,
			selectedNodeId: r.selectedNodeId,
			selection: r.selection,
			focus: n.focus,
			typeFilters: {},
			positions: n.positions,
			aggregationMarkers: e.aggregationMarkers,
			pathCache: e.pathCache,
			viewportSize: a,
			sourceCommunityId: e.sourceCommunityId
		}), e.hitTargetResolver.refresh();
		let o = !Ec(i, e.graph.worldBounds);
		o && e.dom.svgElement && Tc(e.dom.svgElement, e.graph);
		let s = new Map(e.graph.nodes.map((e) => [e.id, e]));
		for (let t of e.graph.nodes) {
			let n = e.dom.nodeElements.get(t.id), r = e.dom.basePoints.get(t.id);
			if (!(!n || !r)) {
				if (o) n.style.left = `${t.x}%`, n.style.top = `${t.y}%`, n.style.translate = "calc(-50% + 0px) calc(-50% + 0px)", e.dom.basePoints.set(t.id, t.point);
				else {
					let i = bn(r, t.point, a, e.graph.worldBounds);
					n.style.translate = `calc(-50% + ${Q(i.x)}px) calc(-50% + ${Q(i.y)}px)`;
				}
				n.dataset.liveX = String(Q(t.point.x)), n.dataset.liveY = String(Q(t.point.y)), n.dataset.worldX = String(Q(t.point.x)), n.dataset.worldY = String(Q(t.point.y));
			}
		}
		for (let t of e.graph.edges) {
			let n = e.dom.edgeElements.get(t.id), r = s.get(t.source), i = s.get(t.target);
			!n || !r || !i || n.setAttribute("d", Cr(r.point, i.point, t.curveOffset));
		}
		for (let t of e.graph.communities) {
			let n = e.dom.communityWashElements.get(t.id);
			!n || !t.wash || (n.setAttribute("cx", String(t.wash.cx)), n.setAttribute("cy", String(t.wash.cy)), n.setAttribute("rx", String(t.wash.rx)), n.setAttribute("ry", String(t.wash.ry)), n.setAttribute("opacity", String(t.wash.opacity)));
		}
		for (let t of e.graph.minimap.nodes) {
			let n = e.dom.miniNodeElements.get(t.id);
			n && (n.setAttribute("cx", String(t.x)), n.setAttribute("cy", String(t.y)));
		}
		T();
	}
	function x(t) {
		let n = new Set(t);
		e.root.dataset.pinnedCount = String(n.size);
		for (let [t, r] of e.dom.nodeElements) r.classList.toggle("is-pinned", n.has(t)), r.dataset.pinned = n.has(t) ? "true" : "false", D(r);
	}
	function S() {
		let t = e.root.ownerDocument.defaultView?.ResizeObserver;
		t && (e.lastViewportSize = A(), e.resizeObserver = new t(() => {
			let t = e.lastViewportSize, n = A();
			if (Math.abs(t.width - n.width) < 1 && Math.abs(t.height - n.height) < 1) return;
			e.lastViewportSize = n;
			let r = xc(e), i = r ? e.graph.nodes.find((e) => e.id === r)?.point ?? null : null;
			O(!1), C(To(e.runtimeState.snapshot().viewport, t, n, {
				anchorPoint: i,
				worldBounds: e.graph.worldBounds
			}));
		}), e.resizeObserver.observe(e.root));
	}
	function C(t, n = {}) {
		j(), n.lightweight && k(!0);
		let r = e.runtimeState.setViewport(t).viewport;
		e.root.dataset.viewportScale = String(Q(r.scale)), e.dom.contentLayer && yo(e.dom.contentLayer, r), n.lightweight || w(), E(), n.lightweight || T();
		for (let t of e.dom.nodeElements.values()) D(t);
	}
	function w() {
		let t = kr(e.graph.counts.visibleNodes, e.runtimeState.snapshot().viewport.scale);
		if (e.root.dataset.density = t, e.root.dataset.effectiveDensity = t, t !== e.lastEffectiveDensityMode && (e.lastEffectiveDensityMode = t, e.graph.focus?.kind !== "community")) for (let n of e.graph.nodes) {
			let r = e.dom.nodeElements.get(n.id);
			r && zs(r, Ar(n, t));
		}
	}
	function T() {
		e.dom.readerElement?.dataset.state === "open" && t.overlays.renderReader(), e.dom.selectionElement?.dataset.state === "open" && t.overlays.renderSelectionPanel();
		let n = e.runtimeState.snapshot().hover;
		(n?.kind === "node" || n?.kind === "edge" || e.dom.previewElement?.dataset.state === "open") && t.overlays.renderHoverPreview();
	}
	function E() {
		if (!e.dom.miniViewportElement) return;
		let t = Eo(e.runtimeState.snapshot().viewport, A(), { worldBounds: e.graph.worldBounds });
		e.dom.miniViewportElement.setAttribute("x", String(Q(t.x))), e.dom.miniViewportElement.setAttribute("y", String(Q(t.y))), e.dom.miniViewportElement.setAttribute("width", String(Q(t.width))), e.dom.miniViewportElement.setAttribute("height", String(Q(t.height)));
	}
	function D(e) {
		let t = e.dataset.coreAnchor === "true" || e.dataset.searchBoost === "true" || e.dataset.interactionLabelVisible === "true" || e.dataset.pinned === "true" || e.getAttribute("aria-pressed") === "true";
		e.dataset.traceable = t ? "true" : "false";
	}
	function O(t) {
		e.viewportAnimationTimer &&= (clearTimeout(e.viewportAnimationTimer), null), e.root.dataset.viewportAnimating = t ? "true" : "false", e.dom.contentLayer?.classList.toggle("is-viewport-animating", t), t && (e.viewportAnimationTimer = setTimeout(() => O(!1), 240));
	}
	function k(t, n = {}) {
		if (e.interactionDegradationTimer &&= (clearTimeout(e.interactionDegradationTimer), null), e.root.dataset.interactionMode = t ? "active" : "idle", e.root.dataset.interactionUpdatedObjects = String(e.graph.interaction.updatedObjects), e.root.dataset.interactionHiddenObjects = String(e.graph.interaction.hiddenObjects), e.root.dataset.interactionPreservedNodes = String(e.graph.interaction.preservedNodeIds.length), t) {
			let t = n.restoreDelayMs ?? 180;
			e.interactionDegradationTimer = setTimeout(() => k(!1), t);
		}
	}
	function A() {
		let t = e.root.getBoundingClientRect(), n = kn();
		return {
			width: Math.max(1, t.width || n.width),
			height: Math.max(1, t.height || n.height)
		};
	}
	function j() {
		e.root.scrollLeft = 0, e.root.scrollTop = 0;
	}
	async function M(t, n = {}) {
		if (e.destroyed) return;
		let r = ++e.renderEpoch, i = n.reducedMotion ?? Mc(e.root.ownerDocument || document);
		if (e.activeDiff = t, e.root.dataset.diffState = i ? "settled" : "playing", e.root.dataset.diffAddedNodes = String(t.addedNodes.length), e.root.dataset.diffAddedEdges = String(t.addedEdges.length), e.root.dataset.diffRemovedNodes = String(t.removedNodes.length), e.root.dataset.diffNewCommunities = String(t.newCommunities.length), N(t), i) {
			e.root.dataset.diffReducedMotion = "true", P();
			return;
		}
		delete e.root.dataset.diffReducedMotion, await Nc(kc(n.durationMs ?? jc(t), 420, 3e3)), !e.destroyed && e.renderEpoch === r && P();
	}
	function N(t) {
		let n = new Set(t.addedNodes), r = new Set(t.removedNodes), i = new Set(t.recoloredNodes.map((e) => e.id)), a = new Set(t.addedEdges), o = new Set(t.removedEdges), s = new Set(t.newCommunities), c = new Map(e.graph.nodes.map((e) => [e.id, e]));
		for (let [a, o] of e.dom.nodeElements) {
			o.classList.toggle("is-diff-added", n.has(a)), o.classList.toggle("is-diff-removed", r.has(a)), o.classList.toggle("is-diff-recolored", i.has(a));
			let e = t.addedNodes.indexOf(a);
			o.style.setProperty("--diff-delay", e >= 0 ? `${Math.min(e * 55, 550)}ms` : "0ms");
			let s = n.has(a) ? F(a) : null, l = c.get(a);
			s ? (o.style.setProperty("--diff-anchor-dx", `${Q(s.x - (l?.point.x ?? s.x))}px`), o.style.setProperty("--diff-anchor-dy", `${Q(s.y - (l?.point.y ?? s.y))}px`)) : (o.style.removeProperty("--diff-anchor-dx"), o.style.removeProperty("--diff-anchor-dy"));
		}
		for (let [t, n] of e.dom.edgeElements) if (n.classList.toggle("is-diff-added", a.has(t)), n.classList.toggle("is-diff-removed", o.has(t)), a.has(t)) {
			let e = Math.max(1, Math.ceil(typeof n.getTotalLength == "function" ? n.getTotalLength() : 180));
			n.style.setProperty("--diff-edge-length", String(e));
		} else n.style.removeProperty("--diff-edge-length");
		for (let [t, n] of e.dom.communityWashElements) n.classList.toggle("is-diff-new-community", s.has(t));
	}
	function P() {
		e.activeDiff = null, e.root.dataset.diffState = "settled";
		for (let t of e.dom.nodeElements.values()) t.classList.remove("is-diff-added", "is-diff-removed", "is-diff-recolored"), t.style.removeProperty("--diff-anchor-dx"), t.style.removeProperty("--diff-anchor-dy"), t.style.removeProperty("--diff-delay");
		for (let t of e.dom.edgeElements.values()) t.classList.remove("is-diff-added", "is-diff-removed"), t.style.removeProperty("--diff-edge-length");
		for (let t of e.dom.communityWashElements.values()) t.classList.remove("is-diff-new-community");
	}
	function F(t) {
		let n = e.graph.nodes.find((e) => e.id === t);
		if (!n) return null;
		let r = e.graph.edges.filter((e) => e.source === t || e.target === t).map((e) => e.source === t ? e.target : e.source).find((e) => e !== t), i = r ? e.graph.nodes.find((e) => e.id === r) : null;
		return i ? i.point : An(n.point, 80, e.graph.worldBounds);
	}
	function ee() {
		e.simulation?.destroy(), e.simulation = null, e.resizeObserver?.disconnect(), e.resizeObserver = null, e.viewportAnimationTimer && clearTimeout(e.viewportAnimationTimer), e.viewportAnimationTimer = null, e.interactionDegradationTimer && clearTimeout(e.interactionDegradationTimer), e.interactionDegradationTimer = null, e.relationFocusClearTimer && clearTimeout(e.relationFocusClearTimer), e.relationFocusClearTimer = null;
	}
	return {
		rebuildAndPaint: i,
		paint: a,
		mountSearchControl: o,
		mountGraphToolbar: c,
		mountCommunityLegend: s,
		applyTypeFilters: l,
		showTemporaryObject: u,
		clearTemporaryObjectDisplay: d,
		applyCommunityHover: g,
		applyRelationFocus: _,
		bindResizeObserver: S,
		commitViewport: C,
		resetRootScroll: j,
		updateEffectiveDensity: w,
		renderMotionOverlays: T,
		updateMinimapViewport: E,
		setViewportAnimating: O,
		setInteractionDegraded: k,
		viewportSize: A,
		restartSimulation: y,
		applyMotionFrame: b,
		markPinnedNodes: x,
		animateDiff: M,
		markDiffElements: N,
		settleDiffElements: P,
		semanticAnchorForNode: F,
		destroy: ee
	};
}
function yc(e, t) {
	let n = {}, r = new Set([...Object.keys(t), ...Object.keys(e)]);
	for (let t of r) n[t] = e[t] !== !1;
	return n;
}
function bc(e) {
	return e.selectionSurface === "reader" && e.selection?.kind === "node" ? {
		selectedNodeId: e.selection.id,
		selection: null
	} : {
		selectedNodeId: null,
		selection: e.selection
	};
}
function xc(e) {
	let t = e.runtimeState.snapshot();
	return t.selectionSurface === "reader" && t.selection?.kind === "node" ? t.selection.id : null;
}
function Sc(e) {
	return Object.fromEntries(e.nodes.map((e) => [e.id, {
		x: e.point.x,
		y: e.point.y
	}]));
}
function Cc(e) {
	let t = e.getBoundingClientRect(), n = kn();
	return {
		width: t.width || n.width,
		height: t.height || n.height
	};
}
function wc() {
	return {
		contentLayer: null,
		svgElement: null,
		edgeElements: /* @__PURE__ */ new Map(),
		communityWashElements: /* @__PURE__ */ new Map(),
		aggregationContainerElements: /* @__PURE__ */ new Map(),
		nodeElements: /* @__PURE__ */ new Map(),
		miniNodeElements: /* @__PURE__ */ new Map(),
		miniViewportElement: null,
		basePoints: /* @__PURE__ */ new Map(),
		readerElement: null,
		selectionElement: null,
		searchElement: null,
		searchInput: null,
		searchStatusElement: null,
		toolbarElement: null,
		toolbarPanelElement: null,
		legendElement: null,
		legendRows: /* @__PURE__ */ new Map(),
		previewElement: null
	};
}
function Tc(e, t) {
	e.setAttribute("viewBox", `${Q(t.worldBounds.minX)} ${Q(t.worldBounds.minY)} ${Q(t.worldBounds.width)} ${Q(t.worldBounds.height)}`);
}
function Ec(e, t) {
	let n = .5;
	return Math.abs(e.minX - t.minX) < n && Math.abs(e.minY - t.minY) < n && Math.abs(e.maxX - t.maxX) < n && Math.abs(e.maxY - t.maxY) < n && Math.abs(e.width - t.width) < n && Math.abs(e.height - t.height) < n;
}
function Dc(e) {
	try {
		return e.defaultView?.localStorage?.getItem(gc) === "true";
	} catch {
		return !1;
	}
}
function Oc(e, t) {
	try {
		e.defaultView?.localStorage?.setItem(gc, t ? "true" : "false");
	} catch {}
}
function kc(e, t, n) {
	return Math.max(t, Math.min(n, e));
}
function Q(e) {
	return Math.round(e * 1e3) / 1e3;
}
function Ac(e, t) {
	e.dataset.theme = t, e.style.colorScheme = ln(t).colorScheme;
	let n = un(t);
	for (let [t, r] of Object.entries(n)) e.style.setProperty(t, r);
}
function jc(e) {
	let t = e.addedNodes.length + e.addedEdges.length + e.removedNodes.length + e.removedEdges.length + e.newCommunities.length;
	return Math.min(2600, 520 + t * 80);
}
function Mc(e) {
	return !!e.defaultView?.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}
function Nc(e) {
	return new Promise((t) => setTimeout(t, e));
}
//#endregion
//#region src/render/preview.ts
var Pc = 140;
function Fc(e) {
	let t = String(e.label || e.id || "");
	return {
		id: String(e.id || t),
		title: t,
		typeLabel: Be(e.type),
		summary: Ic(e)
	};
}
function Ic(e) {
	let t = Rc(String(e.summary || ""));
	if (t) return zc(t);
	let n = Lc(String(e.content || ""));
	return n ? zc(Rc(n)) : "";
}
function Lc(e) {
	let t = String(e || "").replace(/^---[\s\S]*?---\s*/, "").split(/\r?\n/), n = [], r = [], i = !1;
	for (let e of t) {
		let t = e.trim();
		if (/^```/.test(t)) {
			i = !i;
			continue;
		}
		if (!(i || /^#{1,6}\s+/.test(t))) {
			if (!t) {
				r.length && (n.push(r.join("\n")), r = []);
				continue;
			}
			r.push(e);
		}
	}
	return r.length && n.push(r.join("\n")), n.map(Rc).find(Boolean) || "";
}
function Rc(e) {
	return tt(e).replace(/\s+/g, " ").trim();
}
function zc(e) {
	return e.length <= Pc ? e : `${e.slice(0, Pc).trim()}...`;
}
//#endregion
//#region src/render/hover-card.ts
function Bc(e, t) {
	let n = e.createElement("article");
	n.className = "graph-hover-preview-card";
	let r = e.createElement("div");
	r.className = "graph-hover-preview-type", r.textContent = t.typeLabel;
	let i = e.createElement("div");
	if (i.className = "graph-hover-preview-title", i.textContent = t.title, n.append(r, i), t.summary) {
		let r = e.createElement("p");
		r.className = "graph-hover-preview-summary", r.textContent = t.summary, n.appendChild(r);
	}
	return n;
}
function Vc(e, t, n) {
	let r = e.createElement("article");
	r.className = "graph-hover-preview-card graph-edge-hover-card";
	let i = e.createElement("div");
	i.className = "graph-hover-preview-type", i.textContent = "关系";
	let a = e.createElement("div");
	a.className = "graph-hover-preview-title", a.textContent = t;
	let o = e.createElement("p");
	return o.className = "graph-hover-preview-summary", o.textContent = `置信度：${qs(n)}`, r.append(i, a, o), r;
}
//#endregion
//#region src/render/offline-reader.ts
function Hc(e, t, n) {
	let { selected: r, rawNode: i } = n;
	if (t.dataset.state = r ? "open" : "closed", t.replaceChildren(), !r || !i) {
		let n = e.createElement("p");
		n.className = "graph-reader-empty", n.textContent = "选择一个节点查看内容", t.appendChild(n);
		return;
	}
	let a = e.createElement("div");
	a.className = "graph-reader-header";
	let o = e.createElement("div");
	o.className = "graph-reader-title", o.textContent = r.label;
	let s = Kc(i), c = e.createElement("div");
	c.className = "graph-reader-meta";
	for (let t of Yc(s)) {
		let n = e.createElement("span");
		n.textContent = t, c.appendChild(n);
	}
	let l = e.createElement("button");
	l.type = "button", l.className = "graph-reader-close", l.setAttribute("aria-label", "关闭阅读面板"), l.textContent = "×", l.addEventListener("click", n.onClose), a.append(o, c, l);
	let u = e.createElement("div");
	if (u.className = "graph-reader-body", s.type === "source" && s.sourcePath) {
		let t = e.createElement("a");
		t.className = "graph-reader-source", t.href = s.sourcePath, t.textContent = s.sourcePath, u.appendChild(t);
	}
	let d = String(i.content || i.summary || r.label), f = Xc(d);
	if (f) {
		let t = e.createElement("article");
		t.className = "graph-reader-markdown", t.innerHTML = f, u.appendChild(t);
	} else {
		let t = e.createElement("pre");
		t.textContent = d, u.appendChild(t);
	}
	t.append(a, u);
}
function Uc(e, t, n) {
	if (t.replaceChildren(), t.dataset.state = n.selection ? "open" : "closed", !n.selection || !n.facts) {
		let n = e.createElement("p");
		n.className = "graph-selection-empty", n.textContent = "Shift+点击 可选择多个节点", t.appendChild(n);
		return;
	}
	let r = e.createElement("div");
	r.className = "graph-selection-header";
	let i = e.createElement("div");
	i.className = "graph-selection-title", i.textContent = Gc(n.selection, n.selectedNodes.length);
	let o = e.createElement("button");
	o.type = "button", o.className = "graph-selection-close", o.setAttribute("aria-label", "关闭选区面板"), o.textContent = "×", o.addEventListener("click", n.onClose), r.append(i, o);
	let s = e.createElement("div");
	s.className = "graph-selection-hint", s.textContent = "Shift+点击 增删节点";
	let c = e.createElement("div");
	c.className = "graph-selection-facts", c.append(Wc(e, "页面", n.facts.pageCount), Wc(e, "内部关联", n.facts.internalLinkCount), Wc(e, "社区", n.facts.communityCount), Wc(e, "孤立页", n.facts.isolatedCount));
	let l = e.createElement("ol");
	l.className = "graph-selection-pages";
	for (let t of n.selectedNodes) {
		let n = e.createElement("li");
		n.className = "graph-selection-page";
		let r = e.createElement("span");
		r.className = "graph-selection-page-title", r.textContent = t.label || t.id;
		let i = e.createElement("span");
		i.className = "graph-selection-page-path", i.textContent = a(t), n.append(r, i), l.appendChild(n);
	}
	t.append(r, s, c, l);
}
function Wc(e, t, n) {
	let r = e.createElement("div");
	r.className = "graph-selection-fact";
	let i = e.createElement("strong");
	i.textContent = String(n);
	let a = e.createElement("span");
	return a.textContent = t, r.append(i, a), r;
}
function Gc(e, t) {
	return e.kind === "community" ? `社区选区 · ${t} 页` : e.kind === "neighbors" ? `相邻节点 · ${t} 页` : e.kind === "node" ? "选中页面" : `手动选区 · ${t} 页`;
}
function Kc(e) {
	let t = a(e);
	return {
		type: e.type,
		typeLabel: s(e.type),
		sourcePath: t,
		date: qc(e),
		source: Jc(e)
	};
}
function qc(e) {
	let t = e.date || e.updated_at || e.updatedAt || e.created_at || e.createdAt;
	return t == null || t === "" ? null : String(t);
}
function Jc(e) {
	let t = e.source_title || e.source_url || e.url || e.author || e.source_name;
	return t == null || t === "" ? null : String(t);
}
function Yc(e) {
	let t = [e.typeLabel];
	return e.date && t.push(e.date), e.source && t.push(e.source), t;
}
function Xc(e) {
	let t = globalThis;
	if (typeof t.marked?.parse != "function" || typeof t.DOMPurify?.sanitize != "function") return null;
	let n = t.marked.parse(e, {
		breaks: !1,
		gfm: !0
	});
	return t.DOMPurify.sanitize(n, { ADD_ATTR: [
		"target",
		"data-target",
		"tabindex"
	] });
}
//#endregion
//#region src/render/overlays.ts
function Zc(e, t, n, r) {
	return _n(e.point, t, n, r);
}
function Qc(e, t, n, r) {
	if (!e.source || !e.target) return {
		x: n.width / 2,
		y: n.height / 2
	};
	let i = _n(e.source.point, t, n, r), a = _n(e.target.point, t, n, r);
	return {
		x: (i.x + a.x) / 2,
		y: (i.y + a.y) / 2
	};
}
function $c(e) {
	let t = tl(e.margin, 12), n = e.anchorScreenPoint.x + tl(e.offset.x, 0), r = e.anchorScreenPoint.y + tl(e.offset.y, 0), i = Math.max(t, e.viewportSize.width - tl(e.previewSize.width, 0) - t), a = Math.max(t, e.viewportSize.height - tl(e.previewSize.height, 0) - t);
	return {
		x: el(n, t, i),
		y: el(r, t, a)
	};
}
function el(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
function tl(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/overlays-presenter.ts
function nl(e, t) {
	function n(t = e.runtimeState.snapshot()) {
		return t.selectionSurface === "selection-panel" ? t.selection : null;
	}
	function r() {
		let n = e.dom.readerElement;
		if (!n) return;
		let r = e.graph.selectedNodeId ? e.graph.nodes.find((t) => t.id === e.graph.selectedNodeId) : null, i = r ? e.data.nodes.find((e) => e.id === r.id) : null;
		Hc(e.ownerDocument, n, {
			selected: r ? {
				id: r.id,
				label: r.label,
				type: r.type,
				content: i?.content ? String(i.content) : void 0,
				summary: i?.summary ? String(i.summary) : void 0
			} : null,
			rawNode: i || null,
			onClose: () => t.clearInteractionState()
		});
	}
	function i() {
		let r = e.dom.selectionElement;
		if (!r) return;
		let i = n(), a = i ? yi(e.data, i, { canAsk: !1 }) : null, o = a ? a.nodeIds.map((t) => e.data.nodes.find((e) => e.id === t)).filter((e) => !!e) : [];
		Uc(e.ownerDocument, r, {
			selection: i,
			selectedNodes: o,
			facts: a?.facts || null,
			onClose: () => t.clearInteractionState()
		});
	}
	function a(t) {
		e.graph.focus?.kind !== "community" && (e.previewTimer && clearTimeout(e.previewTimer), e.previewTimer = setTimeout(() => {
			e.previewTimer = null;
			let n = e.runtimeState.snapshot().hover;
			n?.kind !== "node" || n.id !== t || u();
		}, 300));
	}
	function o(t) {
		e.previewTimer &&= (clearTimeout(e.previewTimer), null), l({
			kind: "edge",
			id: t
		}), u();
	}
	function s() {
		e.previewTimer &&= (clearTimeout(e.previewTimer), null);
		let t = e.runtimeState.snapshot().hover;
		t?.kind !== "node" && t?.kind !== "edge" || (l(null), u());
	}
	function c() {
		e.previewTimer &&= (clearTimeout(e.previewTimer), null), e.dom.previewElement?.dataset.kind === "node" && (e.dom.previewElement.dataset.state = "closed", e.dom.previewElement.replaceChildren());
	}
	function l(t) {
		return e.runtimeState.setHover(t);
	}
	function u() {
		let t = e.dom.previewElement;
		if (!t) return;
		let n = e.runtimeState.snapshot().hover, r = n?.kind === "edge" ? e.graph.edges.find((e) => e.id === n.id) : null, i = n?.kind === "node" ? e.data.nodes.find((e) => e.id === n.id) : null, a = n?.kind === "node" ? e.graph.nodes.find((e) => e.id === n.id) : null;
		if (t.replaceChildren(), t.dataset.kind = r ? "edge" : "node", r) {
			t.dataset.state = "open", t.append(Vc(e.ownerDocument, r.relationType, r.confidence)), f(t, r);
			return;
		}
		if (n?.kind === "node" && e.graph.focus?.kind === "community") {
			t.dataset.state = "closed";
			return;
		}
		if (t.dataset.state = i && a ? "open" : "closed", !i || !a) return;
		let o = Fc(i);
		t.append(Bc(e.ownerDocument, o)), d(t, a);
	}
	function d(n, r) {
		let i = n.getBoundingClientRect(), a = t.viewportSize(), o = $c({
			anchorScreenPoint: Zc(r, e.runtimeState.snapshot().viewport, a, e.graph.worldBounds),
			previewSize: {
				width: i.width,
				height: i.height
			},
			viewportSize: a,
			offset: {
				x: 18,
				y: -i.height - 24
			},
			margin: 12
		});
		n.style.left = `${o.x}px`, n.style.top = `${o.y}px`;
	}
	function f(n, r) {
		let i = n.getBoundingClientRect(), a = e.graph.nodes.find((e) => e.id === r.source), o = e.graph.nodes.find((e) => e.id === r.target), s = t.viewportSize(), c = $c({
			anchorScreenPoint: Qc({
				source: a,
				target: o
			}, e.runtimeState.snapshot().viewport, s, e.graph.worldBounds),
			previewSize: {
				width: i.width,
				height: i.height
			},
			viewportSize: s,
			offset: {
				x: 16,
				y: -i.height - 16
			},
			margin: 12
		});
		n.style.left = `${c.x}px`, n.style.top = `${c.y}px`;
	}
	function p() {
		e.previewTimer && clearTimeout(e.previewTimer), e.previewTimer = null;
	}
	return {
		scheduleHoverPreview: a,
		showEdgeHoverPreview: o,
		clearHoverPreview: s,
		cancelHoverPreviewOnly: c,
		setGraphHover: l,
		renderHoverPreview: u,
		renderReader: r,
		renderSelectionPanel: i,
		destroy: p
	};
}
//#endregion
//#region src/render/renderer-surface.ts
function rl(e) {
	return {
		focusRoot(t) {
			e.root.focus(t);
		},
		focusNode(t, n) {
			e.dom().nodeElements.get(t)?.focus(n);
		},
		setNodeDragging(t, n) {
			e.dom().nodeElements.get(t)?.classList.toggle("is-dragging", n);
		},
		clearNodeDragging() {
			for (let t of e.dom().nodeElements.values()) t.classList.remove("is-dragging");
		},
		setViewportDragging(t) {
			t ? e.root.dataset.viewportDragging = "true" : delete e.root.dataset.viewportDragging;
		},
		setDragTarget(t) {
			t ? e.root.dataset.dragging = t : delete e.root.dataset.dragging;
		},
		setFocusDataset(t) {
			t ? e.root.dataset.focus = "true" : delete e.root.dataset.focus;
		},
		setSearchOpen(t) {
			e.root.dataset.searchOpen = t ? "true" : "false";
			let { searchElement: n } = e.dom();
			n && (n.dataset.state = t ? "open" : "closed");
		},
		setSearchState(t) {
			e.root.dataset.searchActive = t.query ? "true" : "false", e.root.dataset.searchQuery = t.query;
			let n = t.focusedNodeId;
			for (let r of t.nodes) {
				let t = e.dom().nodeElements.get(r.id);
				t && (t.dataset.searchState = r.searchState, t.dataset.searchFocus = r.id === n ? "true" : "false", t.dataset.searchBoost = r.searchState === "match" || r.id === n ? "true" : "false", t.dataset.traceable = t.dataset.coreAnchor === "true" || t.dataset.temporaryBoost === "true" || t.dataset.searchBoost === "true" || t.dataset.pinned === "true" || t.getAttribute("aria-pressed") === "true" ? "true" : "false");
			}
		}
	};
}
//#endregion
//#region src/render/graph-renderer-root.ts
var il = 1.5;
function al(e, t) {
	let n = t.pins || {}, r = t.focus || null, i = pr(), a = qo(e), o = t.toolbarContainer || a, s = o !== a, c = e.ownerDocument || document, l, u, d, f, p = mr(t.data, {
		pins: n,
		theme: t.theme,
		selectedNodeId: null,
		selection: null,
		focus: r,
		typeFilters: {},
		pathCache: i,
		aggregationMarkers: t.aggregationMarkers,
		sourceCommunityId: t.sourceCommunityId ?? null
	}), m = Lo({
		viewport: so,
		positions: Sc(p),
		pins: n,
		selection: null,
		selectionSurface: null,
		focus: r
	}), h = gs({
		graph: () => l.graph,
		viewport: () => l.runtimeState.snapshot().viewport,
		viewportSize: () => d.viewportSize()
	});
	l = {
		data: t.data,
		theme: t.theme,
		destroyed: !1,
		simulation: null,
		dom: wc(),
		activeDiff: null,
		searchOpen: !1,
		searchQuery: t.searchQuery || "",
		searchFocusedNodeId: null,
		typeFilters: t.typeFilters || {},
		aggregationMarkers: t.aggregationMarkers || [],
		baseTypeFilters: {},
		availableTypeFilters: {},
		temporaryObject: null,
		searchIndex: void 0,
		previewTimer: null,
		pathCache: i,
		root: a,
		rendererSurface: rl({
			root: a,
			dom: () => l.dom
		}),
		toolbarContainer: o,
		hasExternalToolbarContainer: s,
		ownerDocument: c,
		legendCollapsed: Dc(c),
		toolbarPanelState: Ki(c.defaultView?.localStorage),
		viewportCommitter: Do((e, t) => {
			d.commitViewport(e, t);
		}, a.ownerDocument.defaultView || void 0),
		gestureMachine: new os({ dragThreshold: 4 }),
		gestureController: null,
		viewportAnimationTimer: null,
		interactionDegradationTimer: null,
		relationFocusClearTimer: null,
		lastEffectiveDensityMode: null,
		lastViewportSize: Cc(a),
		resizeObserver: null,
		graph: p,
		runtimeState: m,
		hitTargetResolver: h,
		pinState: new Ha(p, m.snapshot().pins),
		renderEpoch: 0,
		callbacks: {
			onNodeOpen: t.onNodeOpen,
			onSelectionInput: t.onSelectionInput,
			onSelectionClearRequested: t.onSelectionClearRequested,
			onViewReset: t.onViewReset,
			onGlobalResetRequested: t.onGlobalResetRequested,
			onPinsChanged: t.onPinsChanged,
			onDragActiveChange: t.onDragActiveChange,
			onVisibilityStateChange: t.onVisibilityStateChange
		},
		sourceCommunityId: t.sourceCommunityId ?? null
	}, f = nl(l, {
		viewportSize: () => d.viewportSize(),
		clearInteractionState: () => u.clearInteractionState()
	}), u = Ps(l, {
		render: g,
		viewportSize: () => d.viewportSize(),
		setViewportAnimating: (e) => d.setViewportAnimating(e),
		setInteractionDegraded: (e, t) => d.setInteractionDegraded(e, t),
		setGraphHover: (e) => f.setGraphHover(e),
		applyMotionFrame: (e) => d.applyMotionFrame(e),
		markPinnedNodes: (e) => d.markPinnedNodes(e),
		focusFitMaxScale: il
	}), d = vc(l, {
		hasHostReader: !!l.callbacks.onNodeOpen,
		live: t.live !== !1,
		commands: {
			render: g,
			resetViewState: () => u.resetViewState(),
			requestGlobalReset: () => {
				if (l.callbacks.onGlobalResetRequested) {
					l.callbacks.onGlobalResetRequested();
					return;
				}
				u.resetViewState();
			},
			openSearch: () => u.openSearch(),
			applySearchQuery: (e) => u.applySearchQuery(e),
			focusNextSearchResult: () => u.focusNextSearchResult(),
			focusPreviousSearchResult: () => u.focusPreviousSearchResult(),
			activateSearchResult: () => u.activateSearchResult(),
			closeSearch: () => u.closeSearch(),
			selectCommunity: (e) => u.selectCommunity(e),
			selectAggregationContainer: (e) => {
				e && u.selectCommunity(e);
			},
			setCommunityHover: (e) => u.setCommunityHover(e),
			handleNodeClick: (e, t) => u.handleNodeClick(e, t),
			handleNodeDoubleClick: (e) => u.handleNodeDoubleClick(e),
			setNodeFixed: (e, t) => u.setNodeFixed(e, t),
			setNodeHover: (e) => {
				l.relationFocusClearTimer && (clearTimeout(l.relationFocusClearTimer), l.relationFocusClearTimer = null), f.setGraphHover(e ? {
					kind: "node",
					id: e
				} : null), d.applyRelationFocus();
			},
			scheduleHoverPreview: (e) => f.scheduleHoverPreview(e),
			showEdgeHoverPreview: (e) => {
				f.showEdgeHoverPreview(e), d.applyRelationFocus();
			},
			clearHoverPreview: () => {
				f.clearHoverPreview(), d.applyRelationFocus();
			},
			cancelHoverPreviewOnly: () => {
				f.cancelHoverPreviewOnly();
			}
		},
		overlays: {
			renderReader: () => f.renderReader(),
			renderSelectionPanel: () => f.renderSelectionPanel(),
			renderHoverPreview: () => f.renderHoverPreview()
		}
	}), l.root.addEventListener("scroll", d.resetRootScroll, { passive: !0 }), l.ownerDocument.addEventListener("keydown", u.handleDocumentKeydown), l.gestureController = u.bindViewportHandlers(), d.bindResizeObserver();
	function g(e = {}) {
		v(), l.renderEpoch += 1, d.settleDiffElements(), delete l.root.dataset.diffState, delete l.root.dataset.diffAddedNodes, delete l.root.dataset.diffAddedEdges, delete l.root.dataset.diffRemovedNodes, delete l.root.dataset.diffNewCommunities, delete l.root.dataset.diffReducedMotion, _(e), d.rebuildAndPaint();
	}
	function _(e) {
		if (l.data = e.data || l.data, l.theme = e.theme || l.theme, Object.hasOwn(e, "typeFilters") && (l.typeFilters = e.typeFilters || {}), Object.hasOwn(e, "aggregationMarkers") && (l.aggregationMarkers = e.aggregationMarkers || []), Object.hasOwn(e, "sourceCommunityId") && (l.sourceCommunityId = e.sourceCommunityId || null), Object.hasOwn(e, "pins") && l.runtimeState.setPins(e.pins || {}), Object.hasOwn(e, "focus") && l.runtimeState.setFocus(e.focus || null), Object.hasOwn(e, "selectedNodeId")) {
			let t = e.selectedNodeId || null;
			l.runtimeState.setSelection(t ? {
				kind: "node",
				id: t
			} : null, t ? "reader" : null);
		}
		Object.hasOwn(e, "selection") && l.runtimeState.setSelection(e.selection || null, e.selection ? "selection-panel" : null);
	}
	return g(), {
		root: l.root,
		get graph() {
			return l.graph;
		},
		render: g,
		applyDiff(e, t = {}) {
			return v(), d.animateDiff(e, t);
		},
		isDragging() {
			return l.runtimeState.snapshot().activeGesture?.kind === "node-drag";
		},
		setData(e, t) {
			u.clearTransientInteractionForDataRefresh(), g({
				data: e,
				pins: t ?? l.runtimeState.snapshot().pins
			});
		},
		setAggregationMarkers(e) {
			g({ aggregationMarkers: e });
		},
		setTheme(e) {
			g({ theme: e });
		},
		setPins(e) {
			g({ pins: e });
		},
		focusNode(e) {
			let t = l.graph.nodes.find((t) => t.id === e || t.sourcePath === e);
			g({ selectedNodeId: t ? t.id : null }), l.root.dataset.focus = e;
		},
		focusCommunity(e) {
			u.focusCommunity(e);
		},
		setSourceCommunityContext(e) {
			g({ sourceCommunityId: e });
		},
		setTypeFilters(e) {
			d.applyTypeFilters(e);
		},
		showTemporaryObject(e) {
			d.showTemporaryObject(e);
		},
		clearTemporaryObjectDisplay() {
			d.clearTemporaryObjectDisplay();
		},
		resetView() {
			u.resetViewState();
		},
		select(e) {
			g({ selection: e });
		},
		previewNode(e) {
			e ? f.setGraphHover({
				kind: "node",
				id: e
			}) : f.clearHoverPreview(), d.applyRelationFocus(), f.renderHoverPreview();
		},
		clearSelection() {
			u.clearSelectionOnly();
		},
		clearInteraction() {
			u.clearInteractionState();
		},
		resetLayout() {
			let e = l.pinState.reset();
			g({ pins: e.pins }), l.callbacks.onPinsChanged?.(e.pins);
		},
		setNodeFixed(e, t) {
			return u.setNodeFixed(e, t);
		},
		destroy() {
			l.destroyed || (l.destroyed = !0, d.destroy(), f.destroy(), l.root.removeEventListener("scroll", d.resetRootScroll), l.ownerDocument.removeEventListener("keydown", u.handleDocumentKeydown), l.gestureController?.destroy(), l.gestureController = null, l.pathCache.clear(), l.root.remove(), l.hasExternalToolbarContainer && l.dom.toolbarElement && l.toolbarContainer.contains(l.dom.toolbarElement) && l.toolbarContainer.replaceChildren());
		}
	};
	function v() {
		if (l.destroyed) throw Error("Graph renderer has been destroyed");
	}
}
//#endregion
//#region src/summary/index.ts
var ol = 5;
function sl(e, t, n = {}) {
	let r = ml(e), i = r.nodeById.get(t);
	if (!i) return fl(e, {
		kind: "node",
		nodeId: t
	}, "missing-node", n);
	let o = Al(i, n.pins), s = Sl(e, {
		kind: "node",
		nodeId: t
	}, n.selection), c = hl(e, r, t), l = wl(i, o);
	return Hl(n.temporaryObject, {
		kind: "node",
		nodeId: t
	}) && l.push({
		kind: "clear-temporary-object-display",
		label: "清除临时显示"
	}), {
		kind: "node-summary",
		object: {
			kind: "node",
			nodeId: t
		},
		nodeId: t,
		label: i.label || i.id,
		type: i.type,
		communityId: i.community ?? null,
		sourcePath: a(i),
		summary: Wl(i.summary) ?? Wl(i.content),
		connectionCount: r.edgesByNodeId.get(t)?.length ?? 0,
		searchHit: Vl(n).has(t),
		pinHint: o,
		selection: s,
		strongestRelations: _l(c, ol),
		bridgeRelations: _l(c.filter((e) => e.bridge), ol),
		aggregationMarkers: Rl(n.aggregationMarkers, t),
		commands: l
	};
}
function cl(e, t, n = {}) {
	let r = Ml(e, t), i = e.learning?.communities.find((e) => e.id === t) ?? null;
	if (r.length === 0 && !i) return fl(e, {
		kind: "community",
		communityId: t
	}, "missing-community", n);
	let a = ml(e), o = new Set(r.map((e) => e.id)), s = e.edges.filter((e) => o.has(Gl(e.from) || "") || o.has(Gl(e.to) || "")), c = gl(e, s, a), l = (n.searchResultIds ?? []).filter((e) => o.has(e)), u = r.map((e) => Al(e, n.pins)).filter((e) => e.pinned), d = vl(r, o, s, a), f = Ol(t, d.pageCount, d.internalLinkCount, d.isolatedCount), p = t !== "_none" && r.length > 0, m = yl(e, r, ol, bl(e, a));
	return {
		kind: "community-summary",
		object: {
			kind: "community",
			communityId: t
		},
		communityId: t,
		label: El(i?.label, t),
		nodeCount: Number(i?.node_count ?? r.length),
		facts: d,
		structureState: f,
		description: Dl(f),
		canEnterCommunity: p,
		coreNodeIds: m,
		coreNodes: kl(a, m),
		searchResultIds: l,
		pinHints: u,
		selection: Sl(e, {
			kind: "community",
			communityId: t
		}, n.selection),
		strongestRelations: _l(c, ol),
		bridgeRelations: _l(c.filter((e) => e.bridge), ol),
		aggregationMarkers: zl(n.aggregationMarkers, t),
		commands: Tl(t, p)
	};
}
function ll(e, t = {}) {
	let n = Pl(e, t.searchResultIds ?? []), r = e.nodes.map((e) => Al(e, t.pins)).filter((e) => e.pinned);
	return {
		kind: "global-overview",
		nodeCount: e.nodes.length,
		edgeCount: e.edges.length,
		communityCount: Fl(e).length,
		coreNodeIds: yl(e, e.nodes),
		searchResultIds: n,
		pinHints: r,
		selection: Sl(e, null, t.selection),
		aggregationMarkers: t.aggregationMarkers ?? [],
		commands: []
	};
}
function ul(e, t, n, r = {}) {
	let i = Pl(e, n), a = new Set(i), o = n.filter((e) => !a.has(e)), s = e.nodes.filter((e) => a.has(e.id)).map((e) => Al(e, r.pins)).filter((e) => e.pinned);
	return {
		kind: "search-results",
		query: t,
		searchResultIds: [...n],
		visibleResultIds: i,
		unavailableResultIds: o,
		selection: Sl(e, null, r.selection),
		pinHints: s,
		aggregationMarkers: Bl(r.aggregationMarkers, n),
		commands: i.slice(0, ol).map((e) => ({
			kind: "show-this-object",
			object: {
				kind: "node",
				nodeId: e
			},
			label: "显示这个对象"
		}))
	};
}
function dl(e, t, n, r = {}) {
	let i = Il(e, t);
	return {
		kind: "excluded-object",
		object: t,
		reason: n,
		selection: Sl(e, t, r.selection),
		searchResultIds: i.filter((e) => Vl(r).has(e)),
		pinHints: jl(e, i, r.pins),
		aggregationMarkers: Ll(r.aggregationMarkers, t),
		commands: [{
			kind: "show-this-object",
			object: t,
			label: "显示这个对象"
		}, {
			kind: "clear-temporary-object-display",
			label: "清除临时显示"
		}]
	};
}
function fl(e, t, n, r = {}) {
	return {
		kind: "unavailable-object",
		object: t,
		reason: n,
		selection: Sl(e, t, r.selection),
		searchResultIds: r.searchResultIds ?? [],
		pinHints: jl(e, Il(e, t), r.pins),
		aggregationMarkers: Ll(r.aggregationMarkers, t),
		commands: []
	};
}
function pl(e, t = {}) {
	let n = Math.max(1, Math.floor(Number(t.minCommunitySize) || 6)), r = /* @__PURE__ */ new Map();
	for (let t of e.nodes) {
		if (!t.community) continue;
		let e = r.get(t.community) ?? [];
		e.push(t.id), r.set(t.community, e);
	}
	let i = new Map((e.learning?.communities ?? []).map((e) => [e.id, e])), o = new Set(Object.keys(t.pins ?? {}));
	return [...r.entries()].filter(([, e]) => e.length >= n).map(([t, n]) => {
		let r = i.get(t) ?? null, s = e.nodes.filter((e) => e.community === t && o.has(a(e))).map((e) => e.id);
		return {
			id: `community-container:${t}`,
			label: r?.label ?? t,
			communityId: t,
			nodeIds: n,
			pinnedNodeIds: s,
			totalCount: Number(r?.node_count ?? n.length)
		};
	});
}
function ml(e) {
	let t = new Map(e.nodes.map((e) => [e.id, e])), n = new Map(e.nodes.map((e) => [e.id, []]));
	for (let r of e.edges) {
		let e = Gl(r.from), i = Gl(r.to);
		!e || !i || !t.has(e) || !t.has(i) || (n.get(e)?.push(r), n.get(i)?.push(r));
	}
	return {
		nodeById: t,
		edgesByNodeId: n
	};
}
function hl(e, t, n) {
	return gl(e, t.edgesByNodeId.get(n) ?? [], t);
}
function gl(e, t, n) {
	return t.flatMap((e) => {
		let t = Gl(e.from), r = Gl(e.to), i = t ? n.nodeById.get(t) : null, a = r ? n.nodeById.get(r) : null;
		return !i || !a ? [] : [{
			edgeId: e.id || Kl(i.id, a.id),
			fromNodeId: i.id,
			toNodeId: a.id,
			relationType: e.relation_type ?? null,
			confidence: e.confidence ?? e.type ?? null,
			weight: Ul(e.weight),
			bridge: (i.community ?? null) !== (a.community ?? null)
		}];
	});
}
function _l(e, t) {
	return [...e].sort((e, t) => t.weight - e.weight || e.edgeId.localeCompare(t.edgeId)).slice(0, t);
}
function vl(e, t, n, r) {
	let i = /* @__PURE__ */ new Set(), a = 0;
	for (let e of n) {
		let n = Gl(e.from), o = Gl(e.to);
		if (!n || !o || n === o || !r.nodeById.has(n) || !r.nodeById.has(o)) continue;
		let s = t.has(n), c = t.has(o);
		!s && !c || (s && i.add(n), c && i.add(o), s && c && (a += 1));
	}
	return {
		pageCount: e.length,
		internalLinkCount: a,
		communityCount: new Set(e.map(Nl)).size,
		isolatedCount: e.filter((e) => !i.has(e.id)).length
	};
}
function yl(e, t, n = ol, r) {
	let i = r ?? bl(e);
	return [...t].map((e) => ({
		id: e.id,
		rank: xl(i, e)
	})).sort((e, t) => t.rank - e.rank || e.id.localeCompare(t.id)).slice(0, n).map((e) => e.id);
}
function bl(e, t = ml(e)) {
	return {
		index: t,
		recommendedStartNodeId: e.learning?.entry.recommended_start_node_id ?? null,
		bridgeNodeIds: new Set((e.insights?.bridge_nodes ?? []).map((e) => e.id))
	};
}
function xl(e, t) {
	return (e.recommendedStartNodeId === t.id ? 1e4 : 0) + (e.bridgeNodeIds.has(t.id) ? 1e3 : 0) + Ul(t.score) * 100 + Ul(t.weight) * 10 + (e.index.edgesByNodeId.get(t.id)?.length ?? 0);
}
function Sl(e, t, n) {
	if (!n) return {
		input: null,
		selectionId: null,
		selectedNodeIds: [],
		selectedCommunityIds: [],
		containsCurrentObject: !1
	};
	let r = yi(e, n, { canAsk: !1 });
	return {
		input: n,
		selectionId: r.id,
		selectedNodeIds: r.nodeIds,
		selectedCommunityIds: r.communityIds,
		containsCurrentObject: t ? Cl(e, t, r.nodeIds, r.communityIds) : r.nodeIds.length > 0
	};
}
function Cl(e, t, n, r) {
	let i = new Set(n), a = new Set(r);
	return t.kind === "node" ? i.has(t.nodeId) : t.kind === "community" ? a.has(t.communityId) : t.nodeIds.some((e) => i.has(e)) || !!(t.communityId && a.has(t.communityId));
}
function wl(e, t) {
	let n = [
		{
			kind: "open-detail-read",
			nodeId: e.id,
			path: a(e),
			label: "打开详情"
		},
		{
			kind: "select-neighbors",
			nodeId: e.id,
			label: "+邻居"
		},
		{
			kind: "set-fixed-position",
			mode: t.pinned ? "unfix" : "fix",
			nodeId: e.id,
			wikiPath: a(e),
			label: t.pinned ? "取消固定位置" : "固定位置"
		}
	];
	return e.community && n.push({
		kind: "enter-community",
		communityId: e.community,
		label: "进入社区"
	}), n;
}
function Tl(e, t) {
	return t ? [{
		kind: "enter-community",
		communityId: e,
		label: "进入社区"
	}] : [];
}
function El(e, n) {
	return n === "_none" ? t : e || n;
}
function Dl(e) {
	return e === "ungrouped" ? "这些页面暂未形成明确社区。你可以让 agent 探索它们之间是否存在潜在关系。" : e === "loose" ? "这组页面结构还比较松散。你可以先找知识缺口，也可以继续探索潜在关系。" : "这组页面围绕同一主题聚在一起。你可以先看结构，也可以直接让 agent 基于这一组页面继续工作。";
}
function Ol(e, t, n, r) {
	return e === "_none" ? "ungrouped" : t <= 1 || n === 0 || r > Math.floor(t / 2) ? "loose" : "clear";
}
function kl(e, t) {
	return t.flatMap((t, n) => {
		let r = e.nodeById.get(t);
		return r ? [{
			nodeId: r.id,
			label: r.label || r.id,
			type: r.type,
			role: n === 0 ? "核心" : r.type === "topic" ? "主题" : "相关"
		}] : [];
	});
}
function Al(e, t) {
	let n = a(e), r = t?.[n] ?? null;
	return {
		nodeId: e.id,
		wikiPath: n,
		pinned: !!r,
		position: r
	};
}
function jl(e, t, n) {
	let r = new Map(e.nodes.map((e) => [e.id, e]));
	return t.map((e) => r.get(e)).filter((e) => !!e).map((e) => Al(e, n)).filter((e) => e.pinned);
}
function Ml(e, t) {
	return e.nodes.filter((e) => Nl(e) === t);
}
function Nl(e) {
	return String(e.community || "_none");
}
function Pl(e, t) {
	let n = new Set(t);
	return e.nodes.map((e) => e.id).filter((e) => n.has(e));
}
function Fl(e) {
	let t = /* @__PURE__ */ new Set();
	for (let n of e.learning?.communities ?? []) t.add(n.id);
	for (let n of e.nodes) t.add(Nl(n));
	return [...t];
}
function Il(e, t) {
	return t.kind === "node" ? [t.nodeId] : t.kind === "aggregation" ? [...t.nodeIds] : Ml(e, t.communityId).map((e) => e.id);
}
function Ll(e, t) {
	if (!e) return [];
	if (t.kind === "community") return zl(e, t.communityId);
	if (t.kind === "node") return Rl(e, t.nodeId);
	let n = new Set(t.nodeIds);
	return e.filter((e) => e.id === t.aggregationId || e.nodeIds.some((e) => n.has(e)));
}
function Rl(e, t) {
	return (e ?? []).filter((e) => e.nodeIds.includes(t));
}
function zl(e, t) {
	return (e ?? []).filter((e) => e.communityId === t);
}
function Bl(e, t) {
	let n = new Set(t);
	return (e ?? []).filter((e) => e.nodeIds.some((e) => n.has(e)));
}
function Vl(e) {
	return new Set(e.searchResultIds ?? []);
}
function Hl(e, t) {
	return !e || e.kind !== t.kind ? !1 : e.kind === "node" && t.kind === "node" ? e.nodeId === t.nodeId : e.kind === "community" && t.kind === "community" ? e.communityId === t.communityId : e.kind === "aggregation" && t.kind === "aggregation" ? e.aggregationId === t.aggregationId : !1;
}
function Ul(e) {
	return typeof e == "number" && Number.isFinite(e) ? e : 0;
}
function Wl(e) {
	return typeof e == "string" && e.trim() ? e : null;
}
function Gl(e) {
	return e == null || e === "" ? null : String(e);
}
function Kl(e, t) {
	return `${e}->${t}`;
}
//#endregion
//#region src/diff.ts
var ql = .5;
function Jl(e, t) {
	let n = new Set(e.nodes.map((e) => e.id)), r = new Set(t.nodes.map((e) => e.id)), i = new Set(e.edges.map((e) => e.id)), a = new Set(t.edges.map((e) => e.id)), o = Xl(e, t), s = eu(r, n, t.nodes.map((e) => e.id)), c = eu(n, r, e.nodes.map((e) => e.id)), l = eu(a, i, t.edges.map((e) => e.id)), u = eu(i, a, e.edges.map((e) => e.id));
	return {
		addedNodes: s,
		removedNodes: c,
		recoloredNodes: Yl(e, t, o),
		addedEdges: l,
		removedEdges: u,
		newCommunities: o.newCommunities,
		stats: {
			nodeCount: t.nodes.length,
			edgeCount: t.edges.length,
			communityCount: Zl(t).length
		}
	};
}
function Yl(e, t, n) {
	let r = new Map(e.nodes.map((e) => [e.id, e])), i = [];
	for (let e of t.nodes) {
		let t = r.get(e.id);
		if (!t) continue;
		let a = Ql(t), o = Ql(e);
		if (!a || !o) continue;
		let s = n.nextToPrevious.get(o);
		s && a !== s && i.push({
			id: e.id,
			from: a,
			to: o
		});
	}
	return i;
}
function Xl(e, t) {
	let n = Zl(e), r = Zl(t), i = [];
	for (let e of n) for (let t of r) {
		let n = $l(e.members, t.members);
		n >= ql && i.push({
			previous: e.id,
			next: t.id,
			score: n
		});
	}
	i.sort((e, t) => t.score - e.score || e.previous.localeCompare(t.previous) || e.next.localeCompare(t.next));
	let a = /* @__PURE__ */ new Set(), o = /* @__PURE__ */ new Set(), s = /* @__PURE__ */ new Map();
	for (let e of i) a.has(e.previous) || o.has(e.next) || (a.add(e.previous), o.add(e.next), s.set(e.next, e.previous));
	return {
		nextToPrevious: s,
		newCommunities: r.map((e) => e.id).filter((e) => !s.has(e))
	};
}
function Zl(e) {
	let t = /* @__PURE__ */ new Map();
	for (let n of e.nodes) {
		let e = Ql(n);
		if (!e) continue;
		let r = t.get(e) ?? /* @__PURE__ */ new Set();
		r.add(n.id), t.set(e, r);
	}
	return Array.from(t.entries()).map(([e, t]) => ({
		id: e,
		members: t
	}));
}
function Ql(e) {
	return e.community == null || e.community === "" ? null : String(e.community);
}
function $l(e, t) {
	if (e.size === 0 && t.size === 0) return 1;
	let n = 0;
	for (let r of e) t.has(r) && n++;
	let r = new Set([...e, ...t]).size;
	return r === 0 ? 0 : n / r;
}
function eu(e, t, n) {
	return n.filter((n) => e.has(n) && !t.has(n));
}
//#endregion
//#region src/anim/index.ts
var tu = class {
	pending = null;
	visibility;
	dragState = "idle";
	isAnimating = !1;
	constructor(e = {}) {
		this.visibility = e.visible === !1 ? "hidden" : "visible";
	}
	get snapshot() {
		return {
			pending: this.pending,
			isAnimating: this.isAnimating,
			visibility: this.visibility,
			dragState: this.dragState
		};
	}
	push(e) {
		return !e || ru(e) ? this.decision("queue", null, this.blockedReason()) : this.canConsume() ? (this.isAnimating = !0, this.decision("consume", e, "visible")) : (this.pending = nu(this.pending, e), this.decision("queue", this.pending, this.blockedReason()));
	}
	setVisible(e) {
		return this.visibility = e ? "visible" : "hidden", this.flushIfReady(e ? "visible" : "hidden");
	}
	setDragging(e) {
		return this.dragState = e ? "dragging" : "idle", this.flushIfReady(e ? "dragging" : "visible");
	}
	finishAnimation() {
		return this.isAnimating = !1, this.flushIfReady("visible");
	}
	clear() {
		this.pending = null, this.isAnimating = !1;
	}
	flushIfReady(e) {
		if (!this.pending || !this.canConsume()) return this.decision("queue", this.pending, this.blockedReason(e));
		let t = this.pending;
		return this.pending = null, this.isAnimating = !0, this.decision("consume", t, "visible");
	}
	canConsume() {
		return this.visibility === "visible" && this.dragState === "idle" && !this.isAnimating;
	}
	blockedReason(e = "visible") {
		return this.visibility === "hidden" ? "hidden" : this.dragState === "dragging" ? "dragging" : e;
	}
	decision(e, t, n) {
		return {
			action: e,
			diff: t,
			reason: n,
			snapshot: this.snapshot
		};
	}
};
function nu(e, t) {
	if (!e) return au(t);
	let n = new Set(e.addedNodes), r = new Set(e.removedNodes);
	for (let e of t.addedNodes) r.has(e) ? r.delete(e) : n.add(e);
	for (let e of t.removedNodes) n.has(e) ? n.delete(e) : r.add(e);
	let i = new Set(e.addedEdges), a = new Set(e.removedEdges);
	for (let e of t.addedEdges) a.has(e) ? a.delete(e) : i.add(e);
	for (let e of t.removedEdges) i.has(e) ? i.delete(e) : a.add(e);
	return {
		addedNodes: ou(n),
		removedNodes: ou(r),
		recoloredNodes: iu(e.recoloredNodes, t.recoloredNodes, n, r),
		addedEdges: ou(i),
		removedEdges: ou(a),
		newCommunities: ou(new Set([...e.newCommunities, ...t.newCommunities])),
		stats: t.stats
	};
}
function ru(e) {
	return e.addedNodes.length === 0 && e.removedNodes.length === 0 && e.recoloredNodes.length === 0 && e.addedEdges.length === 0 && e.removedEdges.length === 0 && e.newCommunities.length === 0;
}
function iu(e, t, n, r) {
	let i = /* @__PURE__ */ new Map();
	for (let t of e) i.set(t.id, { ...t });
	for (let e of t) {
		let t = i.get(e.id);
		i.set(e.id, {
			id: e.id,
			from: t?.from ?? e.from,
			to: e.to
		});
	}
	for (let e of [...n, ...r]) i.delete(e);
	return Array.from(i.values()).filter((e) => e.from !== e.to);
}
function au(e) {
	return {
		addedNodes: [...e.addedNodes],
		removedNodes: [...e.removedNodes],
		recoloredNodes: e.recoloredNodes.map((e) => ({ ...e })),
		addedEdges: [...e.addedEdges],
		removedEdges: [...e.removedEdges],
		newCommunities: [...e.newCommunities],
		stats: { ...e.stats }
	};
}
function ou(e) {
	return Array.from(e);
}
//#endregion
//#region src/architecture.ts
var su = [
	{
		id: "data",
		name: "GraphData",
		owns: [
			"graph schema",
			"node and edge facts",
			"selection data inputs"
		],
		entrypoints: [
			"src/types.ts",
			"src/model/",
			"src/graph-node.ts",
			"src/select/"
		],
		mustNotOwn: [
			"DOM",
			"screen projection",
			"host callbacks",
			"pointer or wheel events"
		]
	},
	{
		id: "layout",
		name: "GraphLayout",
		owns: [
			"world positions",
			"layout bounds",
			"community wash geometry",
			"spatial hit testing"
		],
		entrypoints: [
			"src/layout/",
			"src/render/model.ts",
			"src/render/community-wash.ts",
			"src/sim/"
		],
		mustNotOwn: [
			"host callbacks",
			"browser default policy",
			"screen projection"
		]
	},
	{
		id: "viewport",
		name: "GraphViewport",
		owns: [
			"camera",
			"world/screen projection",
			"fit, pan, zoom, minimap projection",
			"resize anchoring"
		],
		entrypoints: ["src/render/viewport.ts", "src/render/geometry.ts"],
		mustNotOwn: [
			"graph data mutation",
			"DOM event classification",
			"host callbacks"
		]
	},
	{
		id: "controller",
		name: "GraphController",
		owns: [
			"semantic graph commands",
			"keyboard routing",
			"node drag coordination"
		],
		entrypoints: ["src/render/controller.ts"],
		mustNotOwn: [
			"host callbacks",
			"graph drawing",
			"render-model computation"
		]
	},
	{
		id: "renderer",
		name: "GraphRenderer",
		owns: [
			"DOM/SVG drawing",
			"node, edge, wash, toolbar, overlay, reader painting",
			"render-only CSS state"
		],
		entrypoints: [
			"src/render/graph-renderer-root.ts",
			"src/render/render-pipeline.ts",
			"src/render/overlays-presenter.ts",
			"src/render/nodes.ts",
			"src/render/edges.ts",
			"src/render/community-washes.ts",
			"src/render/minimap.ts",
			"src/render/controls.ts",
			"src/render/hover-card.ts",
			"src/render/offline-reader.ts"
		],
		mustNotOwn: [
			"host callbacks",
			"selection semantics",
			"browser default policy"
		]
	},
	{
		id: "gestures",
		name: "GraphGestures",
		owns: [
			"raw wheel, pointer, and keyboard ownership",
			"gesture blockers",
			"graph-owned intent classification"
		],
		entrypoints: ["src/render/gestures.ts"],
		mustNotOwn: [
			"host callbacks",
			"graph drawing",
			"data persistence"
		]
	},
	{
		id: "facade",
		name: "GraphFacade",
		owns: [
			"public graph engine API",
			"host capability callbacks",
			"selection resolution",
			"renderer lifecycle"
		],
		entrypoints: ["src/facade.ts", "src/index.ts"],
		mustNotOwn: [
			"raw DOM event policy",
			"node layout physics",
			"drawing internals"
		]
	}
];
function cu(e) {
	return {
		nodeId: e.nodeId,
		pinKey: e.pinKey,
		startPoint: e.startPoint,
		currentPoint: e.startPoint,
		initiallyPinned: e.initiallyPinned,
		initialPinPosition: e.initialPinPosition,
		pointerStart: e.pointerStart,
		grabOffset: {
			x: e.pointerWorldPoint.x - e.startPoint.x,
			y: e.pointerWorldPoint.y - e.startPoint.y
		},
		previousCameraPanning: e.previousCameraPanning,
		moved: !1
	};
}
function lu(e, t, n) {
	if (!e.moved) {
		let n = t.x - e.pointerStart.x, r = t.y - e.pointerStart.y;
		e.moved = Math.hypot(n, r) >= 2;
	}
	e.currentPoint = {
		x: n.x - e.grabOffset.x,
		y: n.y - e.grabOffset.y
	};
}
function uu(e, t, n, r, i) {
	let a = !1, o = e.nodes.map((e) => e.id === t ? (a = !0, pu(e, n, r, i)) : e);
	if (!a) return e;
	let s = new Map(o.map((e) => [e.id, e])), c = new Set(o.filter((e) => e.pinHint.pinned).map((e) => e.id)), l = (e) => e.map((e) => s.get(e)?.pinHint).filter((e) => !!e?.pinned);
	return {
		...e,
		nodes: o,
		communities: e.communities.map((e) => ({
			...e,
			pinHints: e.pinHints.some((e) => e.nodeId === t) || r ? l(e.nodeIds) : e.pinHints
		})),
		aggregations: e.aggregations.map((e) => ({
			...e,
			pinnedNodeIds: e.nodeIds.filter((e) => c.has(e)),
			pinHints: l(e.nodeIds)
		})),
		renderable: {
			...e.renderable,
			nodes: e.renderable.nodes.map((e) => e.id === t ? {
				...e,
				x: n.x,
				y: n.y,
				point: {
					x: n.x,
					y: n.y
				}
			} : e),
			aggregationContainers: e.renderable.aggregationContainers.map((e) => ({
				...e,
				pinnedNodeIds: e.nodeIds.filter((e) => c.has(e)),
				pinHints: l(e.nodeIds),
				pinnedCount: e.nodeIds.filter((e) => c.has(e)).length
			}))
		}
	};
}
function du(e) {
	e.element.setPointerCapture?.(e.pointerId);
	let t = (t) => {
		t.pointerId !== e.pointerId || !e.isActive(e.nodeId) || (t.preventDefault(), t.stopPropagation(), e.onMove(e.screenPointFromEvent(t), t));
	}, n = (t) => {
		t.pointerId !== e.pointerId || !e.isActive(e.nodeId) || (t.preventDefault(), t.stopPropagation(), e.element.releasePointerCapture?.(e.pointerId), e.onEnd(e.screenPointFromEvent(t), t));
	}, r = (t) => {
		t.pointerId !== e.pointerId || !e.isActive(e.nodeId) || (t.preventDefault(), t.stopPropagation(), e.element.releasePointerCapture?.(e.pointerId), e.onCancel());
	};
	return e.ownerDocument.addEventListener("pointermove", t, !0), e.ownerDocument.addEventListener("pointerup", n, !0), e.ownerDocument.addEventListener("pointercancel", r, !0), () => {
		e.ownerDocument.removeEventListener("pointermove", t, !0), e.ownerDocument.removeEventListener("pointerup", n, !0), e.ownerDocument.removeEventListener("pointercancel", r, !0);
	};
}
function fu(e) {
	let t = (t) => {
		e.isActive(e.nodeId) && (t.preventDefault(), t.stopPropagation(), e.onMove(e.screenPointFromEvent(t), t));
	}, n = (t) => {
		e.isActive(e.nodeId) && (t.preventDefault(), t.stopPropagation(), e.onEnd(e.screenPointFromEvent(t), t));
	};
	return e.ownerDocument.addEventListener("mousemove", t, !0), e.ownerDocument.addEventListener("mouseup", n, !0), () => {
		e.ownerDocument.removeEventListener("mousemove", t, !0), e.ownerDocument.removeEventListener("mouseup", n, !0);
	};
}
function pu(e, t, n, r) {
	return {
		...e,
		point: {
			x: t.x,
			y: t.y
		},
		pinHint: {
			...e.pinHint,
			pinned: n,
			position: n ? r ?? {
				x: t.x,
				y: t.y,
				coordinateSpace: "world"
			} : null
		}
	};
}
//#endregion
//#region src/render/sigma-coordinates.ts
function mu(e, t) {
	return pn({
		x: e.clientX,
		y: e.clientY
	}, t.getBoundingClientRect());
}
function hu(e, t, n) {
	let r = e.viewportToGraph?.(t);
	return r && Number.isFinite(r.x) && Number.isFinite(r.y) ? r : vn(t, n.viewport ?? so, n.viewportSize ?? {
		width: 1,
		height: 1
	}, n.adapterData.renderable.worldBounds);
}
function gu(e, t, n) {
	let r = e.graphToViewport?.(t);
	if (r && Number.isFinite(r.x) && Number.isFinite(r.y)) return r;
	let i = hn(t, n.adapterData.renderable.worldBounds), a = n.viewportSize ?? {
		width: 1,
		height: 1
	};
	return {
		x: i.x / 100 * a.width,
		y: i.y / 100 * a.height
	};
}
function _u(e, t, n, r) {
	let i = e.graphToViewport?.(t, { cameraState: n });
	return i && Number.isFinite(i.x) && Number.isFinite(i.y) ? i : gu(e, t, r);
}
//#endregion
//#region src/render/community-cloud-geometry.ts
function vu(e) {
	let t = new Map(e.renderable.communities.map((e) => [e.id, e.wash])), n = /* @__PURE__ */ new Map();
	for (let r of e.nodes) {
		if (!r.communityId) continue;
		let e = t.get(r.communityId);
		if (!e) continue;
		let i = n.get(r.communityId), a = Cu(r.point, e);
		i ? i.push(a) : n.set(r.communityId, [a]);
	}
	let r = /* @__PURE__ */ new Map();
	for (let [e, i] of n) r.set(e, {
		hullPoints: Eu(i),
		signature: xu(i, t.get(e))
	});
	return r;
}
function yu(e, t) {
	let n = new Map(t.renderable.communities.map((e) => [e.id, e.wash])), r = /* @__PURE__ */ new Map();
	for (let e of t.nodes) {
		if (!e.communityId) continue;
		let t = n.get(e.communityId);
		if (!t) continue;
		let i = r.get(e.communityId), a = Cu(e.point, t);
		i ? i.push(a) : r.set(e.communityId, [a]);
	}
	let i = /* @__PURE__ */ new Map();
	for (let [t, a] of r) {
		let r = xu(a, n.get(t)), o = e.get(t);
		i.set(t, o?.signature === r ? o : {
			hullPoints: Eu(a),
			signature: r
		});
	}
	return i;
}
function bu(e, t, n) {
	let r = t.nodes.find((e) => e.id === n);
	if (!r?.communityId) return e;
	let i = t.renderable.communities.find((e) => e.id === r.communityId);
	if (!i?.wash) return e;
	let a = i.wash, o = t.nodes.filter((e) => e.communityId === r.communityId).map((e) => Cu(e.point, a)), s = xu(o, a);
	if (e.get(r.communityId)?.signature === s) return e;
	let c = new Map(e);
	return c.set(r.communityId, {
		hullPoints: Eu(o),
		signature: s
	}), c;
}
function xu(e, t) {
	let n = t ? [
		t.cx,
		t.cy,
		t.rx,
		t.ry
	] : [];
	for (let t of e) n.push(t.x, t.y);
	return n.map((e) => String(Math.round(e * 1e3) / 1e3)).join(",");
}
function Su(e, t, n) {
	return e?.hullPoints.map((e) => gu(t, e, n)) ?? [];
}
function Cu(e, t) {
	let n = Math.max(1, t.rx), r = Math.max(1, t.ry), i = e.x - t.cx, a = e.y - t.cy, o = Math.hypot(i / n, a / r);
	return o <= 1 ? {
		x: e.x,
		y: e.y
	} : {
		x: t.cx + i / o,
		y: t.cy + a / o
	};
}
function wu(e, t) {
	let n = e;
	if (n.length >= 3) {
		let e = n.reduce((e, t) => e + t.x, 0) / n.length, r = n.reduce((e, t) => e + t.y, 0) / n.length, i = n.map((n) => Tu({
			x: n.x + (n.x - e) * .4,
			y: n.y + (n.y - r) * .4
		}, t)), a = Infinity, o = Infinity, s = -Infinity, c = -Infinity;
		for (let e of i) a = Math.min(a, e.x), o = Math.min(o, e.y), s = Math.max(s, e.x), c = Math.max(c, e.y);
		let l = {
			left: a,
			top: o,
			width: Math.max(8, s - a),
			height: Math.max(8, c - o)
		};
		return {
			box: l,
			localPoints: i.map((e) => ({
				x: e.x - l.left,
				y: e.y - l.top
			}))
		};
	}
	return {
		box: t,
		localPoints: null
	};
}
function Tu(e, t) {
	let n = t.left + t.width / 2, r = t.top + t.height / 2, i = Math.max(1, t.width / 2), a = Math.max(1, t.height / 2), o = e.x - n, s = e.y - r, c = Math.hypot(o / i, s / a);
	return c <= 1 ? e : {
		x: n + o / c,
		y: r + s / c
	};
}
function Eu(e) {
	if (e.length < 3) return e.slice();
	let t = e.slice().sort((e, t) => e.x - t.x || e.y - t.y), n = (e, t, n) => (t.x - e.x) * (n.y - e.y) - (t.y - e.y) * (n.x - e.x), r = [];
	for (let e of t) {
		for (; r.length >= 2 && n(r[r.length - 2], r[r.length - 1], e) <= 0;) r.pop();
		r.push(e);
	}
	let i = [];
	for (let e = t.length - 1; e >= 0; --e) {
		let r = t[e];
		for (; i.length >= 2 && n(i[i.length - 2], i[i.length - 1], r) <= 0;) i.pop();
		i.push(r);
	}
	return r.pop(), i.pop(), r.concat(i);
}
//#endregion
//#region src/render/sigma-overlay-svg.ts
var Du = "http://www.w3.org/2000/svg";
function Ou(e) {
	let t = e.ownerDocument.createElement("div");
	return t.className = "sigma-global-overlay", t.dataset.role = "sigma-global-overlay", e.append(t), t;
}
function ku(e, t, n, r) {
	let i = e.createElement("button");
	return i.type = "button", i.dataset.kind = t, i.dataset.id = n, i.setAttribute("aria-label", r), i;
}
function Au(e, t, n) {
	let r = e.createElement("div");
	return r.dataset.kind = t, r.dataset.id = n, r.setAttribute("aria-hidden", "true"), r.tabIndex = -1, r.style.pointerEvents = "none", r;
}
function ju(e, t) {
	e.style.left = `${t.left}px`, e.style.top = `${t.top}px`, e.style.width = `${t.width}px`, e.style.height = `${t.height}px`;
}
var Mu = 0;
function Nu() {
	return Mu += 1, Mu;
}
function Pu(e, t) {
	let n = e.createElementNS(Du, "svg");
	n.setAttribute("aria-hidden", "true"), n.style.position = "absolute", n.style.width = "0", n.style.height = "0", n.style.overflow = "hidden";
	let r = e.createElementNS(Du, "defs"), i = e.createElementNS(Du, "filter");
	i.setAttribute("id", t), i.setAttribute("x", "-50%"), i.setAttribute("y", "-50%"), i.setAttribute("width", "200%"), i.setAttribute("height", "200%");
	let a = e.createElementNS(Du, "feGaussianBlur");
	return a.setAttribute("stdDeviation", "20"), i.append(a), r.append(i), n.append(r), n;
}
function Fu(e, t, n, r) {
	let i = e.createElementNS(Du, "svg");
	i.setAttribute("width", "100%"), i.setAttribute("height", "100%"), i.style.position = "absolute", i.style.inset = "0", i.style.overflow = "visible", i.style.pointerEvents = "none";
	let a = t.localPoints ? "polygon" : "ellipse", o = e.createElementNS(Du, a);
	return o.setAttribute("filter", `url(#${n})`), o.style.pointerEvents = "fill", o.style.cursor = "pointer", o.addEventListener("click", (e) => {
		e.stopPropagation(), r();
	}), Lu(o, a, t), i.append(o), {
		svg: i,
		shape: o,
		kind: a
	};
}
function Iu(e, t, n) {
	e.setAttribute("fill", t), e.setAttribute("fill-opacity", n ? "0.06" : "0.2");
}
function Lu(e, t, n) {
	if (t === "polygon") {
		n.localPoints && e.setAttribute("points", n.localPoints.map((e) => `${e.x},${e.y}`).join(" "));
		return;
	}
	e.setAttribute("cx", String(n.box.width / 2)), e.setAttribute("cy", String(n.box.height / 2)), e.setAttribute("rx", String(Math.max(8, n.box.width / 2))), e.setAttribute("ry", String(Math.max(8, n.box.height / 2)));
}
var Ru = .0016, zu = .2, Bu = .3, Vu = 1.18;
function Hu(e) {
	let t = Gu(e.deltaY, 0);
	return e.deltaMode === 1 ? t * 18 : e.deltaMode === 2 ? t * 720 : t;
}
function Uu(e, t) {
	let n = Gu(e, 1), r = Hu(t);
	return Ku(n * Ku(Math.exp(r * Ru), zu, 5), Bu, 3);
}
function Wu(e, t) {
	return Ku(Gu(e, 1) * (t === "in" ? 1 / Vu : Vu), Bu, 3);
}
function Gu(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function Ku(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
//#endregion
//#region src/render/sigma-events.ts
function qu(e) {
	let t = e;
	t?.preventSigmaDefault?.(), t?.event?.preventSigmaDefault?.(), e instanceof Event && e.preventDefault();
}
//#endregion
//#region src/render/sigma-graphology-model.ts
function Ju(e, t, n = "shan-shui", r) {
	let i = new t.GraphologyGraph({
		multi: !0,
		type: "mixed"
	}), a = new Map(e.renderable.communities.map((e) => [e.id, e.color])), o = new Map(e.renderable.aggregationContainers.map((e) => [e.id, e])), s = Qu(e), c = $u(e);
	for (let t of e.nodes) i.addNode(t.id, Zu(t, a, c, n));
	for (let t of e.edges) i.addEdgeWithKey(t.id, t.sourceNodeId, t.targetNodeId, nd(t, n, r, s));
	return i.setAttribute("counts", e.counts), i.setAttribute("selection", e.selection), i.setAttribute("communities", e.communities.map((e) => od(e, a))), i.setAttribute("aggregations", e.aggregations.map((e) => sd(e, o))), i;
}
function Yu(e, t, n, r) {
	return n !== r || e.nodes.length !== t.nodes.length || e.edges.length !== t.edges.length ? !1 : e.nodes.every((e, n) => e.id === t.nodes[n]?.id) && e.edges.every((e, n) => {
		let r = t.edges[n];
		return !!r && e.id === r.id && e.sourceNodeId === r.sourceNodeId && e.targetNodeId === r.targetNodeId;
	});
}
function Xu(e, t, n, r) {
	let i = new Map(t.renderable.communities.map((e) => [e.id, e.color])), a = new Map(t.renderable.aggregationContainers.map((e) => [e.id, e])), o = Qu(t), s = $u(t);
	for (let r of t.nodes) e.hasNode(r.id) && e.mergeNodeAttributes(r.id, Zu(r, i, s, n));
	for (let i of t.edges) e.mergeEdgeAttributes(i.id, nd(i, n, r, o));
	e.setAttribute("counts", t.counts), e.setAttribute("selection", t.selection), e.setAttribute("communities", t.communities.map((e) => od(e, i))), e.setAttribute("aggregations", t.aggregations.map((e) => sd(e, a)));
}
function Zu(e, t, n = /* @__PURE__ */ new Set(), r) {
	let i = td(e, n), a = cd(e), o = ld(e, t, r);
	return {
		x: ud(e.point.x, 0),
		y: ud(e.point.y, 0),
		label: e.render.labelVisible ? e.label : "",
		size: i.dimmed ? fd(a * .72, 2) : a,
		color: i.dimmed ? ad(o, .2) : o,
		type: "circle",
		graphNodeType: e.type,
		communityId: e.communityId,
		sourcePath: e.sourcePath,
		selected: e.selected,
		searchHit: e.searchHit,
		pinned: e.pinHint.pinned,
		communityDimmed: i.dimmed,
		communitySpotlightVisible: i.forceVisible,
		aggregationIds: [...e.aggregationIds],
		labelVisible: e.render.labelVisible,
		displayMode: e.render.displayMode,
		visualRole: e.render.visualRole,
		priority: ud(e.render.priority, 0),
		communityMapTier: e.render.communityMapTier,
		communityMapImportance: ud(e.render.communityMapImportance, 0),
		drawerTarget: e.drawerTarget
	};
}
function Qu(e) {
	return new Set(e.communities.filter((e) => e.selected).map((e) => e.id));
}
function $u(e) {
	let t = ed(e);
	return t ? new Set([t]) : /* @__PURE__ */ new Set();
}
function ed(e) {
	return e.selection.input?.kind === "community" ? e.selection.input.id : e.sourceCommunityId ?? null;
}
function td(e, t) {
	let n = e.selected || e.searchHit || e.pinHint.pinned, r = !!(e.communityId && t.has(e.communityId));
	return {
		forceVisible: n,
		dimmed: t.size > 0 && !r && !n
	};
}
function nd(e, t = "shan-shui", n, r = /* @__PURE__ */ new Set()) {
	let i = rd(e, t, n, r);
	return {
		size: i.size,
		color: i.color,
		relationType: e.relationType == null ? null : String(e.relationType),
		confidence: e.confidence == null ? null : String(e.confidence),
		weight: ud(e.weight, 0),
		sourceCommunityId: e.sourceCommunityId,
		targetCommunityId: e.targetCommunityId,
		communityMapLayer: e.render.communityMapLayer
	};
}
function rd(e, t = "shan-shui", n, r = /* @__PURE__ */ new Set()) {
	let i = Or(e.relationType), a = i === "relation-contrast" || i === "relation-conflict", o = !!(e.sourceCommunityId && e.targetCommunityId && e.sourceCommunityId !== e.targetCommunityId), s = dd(ud(e.weight, 0), 0, 1), c = a ? (o ? .58 : .5) + s * .08 : (o ? .34 : .1) + s * (o ? .08 : .06), l = a ? (o ? 1.65 : 1.25) + s * .6 : (o ? 1.1 : .72) + s * (o ? .85 : .55);
	return n?.semanticEmphasis && (a ? (c = c * 1.16 + .04, l += .45) : (c *= .6, l *= .75)), n?.focusHighlight && r.size > 0 && (e.sourceCommunityId && r.has(e.sourceCommunityId) || e.targetCommunityId && r.has(e.targetCommunityId) ? (c = c * 1.12 + .02, l += a ? .2 : .12) : (c *= .05, l *= .55)), c = fd(dd(c, .05, .7), 3), l = fd(dd(l, .6, 4), 2), {
		color: ad(id(i, t), c),
		size: l
	};
}
function id(e, t) {
	let n = ln(t).vars;
	return e === "relation-contrast" ? n["--amber"] ?? (t === "mo-ye" ? "#e0b35e" : "#b7791f") : e === "relation-conflict" ? t === "mo-ye" ? "#f472b6" : "#d94693" : t === "mo-ye" ? n["--line"] ?? "#8e8778" : n["--night"] ?? "#315f72";
}
function ad(e, t) {
	let n = e.trim().replace(/^#/, ""), r = n.length === 3 ? n.split("").map((e) => `${e}${e}`).join("") : n, i = Number.parseInt(r.slice(0, 2), 16), a = Number.parseInt(r.slice(2, 4), 16), o = Number.parseInt(r.slice(4, 6), 16);
	return [
		i,
		a,
		o
	].every(Number.isFinite) ? `rgba(${i}, ${a}, ${o}, ${t})` : `rgba(49, 95, 114, ${t})`;
}
function od(e, t) {
	return {
		id: e.id,
		label: e.label,
		color: t.get(e.id) ?? "#64748b",
		nodeIds: [...e.nodeIds],
		nodeCount: e.nodeCount,
		selected: e.selected,
		searchResultIds: [...e.searchResultIds],
		pinnedNodeIds: e.pinHints.map((e) => e.nodeId),
		aggregationIds: [...e.aggregationIds],
		drawerTarget: e.drawerTarget,
		commands: e.commands
	};
}
function sd(e, t) {
	let n = t.get(e.id);
	return {
		id: e.id,
		label: e.label,
		communityId: e.communityId,
		nodeIds: [...e.nodeIds],
		selectedNodeIds: [...e.selectedNodeIds],
		searchResultIds: [...e.searchResultIds],
		pinnedNodeIds: [...e.pinnedNodeIds],
		totalCount: e.totalCount,
		selected: e.selected,
		color: n?.color ?? "#64748b",
		point: n ? { ...n.point } : null,
		radius: n ? ud(n.radius, 0) : null,
		drawerTarget: e.drawerTarget,
		commands: e.commands
	};
}
function cd(e) {
	return e.pinHint.pinned || e.selected ? 10 : e.searchHit ? 9 : e.render.displayMode === "card" ? 8 : e.render.displayMode === "compact-card" ? 7 : e.render.displayMode === "overview" ? 6 : 5;
}
function ld(e, t, n) {
	let r = ln(n).vars;
	return e.selected ? r["--cinnabar"] : e.searchHit ? r["--amber"] : e.pinHint.pinned ? r["--violet"] : e.communityId ? t.get(e.communityId) ?? r["--muted"] : r["--muted"];
}
function ud(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function dd(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
function fd(e, t) {
	let n = 10 ** t;
	return Math.round(e * n) / n;
}
//#endregion
//#region src/render/sigma-hit-projector.ts
function pd(e) {
	let t = new Set(e.adapterData.nodes.map((e) => e.id)), n = St(_d(e.adapterData));
	return {
		targetFromSigmaHit(r) {
			if (r.nodeId && t.has(r.nodeId)) return {
				kind: "node",
				id: r.nodeId
			};
			let i = r.renderedObject ? vd(r.renderedObject, e.adapterData) : null;
			if (i) return i;
			if (r.screenPoint) {
				let t = e.screenPointToWorldPoint ? e.screenPointToWorldPoint(r.screenPoint) : vn(r.screenPoint, e.viewport, e.viewportSize, e.adapterData.renderable.worldBounds);
				return is(n.hitTest(t));
			}
			return { kind: "graph-blank" };
		},
		index() {
			return n;
		}
	};
}
function md(e) {
	let t = e;
	return typeof t?.node == "string" ? t.node : null;
}
function hd(e) {
	let t = e;
	return t?.shiftKey === !0 || t?.event?.shiftKey === !0 || t?.event?.original?.shiftKey === !0 || t?.event?.originalEvent?.shiftKey === !0 || t?.originalEvent?.shiftKey === !0;
}
function gd(e) {
	let t = e, n = t?.event?.x ?? t?.x, r = t?.event?.y ?? t?.y;
	return typeof n == "number" && typeof r == "number" ? {
		x: n,
		y: r
	} : null;
}
function _d(e) {
	let t = new Map(e.renderable.edges.map((e) => [e.id, e]));
	return {
		nodes: e.nodes.map((e) => ({
			id: e.id,
			label: e.label,
			type: e.type,
			point: e.point,
			displayMode: e.render.displayMode,
			visualRole: e.render.visualRole
		})),
		edges: e.edges.map((e) => ({
			id: e.id,
			source: e.sourceNodeId,
			target: e.targetNodeId,
			curveOffset: t.get(e.id)?.curveOffset ?? 0
		})),
		communities: e.renderable.communities.map((e) => ({
			id: e.id,
			wash: e.wash
		})),
		aggregationContainers: e.renderable.aggregationContainers.map((e) => ({
			id: e.id,
			communityId: e.communityId,
			point: e.point,
			radius: e.radius
		}))
	};
}
function vd(e, t) {
	switch (e.kind) {
		case "node": return t.nodes.some((t) => t.id === e.id) ? {
			kind: "node",
			id: e.id
		} : null;
		case "edge": return t.edges.some((t) => t.id === e.id) ? {
			kind: "edge",
			id: e.id
		} : null;
		case "community-wash": return t.communities.some((t) => t.id === e.id) ? {
			kind: "community-wash",
			id: e.id
		} : null;
		case "aggregation-container": {
			let n = t.aggregations.find((t) => t.id === e.id);
			return n ? {
				kind: "aggregation-container",
				id: e.id,
				communityId: e.communityId ?? n.communityId
			} : null;
		}
		default: return null;
	}
}
function yd(e) {
	let t = e.getCamera?.().getState?.();
	return t ? {
		x: $(t.x, 0),
		y: $(t.y, 0),
		angle: $(t.angle, 0),
		ratio: $(t.ratio, 1)
	} : null;
}
function bd(e, t) {
	t && e.getCamera?.().setState?.(t);
}
function xd(e, t, n, r, i, a) {
	if (!r) return {
		communityId: null,
		movement: "skipped",
		skipReason: "no-community"
	};
	if (r === i) return {
		communityId: r,
		movement: "skipped",
		skipReason: "already-settled"
	};
	let o = Cd(e, n, r);
	return o ? {
		communityId: r,
		...Sd(e, o, Od(t.ownerDocument.defaultView), a)
	} : {
		communityId: r,
		movement: "skipped",
		skipReason: "no-target"
	};
}
function Sd(e, t, n, r) {
	let i = e.getCamera?.();
	if (!i) return {
		movement: "skipped",
		skipReason: "camera-unavailable"
	};
	if (n || !i.animate) return i.setState ? (i.setState(t), {
		movement: "immediate",
		skipReason: i.animate ? void 0 : "animate-unavailable"
	}) : {
		movement: "skipped",
		skipReason: "animate-unavailable"
	};
	try {
		let e = i.animate(t, {
			duration: 380,
			easing: "quadraticInOut"
		});
		return e && typeof e.catch == "function" && e.catch((e) => r?.(e)), { movement: "animated" };
	} catch (e) {
		return r?.(e), {
			movement: "skipped",
			skipReason: "animate-error"
		};
	}
}
function Cd(e, t, n) {
	let r = yd(e) ?? {
		x: 0,
		y: 0,
		angle: 0,
		ratio: 1
	}, i = Dd(t, n);
	if (!i) return null;
	let a = t.renderable.worldBounds, o = Math.max(0, $(a.maxX, i.x) - $(a.minX, i.x)), s = o * .08, c = {
		x: i.x + s,
		y: i.y
	}, l = Td(e, c), u = Ad(l.x, 3), d = Ad(l.y, 3), f = Ed(e, c, Math.max(o * .015, 4)), p = Math.abs(r.x - u) <= f && Math.abs(r.y - d) <= f, m = {
		x: u,
		y: d,
		angle: r.angle,
		ratio: p || r.ratio <= .9 ? r.ratio : Ad(kd(r.ratio * .92, .72, r.ratio), 3)
	};
	return p && Math.abs(r.ratio - m.ratio) <= .025 ? null : m;
}
function wd(e, t) {
	let n = t.renderable.worldBounds, r = Td(e, {
		x: ($(n.minX, 0) + $(n.maxX, 0)) / 2,
		y: ($(n.minY, 0) + $(n.maxY, 0)) / 2
	});
	return {
		x: Ad(r.x, 3),
		y: Ad(r.y, 3),
		angle: 0,
		ratio: 1
	};
}
function Td(e, t) {
	let n = e.graphToViewport?.(t);
	if (n && (!Number.isFinite(n.x) || !Number.isFinite(n.y))) return t;
	let r = n ? e.viewportToFramedGraph?.(n) : null;
	return r && Number.isFinite(r.x) && Number.isFinite(r.y) ? r : t;
}
function Ed(e, t, n) {
	if (n <= 0) return 0;
	let r = Td(e, t), i = Td(e, {
		x: t.x + n,
		y: t.y
	}), a = Math.abs(i.x - r.x);
	return Number.isFinite(a) && a > 0 ? a : n;
}
function Dd(e, t) {
	let n = e.renderable.communities.find((e) => e.id === t);
	if (n?.wash) return {
		x: $(n.wash.cx, 0),
		y: $(n.wash.cy, 0)
	};
	let r = e.nodes.filter((e) => e.communityId === t);
	if (r.length === 0) return null;
	let i = r.reduce((e, t) => ({
		x: e.x + $(t.point.x, 0),
		y: e.y + $(t.point.y, 0)
	}), {
		x: 0,
		y: 0
	});
	return {
		x: i.x / r.length,
		y: i.y / r.length
	};
}
function Od(e) {
	return !!e?.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}
function $(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function kd(e, t, n) {
	return Math.min(n, Math.max(t, e));
}
function Ad(e, t) {
	let n = 10 ** t;
	return Math.round(e * n) / n;
}
//#endregion
//#region src/render/sigma-wheel-zoom.ts
function jd(e) {
	let t = e.sigma.getMouseCaptor?.();
	if (!t?.on) return { destroy: () => void 0 };
	let n = (t) => {
		if (!e.isDestroyed()) try {
			let n = Md(t, Pd(e.root));
			if (!n || (qu(t), Nd(t))) return;
			let r = Uu(e.currentRatio(), n.delta);
			e.onZoomAtPoint(n.point, r);
		} catch (t) {
			e.onFatalError?.(t);
		}
	};
	return t.on("wheel", n), { destroy() {
		t.off?.("wheel", n);
	} };
}
function Md(e, t) {
	let n = e, r = n?.original?.deltaY, i = n?.delta, a = typeof r == "number" ? r : typeof i == "number" ? -i * 120 : null;
	if (a == null || !Number.isFinite(a)) return null;
	let o = Fd(n?.x, NaN), s = Fd(n?.y, NaN), c = Number.isFinite(o) && Number.isFinite(s) ? {
		x: o,
		y: s
	} : t, l = n?.original?.deltaMode;
	return {
		point: c,
		delta: {
			deltaY: a,
			deltaMode: typeof l == "number" ? l : 0
		}
	};
}
function Nd(e) {
	let t = e?.original?.target;
	return !!(t?.closest?.("[data-control=\"sigma-zoom\"]") || t?.parentElement?.closest?.("[data-control=\"sigma-zoom\"]"));
}
function Pd(e) {
	let t = typeof e.getBoundingClientRect == "function" ? e.getBoundingClientRect() : null, n = Fd(t?.width, 1e3), r = Fd(t?.height, 680);
	return {
		x: n / 2,
		y: r / 2
	};
}
function Fd(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
//#endregion
//#region src/render/sigma-overlay-camera-transform.ts
var Id = 1e-6, Ld = .08, Rd = .985;
function zd(e) {
	let t = {
		x: (Kd(e.minX, 0) + Kd(e.maxX, 0)) / 2,
		y: (Kd(e.minY, 0) + Kd(e.maxY, 0)) / 2
	}, n = Math.max(1, Math.abs(Kd(e.maxX, t.x) - Kd(e.minX, t.x)) / 4), r = Math.max(1, Math.abs(Kd(e.maxY, t.y) - Kd(e.minY, t.y)) / 4);
	return {
		center: t,
		right: {
			x: t.x + n,
			y: t.y
		},
		down: {
			x: t.x,
			y: t.y + r
		}
	};
}
function Bd(e, t) {
	return {
		center: t(e.center),
		right: t(e.right),
		down: t(e.down)
	};
}
function Vd(e, t) {
	let n = Ud(e.center, e.right), r = Ud(e.center, e.down), i = Ud(t.center, t.right), a = Ud(t.center, t.down), o = Wd(n), s = Wd(r), c = Wd(i), l = Wd(a);
	if (o < Id || s < Id || c < Id || l < Id) return null;
	let u = c / o, d = l / s, f = (u + d) / 2;
	return !Number.isFinite(f) || f <= 0 || Math.abs(u - d) > Ld || Gd(n, i) < Rd || Gd(r, a) < Rd ? null : {
		translateX: qd(t.center.x - e.center.x * f),
		translateY: qd(t.center.y - e.center.y * f),
		scale: qd(f)
	};
}
function Hd(e) {
	return e ? `translate(${e.translateX}px, ${e.translateY}px) scale(${e.scale})` : "";
}
function Ud(e, t) {
	return {
		x: t.x - e.x,
		y: t.y - e.y
	};
}
function Wd(e) {
	return Math.hypot(e.x, e.y);
}
function Gd(e, t) {
	let n = Wd(e), r = Wd(t);
	return n < Id || r < Id ? -1 : (e.x * t.x + e.y * t.y) / (n * r);
}
function Kd(e, t) {
	return Number.isFinite(e) ? e : t;
}
function qd(e) {
	return Math.round(e * 1e3) / 1e3;
}
//#endregion
//#region src/render/sigma-overlay-dom.ts
var Jd = 8, Yd = 160;
function Xd(e) {
	let t = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map(), i = null, a = null;
	return {
		rebuild: o,
		reposition: s,
		repositionForCameraAnimation: c,
		invalidateAnimationBaseline: l,
		clearActiveDragListeners: _,
		destroy: f
	};
	function o() {
		if (e.isDestroyed()) return;
		let i = e.getAdapterData(), a = [], o = $u(i), c = new Set([...Qu(i), ...o]), l = /* @__PURE__ */ new Set();
		for (let n of i.renderable.communities) {
			if (!n.wash) continue;
			l.add(n.id);
			let r = e.communityCloudFor(n.id, n.wash), i = r.localPoints ? "polygon" : "ellipse", o = t.get(n.id);
			if (!o || o.kind !== i) {
				let i = Au(e.overlayRoot.ownerDocument, "community-region", n.id);
				i.className = "sigma-global-community-region", i.dataset.communityId = n.id, i.style.overflow = "visible";
				let a = Fu(e.overlayRoot.ownerDocument, r, e.cloudFilterId, () => {
					e.onHit({
						kind: "community-wash",
						id: n.id
					});
				});
				i.append(a.svg), o = {
					element: i,
					shape: a.shape,
					kind: a.kind
				}, t.set(n.id, o);
			}
			let s = c.has(n.id), u = c.size > 0 && !s;
			o.element.dataset.selected = s ? "true" : "false", Iu(o.shape, n.color, u), a.push(o.element);
		}
		$d(t, l);
		let u = /* @__PURE__ */ new Set();
		for (let e of Zd(i)) {
			u.add(e.id);
			let t = n.get(e.id);
			t || (t = p(e.id, e.label || e.id), n.set(e.id, t)), t.setAttribute("aria-label", e.label || e.id), t.dataset.nodeId = e.id, t.dataset.searchHit = e.searchHit ? "true" : "false", t.dataset.selected = e.selected ? "true" : "false", t.dataset.pinned = e.pinHint.pinned ? "true" : "false", t.dataset.communityDimmed = td(e, o).dimmed ? "true" : "false", a.push(t);
		}
		$d(n, u);
		let d = /* @__PURE__ */ new Set();
		for (let t of Qd(i, Jd)) {
			if (!t.wash) continue;
			d.add(t.id);
			let n = r.get(t.id);
			n || (n = Au(e.overlayRoot.ownerDocument, "community-label", t.id), n.className = "sigma-global-community-label", n.dataset.communityId = t.id, r.set(t.id, n));
			let i = c.has(t.id);
			n.dataset.selected = i ? "true" : "false", n.dataset.dim = c.size > 0 && !i ? "true" : "false", n.textContent = t.label || t.id, a.push(n);
		}
		$d(r, d), e.overlayRoot.replaceChildren(...a), s();
	}
	function s() {
		if (e.isDestroyed()) return;
		d();
		let i = e.getAdapterData(), a = e.getSigma(), o = e.getOptions();
		for (let n of i.renderable.communities) {
			if (!n.wash) continue;
			let r = t.get(n.id);
			if (!r) continue;
			let i = e.communityCloudFor(n.id, n.wash);
			ju(r.element, i.box), Lu(r.shape, r.kind, i);
		}
		for (let e of Zd(i)) {
			let t = n.get(e.id);
			if (!t) continue;
			let r = Math.max(16, cd(e) * 3), i = gu(a, e.point, o);
			ju(t, {
				left: i.x - r / 2,
				top: i.y - r / 2,
				width: r,
				height: r
			});
		}
		for (let e of Qd(i, Jd)) {
			if (!e.wash) continue;
			let t = r.get(e.id);
			if (!t) continue;
			let n = gu(a, {
				x: e.wash.cx,
				y: e.wash.cy - e.wash.ry * .16
			}, o);
			ju(t, {
				left: n.x,
				top: n.y,
				width: 160,
				height: 22
			});
		}
		u(i, a, o);
	}
	function c() {
		if (e.isDestroyed()) return !1;
		if (!a) return s(), !1;
		let t = e.getSigma(), n = e.getOptions(), r = t.getCamera?.().getState?.(), i = Bd(a.world, (e) => r ? _u(t, e, r, n) : gu(t, e, n)), o = Hd(Vd(a.screen, i));
		return o ? (e.overlayRoot.style.transformOrigin = "0 0", e.overlayRoot.style.transform = o, e.overlayRoot.style.willChange = "transform", !0) : (s(), !1);
	}
	function l() {
		a = null, d();
	}
	function u(e, t, n) {
		let r = zd(e.renderable.worldBounds);
		a = {
			world: r,
			screen: Bd(r, (e) => gu(t, e, n))
		};
	}
	function d() {
		e.overlayRoot.style.transform = "", e.overlayRoot.style.transformOrigin = "", e.overlayRoot.style.willChange = "";
	}
	function f() {
		l(), _(), t.clear(), n.clear(), r.clear(), e.overlayRoot.replaceChildren();
	}
	function p(t, n) {
		let r = ku(e.overlayRoot.ownerDocument, "node", t, n);
		return r.className = "sigma-global-node-hit-target", r.addEventListener("click", (n) => {
			n.stopPropagation(), !e.consumeSuppressedNodeClick(t) && e.onHit({
				kind: "node",
				id: t
			});
		}), r.addEventListener("pointerdown", (n) => {
			n.button === 0 && (n.preventDefault(), n.stopPropagation(), e.beginNodeDrag(t, e.screenPointFromEvent(n), n), e.activeNodeDragId() === t && m(r.ownerDocument, r, t, n.pointerId));
		}), r.addEventListener("mousedown", (n) => {
			n.button === 0 && (r.ownerDocument.defaultView?.PointerEvent || (n.preventDefault(), n.stopPropagation(), e.activeNodeDragId() !== t && e.beginNodeDrag(t, e.screenPointFromEvent(n), n), e.activeNodeDragId() === t && h(r.ownerDocument, t)));
		}), r.addEventListener("dragstart", (e) => {
			e.preventDefault();
		}), r;
	}
	function m(t, n, r, a) {
		_();
		let o = du({
			ownerDocument: t,
			element: n,
			nodeId: r,
			pointerId: a,
			isActive: g,
			screenPointFromEvent: e.screenPointFromEvent,
			onMove: e.moveNodeDrag,
			onEnd: (t, n) => {
				e.commitNodeDrag(t, n), _();
			},
			onCancel: () => {
				e.cancelNodeDrag(), _();
			}
		});
		i = () => {
			o(), i = null;
		};
	}
	function h(t, n) {
		_();
		let r = fu({
			ownerDocument: t,
			nodeId: n,
			isActive: g,
			screenPointFromEvent: e.screenPointFromEvent,
			onMove: e.moveNodeDrag,
			onEnd: (t, n) => {
				e.commitNodeDrag(t, n), _();
			}
		});
		i = () => {
			r(), i = null;
		};
	}
	function g(t) {
		return e.activeNodeDragId() === t;
	}
	function _() {
		i?.();
	}
}
function Zd(e) {
	let t = e.nodes, n = /* @__PURE__ */ new Set(), r = [], i = (e, t) => {
		let i = 0;
		for (let a of e) r.length >= Yd || i >= t || n.has(a.id) || (n.add(a.id), r.push(a), i += 1);
	};
	return e.selection.input?.kind !== "community" && i(t.filter((e) => e.selected), Infinity), i(t.filter((e) => e.searchHit), 80), i(t.filter((e) => e.pinHint.pinned), 80), r;
}
function Qd(e, t) {
	let n = new Set(e.communities.filter((e) => e.selected).map((e) => e.id));
	return e.renderable.communities.filter((e) => e.wash).map((e, t) => ({
		community: e,
		index: t,
		selected: n.has(e.id)
	})).sort((e, t) => e.selected === t.selected ? e.community.nodeCount === t.community.nodeCount ? e.index - t.index : t.community.nodeCount - e.community.nodeCount : e.selected ? -1 : 1).slice(0, t).map((e) => e.community);
}
function $d(e, t) {
	for (let n of [...e.keys()]) t.has(n) || e.delete(n);
}
//#endregion
//#region src/render/sigma-global-renderer.ts
var ef = "sigma-global", tf = 1;
async function nf() {
	let [{ default: e }, { default: t }] = await Promise.all([import("./sigma.esm-D09ll5rr.js"), import("./graphology-CxGlL2fi.js")]);
	return {
		Sigma: e,
		GraphologyGraph: t
	};
}
function rf(e) {
	if (!e.container) throw Error("createSigmaGlobalRenderer requires a container element");
	if (!e.runtime) throw Error("createSigmaGlobalRenderer requires a loaded Sigma runtime boundary");
	let t = e.runtime, n = !1, r = e.theme, i = e.edgeStyle, a = e.adapterData, o = Ju(a, t, r, i), s = af(e.container, r), c = Ou(s), l = `sigma-community-cloud-blur-${Nu()}`, u = s.ownerDocument.createElement("div");
	u.setAttribute("aria-hidden", "true"), u.style.position = "absolute", u.style.inset = "0", u.style.pointerEvents = "none", u.append(Pu(s.ownerDocument, l)), s.append(u);
	let d = vu(a), f = pd({
		adapterData: a,
		viewport: e.viewport ?? so,
		viewportSize: e.viewportSize ?? {
			width: 1,
			height: 1
		},
		screenPointToWorldPoint: (t) => hu(p, t, e)
	}), p, m = 0, h = null, g = null, _ = { ...e.pins ?? {} }, v = ed(a), y = null, b = null, x = null, S = [], C = [], w = null, T = null, E = null, D = !1, O = 0, k = !1, A = 0, j = 0, M = null, N = 0, P = null, F = null;
	try {
		p = new t.Sigma(o, s, of(r)), b = Xd({
			overlayRoot: c,
			cloudFilterId: l,
			getAdapterData: () => a,
			getSigma: () => p,
			getOptions: () => ({
				...e,
				adapterData: a
			}),
			communityCloudFor: Ce,
			isDestroyed: () => n,
			onHit: (e) => fe({ renderedObject: e }),
			beginNodeDrag: pe,
			moveNodeDrag: me,
			commitNodeDrag: he,
			cancelNodeDrag: ge,
			screenPointFromEvent: (e) => mu(e, s),
			consumeSuppressedNodeClick: Se,
			activeNodeDragId: () => g?.nodeId ?? null
		}), x = jd({
			sigma: p,
			root: s,
			isDestroyed: () => n,
			currentRatio: () => yd(p)?.ratio ?? 1,
			onZoomAtPoint: (e, t) => oe(e, t, !1),
			onFatalError: e.onFatalError
		}), ee(), se(), b.rebuild();
	} catch (t) {
		throw e.onFatalError?.(t), s.remove(), t;
	}
	return {
		id: ef,
		root: s,
		overlayRoot: c,
		get graph() {
			return o;
		},
		updateStrategy: "rebuild-graph-preserve-camera",
		get lastHitTarget() {
			return h;
		},
		isDragging() {
			return !!g;
		},
		resetView() {
			Te(), v = null, p.getCamera?.().setState?.(wd(p, a)), ne();
		},
		zoomIn() {
			Te(), oe(Pd(s), "in", !0);
		},
		zoomOut() {
			Te(), oe(Pd(s), "out", !0);
		},
		update(n) {
			Te();
			let c = yd(p), l = v;
			ge(), m += 1;
			let u = () => {
				try {
					bd(p, c), p.refresh?.(), b?.rebuild(), ae(l, m);
				} catch (t) {
					e.onFatalError?.(t);
				}
			}, h = n.adapterData, g = n.theme ?? r, y = n.edgeStyle ?? i, x = { ...n.pins ?? _ };
			if (Yu(a, h, r, g)) {
				a = h, i = y, _ = x, d = yu(d, a), Xu(o, a, r, i), f = pd({
					adapterData: a,
					viewport: e.viewport ?? so,
					viewportSize: e.viewportSize ?? {
						width: 1,
						height: 1
					},
					screenPointToWorldPoint: (t) => hu(p, t, e)
				}), u();
				return;
			}
			a = n.adapterData, d = yu(d, a), r = n.theme ?? r, i = n.edgeStyle ?? i, _ = { ...n.pins ?? _ }, o = Ju(a, t, r, i), f = pd({
				adapterData: a,
				viewport: e.viewport ?? so,
				viewportSize: e.viewportSize ?? {
					width: 1,
					height: 1
				},
				screenPointToWorldPoint: (t) => hu(p, t, e)
			});
			try {
				p.setGraph?.(o), n.theme && (s.dataset.theme = r, p.setSetting?.("labelColor", sf(r))), u();
			} catch (t) {
				e.onFatalError?.(t);
			}
		},
		destroy() {
			if (!n) {
				ge(), n = !0, m += 1, x?.destroy(), x = null, b?.destroy(), b = null, I(), le(), re(), B(), w?.disconnect(), w = null;
				try {
					p.kill?.();
				} catch (t) {
					e.onFatalError?.(t);
				}
				s.remove();
			}
		}
	};
	function ee() {
		let e = (e) => {
			let t = md(e);
			Se(t) || fe({
				nodeId: t,
				additive: hd(e)
			});
		}, t = (e) => fe({
			screenPoint: gd(e),
			additive: hd(e)
		}), n = () => R(N), r = (e) => pe(md(e), gd(e), e), i = (e) => me(gd(e), e), a = (e) => he(gd(e), e);
		S = [
			{
				event: "clickNode",
				listener: e
			},
			{
				event: "clickStage",
				listener: t
			},
			{
				event: "downNode",
				listener: r
			},
			{
				event: "moveBody",
				listener: i
			},
			{
				event: "upNode",
				listener: a
			},
			{
				event: "upStage",
				listener: a
			},
			{
				event: "afterRender",
				listener: n
			}
		];
		for (let e of S) p.on?.(e.event, e.listener);
		let o = p.getCamera?.();
		if (o?.on) {
			let e = () => R(N);
			o.on("updated", e), C = [{
				event: "updated",
				listener: e
			}];
		}
	}
	function I() {
		for (let e of S) p.off?.(e.event, e.listener);
		S = [];
		let e = p.getCamera?.();
		for (let t of C) e?.off?.(t.event, t.listener);
		C = [];
	}
	function L() {
		te(140, tf);
	}
	function te(e, t = 0) {
		N += 1, O = Math.max(O, V() + e), k = !1, A = 0, j = Math.max(j, t), R(N);
	}
	function R(e) {
		let t = s.ownerDocument.defaultView;
		if (!t?.requestAnimationFrame) {
			z(e, !1);
			return;
		}
		M !== null && P === e || (M !== null && (t.cancelAnimationFrame?.(M), M = null), P = e, M = t.requestAnimationFrame(() => {
			M = null, P = null, z(e, !0);
		}));
	}
	function z(t, r) {
		if (!(n || t !== N)) try {
			let e = !!(p.getCamera?.())?.isAnimated?.();
			e && (k = !0);
			let n = A < j, i = O > V() && !k || n, a = e || i;
			if (g || D || !a) {
				if (b?.reposition(), !a) {
					O = 0, k = !1, A = 0, j = 0, D = !1, re();
					return;
				}
				r && R(t);
				return;
			}
			b?.repositionForCameraAnimation() ?? !1 ? A += 1 : j = A, r && R(t);
		} catch (t) {
			e.onFatalError?.(t);
		}
	}
	function ne() {
		if (N += 1, O = 0, k = !1, A = 0, j = 0, D = !0, b?.invalidateAnimationBaseline(), !p.getCamera?.().isAnimated?.()) {
			D = !1, b?.reposition();
			return;
		}
		R(N);
	}
	function re() {
		M !== null && (s.ownerDocument.defaultView?.cancelAnimationFrame?.(M), M = null, P = null);
	}
	function ie(e) {
		if (v = e.communityId, e.movement === "animated") {
			te(380, tf);
			return;
		}
		e.movement === "immediate" && b?.reposition();
	}
	function ae(t, r) {
		let i = () => {
			if (F = null, !(n || r !== m)) try {
				ie(xd(p, s, a, ed(a), t, e.onFatalError));
			} catch (t) {
				e.onFatalError?.(t);
			}
		}, o = s.ownerDocument.defaultView;
		if (!o?.requestAnimationFrame) {
			i();
			return;
		}
		B(), F = o.requestAnimationFrame(i);
	}
	function B() {
		F !== null && (s.ownerDocument.defaultView?.cancelAnimationFrame?.(F), F = null);
	}
	function V() {
		return s.ownerDocument.defaultView?.performance?.now?.() ?? Date.now();
	}
	function oe(t, n, r) {
		let i = p.getCamera?.(), a = yd(p) ?? {
			x: 0,
			y: 0,
			angle: 0,
			ratio: 1
		}, o = typeof n == "number" ? n : Wu(a.ratio, n), c = p.getViewportZoomedState?.(t, o) ?? {
			...a,
			ratio: o
		};
		if (r && i?.animate && !Od(s.ownerDocument.defaultView)) {
			let t = i.animate(c, {
				duration: 140,
				easing: "quadraticOut"
			});
			t && typeof t.catch == "function" && t.catch((t) => e.onFatalError?.(t)), L();
			return;
		}
		ne(), i?.setState?.(c);
	}
	function se() {
		let e = s.ownerDocument.defaultView?.ResizeObserver;
		e && (E = de(), w = new e((e) => {
			if (n) return;
			let t = ue(e) ?? de();
			t && E && lf(t, E) || (t && (E = t), ce());
		}), w.observe(s));
	}
	function ce() {
		if (T !== null) return;
		let t = s.ownerDocument.defaultView, r = () => {
			T = null;
			try {
				if (n) return;
				ne(), p.refresh?.(), b?.reposition();
			} catch (t) {
				e.onFatalError?.(t);
			}
		};
		if (t?.requestAnimationFrame) {
			T = t.requestAnimationFrame(r);
			return;
		}
		r();
	}
	function le() {
		T !== null && (s.ownerDocument.defaultView?.cancelAnimationFrame?.(T), T = null);
	}
	function ue(e) {
		let t = e.find((e) => e.target === s) ?? e[0];
		if (!t?.contentRect) return null;
		let n = cf(t.contentRect.width, 0), r = cf(t.contentRect.height, 0);
		return n <= 0 || r <= 0 ? null : {
			width: n,
			height: r
		};
	}
	function de() {
		let e = typeof s.getBoundingClientRect == "function" ? s.getBoundingClientRect() : null, t = cf(e?.width, 0), n = cf(e?.height, 0);
		return t <= 0 || n <= 0 ? null : {
			width: t,
			height: n
		};
	}
	function fe(t) {
		if (n) return;
		let r = m, i = f.targetFromSigmaHit(t);
		n || r !== m || (h = i, e.onHitTarget?.(i, { additive: !!t.additive }));
	}
	function pe(t, r, i) {
		if (n || !t || !r || !o.hasNode(t)) return;
		qu(i), ge(), ne();
		let a = ye(t), c = hu(p, r, e);
		g = cu({
			nodeId: t,
			pinKey: be(t),
			startPoint: a,
			pointerStart: r,
			pointerWorldPoint: c,
			initiallyPinned: !!o.getNodeAttribute(t, "pinned"),
			initialPinPosition: xe(t),
			previousCameraPanning: p.getSetting?.("enableCameraPanning")
		}), p.setSetting?.("enableCameraPanning", !1), s.dataset.draggingNodeId = t, e.onDragActiveChange?.(!0);
	}
	function me(t, r) {
		let i = g;
		!i || n || !t || (qu(r), lu(i, t, hu(p, t, e)), i.moved && ve(i.nodeId, i.currentPoint, i.initiallyPinned, i.initialPinPosition));
	}
	function he(t, r) {
		let i = g;
		if (!i || n || (qu(r), t && me(t, r), b?.clearActiveDragListeners(), _e(i), g = null, delete s.dataset.draggingNodeId, e.onDragActiveChange?.(!1), !i.moved)) return;
		y = i.nodeId;
		let a = {
			x: i.currentPoint.x,
			y: i.currentPoint.y,
			coordinateSpace: "world"
		};
		_ = {
			..._,
			[i.pinKey]: a
		}, ve(i.nodeId, i.currentPoint, !0, a), e.onPinsChanged?.(_);
	}
	function ge() {
		let t = g;
		t && (b?.clearActiveDragListeners(), _e(t), g = null, delete s.dataset.draggingNodeId, ve(t.nodeId, t.startPoint, !!_[t.pinKey], _[t.pinKey] ?? null), e.onDragActiveChange?.(!1));
	}
	function _e(e) {
		let t = typeof e.previousCameraPanning == "boolean" ? e.previousCameraPanning : !0;
		p.setSetting?.("enableCameraPanning", t);
	}
	function ve(e, t, n, r = null) {
		let i = !!g;
		o.hasNode(e) && (o.mergeNodeAttributes(e, {
			x: cf(t.x, 0),
			y: cf(t.y, 0),
			pinned: n
		}), a = uu(a, e, t, n, r), p.refresh?.(), i || (d = bu(d, a, e), b?.rebuild()));
	}
	function ye(e) {
		return {
			x: cf(o.getNodeAttribute(e, "x"), 0),
			y: cf(o.getNodeAttribute(e, "y"), 0)
		};
	}
	function be(e) {
		let t = o.getNodeAttribute(e, "sourcePath");
		return typeof t == "string" && t ? t : e;
	}
	function xe(e) {
		let t = be(e);
		return _[t] ?? null;
	}
	function Se(e) {
		return !e || y !== e ? !1 : (y = null, !0);
	}
	function Ce(t, n) {
		let r = we(n.cx, n.cy, n.rx, n.ry);
		return wu(Su(d.get(t), p, e), r);
	}
	function we(t, n, r, i) {
		let a = gu(p, {
			x: t - r,
			y: n - i
		}, e), o = gu(p, {
			x: t + r,
			y: n + i
		}, e);
		return {
			left: Math.min(a.x, o.x),
			top: Math.min(a.y, o.y),
			width: Math.max(8, Math.abs(o.x - a.x)),
			height: Math.max(8, Math.abs(o.y - a.y))
		};
	}
	function Te() {
		if (n) throw Error("Sigma global renderer has been destroyed");
	}
}
function af(e, t) {
	let n = e.ownerDocument.createElement("div");
	return n.className = "sigma-global-renderer", n.dataset.renderer = ef, n.dataset.theme = t, n.tabIndex = 0, e.append(n), n;
}
function of(e) {
	let t = ln(e);
	return {
		renderEdgeLabels: !1,
		allowInvalidContainer: !1,
		labelColor: sf(e),
		labelFont: t.vars["--font-ui"],
		zoomingRatio: Vu,
		zoomDuration: 120,
		minCameraRatio: Bu,
		maxCameraRatio: 3
	};
}
function sf(e) {
	return { color: e === "mo-ye" ? "#f8fafc" : "#6b6256" };
}
function cf(e, t) {
	return typeof e == "number" && Number.isFinite(e) ? e : t;
}
function lf(e, t) {
	return Math.abs(e.width - t.width) < 1 && Math.abs(e.height - t.height) < 1;
}
//#endregion
//#region src/graph-routes/sigma-global-route.ts
function uf(e, t, n, r) {
	return n.kind === "node" ? n.id ? r.additive ? vi(e, t, n.id) : {
		kind: "node",
		id: n.id
	} : t ?? null : n.kind === "community-wash" ? n.id ? {
		kind: "community",
		id: n.id
	} : null : n.kind === "aggregation-container" && n.communityId ? {
		kind: "community",
		id: n.communityId
	} : null;
}
function df(e) {
	let t = e.options, n = !1, r = null, i = !!t.searchQuery, o = null, s = !1, c = Ki(e.container.ownerDocument.defaultView?.localStorage), l = null, u = ff(t), d = e.container.ownerDocument.createElement("div");
	return d.className = "sigma-global-route llm-wiki-graph-engine", d.dataset.route = "sigma-global", pf(d, t.theme), e.container.append(d), pc(e.container.ownerDocument), _(), nf().then((i) => {
		if (!n) try {
			r = rf({
				container: d,
				adapterData: u,
				theme: t.theme,
				edgeStyle: t.edgeStyle,
				runtime: i,
				pins: t.pins,
				onPinsChanged: m,
				onDragActiveChange: e.options.callbacks.onDragActiveChange,
				onHitTarget: h,
				onFatalError: (t) => e.onSigmaUnavailable?.(t)
			});
		} catch (t) {
			e.onSigmaUnavailable?.(t);
		}
	}).catch((t) => e.onSigmaUnavailable?.(t)), {
		applyDiff() {
			return Promise.resolve();
		},
		isDragging() {
			return !!r?.isDragging();
		},
		setData(e, n) {
			t = {
				...t,
				data: e,
				pins: n || t.pins
			}, x(), _(), f();
		},
		setEdgeStyle(e) {
			t = {
				...t,
				edgeStyle: e
			}, f();
		},
		setAggregationMarkers(e) {
			t = {
				...t,
				aggregationMarkers: e
			}, f();
		},
		focusNode(e) {
			let n = t.data.nodes.find((t) => t.id === e || a(t) === e);
			t = {
				...t,
				selection: n ? {
					kind: "node",
					id: n.id
				} : null
			}, f();
		},
		focusCommunity() {
			f();
		},
		setSourceCommunityContext(e) {
			t = {
				...t,
				sourceCommunityId: e
			}, f();
		},
		setTypeFilters(e) {
			t = {
				...t,
				typeFilters: e
			}, x(), _(), f();
		},
		showTemporaryObject(e) {
			t = {
				...t,
				temporaryObject: e
			}, f();
		},
		clearTemporaryObjectDisplay() {
			t = {
				...t,
				temporaryObject: null
			}, f();
		},
		resetView() {
			t = {
				...t,
				focus: null
			}, p(null), r?.resetView();
		},
		select(e) {
			p(e);
		},
		previewNode() {},
		clearSelection() {
			t = {
				...t,
				sourceCommunityId: null
			}, p(null), e.options.callbacks.onSelectionClearRequested?.();
		},
		clearInteraction() {
			t = {
				...t,
				focus: null,
				selection: null,
				temporaryObject: null
			}, f();
		},
		setNodeFixed(n, r) {
			let i = t.data.nodes.find((e) => e.id === n);
			if (!i) return !1;
			let o = a(i), s = { ...t.pins };
			if (r === "fix") {
				let e = ff(t).nodes.find((e) => e.id === n);
				s[o] = {
					x: e?.point.x ?? mf(i.x),
					y: e?.point.y ?? mf(i.y),
					coordinateSpace: "world"
				};
			} else delete s[o];
			return t = {
				...t,
				pins: s
			}, e.options.callbacks.onPinsChanged?.(s), f(), !0;
		},
		setTheme(e) {
			t = {
				...t,
				theme: e
			}, pf(d, e), f();
		},
		setPins(e) {
			t = {
				...t,
				pins: e
			}, f();
		},
		resetLayout() {
			t = {
				...t,
				pins: {}
			}, f();
		},
		destroy() {
			n || (n = !0, r?.destroy(), r = null, d.remove());
		}
	};
	function f() {
		u = ff(t), !(!r || n) && r.update({
			adapterData: u,
			theme: t.theme,
			edgeStyle: t.edgeStyle,
			pins: t.pins
		});
	}
	function p(e) {
		t = {
			...t,
			selection: e
		}, f();
	}
	function m(n) {
		t = {
			...t,
			pins: n
		}, e.options.callbacks.onPinsChanged?.(n), f();
	}
	function h(n, i) {
		let a = uf(t.data, t.selection, n, i);
		if (a) {
			g(a);
			return;
		}
		switch (n.kind) {
			case "node":
			case "community-wash":
			case "aggregation-container":
				t = {
					...t,
					sourceCommunityId: null
				}, e.options.callbacks.onSelectionClearRequested?.(), p(null);
				break;
			case "edge": break;
			case "graph-blank":
				let n = t.selection?.kind === "community";
				t = {
					...t,
					temporaryObject: null,
					sourceCommunityId: null
				}, e.options.callbacks.onSelectionClearRequested?.(), p(null), n && r?.resetView();
				break;
		}
	}
	function g(t) {
		e.options.callbacks.onSelectionInput?.(t), p(t);
	}
	function _() {
		d.dataset.theme = t.theme, d.dataset.searchOpen = i ? "true" : "false", d.querySelector(".graph-search")?.remove(), d.querySelector(".graph-toolbar")?.remove(), d.querySelector(".graph-zoom-controls")?.remove();
		let n = ic(e.container.ownerDocument, {
			open: i,
			query: t.searchQuery,
			onOpen: () => {
				i = !0, _();
			},
			onQuery: v,
			onNext: () => y("next"),
			onPrevious: () => y("previous"),
			onActivate: b,
			onClose: () => {
				i = !1, o = null, v("");
			}
		});
		d.prepend(n.element), l = n.status, S(n.status);
		let a = u, p = mi(a.renderable.communities, a.renderable.nodes), m = rc(e.container.ownerDocument, {
			rows: p,
			collapsed: s,
			onToggle: () => {
				s = !s, _();
			},
			onHover: (e) => {
				d.dataset.legendHover = e || "";
			},
			onSelect: (e) => g({
				kind: "community",
				id: e
			})
		}), h = tc(e.container.ownerDocument, {
			panelState: c,
			typeFilters: t.typeFilters,
			onPanelToggle: (t) => {
				c = Ji(c, t), qi(e.container.ownerDocument.defaultView?.localStorage, c), _();
			},
			onTypeFilterToggle: (e, n) => {
				t = {
					...t,
					typeFilters: {
						...t.typeFilters,
						[e]: n
					}
				}, x(), _(), f();
			},
			onReset: () => {
				e.options.callbacks.onGlobalResetRequested?.();
			}
		});
		h.filtersPanel.appendChild(m.element), d.prepend(h.element);
		let C = nc(e.container.ownerDocument, {
			onZoomIn: () => r?.zoomIn(),
			onZoomOut: () => r?.zoomOut()
		});
		d.prepend(C.element);
	}
	function v(e) {
		let n = Ds(t.data.nodes, e);
		t = {
			...t,
			searchQuery: n.query,
			searchResultIds: n.matchIds
		}, n.matchIds.includes(o || "") || (o = null), x(), l && S(l), f();
	}
	function y(e) {
		let n = Ds(t.data.nodes, t.searchQuery), r = o ? n.matchIds.indexOf(o) : -1;
		if (!n.matchIds.length) return;
		let i = e === "next" ? (r + 1 + n.matchIds.length) % n.matchIds.length : (r - 1 + n.matchIds.length) % n.matchIds.length;
		o = n.matchIds[i], _();
	}
	function b() {
		let e = Ds(t.data.nodes, t.searchQuery), n = o || e.matchIds[0];
		n && g({
			kind: "node",
			id: n
		});
	}
	function x() {
		e.options.callbacks.onVisibilityStateChange?.({
			searchQuery: t.searchQuery,
			searchResultIds: t.searchResultIds,
			typeFilters: t.typeFilters,
			temporaryObject: t.temporaryObject
		});
	}
	function S(e) {
		let n = Ds(t.data.nodes, t.searchQuery), r = o ? n.matchIds.indexOf(o) : -1;
		e.textContent = n.query ? `${n.matchIds.length} 个结果${r >= 0 ? ` · ${r + 1}/${n.matchIds.length}` : ""}` : "输入关键词";
	}
}
function ff(e) {
	return Pi(e.data, {
		theme: e.theme,
		pins: e.pins,
		selection: e.selection,
		searchResultIds: e.searchResultIds,
		aggregationMarkers: e.aggregationMarkers,
		focus: null,
		typeFilters: e.typeFilters,
		sourceCommunityId: e.sourceCommunityId
	});
}
function pf(e, t) {
	e.dataset.theme = t, e.style.colorScheme = ln(t).colorScheme;
	let n = un(t);
	for (let [t, r] of Object.entries(n)) e.style.setProperty(t, r);
}
function mf(e) {
	let t = typeof e == "number" ? e : Number(e);
	return Number.isFinite(t) ? t : 0;
}
//#endregion
//#region src/facade.ts
function hf(e) {
	return {
		mode: "workbench",
		capabilities: {
			onOpenPage: e.onOpenPage,
			onSelectionChange: e.onSelectionChange,
			onSelectionClear: e.onSelectionClear,
			onViewReset: e.onViewReset,
			onAsk: e.onAsk,
			persistPins: e.persistPins,
			onDragStateChange: e.onDragStateChange,
			onVisibilityStateChange: e.onVisibilityStateChange
		}
	};
}
function gf(e = {}) {
	return {
		mode: "offline",
		capabilities: { persistPins: e.persistPins }
	};
}
function _f() {
	return {
		mode: "standalone",
		capabilities: void 0
	};
}
var vf = 2e3, yf = 160;
function bf(e, t) {
	if (!e) throw Error("createGraphEngine requires a container element");
	let n = t.capabilities, r = {
		data: t.data,
		pins: t.pins || {},
		theme: t.theme,
		edgeStyle: t.edgeStyle,
		focus: t.focus || null,
		typeFilters: t.typeFilters || {},
		aggregationMarkers: t.aggregationMarkers || [],
		selection: null,
		searchQuery: "",
		searchResultIds: [],
		temporaryObject: null
	}, i = {
		onNodeOpen: n?.onOpenPage ? (e) => n.onOpenPage?.(Af(r.data, e)) : void 0,
		onSelectionInput: kf(n) ? (e) => {
			let t = yi(r.data, e, { canAsk: !!n?.onAsk });
			n?.onSelectionChange?.(t), n?.onSelectionChange || n?.onAsk?.(t);
		} : void 0,
		onPinsChanged: n?.persistPins ? (e) => {
			r.pins = e, n.persistPins?.(e);
		} : void 0,
		onSelectionClearRequested: n?.onSelectionClear,
		onViewReset: () => {
			delete e.dataset.llmWikiGraphFocus, n?.onViewReset?.();
		},
		onDragActiveChange: n?.onDragStateChange,
		onVisibilityStateChange: (e) => {
			r.searchQuery = e.searchQuery, r.searchResultIds = e.searchResultIds, r.typeFilters = e.typeFilters, r.temporaryObject = e.temporaryObject, n?.onVisibilityStateChange?.(e);
		}
	};
	return Df(e, xf(e, {
		state: r,
		toolbarContainer: t.toolbarContainer,
		callbacks: i
	}), t, r);
}
function xf(e, t) {
	let n = t.state;
	n.theme = n.theme || "shan-shui", n.edgeStyle = n.edgeStyle || void 0, n.focus = n.focus || null, n.typeFilters = n.typeFilters || {}, n.aggregationMarkers = n.aggregationMarkers || [], n.selection = n.selection || null, n.searchQuery = n.searchQuery || "", n.searchResultIds = n.searchResultIds || [], n.temporaryObject = n.temporaryObject || null;
	let r = {
		createSigmaGlobal: t.factories?.createSigmaGlobal || df,
		createDomSvgCommunity: t.factories?.createDomSvgCommunity || ((e) => Sf(e, t.toolbarContainer, !0)),
		createDomSvgSmallFallback: t.factories?.createDomSvgSmallFallback || ((e) => Sf(e, t.toolbarContainer, !0)),
		createOverLimitNotice: t.factories?.createOverLimitNotice || Ef
	}, i = "sigma-global", o = !1, s = 0, c = !1, l, u, d = !1, f = null, p = {
		get routeId() {
			return i;
		},
		get sigmaKnownUnavailable() {
			return o;
		},
		get sigmaAttemptCount() {
			return s;
		},
		get sourceCommunityId() {
			return n.sourceCommunityId ?? null;
		},
		setSourceCommunityContext(e) {
			O(), n.sourceCommunityId = e, i === "sigma-global" && k().setSourceCommunityContext?.(e);
		},
		retrySigma() {
			O(), o = !1, w("sigma-global", v);
		},
		applyDiff(e, t) {
			return O(), k().applyDiff(e, t);
		},
		isDragging() {
			return O(), k().isDragging();
		},
		setData(e, t) {
			O(), n.data = e, t && (n.pins = t);
			let r = !1;
			if (n.sourceCommunityId && !wf(n.data, n.sourceCommunityId) && (n.sourceCommunityId = null, r = !0), r && k().setSourceCommunityContext?.(null), Cf(n.data)) {
				i === "over-limit-notice" && l ? k().setData(e, t) : S();
				return;
			}
			if (i === "over-limit-notice") {
				m();
				return;
			}
			if (o) {
				i === "dom-svg-small-fallback" && l ? k().setData(e, t) : b();
				return;
			}
			k().setData(e, t);
		},
		setEdgeStyle(e) {
			O(), n.edgeStyle = e, i === "sigma-global" && k().setEdgeStyle(e);
		},
		setAggregationMarkers(e) {
			O(), n.aggregationMarkers = e, k().setAggregationMarkers(e);
		},
		focusNode(e) {
			O(), k().focusNode(e);
		},
		focusCommunity(e) {
			O(), n.focus = {
				kind: "community",
				id: e
			}, n.sourceCommunityId = e, w("dom-svg-community", () => r.createDomSvgCommunity(D())), k().focusCommunity(e);
		},
		setTypeFilters(e) {
			O(), n.typeFilters = e, k().setTypeFilters(e);
		},
		showTemporaryObject(e) {
			O(), n.temporaryObject = e, k().showTemporaryObject(e);
		},
		clearTemporaryObjectDisplay() {
			O(), n.temporaryObject = null, k().clearTemporaryObjectDisplay();
		},
		resetView() {
			O(), g();
		},
		select(e) {
			O(), n.selection = e, e.kind === "community" && (n.sourceCommunityId = e.id), k().select(e);
		},
		previewNode(e) {
			O(), k().previewNode(e);
		},
		clearSelection() {
			O();
			let e = n.sourceCommunityId != null;
			n.selection = null, n.sourceCommunityId = null, e && k().setSourceCommunityContext?.(null), k().clearSelection();
		},
		clearInteraction() {
			O();
			let e = n.sourceCommunityId != null;
			n.focus = null, n.selection = null, n.sourceCommunityId = null, n.temporaryObject = null, e && k().setSourceCommunityContext?.(null), k().clearInteraction();
		},
		setNodeFixed(e, t) {
			O();
			let r = k().setNodeFixed(e, t);
			if (r && t === "unfix") {
				let t = n.data.nodes.find((t) => t.id === e), r = t ? a(t) : e;
				if (n.pins[r]) {
					let e = { ...n.pins };
					delete e[r], n.pins = e;
				}
			}
			return r;
		},
		setTheme(e) {
			O(), n.theme = e, k().setTheme(e);
		},
		setPins(e) {
			O(), n.pins = e, k().setPins(e);
		},
		resetLayout() {
			O();
			let e = {};
			n.pins = e, d = !0, f = null;
			try {
				k().resetLayout();
			} finally {
				d = !1;
			}
			let r = f ?? e;
			f = null, n.pins = r, t.callbacks?.onPinsChanged?.(r);
		},
		destroy() {
			c || (c = !0, E(), delete e.dataset.llmWikiGraphRoute, delete e.dataset.llmWikiGraphRouteTransition, l?.destroy());
		}
	};
	return l = v(), T(i, null), p;
	function m() {
		if (Cf(n.data)) {
			S();
			return;
		}
		if (o) {
			b();
			return;
		}
		w("sigma-global", v);
	}
	function h() {
		let e = i;
		return n.focus = null, _(), m(), i === "sigma-global" ? (e === i && k().resetView(), { shouldNotifyViewReset: !0 }) : (k().resetView(), { shouldNotifyViewReset: i !== "dom-svg-small-fallback" });
	}
	function g() {
		let e = i, t = n.sourceCommunityId != null;
		if (n.sourceCommunityId = null, e === "sigma-global" && n.selection?.kind === "community") {
			_(), t && k().setSourceCommunityContext?.(null), k().resetView();
			return;
		}
		n.focus = null, _(), m(), e === i && (t && k().setSourceCommunityContext?.(null), k().resetView());
	}
	function _() {
		n.selection?.kind === "community" && (n.selection = null, n.temporaryObject = null, t.callbacks?.onSelectionClearRequested?.());
	}
	function v() {
		if (Cf(n.data)) return C();
		if (o) return x();
		s += 1, i = "sigma-global";
		try {
			return r.createSigmaGlobal(D((e) => {
				y(e);
			}));
		} catch {
			return o = !0, x();
		}
	}
	function y(e) {
		c || o || (o = !0, i === "sigma-global" && b());
	}
	function b() {
		if (Cf(n.data)) {
			S();
			return;
		}
		w("dom-svg-small-fallback", () => x());
	}
	function x() {
		return Cf(n.data) ? C() : (i = "dom-svg-small-fallback", r.createDomSvgSmallFallback(D(void 0, () => p.retrySigma())));
	}
	function S() {
		w("over-limit-notice", C);
	}
	function C() {
		return i = "over-limit-notice", r.createOverLimitNotice(D());
	}
	function w(e, t) {
		if (c || i === e && l) return;
		let n = i, r = l;
		i = e;
		let a = t();
		T(i, n), l = a, r?.destroy();
	}
	function T(t, n) {
		e.dataset.llmWikiGraphRoute = t, E(), !(!n || n === t) && (e.dataset.llmWikiGraphRouteTransition = `${n}->${t}`, u = setTimeout(() => {
			c || delete e.dataset.llmWikiGraphRouteTransition, u = void 0;
		}, yf));
	}
	function E() {
		u &&= (clearTimeout(u), void 0), delete e.dataset.llmWikiGraphRouteTransition;
	}
	function D(r, i) {
		return {
			container: e,
			options: {
				data: n.data,
				pins: n.pins,
				theme: n.theme || "shan-shui",
				edgeStyle: n.edgeStyle,
				focus: n.focus || null,
				typeFilters: n.typeFilters || {},
				aggregationMarkers: n.aggregationMarkers || [],
				selection: n.selection || null,
				sourceCommunityId: n.sourceCommunityId || null,
				searchQuery: n.searchQuery || "",
				searchResultIds: n.searchResultIds || [],
				temporaryObject: n.temporaryObject || null,
				callbacks: {
					...t.callbacks || {},
					onSelectionInput: (e) => {
						n.selection = e, t.callbacks?.onSelectionInput?.(e);
					},
					onSelectionClearRequested: () => {
						n.selection = null, n.sourceCommunityId = null, n.temporaryObject = null, t.callbacks?.onSelectionClearRequested?.();
					},
					onPinsChanged: (e) => {
						if (n.pins = e, d) {
							f = e;
							return;
						}
						t.callbacks?.onPinsChanged?.(e);
					},
					onGlobalResetRequested: () => {
						O(), h().shouldNotifyViewReset && t.callbacks?.onViewReset?.();
					},
					onVisibilityStateChange: (e) => {
						n.searchQuery = e.searchQuery, n.searchResultIds = e.searchResultIds, n.typeFilters = e.typeFilters, n.temporaryObject = e.temporaryObject, t.callbacks?.onVisibilityStateChange?.(e);
					}
				}
			},
			onSigmaUnavailable: r,
			onRetrySigma: i
		};
	}
	function O() {
		if (c) throw Error("Graph facade route manager has been destroyed");
	}
	function k() {
		if (!l) throw Error("Graph facade route manager has no active renderer");
		return l;
	}
}
function Sf(e, t, n) {
	let r = al(e.container, {
		data: e.options.data,
		pins: e.options.pins,
		theme: e.options.theme,
		toolbarContainer: t,
		focus: e.options.focus || void 0,
		typeFilters: e.options.typeFilters,
		aggregationMarkers: e.options.aggregationMarkers,
		searchQuery: e.options.searchQuery,
		live: n,
		sourceCommunityId: e.options.sourceCommunityId,
		onNodeOpen: e.options.callbacks.onNodeOpen,
		onSelectionInput: e.options.callbacks.onSelectionInput,
		onPinsChanged: e.options.callbacks.onPinsChanged,
		onSelectionClearRequested: e.options.callbacks.onSelectionClearRequested,
		onViewReset: e.options.callbacks.onViewReset,
		onGlobalResetRequested: e.options.callbacks.onGlobalResetRequested,
		onDragActiveChange: e.options.callbacks.onDragActiveChange,
		onVisibilityStateChange: e.options.callbacks.onVisibilityStateChange
	});
	return e.options.selection && e.options.selection.kind !== "community" && r.select(e.options.selection), e.options.temporaryObject && r.showTemporaryObject(e.options.temporaryObject), {
		...r,
		setEdgeStyle() {}
	};
}
function Cf(e) {
	return Tf(e) > vf;
}
function wf(e, t) {
	return e.nodes.some((e) => e.community === t) ? !0 : (e.learning?.communities ?? []).some((e) => e.id === t);
}
function Tf(e) {
	return e.nodes.length;
}
function Ef(e) {
	let t = e.options, n = !1, r = e.container.ownerDocument;
	if (!r) throw Error("over-limit notice requires a DOM container");
	let i = r.createElement("div");
	return i.className = "graph-over-limit-notice-view", i.dataset.route = "over-limit-notice", i.dataset.notice = "node-count-over-limit", e.container.append(i), o(), {
		applyDiff() {
			return Promise.resolve();
		},
		isDragging() {
			return !1;
		},
		setData(e, n) {
			t = {
				...t,
				data: e,
				pins: n || t.pins
			}, o();
		},
		setEdgeStyle(e) {
			t = {
				...t,
				edgeStyle: e
			};
		},
		setAggregationMarkers(e) {
			t = {
				...t,
				aggregationMarkers: e
			}, o();
		},
		focusNode(e) {
			let n = t.data.nodes.find((t) => t.id === e || a(t) === e);
			t = {
				...t,
				selection: n ? {
					kind: "node",
					id: n.id
				} : t.selection
			}, o();
		},
		focusCommunity(e) {
			t = {
				...t,
				focus: {
					kind: "community",
					id: e
				}
			}, o();
		},
		setTypeFilters(e) {
			t = {
				...t,
				typeFilters: e
			}, o();
		},
		showTemporaryObject(e) {
			t = {
				...t,
				temporaryObject: e
			}, o();
		},
		clearTemporaryObjectDisplay() {
			t = {
				...t,
				temporaryObject: null
			}, o();
		},
		resetView() {
			t = {
				...t,
				focus: null
			}, o();
		},
		select(e) {
			t = {
				...t,
				selection: e
			}, o();
		},
		previewNode() {},
		clearSelection() {
			t = {
				...t,
				selection: null
			}, e.options.callbacks.onSelectionClearRequested?.(), o();
		},
		clearInteraction() {
			t = {
				...t,
				focus: null,
				selection: null,
				temporaryObject: null
			}, o();
		},
		setNodeFixed() {
			return !1;
		},
		setTheme(e) {
			t = {
				...t,
				theme: e
			}, o();
		},
		setPins(e) {
			t = {
				...t,
				pins: e
			}, o();
		},
		resetLayout() {
			t = {
				...t,
				pins: {}
			}, o();
		},
		destroy() {
			n || (n = !0, i.remove());
		}
	};
	function o() {
		if (n) return;
		i.replaceChildren(), i.dataset.nodeCount = String(Tf(t.data)), i.dataset.edgeCount = String(t.data.meta.total_edges || t.data.edges.length), i.dataset.nodeLimit = String(vf), i.dataset.containerCount = "0", i.dataset.searchResultCount = String(t.searchResultIds.length), i.dataset.selectedCount = String(t.selection ? yi(t.data, t.selection, { canAsk: !1 }).nodeIds.length : 0), i.dataset.pinnedCount = String(Object.keys(t.pins).length), i.dataset.temporaryObject = t.temporaryObject ? t.temporaryObject.kind : "";
		let e = r.createElement("div");
		e.className = "graph-over-limit-notice", e.dataset.role = "over-limit-notice", i.append(e);
		let a = r.createElement("strong");
		a.className = "graph-over-limit-notice-title", a.textContent = "图谱节点较多", e.append(a);
		let o = r.createElement("p");
		o.className = "graph-over-limit-notice-body", o.textContent = "当前图谱超过 2000 个节点。请用搜索、筛选或进入社区缩小范围。", e.append(o);
	}
}
function Df(e, t, n, r = {
	data: n.data,
	pins: n.pins || {}
}) {
	let i = n.theme, o = !1, s = n.capabilities, c = !!n.capabilities?.onAsk, l = (e) => yi(r.data, e, { canAsk: c });
	return e.dataset.llmWikiGraphEngine = "mounted", e.dataset.llmWikiGraphTheme = i, {
		async applyDiff(e, n) {
			u(), await t.applyDiff(e, n);
		},
		isDragging() {
			return u(), t.isDragging();
		},
		setData(e, n) {
			u(), r.data = e, n && (r.pins = n);
			let i = !1;
			r.sourceCommunityId && !wf(e, r.sourceCommunityId) && (r.sourceCommunityId = null, i = !0), i && t.setSourceCommunityContext?.(null), t.setData(e, n);
		},
		setEdgeStyle(e) {
			u(), r.edgeStyle = e, t.setEdgeStyle(e);
		},
		setAggregationMarkers(e) {
			u(), r.aggregationMarkers = e, t.setAggregationMarkers(e);
		},
		focusNode(n) {
			u(), e.dataset.llmWikiGraphFocus = n;
			let i = r.data.nodes.find((e) => e.id === n || a(e) === n);
			r.selection = i ? {
				kind: "node",
				id: i.id
			} : null, t.focusNode(n);
		},
		focusCommunity(n) {
			return u(), e.dataset.llmWikiGraphFocus = `community:${n}`, r.focus = {
				kind: "community",
				id: n
			}, r.sourceCommunityId = n, t.focusCommunity(n), l({
				kind: "community",
				id: n
			});
		},
		get sourceCommunityId() {
			return r.sourceCommunityId ?? null;
		},
		setSourceCommunityContext(e) {
			u(), r.sourceCommunityId = e, t.setSourceCommunityContext?.(e);
		},
		setTypeFilters(e) {
			u(), r.typeFilters = e, t.setTypeFilters(e);
		},
		showTemporaryObject(e) {
			u(), r.temporaryObject = e, t.showTemporaryObject(e);
		},
		clearTemporaryObjectDisplay() {
			u(), r.temporaryObject = null, t.clearTemporaryObjectDisplay();
		},
		resetView() {
			u(), delete e.dataset.llmWikiGraphFocus, r.selection?.kind === "community" && (r.selection = null, r.temporaryObject = null, s?.onSelectionClear?.()), r.focus = null;
			let n = r.sourceCommunityId != null;
			r.sourceCommunityId = null, n && t.setSourceCommunityContext?.(null), t.resetView(), s?.onViewReset?.();
		},
		select(e) {
			return u(), r.selection = e, e.kind === "community" && (r.sourceCommunityId = e.id), t.select(e), l(e);
		},
		previewNode(e) {
			u(), t.previewNode(e);
		},
		summarizeNode(e, t) {
			return u(), sl(r.data, e, Of(r, t));
		},
		summarizeCommunity(e, t) {
			return u(), cl(r.data, e, Of(r, t));
		},
		summarizeGlobal(e) {
			return u(), ll(r.data, Of(r, e));
		},
		summarizeSearchResults(e, t, n) {
			return u(), ul(r.data, e, t, Of(r, n));
		},
		summarizeExcludedObject(e, t, n) {
			return u(), dl(r.data, e, t, Of(r, n));
		},
		summarizeUnavailableObject(e, t, n) {
			return u(), fl(r.data, e, t, Of(r, n));
		},
		clearSelection() {
			u();
			let e = r.sourceCommunityId != null;
			r.selection = null, r.sourceCommunityId = null, e && t.setSourceCommunityContext?.(null), t.clearSelection();
		},
		clearInteraction() {
			u(), delete e.dataset.llmWikiGraphFocus;
			let n = r.sourceCommunityId != null;
			r.focus = null, r.selection = null, r.sourceCommunityId = null, r.temporaryObject = null, n && t.setSourceCommunityContext?.(null), t.clearInteraction();
		},
		setNodeFixed(e, n) {
			return u(), t.setNodeFixed(e, n);
		},
		setTheme(n) {
			u(), i = n, e.dataset.llmWikiGraphTheme = i, t.setTheme(n);
		},
		setPins(e) {
			u(), r.pins = e, t.setPins(e);
		},
		resetLayout() {
			u(), r.pins = {}, t.resetLayout();
		},
		destroy() {
			o || (o = !0, t.destroy(), delete e.dataset.llmWikiGraphEngine, delete e.dataset.llmWikiGraphTheme, delete e.dataset.llmWikiGraphFocus);
		}
	};
	function u() {
		if (o) throw Error("Graph engine has been destroyed");
	}
}
function Of(e, t = {}) {
	return {
		...t,
		selection: t.selection ?? e.selection ?? null,
		searchResultIds: t.searchResultIds ?? e.searchResultIds ?? [],
		pins: t.pins ?? e.pins,
		aggregationMarkers: t.aggregationMarkers ?? e.aggregationMarkers ?? [],
		temporaryObject: t.temporaryObject ?? e.temporaryObject ?? null
	};
}
function kf(e) {
	return !!(e?.onSelectionChange || e?.onAsk);
}
function Af(e, t) {
	let n = e.nodes.find((e) => e.id === t);
	if (!n) return {
		path: t,
		node: {
			id: t,
			title: t,
			type: "entity",
			typeLabel: "实体",
			sourcePath: t,
			community: null,
			date: null,
			source: null,
			isolated: !0
		}
	};
	let r = a(n);
	return {
		path: r,
		node: {
			id: n.id,
			title: n.label || n.id,
			type: n.type,
			typeLabel: s(n.type),
			sourcePath: r,
			community: n.community ?? null,
			date: Mf(n),
			source: Nf(n),
			isolated: jf(e, n.id)
		}
	};
}
function jf(e, t) {
	return !e.edges.some((e) => e.from === t || e.to === t);
}
function Mf(e) {
	let t = e.date || e.updated_at || e.updatedAt || e.created_at || e.createdAt;
	return t == null || t === "" ? null : String(t);
}
function Nf(e) {
	let t = e.source_title || e.source_url || e.url || e.author || e.source_name;
	return t == null || t === "" ? null : String(t);
}
//#endregion
//#region src/index.ts
function Pf(e, t) {
	return bf(e, t);
}
//#endregion
export { yt as DEFAULT_GRAPH_EDGE_HIT_TOLERANCE, Ka as DEFAULT_GRAPH_LAYOUT_BOUNDS, bt as DEFAULT_GRAPH_NODE_FALLBACK_RADIUS, so as DEFAULT_RENDERER_VIEWPORT, su as GRAPH_ARCHITECTURE_LAYERS, fr as GRAPH_COMMUNITY_FOCUS_BUDGETS, dr as GRAPH_COMMUNITY_FOCUS_THRESHOLDS, Yo as GRAPH_GESTURE_BLOCKER_TARGET_KINDS, Xo as GRAPH_GESTURE_SELECTORS, fn as GRAPH_MINIMAP_VIEWBOX, Jo as GRAPH_OWNED_TARGET_KINDS, Ni as GRAPH_RENDERER_ADAPTER_ROUTES, ur as GRAPH_RENDER_BUDGETS, Wi as GRAPH_TOOLBAR_PANEL_KEY, W as GRAPH_WORLD_BOUNDS, U as GRAPH_WORLD_SIZE, tu as GraphDiffQueue, ss as GraphGestureController, os as GraphGestureStateMachine, Io as GraphRuntimeState, xt as GraphSpatialIndex, r as LEGACY_PERCENT_PIN_COORDINATE_SPACE, Ja as LiveGraphSimulation, Ha as PinState, cn as THEMES, e as UNGROUPED_COMMUNITY_ID, t as UNGROUPED_COMMUNITY_LABEL, n as WORLD_PIN_COORDINATE_SPACE, ge as appendQueueNote, Ae as applyFocusMode, yo as applyRendererViewportTransform, De as applySearchToNodeIds, Re as atlasConfidenceLabel, Ve as atlasNodeKind, We as atlasNodePoint, Ze as atlasPointToMinimap, Be as atlasTypeLabel, Xe as atlasViewportRect, $e as atlasViewportToMinimapRect, As as beginGraphNodeDrag, ut as buildAtlasModel, pl as buildCommunityAggregationMarkers, mi as buildCommunityLegend, Pi as buildGraphRendererAdapterData, Fi as buildGraphRendererBehaviorContract, Fc as buildHoverPreview, mr as buildRenderableGraph, we as buildSearchHaystack, Te as buildSearchIndex, ce as cardDims, Je as centerAtlasViewportOnPoint, wo as centerRendererViewportOnPoint, Ke as clampAtlasViewport, Zo as classifyGraphEventTarget, vs as classifyGraphKeyboardIntent, rs as classifyGraphPointerDownTarget, as as classifyGraphPointerDownTargetFromGraphTarget, ts as classifyGraphWheelTarget, ns as classifyGraphWheelTargetFromGraphTarget, Xa as constrainDragTargetToLayoutBounds, rl as createDomSvgRendererSurface, Pf as createGraphEngine, bf as createGraphFacade, gf as createGraphOfflineCapabilities, al as createGraphRenderer, al as createStaticGraphRenderer, Lo as createGraphRuntimeState, St as createGraphSpatialIndex, _f as createGraphStandaloneCapabilities, hf as createGraphWorkbenchCapabilities, Ya as createLiveGraphSimulation, pr as createRenderPathCache, le as createSafeStorage, Do as createViewportFrameCommitter, kn as defaultGraphViewportSize, ve as defaultLearning, pe as defaultQueue, dt as deriveAtlasLayout, Jl as diffGraphData, Tr as edgeOpacity, Or as edgeRelationClass, wr as edgeStrokeWidth, Dr as edgeVisualOpacity, Er as edgeVisualStrokeWidth, hr as evaluateCommunityQuality, Ee as filterLinksByTypes, Lc as firstUsefulParagraph, qe as fitAtlasViewport, Co as fitRendererViewportToPoints, ft as getAtlasDensityMode, Ge as getAtlasModelBounds, dn as getCommunityColor, xe as getCommunityNodeIds, ln as getThemeTokens, Ce as getVisibleLinks, Se as getVisibleNodeIds, fe as getWikiStorageNamespace, Qc as graphEdgeHoverAnchor, Qo as graphGestureTargetOwnership, Zc as graphNodeHoverAnchor, s as graphNodeTypeLabel, is as graphSpatialHitToGestureTarget, Si as groupDrawerActionById, xi as groupDrawerActions, ru as isEmptyDiff, es as isGraphGestureBlockerTarget, $o as isGraphOwnedGestureTarget, i as isPinCoordinateSpace, ys as isTextEditingElement, V as labelCharWidth, xn as layerDeltaToWorldDelta, gn as layerPointToWorldPoint, Sr as makeEdgePath, Cr as makeEdgePathFromPoints, oe as measureLabelWidth, nu as mergeGraphDiffs, Qe as minimapPointToAtlasPoint, Tn as minimapPointToWorldPoint, Ji as nextToolbarPanelState, Ar as nodeDisplayModeForDensity, Ue as normalizeAtlasViewport, Xt as normalizeGraphLayoutFile, Zt as normalizeGraphPinMap, ye as normalizeLearning, me as normalizeQueue, _o as normalizeRendererViewport, Gi as normalizeToolbarPanelState, bo as normalizeWheelDelta, gi as pageReaderActions, hi as pageSelectionActions, So as panRendererViewport, sn as parseCssTokens, Ua as pinsToPositions, Ic as previewSummary, Ki as readToolbarPanelState, Ci as recommendedGroupActionForCommunity, wi as recommendedGroupActionForSelection, On as rendererPointToScreenPoint, Eo as rendererViewportToMinimapRect, vo as rendererViewportToTransform, gt as resolveAtlasSelectedNodeId, ht as resolveAtlasVisibleSnapshot, xr as resolveCommunityFocusScale, $c as resolveGraphHoverPreviewPosition, js as resolveGraphNodeDragTarget, br as resolveGraphRenderBudget, Ds as resolveGraphSearchState, be as resolveInitialMode, Os as resolveNextGraphSearchFocus, ks as resolvePreviousGraphSearchFocus, _i as resolveSelection, yi as resolveSelectionForCapabilities, je as resolveVisibleSnapshot, pn as rootClientPointToScreenPoint, kr as screenEffectiveDensityMode, vn as screenPointToWorldPoint, bi as selectionActions, Me as shouldAutoOpenDrawer, Yi as shouldBlankClickCloseToolbar, An as sideExitWorldAnchor, B as splitLabelGraphemes, tt as stripAtlasMarkdown, dl as summarizeExcludedGraphObject, cl as summarizeGraphCommunity, ll as summarizeGraphGlobal, sl as summarizeGraphNode, ul as summarizeGraphSearchResults, _e as summarizeQueue, fl as summarizeUnavailableGraphObject, Cn as svgPointToWorldPoint, un as themeTokensToCssVars, vi as toggleNodeInSelection, he as toggleQueueFavorite, Xi as toolbarPanelStateAfterBlankClick, se as truncateLabel, To as viewportAfterResize, xo as viewportAfterWheelZoom, En as visibleWorldRectForViewport, Dn as visibleWorldRectToMinimapRect, o as wikiDirectoryForGraphNodeType, a as wikiPathForGraphNode, jn as worldBoundsForPoints, yn as worldDeltaToLayerDelta, bn as worldPointDeltaToLayerDelta, hn as worldPointToCssPercentPoint, mn as worldPointToLayerPoint, wn as worldPointToMinimapPoint, _n as worldPointToScreenPoint, Sn as worldPointToSvgPoint, qi as writeToolbarPanelState, Ye as zoomAtlasViewport };

//# sourceMappingURL=engine.esm.js.map