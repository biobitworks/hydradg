import { createHash } from "node:crypto";

export type MerkleLeaf = {
  id: string;
  sha256: string;
};

export type MerkleCheckpoint = {
  algorithm: "SHA-256";
  ordering: "LEXICOGRAPHIC_FCO_ID";
  odd_leaf_rule: "DUPLICATE_LAST";
  leaf_count: number;
  leaves: MerkleLeaf[];
  levels: string[][];
  root_sha256: string;
};

function sha256Bytes(leftHex: string, rightHex: string): string {
  return createHash("sha256")
    .update(Buffer.concat([Buffer.from(leftHex, "hex"), Buffer.from(rightHex, "hex")]))
    .digest("hex");
}

export function computeMerkleCheckpoint(leaves: MerkleLeaf[]): MerkleCheckpoint {
  const ordered = [...leaves].sort((a, b) => a.id.localeCompare(b.id));
  if (!ordered.length) throw new Error("Merkle checkpoint requires at least one leaf");
  for (const leaf of ordered) {
    if (!/^[0-9a-f]{64}$/i.test(leaf.sha256)) {
      throw new Error(`invalid SHA-256 leaf for ${leaf.id}`);
    }
  }

  const levels: string[][] = [ordered.map((leaf) => leaf.sha256.toLowerCase())];
  while (levels[levels.length - 1].length > 1) {
    const current = levels[levels.length - 1];
    const next: string[] = [];
    for (let index = 0; index < current.length; index += 2) {
      const left = current[index];
      const right = current[index + 1] || left;
      next.push(sha256Bytes(left, right));
    }
    levels.push(next);
  }

  return {
    algorithm: "SHA-256",
    ordering: "LEXICOGRAPHIC_FCO_ID",
    odd_leaf_rule: "DUPLICATE_LAST",
    leaf_count: ordered.length,
    leaves: ordered,
    levels,
    root_sha256: levels[levels.length - 1][0],
  };
}
