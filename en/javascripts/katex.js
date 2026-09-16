function renderKatex() {
  if (typeof renderMathInElement === "function") {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "$$",  right: "$$",  display: true },
        { left: "$",   right: "$",   display: false },
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true }
      ],
      throwOnError: false
    });
  }
}

if (typeof document$ !== "undefined") {
  document$.subscribe(renderKatex);
} else {
  document.addEventListener("DOMContentLoaded", renderKatex);
}
