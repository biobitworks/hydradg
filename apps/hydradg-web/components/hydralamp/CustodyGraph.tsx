"use client";

import { useEffect, useRef } from "react";
import cytoscape, { type Core } from "cytoscape";

export type GraphNode = {
  id: string;
  label: string;
  visual_class: string;
  size?: number;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  label: string;
};

const SHAPE: Record<string, string> = {
  reference: "ellipse",
  canonical: "round-rectangle",
  probabilistic_proposal: "diamond",
  quarantined: "octagon",
  contradicted: "triangle",
  verified: "hexagon",
  repaired: "star",
};

const COLOR: Record<string, string> = {
  reference: "#94a3b8",
  canonical: "#e2e8f0",
  probabilistic_proposal: "#fbbf24",
  quarantined: "#fb7185",
  contradicted: "#f97316",
  verified: "#34d399",
  repaired: "#38bdf8",
};

export default function CustodyGraph({
  nodes,
  edges,
  pulseIds,
  focusId,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  pulseIds?: string[];
  focusId?: string | null;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    if (!cyRef.current) {
      cyRef.current = cytoscape({
        container: ref.current,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "text-valign": "bottom",
              "text-margin-y": 6,
              "font-size": 9,
              color: "#cbd5e1",
              "background-color": "#64748b",
              width: "data(size)",
              height: "data(size)",
              "border-width": 2,
              "border-color": "#1e293b",
            },
          },
          {
            selector: "edge",
            style: {
              width: 1.5,
              "line-color": "#475569",
              "target-arrow-color": "#475569",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
              label: "data(label)",
              "font-size": 7,
              color: "#64748b",
            },
          },
          {
            selector: "node.pulse",
            style: {
              "border-width": 4,
              "border-color": "#fde68a",
            },
          },
          {
            selector: "node.focus",
            style: {
              "border-width": 5,
              "border-color": "#e8e5dc",
              "overlay-opacity": 0.08,
            },
          },
        ],
        layout: { name: "cose", animate: false },
        userZoomingEnabled: true,
        userPanningEnabled: true,
      });
    }

    const cy = cyRef.current;
    cy.elements().remove();
    const elements: cytoscape.ElementDefinition[] = [];
    for (const n of nodes) {
      const size = n.size || 28;
      elements.push({
        data: {
          id: n.id,
          label: `${n.label}\n[${n.visual_class}]`,
          visual_class: n.visual_class,
          size,
        },
        classes: n.visual_class,
        style: {
          shape: SHAPE[n.visual_class] || "ellipse",
          "background-color": COLOR[n.visual_class] || "#64748b",
          width: size,
          height: size,
        },
      });
    }
    for (const e of edges) {
      if (!nodes.some((n) => n.id === e.source) || !nodes.some((n) => n.id === e.target)) continue;
      elements.push({
        data: { id: e.id, source: e.source, target: e.target, label: e.label },
      });
    }
    cy.add(elements);
    cy.layout({ name: "cose", animate: false, padding: 24 }).run();

    cy.nodes().removeClass("pulse focus");
    if (pulseIds?.length) {
      for (const id of pulseIds) cy.$id(id).addClass("pulse");
    }
    if (focusId) {
      const n = cy.$id(focusId);
      if (n.nonempty()) {
        n.addClass("focus");
        cy.animate({ center: { eles: n }, zoom: Math.max(cy.zoom(), 1.2) }, { duration: 280 });
      }
    }
  }, [nodes, edges, pulseIds, focusId]);

  useEffect(() => {
    return () => {
      cyRef.current?.destroy();
      cyRef.current = null;
    };
  }, []);

  return <div ref={ref} className="hlCyto" aria-label="Live KG / FCG graph" />;
}
