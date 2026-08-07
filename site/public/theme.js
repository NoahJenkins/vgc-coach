(() => {
  try {
    const storedTheme = window.localStorage.getItem("vgc-coach-theme");
    document.documentElement.dataset.theme =
      storedTheme === "dark" || storedTheme === "light"
        ? storedTheme
        : window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light";
  } catch {
    document.documentElement.dataset.theme = "light";
  }
})();
