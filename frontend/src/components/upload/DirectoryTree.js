import React from 'react';

export default function DirectoryTree({ node }) {
  if (!node) return null;
  return (
    <ul className="ml-4 list-disc text-xs">
      {node.children && node.children.map((child, idx) => (
        <li key={idx}>
          {child.type === 'directory' ? (
            <>
              <span className="font-semibold">📁 {child.name}</span>
              <DirectoryTree node={child} />
            </>
          ) : (
            <span>📄 {child.name}</span>
          )}
        </li>
      ))}
    </ul>
  );
}
