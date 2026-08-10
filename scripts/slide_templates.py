#!/usr/bin/env python3
"""Load, validate, and render reusable single-slide templates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "slide-templates"
MANIFEST_PATH = TEMPLATE_ROOT / "manifest.json"


class SlideTemplateError(ValueError):
    pass


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SlideTemplateError(f"not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SlideTemplateError(f"invalid JSON: {path}: {exc}") from exc


_MANIFEST_FIELDS = ("id", "displayName", "pack", "category", "path")


def load_manifest() -> dict:
    manifest = _read_json(MANIFEST_PATH)
    if manifest.get("schemaVersion") != 1:
        raise SlideTemplateError("manifest.schemaVersion must be 1")
    entries = manifest.get("templates")
    if not isinstance(entries, list):
        raise SlideTemplateError("manifest.templates must be an array")
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise SlideTemplateError(f"manifest.templates[{i}] must be an object")
        missing = [key for key in _MANIFEST_FIELDS
                   if not isinstance(entry.get(key), str) or not entry[key]]
        if missing:
            raise SlideTemplateError(
                f"manifest.templates[{i}]: missing or non-string: {', '.join(missing)}")
        if not isinstance(entry.get("tags", []), list):
            raise SlideTemplateError(f"manifest.templates[{i}]: tags must be an array")
    ids = [entry["id"] for entry in entries]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise SlideTemplateError(
            f"manifest contains duplicate ids: {', '.join(duplicates)}")
    return manifest


def template_entries(*, pack: str | None = None) -> list[dict]:
    entries = load_manifest()["templates"]
    return [entry for entry in entries if pack is None or entry.get("pack") == pack]


def template_entry(template_id: str) -> dict:
    for entry in template_entries():
        if entry["id"] == template_id:
            return entry
    raise SlideTemplateError(f"unknown slide template: {template_id}")


def load_template(template_id: str) -> tuple[dict, Path]:
    entry = template_entry(template_id)
    path = TEMPLATE_ROOT / entry["path"]
    return _read_json(path), path


def load_example(template_id: str) -> tuple[dict, Path]:
    template, path = load_template(template_id)
    example_name = template.get("example", "example.json")
    example_path = path.parent / example_name
    return _read_json(example_path), example_path


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_scalar(name: str, value: Any, spec: dict) -> list[str]:
    problems: list[str] = []
    kind = spec.get("type")
    valid = {
        "string": isinstance(value, str),
        "number": _is_number(value),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(kind)
    if valid is None:
        return [f"slot {name}: unknown type {kind!r}"]
    if not valid:
        return [f"slot {name}: expected {kind}, got {type(value).__name__}"]
    if isinstance(value, str):
        if spec.get("minLength") is not None and len(value) < spec["minLength"]:
            problems.append(f"slot {name}: shorter than minLength")
        if spec.get("maxLength") is not None and len(value) > spec["maxLength"]:
            problems.append(f"slot {name}: longer than maxLength")
    if _is_number(value):
        if spec.get("minimum") is not None and value < spec["minimum"]:
            problems.append(f"slot {name}: below minimum {spec['minimum']}")
        if spec.get("maximum") is not None and value > spec["maximum"]:
            problems.append(f"slot {name}: above maximum {spec['maximum']}")
    return problems


# Constraints that describe a leaf value. They cascade through every array level
# down to the scalars, so `string[][]` with maxLength bounds each cell.
_ITEM_CONSTRAINTS = ("minimum", "maximum", "minLength", "maxLength")


def _item_spec(kind: str, spec: dict) -> dict | None:
    """Spec for one element of an array-typed slot, or None when unconstrained."""
    inherited = {k: spec[k] for k in _ITEM_CONSTRAINTS if k in spec}
    declared = spec.get("items")
    if declared is not None:
        if not isinstance(declared, dict):
            return {"type": None}          # reported as "items.type is required"
        # An explicit `items` wins, but still inherits leaf constraints it does
        # not set itself, so maxLength and a row-length bound can coexist.
        return {**inherited, **declared}
    if kind.endswith("[]"):
        return {"type": kind[:-2], **inherited}
    return None


def _check_match_length(name: str, value: list, spec: dict, values: dict | None) -> list[str]:
    """`matchLength` ties this list's length to another slot's length."""
    target = spec.get("matchLength")
    if target is None:
        return []
    if values is None or target not in values:
        return [f"slot {name}: matchLength references unknown slot {target!r}"]
    reference = values[target]
    if not isinstance(reference, list):
        return []                          # the referenced slot's own type error
    if len(value) != len(reference):
        return [f"slot {name}: has {len(value)} entries but {target} has "
                f"{len(reference)}"]
    return []


def _validate_array(name: str, value: Any, spec: dict, kind: str,
                    values: dict | None) -> list[str]:
    if not isinstance(value, list):
        return [f"slot {name}: expected {kind}, got {type(value).__name__}"]
    problems: list[str] = []
    if spec.get("minItems") is not None and len(value) < spec["minItems"]:
        problems.append(f"slot {name}: fewer than minItems {spec['minItems']}")
    if spec.get("maxItems") is not None and len(value) > spec["maxItems"]:
        problems.append(f"slot {name}: more than maxItems {spec['maxItems']}")
    problems.extend(_check_match_length(name, value, spec, values))
    child_spec = _item_spec(kind, spec)
    if child_spec is None:
        return problems
    if not isinstance(child_spec.get("type"), str):
        return problems + [f"slot {name}: items.type is required"]
    for i, item in enumerate(value):
        problems.extend(_validate_value(f"{name}[{i}]", item, child_spec, values))
    return problems


def _validate_tuple(name: str, value: Any, spec: dict, values: dict | None) -> list[str]:
    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        return [f"slot {name}: tuple requires a non-empty fields array"]
    if not isinstance(value, list):
        return [f"slot {name}: expected tuple, got {type(value).__name__}"]
    if len(value) != len(fields):
        return [f"slot {name}: expected {len(fields)} entries, got {len(value)}"]
    problems: list[str] = []
    for i, (item, field) in enumerate(zip(value, fields)):
        if not isinstance(field, dict):
            problems.append(f"slot {name}: fields[{i}] must be an object")
            continue
        problems.extend(_validate_value(f"{name}[{i}]", item, field, values))
    return problems


def _validate_value(name: str, value: Any, spec: dict,
                    values: dict | None = None) -> list[str]:
    kind = spec.get("type")
    if not isinstance(kind, str):
        return [f"slot {name}: type is required"]
    if kind == "tuple":
        return _validate_tuple(name, value, spec, values)
    if kind == "array" or kind.endswith("[]"):
        return _validate_array(name, value, spec, kind, values)
    return _validate_scalar(name, value, spec)


def _collect_references(node: Any, refs: set[str]) -> None:
    if isinstance(node, dict):
        if "$slot" in node:
            if len(node) != 1:
                siblings = ", ".join(sorted(set(node) - {"$slot"}))
                raise SlideTemplateError(
                    f"$slot object must have no sibling keys, found: {siblings}")
            name = node["$slot"]
            if not isinstance(name, str):
                raise SlideTemplateError(f"$slot must name a slot as a string, got {name!r}")
            refs.add(name)
            return
        for value in node.values():
            _collect_references(value, refs)
    elif isinstance(node, list):
        for value in node:
            _collect_references(value, refs)


def slot_references(slide: Any) -> set[str]:
    """Every slot name the slide references. Raises on malformed `$slot` objects."""
    refs: set[str] = set()
    _collect_references(slide, refs)
    return refs


# Figures whose element width is fixed by a sibling key: figure type ->
# (width key, element key, what one element is called). The drawing primitives
# raise on a mismatch (charts.py table / vbars_grouped), so deriving the rule
# from the slide keeps the slot contract in step with the figure automatically —
# editing a literal `headers` list re-tightens the row width with no template edit.
_ARITY_FIGURES = {
    "table": ("headers", "rows", "column"),
}


def _slot_name(node: Any) -> str | None:
    if isinstance(node, dict) and len(node) == 1 and isinstance(node.get("$slot"), str):
        return node["$slot"]
    return None


def _iter_figures(node: Any):
    if isinstance(node, dict):
        if isinstance(node.get("type"), str):
            yield node
        for value in node.values():
            yield from _iter_figures(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_figures(value)


def arity_rules(slide: Any) -> list[dict]:
    """Element-width rules the slide's figures impose on the slots they consume."""
    rules: list[dict] = []
    for figure in _iter_figures(slide):
        spec = _ARITY_FIGURES.get(figure.get("type"))
        if spec is None:
            continue
        width_key, element_key, unit = spec
        target = _slot_name(figure.get(element_key))
        if target is None:
            continue                       # literal rows: the engine checks them
        width = figure.get(width_key)
        rule = {"slot": target, "unit": unit, "via": f"{figure['type']}.{width_key}"}
        if isinstance(width, list):
            rules.append({**rule, "length": len(width)})
        elif (name := _slot_name(width)) is not None:
            rules.append({**rule, "lengthOf": name})
    return rules


def _check_arity(rules: list[dict], values: dict) -> list[str]:
    problems: list[str] = []
    for rule in rules:
        rows = values.get(rule["slot"])
        if not isinstance(rows, list):
            continue                       # type errors are reported by the slot pass
        if "length" in rule:
            expected: Any = rule["length"]
        else:
            reference = values.get(rule["lengthOf"])
            if not isinstance(reference, list):
                continue
            expected = len(reference)
        for i, row in enumerate(rows):
            if isinstance(row, list) and len(row) != expected:
                unit = rule["unit"] + ("" if len(row) == 1 else "s")
                problems.append(
                    f"slot {rule['slot']}[{i}]: has {len(row)} {unit} but "
                    f"{rule['via']} needs {expected}")
    return problems


def resolve_values(slots: dict, data: dict) -> dict:
    """Input merged over the declared defaults."""
    values = {name: spec["default"] for name, spec in slots.items()
              if isinstance(spec, dict) and "default" in spec}
    values.update(data)
    return values


def validate_input(template: dict, data: dict) -> list[str]:
    if not isinstance(data, dict):
        return ["input must be an object"]
    slots = template.get("slots")
    if not isinstance(slots, dict):
        return ["template.slots must be an object"]
    problems: list[str] = []
    unknown = sorted(set(data) - set(slots))
    if unknown:
        problems.append(f"unknown input slots: {', '.join(unknown)}")
    values = resolve_values(slots, data)
    for name, spec in slots.items():
        if not isinstance(spec, dict):
            problems.append(f"slot {name}: spec must be an object")
            continue
        if name not in data:
            if spec.get("required", False) and "default" not in spec:
                problems.append(f"missing required slot: {name}")
            continue
        problems.extend(_validate_value(name, data[name], spec, values))
    # A reference the render step could not resolve is an error here, not a
    # crash later: validate_input and render_template must agree.
    slide = template.get("slide")
    try:
        refs = slot_references(slide)
    except SlideTemplateError as exc:
        return problems + [str(exc)]
    problems.extend(_check_arity(arity_rules(slide), values))
    for name in sorted(refs):
        spec = slots.get(name)
        if not isinstance(spec, dict):
            problems.append(f"slide references undeclared slot: {name}")
        elif (name not in data and "default" not in spec
                and not spec.get("required", False)):
            # Required-and-missing is already reported above; this catches the
            # optional slot that nothing can fill.
            problems.append(f"slot {name} is used by the slide but has no value")
    return problems


def _render_node(node: Any, values: dict) -> Any:
    if isinstance(node, dict):
        if "$slot" in node:
            name = node["$slot"]
            if name not in values:
                raise SlideTemplateError(f"no value for slot: {name}")
            return values[name]
        return {key: _render_node(value, values) for key, value in node.items()}
    if isinstance(node, list):
        return [_render_node(value, values) for value in node]
    return node


def render_template(template: dict, data: dict) -> dict:
    problems = validate_input(template, data)
    if problems:
        raise SlideTemplateError("; ".join(problems))
    refs = slot_references(template.get("slide"))
    unused_required = sorted(name for name, spec in template["slots"].items()
                             if spec.get("required") and name not in refs)
    if unused_required:
        raise SlideTemplateError(
            f"required slots are not mapped into slide: {', '.join(unused_required)}")
    values = resolve_values(template["slots"], data)
    slide = _render_node(template.get("slide"), values)
    if not isinstance(slide, dict) or "layout" not in slide:
        raise SlideTemplateError("rendered slide must be an object with layout")
    return slide


INFERENCE_LEVELS = {"strategic", "descriptive", "diagnostic", "predictive", "causal"}


def validate_template_record(template: dict, entry: dict, path: Path) -> list[str]:
    problems: list[str] = []
    required = {"schemaVersion", "id", "displayName", "pack", "category",
                "description", "slots", "slide"}
    missing = sorted(required - set(template))
    if missing:
        problems.append(f"{path}: missing keys: {', '.join(missing)}")
        return problems
    if template.get("schemaVersion") != 1:
        problems.append(f"{path}: schemaVersion must be 1")
    for key in ("id", "pack", "displayName", "category"):
        if template.get(key) != entry.get(key):
            problems.append(f"{path}: {key} does not match manifest "
                            f"({template.get(key)!r} vs {entry.get(key)!r})")
    if not isinstance(template.get("description"), str) or not template["description"]:
        problems.append(f"{path}: description must be a non-empty string")
    level = template.get("inferenceLevel")
    if level is not None and level not in INFERENCE_LEVELS:
        problems.append(f"{path}: inferenceLevel must be one of "
                        f"{', '.join(sorted(INFERENCE_LEVELS))}")
    slots = template.get("slots")
    slide = template.get("slide")
    if not isinstance(slots, dict):
        problems.append(f"{path}: slots must be an object")
    if not isinstance(slide, dict):
        problems.append(f"{path}: slide must be an object")
    if not isinstance(slots, dict) or not isinstance(slide, dict):
        return problems
    for name, spec in slots.items():
        if not isinstance(spec, dict):
            problems.append(f"{path}: slot {name} must be an object")
        elif not isinstance(spec.get("type"), str):
            problems.append(f"{path}: slot {name} must declare a string type")
    try:
        refs = slot_references(slide)
    except SlideTemplateError as exc:
        return problems + [f"{path}: {exc}"]
    for name in sorted(refs - set(slots)):
        problems.append(f"{path}: slide references undeclared slot: {name}")
    for name in sorted(set(slots) - refs):
        problems.append(f"{path}: slot {name} is declared but never used by the slide")
    for name in sorted(refs & set(slots)):
        spec = slots[name]
        if (isinstance(spec, dict) and not spec.get("required", False)
                and "default" not in spec):
            problems.append(f"{path}: optional slot {name} is used by the slide "
                            f"but has no default")
    return problems
