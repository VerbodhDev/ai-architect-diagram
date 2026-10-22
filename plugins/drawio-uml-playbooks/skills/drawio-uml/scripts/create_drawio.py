#!/usr/bin/env python3
"""Create and validate native, editable Draw.io diagrams from reusable UML templates."""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPLATES = ("component", "class", "sequence", "deployment", "activity", "flow", "architecture")
BOX_STYLE = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
GROUP_STYLE = "swimlane;whiteSpace=wrap;html=1;rounded=1;fillColor=none;strokeColor=#666666;fontStyle=1;fontSize=14;"
TEXT_STYLE = "text;html=1;align=left;verticalAlign=middle;fontSize=20;fontStyle=1;"
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;"

def add_cell(root, cell_id, value="", style="", *, x=None, y=None, width=None, height=None, edge=False, source=None, target=None):
    attrs = {"id": str(cell_id), "value": str(value), "style": style, "parent": "1"}
    if edge:
        attrs.update({"edge": "1", "source": str(source), "target": str(target)})
        cell = ET.SubElement(root, "mxCell", attrs)
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        return
    attrs["vertex"] = "1"
    cell = ET.SubElement(root, "mxCell", attrs)
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})

def starter(template):
    if template == "sequence":
        return {"nodes": [{"id":"client", "label":"Client", "x":80,"y":140}, {"id":"service", "label":"Service", "x":400,"y":140}], "edges": [{"source":"client", "target":"service", "label":"request"}, {"source":"service", "target":"client", "label":"response", "style": EDGE_STYLE + "dashed=1;endArrow=open;"}]}
    if template == "class":
        return {"nodes": [{"id":"entity", "label":"&lt;b&gt;Order&lt;/b&gt;&lt;hr&gt;+ id: UUID&lt;br&gt;+ status: Status&lt;hr&gt;+ submit()", "x":120,"y":160,"width":210,"height":130}, {"id":"repository", "label":"&lt;b&gt;OrderRepository&lt;/b&gt;&lt;hr&gt;+ find(id)&lt;br&gt;+ save(order)", "x":470,"y":160,"width":210,"height":130}], "edges": [{"source":"repository", "target":"entity", "label":"uses", "style": EDGE_STYLE + "dashed=1;endArrow=open;"}]}
    if template in ("activity", "flow"):
        return {"nodes": [{"id":"start","label":"Start","x":90,"y":180,"width":60,"height":40,"style":"ellipse;html=1;fillColor=#000000;"},{"id":"step","label":"Process step","x":300,"y":165},{"id":"end","label":"End","x":610,"y":180,"width":60,"height":40,"style":"ellipse;html=1;fillColor=#000000;"}], "edges": [{"source":"start","target":"step"},{"source":"step","target":"end"}]}
    if template == "deployment":
        return {"nodes": [{"id":"client","label":"Client","x":70,"y":180},{"id":"app","label":"Application node","x":350,"y":180},{"id":"database","label":"Database","x":650,"y":180}], "edges": [{"source":"client","target":"app","label":"HTTPS"},{"source":"app","target":"database","label":"SQL"}]}
    return {"nodes": [{"id":"client","label":"Client","x":70,"y":180},{"id":"service","label":"Service","x":350,"y":180},{"id":"store","label":"Data store","x":650,"y":180}], "edges": [{"source":"client","target":"service","label":"request"},{"source":"service","target":"store","label":"read/write"}]}

def build(template, title, spec):
    graph = ET.Element("mxGraphModel", {"dx":"1200","dy":"800","grid":"1","gridSize":"10","page":"1","pageWidth":"1169","pageHeight":"827"})
    root = ET.SubElement(graph, "root")
    ET.SubElement(root, "mxCell", {"id":"0"})
    ET.SubElement(root, "mxCell", {"id":"1","parent":"0"})
    add_cell(root, "title", title, TEXT_STYLE, x=40, y=25, width=1000, height=40)
    for group in spec.get("groups", []):
        add_cell(root, group["id"], group["label"], group.get("style", GROUP_STYLE), x=group["x"], y=group["y"], width=group.get("width", 300), height=group.get("height", 220))
    node_ids = set()
    for node in spec.get("nodes", []):
        node_ids.add(node["id"])
        add_cell(root, node["id"], node["label"], node.get("style", BOX_STYLE), x=node["x"], y=node["y"], width=node.get("width", 170), height=node.get("height", 70))
    for index, edge in enumerate(spec.get("edges", []), 1):
        if edge["source"] not in node_ids or edge["target"] not in node_ids:
            raise ValueError(f"edge {index} references an unknown node")
        add_cell(root, f"edge-{index}", edge.get("label", ""), edge.get("style", EDGE_STYLE), edge=True, source=edge["source"], target=edge["target"])
    diagram = ET.Element("diagram", {"id":"page-1", "name":"Page-1"})
    diagram.text = ET.tostring(graph, encoding="unicode")
    mxfile = ET.Element("mxfile", {"host":"app.diagrams.net", "agent":"Codex", "version":"26.0.14"})
    mxfile.append(diagram)
    return ET.tostring(mxfile, encoding="unicode", xml_declaration=True)

def create(args):
    spec = starter(args.template)
    if args.spec:
        loaded = json.loads(args.spec.read_text(encoding="utf-8"))
        spec.update(loaded)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(args.template, args.title, spec), encoding="utf-8")
    print(f"created {args.output}")

def validate(args):
    try:
        root = ET.parse(args.file).getroot()
    except (ET.ParseError, OSError) as exc:
        raise SystemExit(f"invalid Draw.io XML: {exc}")
    if root.tag != "mxfile" or root.find("diagram") is None:
        raise SystemExit("invalid Draw.io document: expected mxfile with a diagram")
    print(f"valid Draw.io document: {args.file}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("create")
    create_parser.add_argument("template", choices=TEMPLATES)
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--output", required=True, type=Path)
    create_parser.add_argument("--spec", type=Path)
    create_parser.set_defaults(func=create)
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("file", type=Path)
    validate_parser.set_defaults(func=validate)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
