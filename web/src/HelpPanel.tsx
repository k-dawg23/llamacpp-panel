import type { CSSProperties } from "react";
import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import panelUserGuide from "../../docs/panel-user-guide.md?raw";

const prose: CSSProperties = {
  color: "#c5cad6",
  fontSize: 14,
  lineHeight: 1.55,
};

const mdComponents: Components = {
  h1: ({ children }) => (
    <h1 style={{ color: "#e8eaed", fontSize: "1.5rem", marginTop: 0, marginBottom: "0.75rem" }}>
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 style={{ color: "#e8eaed", fontSize: "1.2rem", marginTop: "1.5rem", marginBottom: "0.5rem", borderBottom: "1px solid #2a3142", paddingBottom: 6 }}>
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 style={{ color: "#e8eaed", fontSize: "1.05rem", marginTop: "1.1rem", marginBottom: "0.4rem" }}>{children}</h3>
  ),
  p: ({ children }) => <p style={{ margin: "0.5rem 0" }}>{children}</p>,
  ul: ({ children }) => <ul style={{ margin: "0.5rem 0", paddingLeft: "1.25rem" }}>{children}</ul>,
  ol: ({ children }) => <ol style={{ margin: "0.5rem 0", paddingLeft: "1.25rem" }}>{children}</ol>,
  li: ({ children }) => <li style={{ margin: "0.25rem 0" }}>{children}</li>,
  a: ({ href, children }) => (
    <a href={href} style={{ color: "#7eb8ff" }} target="_blank" rel="noreferrer noopener">
      {children}
    </a>
  ),
  code: ({ children, className }) => {
    const inline = !className;
    if (inline) {
      return (
        <code style={{ background: "#0e1016", padding: "1px 6px", borderRadius: 4, fontSize: "0.92em" }}>
          {children}
        </code>
      );
    }
    return <code className={className}>{children}</code>;
  },
  pre: ({ children }) => (
    <pre
      style={{
        background: "#0e1016",
        padding: 12,
        borderRadius: 8,
        overflow: "auto",
        fontSize: 13,
        border: "1px solid #2a3142",
      }}
    >
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div style={{ overflowX: "auto", margin: "0.75rem 0" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead style={{ background: "#151821" }}>{children}</thead>,
  th: ({ children }) => (
    <th style={{ textAlign: "left", padding: 8, border: "1px solid #2a3142", color: "#e8eaed" }}>{children}</th>
  ),
  td: ({ children }) => (
    <td style={{ padding: 8, border: "1px solid #2a3142", verticalAlign: "top" }}>{children}</td>
  ),
  hr: () => <hr style={{ border: "none", borderTop: "1px solid #2a3142", margin: "1.25rem 0" }} />,
  blockquote: ({ children }) => (
    <blockquote
      style={{
        margin: "0.75rem 0",
        padding: "0.5rem 0 0.5rem 1rem",
        borderLeft: "3px solid #3d5a9c",
        color: "#9aa3b5",
      }}
    >
      {children}
    </blockquote>
  ),
};

export function HelpPanel() {
  return (
    <div
      style={{
        ...prose,
        maxHeight: "min(70vh, 640px)",
        overflowY: "auto",
        paddingRight: 8,
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
        {panelUserGuide}
      </ReactMarkdown>
    </div>
  );
}
