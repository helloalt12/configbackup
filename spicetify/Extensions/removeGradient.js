(function removeGradients() {
  function stripGradients(node) {
    if (!(node instanceof HTMLElement)) return;
    const s = node.style;
    if (
      s.backgroundImage?.includes("gradient") ||
      s.background?.includes("gradient")
    ) {
      s.backgroundImage = "none";
      s.background = "#2e3440";
    }
    node.querySelectorAll("[style]").forEach(stripGradients);
  }

  const observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      m.addedNodes.forEach(stripGradients);
      if (m.type === "attributes" && m.target instanceof HTMLElement) {
        stripGradients(m.target);
      }
    }
  });

  observer.observe(document.body, {
